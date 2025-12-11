import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 경로 및 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"

def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    if not os.path.exists(PERSIST_DIR):
        raise FileNotFoundError(f"Vector DB가 존재하지 않습니다. 경로: {PERSIST_DIR}")

    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )

    return vectorstore