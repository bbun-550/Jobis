import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 절대 경로로 설정 (어디서 실행하든 DB 위치를 정확히 찾기 위함)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')

def get_vectorstore():
    # embedding.py와 동일한 설정이어야 함
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L12-v2",
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