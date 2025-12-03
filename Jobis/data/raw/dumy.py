import json
import random
from datetime import datetime, timedelta

# --- 1. 상수 정의 및 설정 ---
# 업종별 기업명을 현실적으로 반영하기 위한 더미 리스트
INDUSTRIES = [
    "IT/웹/통신", "제조/화학", "의료/제약/복지", 
    "유통/무역/운송", "교육업", "건설업", 
    "미디어/디자인", "은행/금융업", "기관/협회",
    "서비스업" 
]

# 기업별 더미 이름 템플릿 (현실성을 위해 업종별로 다르게 구성)
COMPANY_TEMPLATES = {
    "IT/웹/통신": ["테크", "솔루션즈", "이노베이션", "플랫폼", "AI랩", "시스템즈", "소프트", "인터랙티브", "모바일", "넥스트"],
    "제조/화학": ["인더스트리", "케미칼", "정공", "소재", "테크놀로지", "하이테크", "엔지니어링", "에너지", "프리미엄", "글로벌"],
    "의료/제약/복지": ["제약", "바이오", "헬스케어", "메디컬", "복지재단", "클리닉", "연구소", "파마", "생명과학", "웰니스"],
    "유통/무역/운송": ["로지스틱스", "트레이딩", "커머스", "익스프레스", "무역", "글로벌", "딜리버리", "상사", "리테일", "마켓"],
    "교육업": ["에듀", "학원", "스터디", "러닝", "아카데미", "컨설팅", "미래", "인재원", "지식", "클래스"],
    "건설업": ["건설", "이앤씨", "개발", "주택", "토건", "산업", "종합", "파트너스", "디자인", "인프라"],
    "미디어/디자인": ["미디어", "스튜디오", "디자인", "콘텐츠", "엔터테인먼트", "아트", "커뮤니케이션", "광고", "필름", "영상"],
    "은행/금융업": ["은행", "투자", "증권", "파이낸셜", "보험", "캐피탈", "자산운용", "신탁", "저축", "금융"],
    "기관/협회": ["재단", "공단", "센터", "진흥원", "협회", "연구원", "기관", "단체", "위원회", "교육청"],
    "서비스업": ["컨설팅", "마케팅", "이벤트", "레저", "호텔", "여행", "에이전시", "HR", "아웃소싱", "경영"] 
}

# 공통 상수
LEVELS = ["매우쉬움", "쉬움", "보통", "어려움", "매우어려움"]
MISSING_RATE = 0.1  # 10% 확률로 결측치 발생

# --- 1-1. 텍스트 다양성 확대를 위한 새로운 템플릿 목록 (창의성/다양성 대폭 강화) ---

