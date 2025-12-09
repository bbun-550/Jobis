def get_retriever(vectorstore, k=3):
    """
    VectorStore에서 Retriever 객체를 생성합니다.
    
    Args:
        vectorstore: Chroma 등의 백터 저장소 객체
        k (int): 검색할 상위 문서 개수 (기본값 3)
    
    Returns:
        retriever: LangChain Retriever 객체
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    return retriever