import os
from typing import TypedDict, Annotated, Sequence

import lancedb
from django.utils.timezone import now, localtime
from langchain_community.vectorstores import LanceDB
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode

from web.documents.utils.custom_embeddings import CustomEmbeddings
from web.documents.utils.reranker import rerank


# 模块级复用：避免每次 tool 调用都重新初始化连接
_db = lancedb.connect('./web/documents/lancedb_storage')
_embeddings = CustomEmbeddings()
_vector_db = LanceDB(
    connection=_db,
    embedding=_embeddings,
    table_name="my_knowledge_base",
)


class ChatGraph:
    @staticmethod
    def create_app():
        @tool
        def get_time():
            """当需要查询精确时间的时候,调用此函数。返回格式为:年-月-日 时:分:秒"""
            return localtime(now()).strftime("%Y-%m-%d %H:%M:%S")

        @tool
        def search_knowledge_base(query: str) -> str:
            """当用户查询知识库相关问题的时候,调用此函数。输入为要查询的问题,输出为查询结果。包含向量召回+重排序以提升精度。"""
            if _vector_db._table.count_rows() == 0:
                return "知识库中没有文档内容"

            # 阶段 1：向量召回（多召回一些候选给 rerank 留空间）
            recall_k = min(10, _vector_db._table.count_rows())
            docs = _vector_db.similarity_search(query, k=recall_k)

            if not docs:
                return "未找到相关内容"

            doc_texts = [doc.page_content for doc in docs]
            doc_metas = [doc.metadata for doc in docs]

            # 阶段 2：Rerank 重排序
            reranked = rerank(query, doc_texts, top_n=3)
            if reranked:
                # rerank 成功，按要求排序
                lines = []
                for i, item in enumerate(reranked, 1):
                    idx = item.get("index", i - 1)
                    if idx < len(docs):
                        title = doc_metas[idx].get("document_title", "未知文档")
                        content = doc_texts[idx]
                        lines.append(f"[来源 {i}] 文档：{title}\n{content[:800]}")
                return "从知识库中找到以下相关信息：\n\n" + "\n\n".join(lines)
            else:
                # fallback：rerank 不可用，使用原始向量距离排序
                lines = []
                for i, doc in enumerate(docs[:3], 1):
                    title = doc.metadata.get("document_title", "未知文档")
                    lines.append(f"[来源 {i}] 文档：{title}\n{doc.page_content[:800]}")
                return "从知识库中找到以下相关信息：\n\n" + "\n\n".join(lines)


        tools = [get_time, search_knowledge_base]

        llm = ChatOpenAI(
            model='deepseek-v4-flash',
            api_key=os.getenv('API_KEY'),
            base_url=os.getenv('API_BASE'),
            streaming=True,
            extra_body={"thinking": {"type": "enabled"}},
            model_kwargs={
                "stream_options": {
                    "include_usage": True, # 输出token消耗数量
                }
            }
        ).bind_tools(tools)

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages] # 将大模型的回复追加到用户消息的末尾

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages'])
            return {
                "messages": [res]
            }

        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"

        tool_node = ToolNode(tools)

        graph = StateGraph(AgentState)
        graph.add_node("agent", model_call)
        graph.add_node("tools", tool_node)

        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        graph.add_edge("tools", "agent")

        return graph.compile()