POSITIVE_TEMPLATES = [
    # 기술 및 성장 관련 (학생님 관심사)
    "주니어에게도 MLOps 파이프라인 설계 기회가 주어지며, 최신 기술 도입에 적극적입니다. 파이썬 기반의 데이터 분석 환경이 잘 구축되어 있어 성장에 최적화된 곳입니다.",
    "정기적으로 딥러닝 스터디를 진행하고, 트랜스포머 아키텍처 같은 심화 주제에 대한 지원이 확실합니다. 기술 블로그 운영을 장려하며 지식 공유 문화가 훌륭합니다.",
    "데이터 시각화 툴(Matplotlib, Seaborn)에 대한 교육 지원이 풍부하며, 통계적 모델링(회귀분석, GMM)을 실제 서비스에 적용해 볼 수 있는 기회가 많습니다.",
    "배깅과 부스팅 같은 앙상블 기법을 활용한 프로젝트 경험을 쌓을 수 있으며, 동료들 모두 머신러닝 기초 이론에 능통하여 배우는 점이 많습니다.",
    "CNN을 이용한 이미지 분류나 RNN을 활용한 시계열 예측 등, 다양한 딥러닝 모델을 직접 배포해 보는 경험이 큰 자산이 됩니다. GPU 인프라도 넉넉합니다.",
    "RDBMS와 SQL 데이터베이스가 잘 정리되어 있어, 데이터 접근성이 매우 뛰어납니다. 복잡한 쿼리를 작성하는 실력이 빠르게 향상됩니다.",
    "Pandas, NumPy를 활용한 데이터 전처리 과정이 체계화되어 있어, 분석에 집중할 수 있습니다. 데이터의 품질 관리가 투명하게 이루어집니다.",
    "비지도 학습(K-means, GMM)을 통해 고객 세분화 프로젝트를 진행할 수 있습니다. 실험적인 시도를 장려하며 실패를 용인하는 분위기입니다.",
    "경력에 관계없이 AI 보안 및 데이터 프라이버시 교육이 철저하여, 윤리적인 AI 개발에 대한 시야를 넓힐 수 있었습니다.",
    
    # 문화, 복지 및 WLB 관련
    "수평적인 조직 문화와 자율 출퇴근제를 운영하여 워라밸이 매우 좋습니다. 개인의 편하게 일하는 문화를 최우선으로 생각하며 존중받는다는 느낌을 받았습니다.",
    "사무실 환경이 쾌적하고 식사 지원이 훌륭합니다. 야근이 거의 없으며, 프로젝트가 끝나면 충분한 보상 휴가가 주어집니다. 복지가 업계 최고 수준입니다.",
    "경영진이 직원들의 의견을 경청하며, 비전이 명확합니다. 신뢰를 바탕으로 업무를 진행하며, 불필요한 보고 절차가 최소화되어 업무 효율이 높습니다.",
    "입사 후 체계적인 온보딩 프로그램이 제공되어 레거시 시스템을 빠르게 이해할 수 있었습니다. 특히 사수와의 1:1 멘토링이 큰 도움이 되었습니다.",
    "성과에 대한 보상이 투명하고 공정합니다. 다중회귀 모델로 측정된 기여도에 따라 인센티브가 지급되는 시스템이 신뢰를 주었습니다.",
    "휴가 사용이 자유롭고, 눈치 볼 필요가 전혀 없습니다. '쉬는 것도 일이다'라는 문화가 정착되어 있어 재충전에 용이합니다.",
    "매년 워크숍 대신 개인 역량 개발비(강의, 도서, 컨퍼런스)를 지원받아 자기 계발에 집중할 수 있었습니다. 실질적인 복지입니다.",
    "동료들이 서로 존중하며 건설적인 피드백을 주고받습니다. 함께 성장하는 느낌을 받을 수 있어 만족도가 높습니다.",
    
    # 산업 및 기타 (다양성 추가)
    f"[은행/금융업] 금융 거래 데이터 분석을 통한 이상 탐지 모델 개발에 참여했습니다. 민감 데이터 처리 경험을 쌓기 좋습니다.",
    f"[의료/제약/복지] 의료 영상 데이터 기반의 딥러닝 진단 보조 시스템 구축 프로젝트는 높은 가치를 창출합니다.",
    f"[제조/화학] 공정 최적화를 위한 시계열 분석 프로젝트는 데이터 분석가로서의 커리어를 넓히는 기회였습니다.",
    f"[{INDUSTRIES[random.randint(0, 9)]}] 업종 내에서 시장 점유율이 높고, 안정적인 현금 흐름을 바탕으로 장기 근속이 가능한 좋은 회사입니다.",
    "최신 IT 트렌드를 놓치지 않으려는 노력이 보입니다. 매주 신기술 동향 보고회를 통해 전사적인 학습이 이루어집니다.",
    "회사 내부의 작은 갤러리나 휴게 공간이 예술적으로 꾸며져 있어, 창의적인 영감을 얻기 좋습니다.",
    "새로운 시도를 두려워하지 않는 스타트업 정신이 남아있어, 수평적인 관계 속에서 아이디어를 자유롭게 개진할 수 있습니다.",
    "점심 식사를 뷔페식으로 제공하고 커피차가 상주하는 등, 소소하지만 확실한 복지가 생활의 만족도를 높여줍니다.",
    "원격 근무가 활성화되어 있어 출퇴근 스트레스 없이 업무에 집중할 수 있습니다. 장비 지원도 최고 사양입니다."
]

