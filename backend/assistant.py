import shutil, os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate


# --- 配置部分 ---
SILICON_FLOW_API_KEY = "sk-rhtilxdcrglqhoqlzipmdqfktgikrnubnbkgbwtscukzgqwr"
FOLDER_PATH = "./wind_farm_docs"
MODEL_NAME = "Pro/deepseek-ai/DeepSeek-V3.2"
EMBEDDING_MODEL = "BAAI/bge-m3"  # 如果不支持，换成 SiliconFlow 支持的 embedding 模型名
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template = (
        "你是企业内部助手，回答要像资深工程师/运维写给同事。\n"
        "规则：\n"
        "1) 只基于上下文回答；没有就回答“很抱歉，我无法准确回答这个问题”。\n"
        "2) 先给1句结论；再给最多3条要点；不要额外科普；如果资料不足就不要回答要点。\n"
        "3) 不要使用“作为AI”“我不能”“建议您”等套话。\n"
        "4) 总字数不超过120字。\n\n"
        "上下文：\n{context}\n\n"
        "问题：{question}\n\n"
        "回答："
    ),
)

def load_files_from_folder(folder_path: str):
    documents = []
    if not os.path.exists(folder_path):
        print(f"文件夹 {folder_path} 不存在")
        return []

    print(f"📂 正在扫描文件夹: {folder_path} ...")
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            print(f"🔍 发现文件: {file_path}")

            try:
                if ext == ".txt":
                    loader = TextLoader(file_path, encoding="utf-8")
                elif ext == ".docx":
                    loader = Docx2txtLoader(file_path)
                else:
                    print(f"⚠️ 不支持的文件类型: {ext}")
                    continue

                documents.extend(loader.load())
            except Exception as e:
                print(f"⚠️ 加载文件 {file_path} 时出错: {e}")

    return documents

def get_or_build_wind_farm_kb():
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=SILICON_FLOW_API_KEY,
        base_url="https://api.siliconflow.cn/v1",
        temperature=0.1,
    )

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=SILICON_FLOW_API_KEY,
        base_url="https://api.siliconflow.cn/v1",
    )

    choice = "1"
    # 检查是否已存在向量数据库
    if os.path.exists("./chroma_db") and os.listdir("./chroma_db"):
        choice = input("已存在向量数据库，请选择加载现有数据库(0)/删除现有数据库并新建向量数据库(1): ")
    if choice == "0" and os.path.exists("./chroma_db") and os.listdir("./chroma_db"):
        vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
    else:
        # 删除现有数据库
        if os.path.exists("./chroma_db") and os.listdir("./chroma_db"):
            shutil.rmtree("./chroma_db")

        print("--- 正在读取文档 ---")
        docs = load_files_from_folder(FOLDER_PATH)
        if not docs:
            print("⚠️ 没有发现任何文档")
            return None
        print(f"✅ 成功加载 {len(docs)} 个文档")

        print("--- 正在切分文档 ---")
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        split_docs = splitter.split_documents(docs)
        print(f"✅ 成功切分 {len(split_docs)} 个文档片段")

        print("--- 正在构建向量数据库 ---")
        vector_db = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory="./chroma_db",
        )
        vector_db.persist()
        print("✅ 成功构建并持久化向量数据库")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_PROMPT},
    )
    return qa_chain


if __name__ == "__main__":
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
        print(f"已自动创建文件夹 '{FOLDER_PATH}'，请把 .txt 或 .docx 文件放进去再运行。")
    else:
        app = get_or_build_wind_farm_kb()
        if app:
            print("✅ 知识库已成功构建")
            while True:
                query = input("\n请输入您的问题（输入 'exit' 退出）: ")
                if query.lower() == "exit":
                    print("✅ 程序已退出")
                    break
                try:
                    result = app.invoke({"query": query})
                    print("\n回答:", result["result"])
                except Exception as e:
                    print(f"⚠️ 处理查询时出错: {e}")
        else:
            print("⚠️ 知识库构建失败")