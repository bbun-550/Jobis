import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 경로 및 설정
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_PATH = os.path.join(BASE_PATH, 'data', 'chroma_db')
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"

def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    if not os.path.exists(PERSIST_PATH):
        raise FileNotFoundError(f"Vector DB가 존재하지 않습니다. 경로: {PERSIST_PATH}")

    vectorstore = Chroma(
        persist_directory=PERSIST_PATH,
        embedding_function=embeddings,
    )

    return vectorstore