NEGATIVE_TEMPLATES = [
    # 기술 및 성장 관련 (학생님 관심사)
    "데이터 분석 환경이 너무 오래된 레거시 시스템에 의존합니다. 파이썬 2.7 환경을 벗어나지 못해 최신 트랜스포머 모델을 적용할 엄두도 내지 못하고 있습니다.",
    "개인의 성장을 위한 교육 지원이 전무합니다. 텐서플로우나 MLOps 같은 신기술은 개인 시간을 할애해서 독학해야 하며, 회사 차원의 투자가 전혀 없습니다.",
    "워라밸은 좋지만, 이는 성장이 멈췄다는 의미이기도 합니다. 다루는 데이터의 종류가 한정적이라 흥미를 잃었고, 커리어 발전 속도가 매우 더딥니다.",
    "관리자들이 데이터 분석의 깊은 이해 없이 겉핥기식의 결과만 요구합니다. CNN이나 RNN의 원리를 설명해도 이해하지 못해 답답함을 느낄 때가 많습니다.",
    "협업 도구가 미비하고, 데이터가 여러 부서에 흩어져 있어 데이터 접근 권한을 얻는 데만 한 달이 걸렸습니다. Pandas로 데이터를 모으는 것 자체가 큰 일이었습니다.",
    "분석 환경이 윈도우 기반이라 리눅스 환경에서 주로 돌아가는 Docker나 Kubernetes 기반 MLOps 툴을 사용하기 어렵습니다. 기술 스택 확장에 제약이 큽니다.",
    "RDBMS 스키마가 너무 복잡하게 꼬여 있어 SQL 쿼리를 작성하는 데만 하루 종일 걸립니다. 데이터베이스 최적화가 시급합니다.",
    "결측치 처리나 이상치 탐지 과정이 수동으로 이루어집니다. 파이프라인 자동화에 대한 필요성을 인지하지 못하고 있습니다.",
    "회귀분석 외에 Clustering, GMM 같은 비지도 학습 모델을 적용하려는 시도 자체가 거부됩니다. 기존 방식만 고수하려는 보수적인 문화가 강합니다.",
    "GPU 서버 지원이 매우 인색하여 딥러닝 모델 학습에 많은 시간이 소요됩니다. 개인 노트북으로 학습하는 것이 더 빠를 지경입니다.",
    
    # 문화, 복지 및 WLB 관련
    "수평적 문화를 외치지만, 실제로는 고압적인 분위기입니다. 보고서의 폰트나 색깔 같은 사소한 것에 시간을 많이 뺏기며, 효율성이 극도로 낮습니다.",
    "야근이 일상입니다. '편하게 일하는 것'은 기대하기 어렵습니다. 주말에도 업무 관련 연락이 자주 오며, 퇴근 후에도 개인 시간을 확보하기 어렵습니다.",
    "연봉 인상률이 물가 상승률보다 낮습니다. 직원들의 불만이 높지만, 경영진은 개선 의지가 전혀 보이지 않습니다. (평점 1점대)",
    "입사 후 사수 없이 바로 현장에 투입되어 OJT(On-the-Job Training)가 거의 불가능합니다. 마치 바다에 던져진 기분이었고, 자생해야 합니다.",
    "불필요한 회의가 너무 많아 업무 집중도를 저해합니다. 회의를 위한 회의가 반복되는 비효율적인 구조입니다.",
    "복지는 겉으로만 화려합니다. 실제로 사용하려고 하면 까다로운 절차가 필요하거나 눈치를 봐야 합니다.",
    "경영진의 잦은 방향 변경으로 프로젝트가 중간에 엎어지는 경우가 많습니다. 비전이 불분명하고 목표가 자주 바뀝니다.",
    "퇴사율이 매우 높고, 인수인계가 제대로 이루어지지 않아 업무 부하가 기존 직원에게 전가됩니다. 팀 분위기가 매우 불안정합니다.",
    "직원들의 사기를 진작시키기 위한 노력이 전혀 없습니다. 당근 없이 채찍만 있는 분위기입니다.",
    "업무 외적인 친목 활동(강제 회식, 주말 등산 등) 참여를 강요하는 분위기가 있어 개인 시간이 부족합니다.",
    
    # 면접 관련 (심층적/부정적 질문 추가)
    f"[{INDUSTRIES[random.randint(0, 9)]}] 업종 특성상 보수적인 문화가 강해, 새로운 시도나 아이디어는 무조건 거부당하는 분위기입니다.",
    f"[IT/웹/통신] 금융 거래 데이터 분석을 통한 이상 탐지 모델 개발에 참여했습니다. 민감 데이터 처리 경험을 쌓기 좋습니다.",
    "MLOps 파이프라인 설계 경험 중 가장 처리가 어려웠던 데이터 버전 관리(Data Versioning) 이슈와 해결 방법을 설명해 주세요.",
    "정규화 모델(L1, L2)의 수학적 원리를 설명하고, 대용량 데이터셋에서 L2 정규화가 L1보다 계산 효율이 좋은 이유를 구체적으로 기술하시오.",
    "K-means 클러스터링을 적용할 때 초기 중심값 설정에 따라 결과가 달라지는 문제를 어떻게 해결했는지, 구체적인 방법(K-means++)과 그 원리를 설명해 보세요."
]


