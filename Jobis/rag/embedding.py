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

# 입력 파일: 전처리된 데이터
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.json')

# 출력 경로: 벡터 DB가 저장될 폴더 (chroma_db)
PERSIST_DIRECTORY = os.path.join(BASE_DIR, 'data', 'chroma_db')

# 임베딩 모델 설정 (HuggingFace의 all-MiniLM-L12-v2 사용)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"

def load_processed_data():
    """전처리된 JSON 파일을 불러옵니다."""
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {INPUT_FILE}")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_documents(data):
    """
    JSON 데이터를 LangChain의 Document 객체 리스트로 변환합니다.
    이때 메타데이터(회사명, 평점, 날짜 등)를 함께 저장해야 나중에 필터링이 가능합니다.
    """
    documents = []
    
    for item in data:
        # 벡터화할 실제 텍스트 내용
        page_content = item.get('content', '')
        
        # 함께 저장할 메타데이터 (검색 시 필터링 용도)
        metadata = {
            "company_name": item.get('company_name', 'Unknown'),
            "industry": item.get('industry', 'Unknown'),
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
    
    # 기존 DB가 있다면 삭제하고 새로 만들지, 아니면 추가할지 결정
    # 여기서는 깔끔한 테스트를 위해 기존 DB 폴더가 있으면 삭제하고 새로 만듭니다.
    if os.path.exists(PERSIST_DIRECTORY):
        print(f"🗑️  기존 DB 삭제 중... ({PERSIST_DIRECTORY})")
        shutil.rmtree(PERSIST_DIRECTORY)

    print(f"🧩 3. 임베딩 모델 로드 중... ({EMBEDDING_MODEL_NAME})")
    # model_kwargs={'device': 'cpu'} : GPU가 없으면 cpu로 설정
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True} # 코사인 유사도 계산을 위해 정규화
    )

    print(f"💾 4. ChromaDB 생성 및 데이터 저장 중... (시간이 걸릴 수 있습니다)")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    
    print(f"✅ 벡터 DB 구축 완료! 저장 경로: {PERSIST_DIRECTORY}")
    return vector_store

def test_search(vector_store, query_text):
    """구축된 DB가 잘 작동하는지 테스트 검색을 수행합니다."""
    print("\n" + "="*30)
    print(f"🔍 테스트 검색: '{query_text}'")
    print("="*30)
    
    # 유사도 검색 실행 (k=3 : 상위 3개 결과)
    results = vector_store.similarity_search(query_text, k=3)
    
    for i, doc in enumerate(results):
        print(f"\n[결과 {i+1}]")
        print(f"🏢 기업: {doc.metadata['company_name']}")
        print(f"🏷️ 유형: {doc.metadata['type']} | 감정: {doc.metadata['sentiment']}")
        print(f"📝 내용: {doc.page_content[:100]}...") # 100자만 출력

if __name__ == "__main__":
    # 1. DB 구축
    db = build_vector_db()
    
    # 2. 테스트 검색 (제대로 저장됐는지 확인)
    # 예: '연봉'이나 '복지' 관련된 내용을 검색해봅니다.
    test_search(db, "복지가 좋고 워라밸이 보장되는 회사")