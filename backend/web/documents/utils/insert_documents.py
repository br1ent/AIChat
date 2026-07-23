"""知识库文档导入脚本 — 扫描 web/documents 目录下所有 txt/md/pdf 文件并索引到 LanceDB

用法:
    python -m web.documents.utils.insert_documents          # 追加模式：扫描目录并导入新文件
    python -m web.documents.utils.insert_documents --clear   # 清空模式：先删除旧表再全部重新导入
"""
import os
import sys

import lancedb
from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
get_wsgi_application()

from web.documents.utils.document_loader import import_from_directory


def insert_documents(clear: bool = False):
    if clear:
        db = lancedb.connect("./web/documents/lancedb_storage")
        try:
            db.drop_table("my_knowledge_base")
            print("已清空旧表")
        except Exception:
            pass

    ids = import_from_directory("./web/documents")
    print(f"已导入 {len(ids)} 个文档: {ids}")


if __name__ == "__main__":
    clear_flag = "--clear" in sys.argv
    insert_documents(clear=clear_flag)
