import json
import os
import re

# 경로 맟 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'jobis_rag_data.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.json')

# 디렉터리가 없으면 생성
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# 회사명 정규화
def normalize_company_name(name) -> str:
    """
    - (주), 주식회사, (매장) 제거
    - 앞뒤 공백 제거
    """
    if not name:
        return ""

    name = name.strip()

    # (주), 주식회사 제거
    name = re.sub(r"\(?주\)?", "", name)
    name = re.sub(r"주식회사", "", name)

    # (매장) 제거
    name = re.sub(r"\(매장\)", "", name)

    # 다중 공백 정리
    name = re.sub(r"\s+", " ", name).strip()

    return name

# 텍스트 정규화
def normalize_null(text):
    """
    null, 공백, 개행 문자만 있는 값 제거
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # "\n", "\r", "\"", 공백만 있는 경우 제거
    if re.fullmatch(r'[\s"\\r\\n]*', text):
        return ""

    return text

# 텍스트 내의 노이즈(결측치 마커 등)를 제거하고 불필요한 공백을 정리
def clean_text(text):
    """
    - 결측치 표현 제거
    - 특수 개행 / 다중 공백 정리
    """
    text = normalize_null(text)
    if not text:
        return ""

    # (결측치 포함) 같은 패턴 제거
    text = re.sub(r'\([^)]*결측치[^)]*\)', '', text)

    # 개행, 탭 → 공백
    text = re.sub(r'[\r\n\t]', ' ', text)

    # 다중 공백 축소
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 🔥 특수문자 노이즈 제거 추가
    text = remove_noise_symbols(text)
    
    return text

# 간단한 규칙(온점, 물음표, 느낌표)을 기준으로 문장을 분리
def split_sentences(text):
    if not text:
        return []
    
    # 문장 끝(. ? !) 뒤에 공백이 오면 분리
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 5]

# 문자열 점수를 float로 변환
def parse_score(score):
    try:
        return float(score)
    except:
        return None

# 평점(1~5)을 기반으로 감정을 라벨링
def get_sentiment_label(score):
    if score is None:
        return "neutral"
    if score >= 4:
        return "positive"
    elif score <= 2:
        return "negative"
    return "neutral"

# 의미 없는 특수문자 노이즈 제거
def remove_noise_symbols(text: str) -> str:
    """
    - 단독 또는 반복된 특수문자 제거
    - 문장 내부의 . , ? 는 유지
    """
    if not text:
        return ""

    # 반복 특수문자 제거 (~~~ , ////, """" 등)
    text = re.sub(r'[~\/"()]{2,}', ' ', text)

    # 단독 특수문자만 있는 토큰 제거
    text = re.sub(r'\b[~\/"()]+\b', ' ', text)

    # 문장 앞뒤의 불필요한 특수문자 제거
    text = re.sub(r'^[~\/"(),.?]+|[~\/"(),.?]+$', '', text)

    # 다중 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# 메인 로직
def process_data():
    print(f"📥 Loading data from {INPUT_FILE}...")

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    processed_list = []

    for company in raw_data:
        company_id = company.get("company_id")
        company_name = normalize_company_name(company.get("company_name"))
        industry = company.get("industry")

        for item in company.get("data", []):
            item_type = item.get("type")

            processed_item = {
                "company_id": company_id,
                "company_name": company_name,
                "industry": industry,
                "type": item_type
            }

            # Review 데이터 처리
            if item_type == "review":
                review = item.get("review", {})

                title = clean_text(review.get("re_title"))
                adv = clean_text(review.get("re_adv"))
                dis = clean_text(review.get("re_dis"))
                score = parse_score(review.get("re_score"))
                date = review.get("re_date")

                sentiment = get_sentiment_label(score)

                # full_text = f"리뷰 제목: {title} 장점: {adv} 단점: {dis}".strip()

                # if not is_meaningful(full_text):
                #     continue
                
                # 내용 조합 (제목 포함)
                content_parts = []
                if title:
                    content_parts.append(f"리뷰 제목: {title}")
                if adv:
                    content_parts.append(f"장점: {adv}")
                if dis:
                    content_parts.append(f"단점: {dis}")

                full_text = " ".join(content_parts)

                sentences = split_sentences(full_text)

                processed_item.update({
                    "content": full_text,
                    "sentences": sentences,
                    "score": score,
                    "sentiment": sentiment,
                    "date": date
                })

            # Interview 데이터 처리
            elif item_type == "interview":
                interview = item.get("interview", {})

                title = clean_text(interview.get("in_title"))
                query = clean_text(interview.get("in_query"))
                vibe = clean_text(interview.get("in_vibe"))
                level = clean_text(interview.get("in_level"))
                date = interview.get("in_date")

                content_parts = []
                if query:
                    content_parts.append(f"면접 질문: {query}")
                if title:
                    content_parts.append(f"면접 후기: {title}")
                if vibe:
                    content_parts.append(f"면접 분위기: {vibe}")
                if level:
                    content_parts.append(f"난이도: {level}")

                full_text = " ".join(content_parts)
                sentences = split_sentences(full_text)

                processed_item.update({
                    "content": full_text,
                    "sentences": sentences,
                    "sentiment": "neutral", # 면접 정보는 중립으로 가정
                    "date": date
                })

            # 내용이 비어있지 않은 경우에만 리스트에 추가
            if processed_item.get("content") and len(processed_item["content"]) >= 20:
                processed_list.append(processed_item)
    

    # 저장
    print(f"💾 Saving processed data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_list, f, ensure_ascii=False, indent=2)

    print(f"✅ Pre-processing completed | Total records: {len(processed_list)}")


if __name__ == "__main__":
    process_data()