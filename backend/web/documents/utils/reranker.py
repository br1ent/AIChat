"""Rerank 重排序 — 调用阿里云 DashScope/Bailian rerank API（OpenAI SDK 兼容接口）"""
import os
from openai import OpenAI


RERANK_MODEL = os.getenv("RERANK_MODEL")
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N"))
BASE_URL = os.getenv("BASE_URL")

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("API_KEY")
        if not BASE_URL or not api_key:
            return None
        _client = OpenAI(api_key=api_key, base_url=BASE_URL)
    return _client


def rerank(query: str, documents: list[str], top_n: int = RERANK_TOP_N) -> list[dict] | None:
    """对候选文档重排序，返回按 relevance_score 降序的结果列表。
    每个结果包含 index（原始序号）和 relevance_score。
    失败时返回 None，调用方应 fallback 到向量距离排序。
    """
    if not documents:
        return None

    client = _get_client()
    if client is None:
        return None

    try:
        resp = client.post(
            "/reranks",
            body={
                "model": RERANK_MODEL,
                "query": query,
                "documents": documents,
                "top_n": min(top_n, len(documents)),
            },
            cast_to=object,
        )
        results = resp["results"] if isinstance(resp, dict) and "results" in resp else []
        if results:
            return sorted(results, key=lambda r: r["relevance_score"], reverse=True)
    except Exception as e:
        print(f"[Rerank] ERROR: {e}")

    return None
