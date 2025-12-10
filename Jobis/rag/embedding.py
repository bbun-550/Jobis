import json
import os
import shutil
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ==========================================
# 1. 경로 및 설정
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.json')
PERSIST_DIRECTORY = os.path.join(BASE_DIR, 'data', 'chroma_db')
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"

def load_processed_data():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_documents(data):
    documents = []
    
    for item in data:
        # [수정된 부분] -------------------------------------------------------
        # 검색 정확도를 위해 본문(page_content)에 기업명과 산업 정보를 포함시킵니다.
        company_name = item.get('company_name', 'Unknown')
        industry = item.get('industry', 'Unknown')
        content_text = item.get('content', '')

        # AI가 검색할 실제 텍스트 구성
        page_content = f"기업명: {company_name}\n산업분야: {industry}\n내용: {content_text}"
        # -------------------------------------------------------------------
        
        metadata = {
            "company_name": company_name,
            "industry": industry,
            "type": item.get('type', 'Unknown'),
            "sentiment": item.get('sentiment', 'neutral'),
            "score": item.get('score', 0) if item.get('score') is not None else 0,
            "date": item.get('date', ''),
            "data_id": item.get('data_id', '')
        }
        
        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)
        
    return documents

def build_vector_db():
    print(f"🔄 1. 데이터 로딩 중... ({INPUT_FILE})")
    data = load_processed_data()
    
    print(f"📄 2. 문서 변환 중... (총 {len(data)}개 항목)")
    documents = create_documents(data)
    
    # 기존 DB 삭제 후 재생성 (깨끗한 상태 유지를 위해)
    if os.path.exists(PERSIST_DIRECTORY):
        print(f"🗑️  기존 DB 삭제 중... ({PERSIST_DIRECTORY})")
        shutil.rmtree(PERSIST_DIRECTORY)

    print(f"🧩 3. 임베딩 모델 로드 중... ({EMBEDDING_MODEL_NAME})")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    print(f"💾 4. ChromaDB 생성 및 데이터 저장 중...")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    
    print(f"✅ 벡터 DB 구축 완료! 저장 경로: {PERSIST_DIRECTORY}")
    return vector_store

def test_search(vector_store, query_text):
    print("\n" + "="*30)
    print(f"🔍 테스트 검색: '{query_text}'")
    print("="*30)
    
    results = vector_store.similarity_search(query_text, k=3)
    
    for i, doc in enumerate(results):
        print(f"\n[결과 {i+1}]")
        print(f"📝 내용 미리보기: {doc.page_content[:100].replace(chr(10), ' ')}...") 

if __name__ == "__main__":
    db = build_vector_db()
    # 테스트: 이제 기업 이름으로 검색이 잘 되는지 확인
    test_search(db, "IT/웹/통신_테크 기업의 장점은?")