import os
from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 初始化主模型 (优先从环境变量读取)
llm = ChatOpenAI(
    temperature=0,
    model=os.getenv("LLM_MODEL", "gpt-4o"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

# 初始化搜索工具
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")
tavily_tool = TavilySearchResults(max_results=1)