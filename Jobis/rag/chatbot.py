from dotenv import load_dotenv
load_dotenv()

from rag.vectorstore import get_vectorstore
from rag.retriever import get_retriever
from rag.pipeline import build_rag_chain

class JobisChatbot:
    def __init__(self):
        # 1. VectorStore 로드 (vectorstore.py)
        self.vectorstore = get_vectorstore()
        
        # 2. Retriever 생성 (retriever.py)
        self.retriever = get_retriever(self.vectorstore, k=5)
        
        # 3. RAG Chain 구축 (pipeline.py)
        self.chain = build_rag_chain(self.retriever)

    def ask(self, query):
        """사용자 질문을 받아 답변을 반환합니다."""
        if not query:
            return "질문을 입력해주세요."
        
        try:
            response = self.chain.invoke(query)
            return response
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"

# 테스트 코드
if __name__ == "__main__":
    bot = JobisChatbot()
    print(bot.ask("복지가 좋은 회사는 어디야?"))