import json
import os
import random

# ==========================================
# 1. 경로 설정 (rag/ 폴더 기준)
# ==========================================
# 현재 파일(check_preprocessing.py)의 상위 폴더(Project)를 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.json')

def verify_data():
    print(f"🔍 검증 파일 경로: {PROCESSED_FILE}")
    
    if not os.path.exists(PROCESSED_FILE):
        print("❌ 오류: 'cleaned_data.json' 파일이 존재하지 않습니다. preprocessing.py를 먼저 실행했는지 확인해주세요.")
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ 총 데이터 개수: {len(data)}개")
    print("-" * 50)

    # 검증 통계 변수
    error_count = 0
    null_remains = 0
    noise_remains = 0
    
    # 샘플 출력을 위한 저장소
    positive_sample = None
    negative_sample = None
    interview_sample = None

    for item in data:
        content = item.get('content', '')
        
        # [체크 1] 결측치(null)나 빈 문자열 처리가 안 된 항목이 있는지
        if content is None or content.strip() == "":
            error_count += 1
            
        # [체크 2] '결측치 포함'이라는 노이즈 텍스트가 여전히 남아있는지 (Regex 확인)
        if "결측치 포함" in content:
            noise_remains += 1
            print(f"⚠️ 노이즈 잔존 발견: {item['data_id']}")

        # [체크 3] 문장 분리(List 형태) 확인
        if not isinstance(item.get('sentences'), list) or len(item['sentences']) == 0:
            print(f"⚠️ 문장 분리 오류: {item['data_id']} (리스트가 아니거나 비어있음)")
            error_count += 1

        # 샘플 수집 (검증 후 눈으로 확인하기 위함)
        if item['type'] == 'review':
            if item['sentiment'] == 'positive' and not positive_sample:
                positive_sample = item
            elif item['sentiment'] == 'negative' and not negative_sample:
                negative_sample = item
        elif item['type'] == 'interview' and not interview_sample:
            interview_sample = item

    # ==========================================
    # 2. 결과 리포트 출력
    # ==========================================
    
    print(f"📊 검증 결과 리포트")
    print(f"   - 데이터 구조 무결성 오류: {error_count}건")
    print(f"   - '결측치' 텍스트 잔존 여부: {noise_remains}건")
    
    if error_count == 0 and noise_remains == 0:
        print("\n🎉 축하합니다! 데이터 전처리가 완벽하게 수행되었습니다.")
    else:
        print("\n⚠️ 일부 데이터에 문제가 있습니다. 위 로그를 확인해주세요.")

    print("\n" + "=" * 20 + " [샘플 데이터 확인] " + "=" * 20)
    
    # 눈으로 직접 확인해보기
    if positive_sample:
        print("\n[긍정 리뷰 샘플 (Score 4 이상)]")
        print(f"ID: {positive_sample['data_id']} | 평점: {positive_sample['score']}")
        print(f"라벨: {positive_sample['sentiment']}")
        print(f"내용(일부): {positive_sample['content'][:100]}...")
        print(f"문장분리 개수: {len(positive_sample['sentences'])}")

    if negative_sample:
        print("\n[부정 리뷰 샘플 (Score 2 이하)]")
        print(f"ID: {negative_sample['data_id']} | 평점: {negative_sample['score']}")
        print(f"라벨: {negative_sample['sentiment']}")
        print(f"내용(일부): {negative_sample['content'][:100]}...")

    if interview_sample:
        print("\n[인터뷰 데이터 샘플]")
        print(f"ID: {interview_sample['data_id']}")
        print(f"내용(일부): {interview_sample['content'][:100]}...")
        print(f"문장분리 예시: {interview_sample['sentences'][0]}")

if __name__ == "__main__":
    verify_data()