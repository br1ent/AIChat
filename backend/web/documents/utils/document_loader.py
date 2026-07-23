"""多文档解析与导入 — 支持 TXT、MD、PDF，写入 LanceDB"""
import os
from pathlib import Path

import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

from web.documents.utils.custom_embeddings import CustomEmbeddings
from web.models.knowledge import KnowledgeDocument


def _parse_file(file_path: str) -> str | None:
    """解析文件内容为纯文本，不支持的格式返回 None"""
    ext = Path(file_path).suffix.lower()
    try:
        if ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        elif ext == ".pdf":
            try:
                import fitz
            except ImportError:
                print("PyMuPDF (fitz) 未安装，无法解析 PDF")
                return None
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
    except Exception as e:
        print(f"[DocumentLoader] 解析失败 {file_path}: {e}")
    return None


def upload_and_index(file_path: str, title: str | None = None) -> int | None:
    """上传并索引单个文档，返回 KnowledgeDocument 的 pk。

    如果 title 未指定，使用文件名作为标题。
    失败时返回 None 并更新 KnowledgeDocument 状态为 failed。
    """
    if title is None:
        title = Path(file_path).name

    file_type = Path(file_path).suffix.lower().lstrip(".")

    # 1. 解析文件
    text = _parse_file(file_path)
    if not text:
        return None

    # 2. 创建数据库记录
    doc = KnowledgeDocument.objects.create(
        title=title,
        file_type=file_type,
        status="processing",
    )

    try:
        # 3. 切片
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )
        chunks = splitter.split_text(text)
        if not chunks:
            doc.status = "completed"
            doc.save()
            return doc.pk

        # 4. 向量化 + 写入 LanceDB（追加模式）
        embeddings = CustomEmbeddings()
        db = lancedb.connect("./web/documents/lancedb_storage")
        vector_db = LanceDB(
            connection=db,
            embedding=embeddings,
            table_name="my_knowledge_base",
            mode="append",
        )

        # LanceDB.from_texts 追加模式
        texts_with_meta = []
        metas = []
        for i, chunk in enumerate(chunks):
            texts_with_meta.append(chunk)
            metas.append({
                "document_title": title,
                "document_id": str(doc.pk),
                "chunk_index": i,
            })

        vector_db.add_texts(texts=texts_with_meta, metadatas=metas)

        # 5. 更新状态
        doc.chunk_count = len(chunks)
        doc.status = "completed"
        doc.save()
        print(f"[DocumentLoader] {title}: {len(chunks)} chunks indexed")

    except Exception as e:
        doc.status = "failed"
        doc.save()
        print(f"[DocumentLoader] 索引失败 {title}: {e}")
        return None

    return doc.pk


def import_from_directory(directory: str = "./web/documents") -> list[int]:
    """扫描目录下所有 txt/md 文件并导入，返回成功导入的 document_id 列表"""
    ids = []
    for fname in sorted(os.listdir(directory)):
        fpath = os.path.join(directory, fname)
        if not os.path.isfile(fpath):
            continue
        ext = Path(fname).suffix.lower()
        if ext not in (".txt", ".md", ".pdf"):
            continue
        doc_id = upload_and_index(fpath, title=fname)
        if doc_id:
            ids.append(doc_id)
    return ids
