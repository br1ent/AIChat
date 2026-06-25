"""
RAG 知识库检索准确率评估脚本

使用方法：
    cd backend
    python -m tests.evaluate_rag

评估指标：
    - Recall@k: top-k 结果中包含相关文档的比例
    - Precision@k: top-k 结果中相关文档的占比
    - MRR (Mean Reciprocal Rank): 第一个相关文档的平均倒数排名
    - Hit Rate: 至少命中一个相关文档的查询比例
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(str(backend_dir))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")
except ImportError:
    # 如果没有 python-dotenv，手动加载
    env_file = backend_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

try:
    import lancedb
    from langchain_community.vectorstores import LanceDB
    from langchain_core.documents import Document
except ImportError as e:
    print(f"请先安装依赖: pip install lancedb langchain-community")
    print(f"错误信息: {e}")
    sys.exit(1)

# 导入自定义 Embeddings
try:
    from web.documents.utils.custom_embeddings import CustomEmbeddings
except ImportError:
    print("无法导入 CustomEmbeddings，请检查路径")
    sys.exit(1)


@dataclass
class RetrievalResult:
    """单次检索结果"""
    query: str
    retrieved_docs: List[str]
    relevant_keywords: List[str]
    expected_topics: List[str]
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    precision_at_3: float = 0.0
    mrr: float = 0.0
    hit: bool = False


@dataclass
class EvaluationReport:
    """评估报告"""
    total_queries: int = 0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    precision_at_3: float = 0.0
    mrr: float = 0.0
    hit_rate: float = 0.0
    results: List[RetrievalResult] = field(default_factory=list)
    details: List[Dict] = field(default_factory=list)


class RAGEvaluator:
    """RAG 检索评估器"""

    def __init__(self, k: int = 5):
        self.k = k
        self.db = None
        self.vector_db = None
        self.embeddings = None

    def initialize(self):
        """初始化 LanceDB 连接"""
        print("正在初始化 LanceDB 连接...")
        self.db = lancedb.connect('./web/documents/lancedb_storage')
        self.embeddings = CustomEmbeddings()
        self.vector_db = LanceDB(
            connection=self.db,
            embedding=self.embeddings,
            table_name="my_knowledge_base",
        )
        print("LanceDB 连接成功")

    def retrieve(self, query: str) -> List[str]:
        """执行检索，返回文档内容"""
        docs = self.vector_db.similarity_search(query, k=self.k)
        return [doc.page_content for doc in docs]

    def calculate_recall(self, retrieved: List[str], relevant_keywords: List[str], k: int) -> float:
        """计算 Recall@k: 检索结果中包含相关关键词的比例"""
        if not relevant_keywords:
            return 0.0

        hits = 0
        for doc in retrieved[:k]:
            for keyword in relevant_keywords:
                if keyword.lower() in doc.lower():
                    hits += 1
                    break  # 每个文档只计一次

        return hits / len(relevant_keywords)

    def calculate_precision(self, retrieved: List[str], relevant_keywords: List[str], k: int) -> float:
        """计算 Precision@k: 检索结果中相关文档的占比"""
        if k == 0:
            return 0.0

        hits = 0
        for doc in retrieved[:k]:
            for keyword in relevant_keywords:
                if keyword.lower() in doc.lower():
                    hits += 1
                    break

        return hits / k

    def calculate_mrr(self, retrieved: List[str], relevant_keywords: List[str]) -> float:
        """计算 MRR: 第一个相关文档的倒数排名"""
        for i, doc in enumerate(retrieved):
            for keyword in relevant_keywords:
                if keyword.lower() in doc.lower():
                    return 1.0 / (i + 1)
        return 0.0

    def evaluate_single(self, query: str, relevant_keywords: List[str], 
                        expected_topics: List[str]) -> RetrievalResult:
        """评估单个查询"""
        # 执行检索
        retrieved = self.retrieve(query)

        # 计算指标
        result = RetrievalResult(
            query=query,
            retrieved_docs=retrieved,
            relevant_keywords=relevant_keywords,
            expected_topics=expected_topics,
        )

        result.recall_at_3 = self.calculate_recall(retrieved, relevant_keywords, 3)
        result.recall_at_5 = self.calculate_recall(retrieved, relevant_keywords, 5)
        result.precision_at_3 = self.calculate_precision(retrieved, relevant_keywords, 3)
        result.mrr = self.calculate_mrr(retrieved, relevant_keywords)
        result.hit = result.recall_at_3 > 0

        return result

    def evaluate(self, test_queries_file: str) -> EvaluationReport:
        """评估所有测试查询"""
        # 加载测试查询
        with open(test_queries_file, 'r', encoding='utf-8') as f:
            test_queries = json.load(f)

        print(f"\n开始评估 {len(test_queries)} 个测试查询...\n")
        print("=" * 80)

        report = EvaluationReport(total_queries=len(test_queries))

        for i, item in enumerate(test_queries, 1):
            query = item['query']
            relevant_keywords = item['relevant_keywords']
            expected_topics = item.get('expected_topics', [])

            print(f"\n[{i}/{len(test_queries)}] 查询: {query}")
            print(f"  相关关键词: {', '.join(relevant_keywords)}")

            result = self.evaluate_single(query, relevant_keywords, expected_topics)
            report.results.append(result)

            # 打印详细结果
            print(f"  Recall@3: {result.recall_at_3:.2%}")
            print(f"  Recall@5: {result.recall_at_5:.2%}")
            print(f"  Precision@3: {result.precision_at_3:.2%}")
            print(f"  MRR: {result.mrr:.2f}")
            print(f"  命中: {'✓' if result.hit else '✗'}")

            # 显示检索到的文档摘要
            print(f"  检索结果:")
            for j, doc in enumerate(result.retrieved_docs[:3], 1):
                # 截取前 100 字符作为摘要
                summary = doc[:100].replace('\n', ' ').strip()
                print(f"    {j}. {summary}...")

            # 添加到详情列表
            report.details.append({
                'query': query,
                'relevant_keywords': relevant_keywords,
                'expected_topics': expected_topics,
                'recall_at_3': result.recall_at_3,
                'recall_at_5': result.recall_at_5,
                'precision_at_3': result.precision_at_3,
                'mrr': result.mrr,
                'hit': result.hit,
                'retrieved_summaries': [doc[:200].replace('\n', ' ').strip() 
                                        for doc in result.retrieved_docs],
            })

        # 计算总体指标
        if report.total_queries > 0:
            report.recall_at_3 = sum(r.recall_at_3 for r in report.results) / report.total_queries
            report.recall_at_5 = sum(r.recall_at_5 for r in report.results) / report.total_queries
            report.precision_at_3 = sum(r.precision_at_3 for r in report.results) / report.total_queries
            report.mrr = sum(r.mrr for r in report.results) / report.total_queries
            report.hit_rate = sum(1 for r in report.results if r.hit) / report.total_queries

        return report

    def print_summary(self, report: EvaluationReport):
        """打印评估摘要"""
        print("\n" + "=" * 80)
        print("                        评估结果摘要")
        print("=" * 80)
        print(f"\n总查询数: {report.total_queries}")
        print(f"\n核心指标:")
        print(f"  Recall@3:     {report.recall_at_3:.2%}")
        print(f"  Recall@5:     {report.recall_at_5:.2%}")
        print(f"  Precision@3:  {report.precision_at_3:.2%}")
        print(f"  MRR:          {report.mrr:.2f}")
        print(f"  Hit Rate:     {report.hit_rate:.2%}")

        print(f"\n达标情况:")
        print(f"  Recall@3 ≥ 85%:  {'✓ 达标' if report.recall_at_3 >= 0.85 else '✗ 未达标'}")
        print(f"  MRR ≥ 0.8:       {'✓ 达标' if report.mrr >= 0.8 else '✗ 未达标'}")
        print(f"  Hit Rate ≥ 90%:  {'✓ 达标' if report.hit_rate >= 0.9 else '✗ 未达标'}")

        print("\n" + "=" * 80)


def main():
    """主函数"""
    # 切换到 backend 目录
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(str(backend_dir))

    # 测试查询文件路径
    test_queries_file = Path(__file__).parent / "test_queries.json"

    if not test_queries_file.exists():
        print(f"错误: 测试查询文件不存在: {test_queries_file}")
        sys.exit(1)

    # 创建评估器
    evaluator = RAGEvaluator(k=5)

    try:
        # 初始化
        evaluator.initialize()

        # 执行评估
        report = evaluator.evaluate(str(test_queries_file))

        # 打印摘要
        evaluator.print_summary(report)

        # 保存详细报告
        report_file = Path(__file__).parent / "rag_evaluation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_queries': report.total_queries,
                    'recall_at_3': report.recall_at_3,
                    'recall_at_5': report.recall_at_5,
                    'precision_at_3': report.precision_at_3,
                    'mrr': report.mrr,
                    'hit_rate': report.hit_rate,
                },
                'details': report.details,
            }, f, ensure_ascii=False, indent=2)

        print(f"\n详细报告已保存至: {report_file}")

    except Exception as e:
        print(f"评估过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
