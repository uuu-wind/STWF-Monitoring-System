import os
from pyexpat import model
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# 引入多种加载器
from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# --- 配置部分 ---
SILICON_FLOW_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # 替换您的 Key
FOLDER_PATH = "./wind_farm_docs"  # 您的文档文件夹路径
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

def load_files_from_folder(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        print(f"文件夹 {folder_path} 不存在")
        return []

    print(f"📂 正在扫描文件夹: {folder_path} ...")

    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            print(f"🔍 发现文件: {file_path}")

            try:
                loader = None
                # 根据文件类型选择加载器
                if file_ext == '.txt':
                    # encoding='utf-8' 解决中文乱码问题
                    loader = TextLoader(file_path, encoding='utf-8')
                elif file_ext == '.docx':
                    loader = Docx2txtLoader(file_path)
                else:
                    print(f"⚠️ 不支持的文件类型: {file_ext}")
                    continue
            except Exception as e:
                print(f"⚠️ 加载文件 {file_path} 时出错: {e}")
                continue
    return documents

def build_wind_farm_kb():
    # 1. 初始化模型
    llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=SILICON_FLOW_API_KEY,
        openai_api_base = "https://api.siliconflow.cn/v1",
        temperature=0.1,
    )

    # 2. 初始化嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name = "BAAI/bge-m3"
    )

    # 3. 读取文档
    print("--- 正在读取文档 ---")
    docs = load_files_from_folder(FOLDER_PATH)

    if not docs:
        print("⚠️ 没有发现任何文档")
        return None
    
    print(f"✅ 成功加载 {len(docs)} 个文档")

    # 4. 切分文档
    print("--- 正在切分文档 ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    split_docs = text_splitter.split_documents(docs)
    print(f"✅ 成功切分 {len(split_docs)} 个文档片段")

    # 5. 构建向量数据库
    print("--- 正在构建向量数据库 ---")
    vector_db = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    db.persist()
    print("✅ 成功构建并持久化向量数据库")

    # 6. 构建问答链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        ),
        return_source_documents=True
    )
    return qa_chain

# --- 测试主程序 ---
if __name__ == "__main__":
    # 确保只要把文件扔进 'wind_farm_docs' 文件夹即可
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
        print(f"已自动创建文件夹 '{FOLDER_PATH}'，请把 .txt 或 .docx 文件放进去再运行。")
    else:
        app = build_wind_farm_kb()

        if app:
            print("✅ 知识库已成功构建")
            while True:
                query = input("\n请输入您的问题（输入 'exit' 退出）: ")
                if query.lower() == 'exit':
                    print("✅ 程序已退出")
                    break
                try:
                    result = app.invoke({"query": query})
                    print("\n回答:", result["result"])
                except Exception as e:
                    print(f"⚠️ 处理查询时出错: {e}")
        else:
            print("⚠️ 知识库构建失败")