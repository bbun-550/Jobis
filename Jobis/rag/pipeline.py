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
    당신은 취업 정보 전문가 'JOBIS'입니다.
    아래 [관련 기업 정보]를 참고하여 질문에 답변해 주세요.
    
    [관련 기업 정보]:
    {context}
    
    질문: {question}
    
    * 정보가 있다면, 기업명과 함께 내용을 정리해 주세요.
    * 만약 제공된 정보에 답이 없다면, "죄송합니다. 해당 내용에 대한 정보가 데이터베이스에 없습니다."라고 답해주세요.
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