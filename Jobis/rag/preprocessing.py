import json
import os
import re

# 경로 맟 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'jobis_rag_data.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.json')

# 디렉터리가 없으면 생성
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# 텍스트 내의 노이즈(결측치 마커 등)를 제거하고 불필요한 공백을 정리
def clean_text(text):
    if not text:
        return ""
    
    # 1. "(... - 결측치 포함)" 또는 "(결측치 포함)" 같은 패턴 제거
    # 괄호와 그 안의 내용 중 '결측치'라는 단어가 들어가면 삭제
    text = re.sub(r'\([^)]*결측치[^)]*\)', '', text)
    
    # 2. 앞뒤 공백 제거 및 다중 공백을 하나로 줄임
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# 간단한 규칙(온점, 물음표, 느낌표)을 기준으로 문장을 분리
def split_sentences(text):
    if not text:
        return []
    
    # 문장 끝(. ? !) 뒤에 공백이 오면 분리
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s for s in sentences if s.strip()]

# 평점(1~5)을 기반으로 감정을 라벨링
def get_sentiment_label(score):
    if score is None:
        return "neutral"
    
    if score >= 4:
        return "positive"
    elif score <= 2:
        return "negative"
    else:
        return "neutral"

# 메인 로직
def process_data():
    print(f"Loading data from {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("Error: 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    processed_list = []

    for company in raw_data:
        company_id = company.get('company_id')
        company_name = company.get('company_name')
        industry = company.get('industry')
        
        for item in company.get('data', []):
            processed_item = {
                "company_id": company_id,
                "company_name": company_name,
                "industry": industry,
                "type": item['type'],
                "data_id": item['data_id']
            }

            # Review 데이터 처리
            if item['type'] == 'review':
                review_content = item.get('review', {})
                
                # 1. 텍스트 필드 클리닝 (결측치 제거)
                re_adv = clean_text(review_content.get('re_adv'))
                re_dis = clean_text(review_content.get('re_dis')) # null인 경우 빈 문자열 반환됨
                
                # 2. 감정 라벨링 (점수 기반)
                score = review_content.get('re_score')
                sentiment = get_sentiment_label(score)
                
                # 3. 텍스트 통합 (장점 + 단점) 및 문장 분리
                full_text = f"장점: {re_adv} 단점: {re_dis}".strip() # 텍스트 통합
                sentences = split_sentences(full_text) # 문장 분리

                processed_item.update({
                    "score": score,
                    "sentiment": sentiment,
                    "content": full_text,
                    "sentences": sentences,
                    "date": review_content.get('re_date')
                })

            # Interview 데이터 처리
            elif item['type'] == 'interview':
                interview_content = item.get('interview', {})
                
                in_title = clean_text(interview_content.get('in_title'))
                in_query = clean_text(interview_content.get('in_query'))
                
                full_text = f"면접 질문: {in_query} 답변/후기: {in_title}"
                sentences = split_sentences(full_text)

                processed_item.update({
                    "content": full_text,
                    "sentences": sentences,
                    "sentiment": "neutral" # 면접 정보는 중립으로 가정
                })

            # 내용이 비어있지 않은 경우에만 리스트에 추가
            if processed_item.get('content'):
                processed_list.append(processed_item)

    # 저장
    print(f"Saving processed data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_list, f, ensure_ascii=False, indent=2)
    
    print("Pre-processing completed successfully!")

if __name__ == "__main__":
    process_data()