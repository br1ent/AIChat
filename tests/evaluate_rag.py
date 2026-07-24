"""
RAG 知识库检索准确率评估脚本

使用方法：
    cd backend
    python -m tests.evaluate_rag

流程：
    1. 向量召回 10 个候选文档
    2. Rerank 重排序后取 top-3
    3. 在 top-3 上计算指标

评估指标：
    - Recall@3: top-3 结果中包含相关文档的比例（基于关键词匹配）
    - Precision@3: top-3 结果中相关文档的占比
    - MRR (Mean Reciprocal Rank): 第一个相关文档的平均倒数排名
    - Hit Rate: 至少命中一个相关文档的查询比例
"""
import json
import os
import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass, field

# 路径处理（支持直接运行和 python -m 两种方式）
try:
    _tests_dir = Path(__file__).parent
except NameError:
    _tests_dir = Path.cwd().parent / "tests"

backend_dir = _tests_dir.parent / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(str(backend_dir))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")
except ImportError:
    env_file = backend_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

import lancedb
from langchain_community.vectorstores import LanceDB

from web.documents.utils.custom_embeddings import CustomEmbeddings
from web.documents.utils.reranker import rerank


@dataclass
class QueryResult:
    """单个查询的评测结果"""
    query: str
    hit: bool
    recall_at_3: float
    precision_at_3: float
    mrr: float
    top_titles: List[str]


class RAGEvaluator:
    VECTOR_RECALL_K = 10    # 向量召回 10 个候选
    FINAL_TOP_K = 3         # Rerank 后取 top-3

    def __init__(self):
        db = lancedb.connect('./web/documents/lancedb_storage')
        self.embeddings = CustomEmbeddings()
        self.vector_db = LanceDB(
            connection=db,
            embedding=self.embeddings,
            table_name="my_knowledge_base",
        )

    def _is_relevant(self, doc_text: str, keywords: list[str]) -> bool:
        """判断文档是否与关键词相关（大小写不敏感的子串匹配）"""
        for kw in keywords:
            if kw.lower() in doc_text.lower():
                return True
        return False

    def _compute_metrics(self, query: str, doc_texts: list[str],
                         doc_metas: list[dict], keywords: list[str]) -> QueryResult:
        """对 top-k 文档计算指标"""
        # Recall: 关键词覆盖率
        covered = set()
        for kw in keywords:
            for doc in doc_texts:
                if kw.lower() in doc.lower():
                    covered.add(kw)
                    break
        recall = len(covered) / len(keywords) if keywords else 0

        # Precision: top-3 中命中的比例
        hits = sum(1 for doc in doc_texts if self._is_relevant(doc, keywords))

        # MRR: 第一个命中文档的倒数排名
        mrr = 0.0
        for i, doc in enumerate(doc_texts):
            if self._is_relevant(doc, keywords):
                mrr = 1.0 / (i + 1)
                break

        return QueryResult(
            query=query,
            hit=recall > 0,
            recall_at_3=recall,
            precision_at_3=hits / self.FINAL_TOP_K,
            mrr=mrr,
            top_titles=[m.get("document_title", "?") for m in doc_metas],
        )

    def evaluate(self, query: str, keywords: list[str]) -> QueryResult:
        """执行检索管线：向量召回 N 个 → Rerank → top-3"""
        # 1. 向量召回
        total = self.vector_db._table.count_rows()
        recall_k = min(self.VECTOR_RECALL_K, total)
        docs = self.vector_db.similarity_search(query, k=recall_k)
        doc_texts = [d.page_content for d in docs]
        doc_metas = [d.metadata for d in docs]

        # 2. Rerank 重排序
        ranked = rerank(query, doc_texts, top_n=self.FINAL_TOP_K)
        if ranked:
            final_texts = []
            final_metas = []
            for item in ranked:
                idx = item["index"]
                if idx < len(doc_texts):
                    final_texts.append(doc_texts[idx])
                    final_metas.append(doc_metas[idx])
        else:
            # Rerank 不可用时，直接取向量召回的 top-3
            final_texts = doc_texts[:self.FINAL_TOP_K]
            final_metas = doc_metas[:self.FINAL_TOP_K]

        # 3. 计算指标
        return self._compute_metrics(query, final_texts, final_metas, keywords)

    def run(self, test_file: str):
        with open(test_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)

        print(f"测试集: {len(queries)} 个查询")
        print(f"管  线: 向量召回 {self.VECTOR_RECALL_K} 个 → Rerank → top-{self.FINAL_TOP_K}")
        print()

        all_results = []

        for i, item in enumerate(queries, 1):
            q = item['query']
            keywords = item['relevant_keywords']
            result = self.evaluate(q, keywords)
            all_results.append(result)

            mark = "[OK]" if result.hit else "[NO]"
            print(f"[{i:2d}] {mark} {q}")
            print(f"     关键词: {', '.join(keywords[:5])}{'…' if len(keywords) > 5 else ''}")
            print(f"     Recall@3={result.recall_at_3:.0%}  Precision@3={result.precision_at_3:.0%}  MRR={result.mrr:.2f}")
            print(f"     top-3: {result.top_titles}")

        # 汇总
        n = len(all_results)
        recall_avg = sum(r.recall_at_3 for r in all_results) / n
        precision_avg = sum(r.precision_at_3 for r in all_results) / n
        mrr_avg = sum(r.mrr for r in all_results) / n
        hit_rate = sum(1 for r in all_results if r.hit) / n

        print()
        print("=" * 60)
        print("                    评测汇总")
        print("=" * 60)
        print(f"{'指标':<20} {'数值':>12} {'达标':>8}")
        print("-" * 60)
        for label, val, threshold in [
            ("Recall@3", recall_avg, 0.85),
            ("Precision@3", precision_avg, None),
            ("MRR", mrr_avg, 0.8),
            ("Hit Rate", hit_rate, 0.90),
        ]:
            ok = val >= threshold if threshold else "—"
            ok_str = "OK" if ok is True else ("FAIL" if ok is False else ok)
            print(f"{label:<20} {val:>11.1%} {ok_str:>8}")
        print("-" * 60)

        # 保存报告
        report = {
            "config": {
                "vector_recall_k": self.VECTOR_RECALL_K,
                "final_top_k": self.FINAL_TOP_K,
                "test_count": n,
            },
            "summary": {
                "recall_at_3": recall_avg,
                "precision_at_3": precision_avg,
                "mrr": mrr_avg,
                "hit_rate": hit_rate,
            },
            "details": [
                {
                    "query": r.query,
                    "hit": r.hit,
                    "recall_at_3": r.recall_at_3,
                    "precision_at_3": r.precision_at_3,
                    "mrr": r.mrr,
                    "top_titles": r.top_titles,
                }
                for r in all_results
            ],
        }

        report_file = _tests_dir / "rag_evaluation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存: {report_file}")


if __name__ == "__main__":
    test_file = _tests_dir / "test_queries.json"
    if not test_file.exists():
        print(f"测试文件不存在: {test_file}")
        sys.exit(1)

    evaluator = RAGEvaluator()
    evaluator.run(str(test_file))
