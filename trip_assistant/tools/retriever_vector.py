import os
import re
import numpy as np
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

# 读取 FAQ 文本文件
faq_text = None
# 获取当前文件所在的目录，并定位到 trip_assistant 根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
faq_path = os.path.join(BASE_DIR, "order_faq.md")

with open(faq_path, encoding='utf8') as f:
    faq_text = f.read()

# 将 FAQ 文本按标题分割，并进行深度清洗
# 资深架构师提示：针对阿里云等接口，需严格过滤空值并限制单段长度
docs_raw = re.split(r"(?=\n##)", faq_text)
docs = []
for txt in docs_raw:
    clean_txt = txt.strip()
    if clean_txt:
        # 截断超长文本（防止单段超过 Token 限制），并强制转换为字符串
        docs.append({"page_content": str(clean_txt)[:2000]})

if not docs:
    raise ValueError("FAQ 文件解析失败或内容为空，请检查 order_faq.md")

from langchain_community.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 使用阿里云百炼专用 SDK 以获得最佳兼容性
embeddings_model = DashScopeEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "text-embedding-v3"),
    dashscope_api_key=os.getenv("OPENAI_API_KEY")
)


# 定义向量存储检索器类
class VectorStoreRetriever:
    def __init__(self, docs: list, vectors: list):
        # 存储文档和对应的向量
        self._arr = np.array(vectors)
        self._docs = docs

    @classmethod
    def from_docs(cls, docs):
        # 从文档生成嵌入向量
        embeddings = embeddings_model.embed_documents([doc["page_content"] for doc in docs])
        vectors = embeddings
        return cls(docs, vectors)

    def query(self, query: str, k: int = 5) -> list[dict]:
        # 对查询生成嵌入向量
        embed = embeddings_model.embed_query(query)
        # 计算查询向量与文档向量的相似度
        scores = np.array(embed) @ self._arr.T
        # 获取相似度最高的 k 个文档的索引
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        # 返回相似度最高的 k 个文档及其相似度
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]


# 创建向量存储检索器实例
retriever = VectorStoreRetriever.from_docs(docs)


# 定义工具函数，用于查询航空公司的政策
@tool
def lookup_policy(query: str) -> str:
    """查询公司政策，检查某些选项是否允许。
    在进行航班变更或其他'写'操作之前使用此函数。"""
    # 查询相似度最高的 k 个文档
    docs = retriever.query(query, k=2)
    # 返回这些文档的内容
    return "\n\n".join([doc["page_content"] for doc in docs])


if __name__ == '__main__':  # 测试代码
    print(lookup_policy('怎么才能退票呢？'))