# --- 2. 헬퍼 함수: 랜덤 데이터 생성 ---

def get_random_date(days_ago=365):
    """최근 1년 이내의 랜덤 날짜 (YYYY-MM-DD) 반환"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_ago)
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime("%Y-%m-%d")

def get_random_text(min_len, max_len, sector_name, is_positive=True):
    """최소-최대 길이 범위의 랜덤 텍스트를 생성 (긍정/부정 템플릿 사용)"""
    
    templates = POSITIVE_TEMPLATES if is_positive else NEGATIVE_TEMPLATES
    
    # 면접 질문을 위한 별도 템플릿 추가
    if min_len >= 30 and not is_positive: 
        templates.extend([
            f"[{sector_name}] 지원자가 경험한 가장 복잡했던 데이터 분석 프로젝트에 대해 설명하시오. 이때 발생한 결측치 처리 방법과 왜 그 방법을 선택했는지 기술적 근거를 제시해주세요. (Data Analysis)",
            "트랜스포머의 인코더와 디코더의 역할 차이점을 설명하고, 시퀀스 투 시퀀스 학습에서 어떻게 활용되는지 구체적인 예시(예: 번역 모델)를 들어 설명하시오. (Deep Learning)",
            "회귀분석 모델을 구축할 때 과적합(Overfitting)을 방지하기 위한 정규화 모델(L1, L2)의 원리를 설명하고, 언제 어떤 정규화 기법을 적용해야 하는지 판단 기준을 설명해 주세요. (Machine Learning)",
        ])

    base_text = random.choice(templates)
    
    # 문장의 길이를 늘리기 위해 반복
    # 텍스트 길이를 늘릴 때, 불필요한 반복을 줄이고 다양한 템플릿의 문장을 섞음
    num_sentences = random.randint(3, 8)
    long_text_parts = random.choices(templates, k=num_sentences)
    long_text = " ".join(long_text_parts)
    
    # 최종적으로 길이를 자르거나 조정 (최소 길이는 보장)
    if len(long_text) > max_len:
        # 문장 경계에서 자르기
        long_text = long_text[:max_len]
        # 문장이 중간에 잘리지 않도록 마침표('.') 이후에 잘림
        last_dot_index = long_text.rfind('.')
        if last_dot_index != -1 and len(long_text) - last_dot_index < 50:
            long_text = long_text[:last_dot_index + 1]
    
    if len(long_text) < min_len:
        # 최소 길이 보장이 어려울 경우, 랜덤 문장을 추가
        long_text += " " + random.choice(POSITIVE_TEMPLATES) 
        if len(long_text) > max_len: long_text = long_text[:max_len]
        
    return long_text.strip()

def apply_missing_value(data_dict, fields_to_check):
    """10% 확률로 지정된 필드 중 하나에 결측치(None) 주입"""
    if random.random() < MISSING_RATE:
        # 결측치를 주입할 필드를 무작위로 선택
        field_to_null = random.choice(fields_to_check)
        data_dict[field_to_null] = None
        # 결측치가 들어갔음을 로그에 표시하기 위해 타이틀 변경
        # 모든 텍스트 필드에 None이 들어갈 수 있으므로, re_title에만 표시
        if 're_title' in data_dict:
            data_dict['re_title'] = f"({data_dict['re_title'][:10]}... - 결측치 포함)" 
        elif 'in_title' in data_dict:
            data_dict['in_title'] = f"({data_dict['in_title'][:10]}... - 결측치 포함)"
    return data_dict


# --- 3. 리뷰 및 면접 데이터 생성 함수 ---

def generate_review(sector_name, data_id):
    """리뷰 데이터 객체 생성"""
    review_data = {
        # re_title은 중립/긍정 템플릿 사용
        "re_title": get_random_text(20, 100, sector_name, is_positive=True).strip(),
        # 장점(re_adv)은 긍정 템플릿 사용
        "re_adv": get_random_text(30, 1000, sector_name, is_positive=True).strip(),
        # 단점(re_dis)은 부정 템플릿 사용
        "re_dis": get_random_text(30, 1000, sector_name, is_positive=False).strip(),
        "re_score": random.randint(1, 5),
        "re_date": get_random_date()
    }
    # re_adv, re_dis, re_score 중 하나에 결측치 주입 시도
    review_data = apply_missing_value(review_data, ['re_adv', 're_dis', 're_score'])
    
    return {
        "type": "review",
        "data_id": f"{data_id}_R", # 데이터 식별자
        "review": review_data
    }

def generate_interview(sector_name, data_id):
    """면접 데이터 객체 생성"""
    interview_data = {
        # in_title은 중립/긍정 템플릿 사용
        "in_title": get_random_text(20, 100, sector_name, is_positive=True).strip(),
        # 질문(in_query)은 심층적/부정적 템플릿 사용
        "in_query": get_random_text(30, 1000, sector_name, is_positive=False).strip(), 
        # 느낌(in_vibe)은 중립/긍정 템플릿 사용
        "in_vibe": get_random_text(30, 1000, sector_name, is_positive=True).strip(),
        "in_level": random.choice(LEVELS),
        "in_date": get_random_date()
    }
    # in_query, in_vibe, in_level 중 하나에 결측치 주입 시도
    interview_data = apply_missing_value(interview_data, ['in_query', 'in_vibe', 'in_level'])
    
    return {
        "type": "interview",
        "data_id": f"{data_id}_I", # 데이터 식별자
        "interview": interview_data
    }


# --- 4. 메인 데이터 생성 로직 ---
def generate_jobis_data_file():
    all_jobis_data = []
    company_counter = 0
    data_id_counter = 0

    print("--- Jobis RAG 더미 데이터 생성 시작 (총 10,000개 목표) ---")
    
    # 10개 업종을 순회 (INDUSTRIES 리스트 길이만큼 자동으로 반복)
    for sector_name in INDUSTRIES:
        # 각 업종별로 10개 기업 생성
        sector_companies = [f"{sector_name}_{template}" for template in COMPANY_TEMPLATES[sector_name][:10]]
        
        for company_name in sector_companies:
            company_counter += 1
            company_data_list = []
            
            # --- 변경 사항: 각 기업별로 리뷰 10개, 면접 후기 10개 생성 ---

            for i in range(10): 
                data_id_counter += 1
                company_data_list.append(generate_review(sector_name, data_id_counter))
                
                data_id_counter += 1
                company_data_list.append(generate_interview(sector_name, data_id_counter))

            # 최종 기업 객체 구조
            company_obj = {
                "company_id": f"CID{company_counter:03d}",
                "company_name": company_name,
                "industry": sector_name,
                "data": company_data_list
            }
            all_jobis_data.append(company_obj)
            
            print(f"  [+] 생성 완료: {company_name} ({sector_name}) - 데이터 {len(company_data_list)}개")

    # --- 5. JSON 파일 저장 ---
    FILE_NAME = "jobis_rag_data.json"
    try:
        with open(FILE_NAME, 'w', encoding='utf-8') as f:
            # indent=2를 사용하여 사람이 읽기 쉬운 형태로 저장
            json.dump(all_jobis_data, f, ensure_ascii=False, indent=2)
        
        # 최종 총 데이터 수 (100개 기업 * 100개 데이터 = 10,000개)
        print("\n==============================================")
        print(f"✅ 총 {company_counter}개 기업, {data_id_counter}개 데이터 생성 완료! (총 10,000개 데이터)")
        print(f"파일 경로: {FILE_NAME}")
        print("==============================================")
        
    except Exception as e:
        print(f"\n❌ 파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    generate_jobis_data_file()