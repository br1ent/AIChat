"""
RAG 知识库检索准确率评估脚本（带 Rerank 对比）

使用方法：
    cd backend
    python -m tests.evaluate_rag

评估指标：
    - Recall@k: top-k 结果中包含相关文档的比例（基于关键词匹配）
    - Precision@k: top-k 结果中相关文档的占比
    - MRR (Mean Reciprocal Rank): 第一个相关文档的平均倒数排名
    - Hit Rate: 至少命中一个相关文档的查询比例
"""
import json
import os
import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass, field

# 确定路径（支持直接运行和 python -m 两种方式）
try:
    _tests_dir = Path(__file__).parent
except NameError:
    _tests_dir = Path.cwd().parent / "tests"

backend_dir = _tests_dir.parent / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(str(backend_dir))

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
class SingleResult:
    query: str
    hit: bool
    recall_at_k: float
    precision_at_k: float
    mrr: float
    top_titles: List[str]


@dataclass
class Report:
    recall: float
    precision: float
    mrr: float
    hit_rate: float
    results: list


class RAGEvaluator:
    def __init__(self):
        db = lancedb.connect('./web/documents/lancedb_storage')
        self.embeddings = CustomEmbeddings()
        self.vector_db = LanceDB(
            connection=db,
            embedding=self.embeddings,
            table_name="my_knowledge_base",
        )

    def _is_relevant(self, doc_text: str, keywords: list[str]) -> bool:
        for kw in keywords:
            if kw.lower() in doc_text.lower():
                return True
        return False

    def _evaluate_retrieved(self, query: str, doc_texts: list[str],
                            doc_metas: list[dict], relevant_keywords: list[str],
                            k: int) -> SingleResult:
        """对已检索的文档列表计算指标"""
        # Recall@k: 至少命中的关键词去重计数 / 总关键词数
        covered = set()
        for kw in relevant_keywords:
            for doc in doc_texts[:k]:
                if kw.lower() in doc.lower():
                    covered.add(kw)
                    break
        recall = len(covered) / len(relevant_keywords) if relevant_keywords else 0

        # Precision@k: 命中的文档数 / k
        hits = 0
        for doc in doc_texts[:k]:
            if self._is_relevant(doc, relevant_keywords):
                hits += 1
        precision = hits / k if k > 0 else 0

        # MRR: 第一个命中文档的倒数排名
        mrr = 0.0
        for i, doc in enumerate(doc_texts):
            if self._is_relevant(doc, relevant_keywords):
                mrr = 1.0 / (i + 1)
                break

        return SingleResult(
            query=query,
            hit=recall > 0,
            recall_at_k=recall,
            precision_at_k=precision,
            mrr=mrr,
            top_titles=[m.get("document_title", "?") for m in doc_metas[:k]],
        )

    def evaluate_vector_only(self, query: str, relevant_keywords: list[str],
                              k: int = 3) -> SingleResult:
        """纯向量检索（无 rerank）"""
        docs = self.vector_db.similarity_search(query, k=k)
        doc_texts = [d.page_content for d in docs]
        doc_metas = [d.metadata for d in docs]
        return self._evaluate_retrieved(query, doc_texts, doc_metas, relevant_keywords, k)

    def evaluate_with_rerank(self, query: str, relevant_keywords: list[str],
                              k: int = 3) -> SingleResult:
        """向量召回 + Rerank 重排序"""
        # 向量召回 6 个候选
        recall_k = min(6, self.vector_db._table.count_rows())
        docs = self.vector_db.similarity_search(query, k=recall_k)
        doc_texts = [d.page_content for d in docs]
        doc_metas = [d.metadata for d in docs]

        # Rerank
        ranked = rerank(query, doc_texts, top_n=k)
        if ranked:
            reordered_texts = []
            reordered_metas = []
            for item in ranked:
                idx = item["index"]
                if idx < len(doc_texts):
                    reordered_texts.append(doc_texts[idx])
                    reordered_metas.append(doc_metas[idx])
        else:
            reordered_texts = doc_texts[:k]
            reordered_metas = doc_metas[:k]

        return self._evaluate_retrieved(query, reordered_texts, reordered_metas, relevant_keywords, k)

    def run(self, test_queries_file: str):
        with open(test_queries_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)

        print(f"共 {len(queries)} 个测试查询\n")

        v_results = []
        r_results = []

        for i, item in enumerate(queries, 1):
            q = item['query']
            keywords = item['relevant_keywords']

            v = self.evaluate_vector_only(q, keywords)
            r = self.evaluate_with_rerank(q, keywords)
            v_results.append(v)
            r_results.append(r)

            # 每个查询的对比
            v_mark = "Y" if v.hit else "N"
            r_mark = "Y" if r.hit else "N"
            print(f"[{i:2d}] {q}")
            print(f"    keywords: {', '.join(keywords[:6])}{'...' if len(keywords) > 6 else ''}")
            print(f"    vector:   Recall@3={v.recall_at_k:.0%}  MRR={v.mrr:.2f}  hit={v_mark}")
            print(f"    +rerank:  Recall@3={r.recall_at_k:.0%}  MRR={r.mrr:.2f}  hit={r_mark}")
            if v.hit != r.hit:
                change = "UP" if r.hit else "DOWN"
                print(f"    >>> hit change: {change}")
            if v.top_titles != r.top_titles:
                print(f"    order change: vector={v.top_titles}  rerank={r.top_titles}")

        # 汇总
        def summarize(name: str, results: list) -> Report:
            n = len(results)
            return Report(
                recall=sum(r.recall_at_k for r in results) / n if n else 0,
                precision=sum(r.precision_at_k for r in results) / n if n else 0,
                mrr=sum(r.mrr for r in results) / n if n else 0,
                hit_rate=sum(1 for r in results if r.hit) / n if n else 0,
                results=[{
                    'query': r.query,
                    'recall_at_3': r.recall_at_k,
                    'precision_at_3': r.precision_at_k,
                    'mrr': r.mrr,
                    'hit': r.hit,
                } for r in results],
            )

        vs = summarize("向量检索", v_results)
        rs = summarize("向量+Rerank", r_results)

        print("\n" + "=" * 70)
        print("                       评估结果对比")
        print("=" * 70)
        print(f"{'指标':<20} {'向量检索':>12} {'向量+Rerank':>12} {'变化':>12}")
        print("-" * 70)
        for label, v_val, r_val in [
            ("Recall@3", vs.recall, rs.recall),
            ("Precision@3", vs.precision, rs.precision),
            ("MRR", vs.mrr, rs.mrr),
            ("Hit Rate", vs.hit_rate, rs.hit_rate),
        ]:
            delta = r_val - v_val
            delta_str = f"{delta:+.1%}" if abs(delta) >= 0.001 else "—"
            print(f"{label:<20} {v_val:>11.1%} {r_val:>11.1%} {delta_str:>12}")

        print("-" * 70)

        # 保存报告
        report_file = _tests_dir / "rag_evaluation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "vector_only": {
                    "recall_at_3": vs.recall,
                    "precision_at_3": vs.precision,
                    "mrr": vs.mrr,
                    "hit_rate": vs.hit_rate,
                },
                "vector_plus_rerank": {
                    "recall_at_3": rs.recall,
                    "precision_at_3": rs.precision,
                    "mrr": rs.mrr,
                    "hit_rate": rs.hit_rate,
                },
                "details": {
                    "vector_only": vs.results,
                    "vector_plus_rerank": rs.results,
                },
            }, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存: {report_file}")


if __name__ == "__main__":
    test_file = _tests_dir / "test_queries.json"
    if not test_file.exists():
        print(f"测试文件不存在: {test_file}")
        sys.exit(1)

    evaluator = RAGEvaluator()
    evaluator.run(str(test_file))
