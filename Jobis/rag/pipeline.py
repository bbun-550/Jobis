# rag/pipeline.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    """검색된 문서들을 하나의 텍스트로 합칩니다."""
    formatted_docs = []
    for doc in docs:
        # 메타데이터를 포함하여 출처를 명확히 함
        company = doc.metadata.get('company_name', 'Unknown')
        content = doc.page_content
        formatted_docs.append(f"<기업명: {company}>\n{content}")
    
    return "\n\n".join(formatted_docs)

def build_rag_chain(retriever):
    """
    Retriever와 LLM을 연결하여 RAG Chain을 생성합니다.
    """
    
    # 1. LLM 설정 (Gemini-1.5-flash)
    # 2.5 버전 사용 가능 시 변경 가능, 현재 안정성을 위해 1.5 사용
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,  # 사실 기반 답변을 위해 0으로 설정
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 2. 프롬프트 템플릿 설정
    template = """
    당신은 구직자들을 돕는 채용 정보 전문가 'JOBIS(자비스)'입니다.
    아래 제공된 [관련 기업 정보]를 바탕으로 질문에 대해 친절하고 정확하게 답변해주세요.
    
    - 정보가 문맥(Context)에 없다면 "죄송합니다. 해당 기업이나 내용에 대한 정보가 데이터에 없습니다."라고 솔직하게 말하세요.
    - 문맥에 없는 내용을 지어내지 마세요.
    - 답변은 보기 좋게 마크다운 형태로 정리해주세요.

    [관련 기업 정보]:
    {context}

    질문: {question}

    답변:
    """
    
    prompt = PromptTemplate.from_template(template)

    # 3. 체인 구성 (LCEL 문법)
    # Retriever -> 문서 포맷팅 -> 프롬프트 -> LLM -> 문자열 출력
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain