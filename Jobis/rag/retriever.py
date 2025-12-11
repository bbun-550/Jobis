def get_retriever(vectorstore, k=3):
    retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,            # 최종적으로 가져올 문서 개수
                "fetch_k": k * 2,  # 다양성 계산을 위해 후보로 먼저 가져올 문서 개수
                "lambda_mult": 0.5 # 0 ~ 1 사이 (0.5는 다양성과 유사도 균형)
            } 
        )
    
    return retriever