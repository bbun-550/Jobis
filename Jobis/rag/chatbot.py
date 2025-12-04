import os
from dotenv import load_dotenv

# LangChain 관련 임포트
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ==========================================
# 1. 설정 및 경로
# ==========================================
load_dotenv() # .env 파일 로드

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIRECTORY = os.path.join(BASE_DIR, 'data', 'chroma_db')

# 임베딩 모델 (DB 저장 때와 동일해야 함)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"

# LLM 모델 설정 (Gemini-2.5-flash)
LLM_MODEL_NAME = "gemini-2.5-flash"

class JobisChatbot:
    def __init__(self):
        self.vector_store = self._load_vector_db()
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3} # 상위 3개 문서 참조
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2, # 사실 기반 답변을 위해 창의성 낮춤
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.chain = self._build_chain()

    def _load_vector_db(self):
        """저장된 ChromaDB를 불러옵니다."""
        print("💾 Loading Vector DB...")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        return Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings
        )

    def _build_chain(self):
        """RAG 체인(파이프라인)을 생성합니다."""
        
        # 프롬프트 템플릿: LLM에게 역할을 부여하고 답변 형식을 지정
        template = """
        당신은 구직자들을 돕는 채용 정보 전문가 'JOBIS(자비스)'입니다.
        아래 제공된 [관련 기업 정보]를 바탕으로 질문에 대해 친절하고 정확하게 답변해주세요.
        
        정보가 없다면 "죄송합니다. 해당 기업이나 내용에 대한 정보가 데이터에 없습니다."라고 솔직하게 말하세요.
        없는 내용을 지어내지 마세요.
        
        [관련 기업 정보]:
        {context}
        
        질문: {question}
        
        답변:
        """
        
        prompt = PromptTemplate.from_template(template)
        
        # LangChain Runnable 연결 (Retriever -> Prompt -> LLM -> String Output)
        chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def _format_docs(self, docs):
        """검색된 문서들을 하나의 텍스트 덩어리로 합칩니다."""
        return "\n\n".join([f"<기업명: {doc.metadata['company_name']}>\n{doc.page_content}" for doc in docs])

    def ask(self, query):
        """질문을 받아 답변을 반환합니다."""
        if not query:
            return "질문을 입력해주세요."
        return self.chain.invoke(query)

# ==========================================
# 2. 테스트 실행 (이 파일을 직접 실행할 때만 작동)
# ==========================================
if __name__ == "__main__":
    # API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: .env 파일에 GOOGLE_API_KEY가 없습니다.")
        exit()

    print("🤖 챗봇 초기화 중...")
    bot = JobisChatbot()
    
    print("\n💬 챗봇과 대화를 시작합니다. (종료하려면 'exit' 입력)")
    while True:
        user_input = input("\n질문: ")
        if user_input.lower() in ["exit", "quit", "종료"]:
            break
        
        response = bot.ask(user_input)
        print(f"답변: {response}")