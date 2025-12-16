import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    if not docs:
        return ""
    
    formatted = []
    for doc in docs:
        company = doc.metadata.get('company_name', 'Unknown')
        content = doc.page_content
        formatted.append(f"[{company}]\n{content}")
        
    return "\n\n".join(formatted)

def build_rag_chain(retriever):
    # LLM 설정
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    template = """
    당신은 취업 정보 전문가 AI 'JOBIS'입니다.
    아래 [관련 기업 정보]를 참고하여 질문에 답변해주세요.
    단, [관련 기업 정보]에 질문에서 물어보는 정확한 단어가 없더라도 유사한 내용이 있다면 답변해주세요.
    
    [관련 기업 정보]:
    {context}
    
    질문: {question}
    
    * 정보가 있다면, 기업명과 함께 내용을 정리해 주세요.
    * 그 후에 AI 전문가 JOBIS가 판단하기에 비슷한 회사의 내용을 찾아 나열해주세요.
    * 답변을 7줄 내외로 나올 수 있도록 작성해주세요. 
    * 답변:
    """
    
    prompt = PromptTemplate.from_template(template)

    # Chain 구성
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain