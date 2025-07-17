네, 그럼요. 그동안 논의한 모든 기능(버전 선택, 복합 채점, 조언 전광판)을 포함한 전체 스트림릿 예시 코드를 작성해 드릴게요.

이 코드를 `app.py`와 같은 파이썬 파일로 저장하고, 필요한 라이브러리(`streamlit`, `pandas`)를 설치한 후 터미널에서 `streamlit run app.py` 명령을 실행하면 바로 테스트할 수 있습니다.

코드의 각 부분에 대한 설명은 주석으로 상세히 달아두었으니, 학생들이 직접 코드를 분석하고 수정하며 학습하는 데 도움이 될 것입니다.

-----

### **전체 스트림릿 코드 (`app.py`)**

```python
import streamlit as st
import pandas as pd
import random
import time

# --------------------------------------------------------------------------
# 1. 데이터 준비: 이 부분에 실제 문항과 조언 데이터를 채워주세요.
# --------------------------------------------------------------------------

# 전체 과목 리스트
SUBJECTS = [
    '국어', '수학', '영어', '독일어', '일본어', '중국어',
    '물리', '화학', '생명과학', '지구과학',
    '일반사회', '역사', '윤리', '지리'
]

# 선배들의 한 줄 조언 리스트
ADVICE_LIST = [
    "물리는 개념을 확실히 잡고 문제를 풀어야 응용이 쉬워져요. - 3학년 김OO",
    "사회문화는 도표 분석 문제가 핵심! 통계 자료에 익숙해지세요. - 졸업생 박OO",
    "일본어는 히라가나, 가타카나만 외워도 절반은 성공! 꾸준함이 중요해요. - 3학년 이OO",
    "수학은 오답 노트를 만드는 습관이 정말 큰 도움이 됩니다. 포기하지 마세요! - 2학년 최OO",
    "화학은 주기율표와 친해지는 것부터 시작하세요! 모든 것의 기본이에요. - 3학년 정OO",
    "역사는 큰 흐름을 먼저 이해하고 세부 사건을 채워나가는 방식으로 공부하세요. - 졸업생 강OO"
]

# 121문항 (정밀 버전) 데이터 예시
# id: 문항 고유 번호, text: 문항 내용
# categories: 연결된 과목 정보 리스트
#   - name: 과목명, reverse: 역척도 여부(True/False)
QUESTIONS_FULL = [
    {
        'id': 'full_1',
        'text': '소설이나 시를 읽고 등장인물의 감정을 상상하는 것을 즐긴다.',
        'categories': [{'name': '국어', 'reverse': False}]
    },
    {
        'id': 'full_2',
        'text': '수학 공식을 증명하는 과정에서 논리적인 희열을 느낀다.',
        'categories': [{'name': '수학', 'reverse': False}]
    },
    {
        'id': 'full_3',
        'text': '사회적 합의보다는 개인의 신념을 따르는 것이 더 중요하다고 생각한다.',
        'categories': [
            {'name': '역사', 'reverse': False},
            {'name': '윤리', 'reverse': True},
            {'name': '일반사회', 'reverse': True}
        ]
    },
    {
        'id': 'full_4',
        'text': '새로운 언어의 문법 구조를 파악하는 것에 흥미를 느낀다.',
        'categories': [
            {'name': '영어', 'reverse': False},
            {'name': '독일어', 'reverse': False},
            {'name': '일본어', 'reverse': False},
            {'name': '중국어', 'reverse': False}
        ]
    },
    # ... 여기에 121번 문항까지 추가 ...
]

# 80문항 (간편 버전) 데이터 예시
QUESTIONS_SIMPLE = [
    {
        'id': 'simple_1',
        'text': '글을 읽고 핵심 내용을 요약하는 것을 잘한다.',
        'categories': [{'name': '국어', 'reverse': False}, {'name': '영어', 'reverse': False}]
    },
    {
        'id': 'simple_2',
        'text': '복잡한 문제의 규칙을 찾아 해결하는 것을 좋아한다.',
        'categories': [{'name': '수학', 'reverse': False}, {'name': '물리', 'reverse': False}]
    },
    {
        'id': 'simple_3',
        'text': '역사적 사건의 원인과 결과에 대해 토론하는 것을 즐긴다.',
        'categories': [{'name': '역사', 'reverse': False}, {'name': '일반사회', 'reverse': False}]
    },
    # ... 여기에 80번 문항까지 추가 ...
]


# --------------------------------------------------------------------------
# 2. 스트림릿 앱 구현
# --------------------------------------------------------------------------

def main():
    # 페이지 기본 설정
    st.set_page_config(page_title="나의 과목 유형 찾기", page_icon="📝", layout="centered")

    # --- 제목 ---
    st.title("📝 나의 과목 유형 찾기")
    st.write("---")

    # --- 선배들의 조언 전광판 ---
    st.subheader("💡 선배들의 꿀팁 한마디!")
    # st.empty()로 공간을 만들고, 매번 다른 조언을 보여줌 (페이지가 재실행될 때마다)
    advice_placeholder = st.empty()
    advice_placeholder.info(f"**{random.choice(ADVICE_LIST)}**")
    st.write("---")


    # --- 검사 버전 선택 ---
    version = st.radio(
        "**원하는 검사 버전을 선택해주세요.**",
        ('간편 버전 (80문항)', '정밀 버전 (121문항)'),
        index=None, # 처음에 아무것도 선택되지 않도록 설정
        horizontal=True
    )
    st.write("---")

    # 선택한 버전에 따라 문항 리스트 결정
    if version == '간편 버전 (80문항)':
        questions_to_display = QUESTIONS_SIMPLE
    elif version == '정밀 버전 (121문항)':
        questions_to_display = QUESTIONS_FULL
    else:
        # 아직 아무것도 선택하지 않았으면 안내 문구 표시
        st.info("👆 위에서 검사 버전을 선택하면 문항이 나타납니다.")
        st.stop() # 코드 실행 중지

    # --- 문항 제시 및 답변 입력 ---
    # st.form을 사용해 모든 문항에 답변 후 한 번에 제출하게 함
    with st.form(key='survey_form'):
        st.header(f"▶️ {version} 테스트 시작")
        st.write("각 문항을 읽고 자신과 가장 가깝다고 생각하는 정도를 선택해주세요.")
        st.write("(1점: 전혀 그렇지 않다 ~ 5점: 매우 그렇다)")

        # 답변을 저장할 딕셔너리
        user_responses = {}
        # 선택한 버전의 문항들을 화면에 표시
        for question in questions_to_display:
            q_id = question['id']
            q_text = question['text']
            # 각 문항의 답변을 user_responses에 저장
            user_responses[q_id] = st.radio(
                label=q_text,
                options=[1, 2, 3, 4, 5],
                key=q_id,
                horizontal=True
            )
            st.markdown("---") # 문항 사이에 구분선 추가

        # 제출 버튼
        submit_button = st.form_submit_button(label="결과 분석하기")


    # --- 결과 계산 및 출력 ---
    # 제출 버튼을 눌렀을 때만 아래 코드 실행
    if submit_button:
        # 로딩 스피너 표시
        with st.spinner('결과를 분석하는 중입니다... 잠시만 기다려주세요.'):
            # 과목별 점수 초기화
            scores = {subject: 0 for subject in SUBJECTS}

            # 답변을 바탕으로 점수 계산
            for question in questions_to_display:
                q_id = question['id']
                user_answer = user_responses[q_id]

                # 해당 문항에 연결된 모든 과목 정보에 대해 점수 계산
                for category_info in question['categories']:
                    subject_name = category_info['name']
                    is_reverse = category_info['reverse']

                    # 역척도 처리: (최대점수+1) - 현재점수
                    score_to_add = (6 - user_answer) if is_reverse else user_answer

                    # 계산된 점수를 해당 과목에 누적
                    scores[subject_name] += score_to_add

            # 점수가 0인 과목은 결과에서 제외
            final_scores = {subject: score for subject, score in scores.items() if score > 0}
            # 점수가 높은 순으로 정렬
            sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)

            # 2초간 대기 (결과 분석 중인 것처럼 보이기 위함)
            time.sleep(2)

        # 결과 출력
        st.balloons() # 결과가 나왔을 때 풍선 효과!
        st.header("📈 나의 과목 선호도 분석 결과")

        # 최고 선호 과목 표시
        if sorted_scores:
            top_subject = sorted_scores[0][0]
            st.success(f"### 🥇 당신의 최고 선호 과목 유형은 **{top_subject}** 입니다!")

        # 전체 점수 시각화 (Pandas DataFrame으로 변환 후 st.bar_chart 사용)
        st.subheader("과목별 선호도 점수")
        chart_data = pd.DataFrame.from_dict(final_scores, orient='index', columns=['점수'])
        st.bar_chart(chart_data)

        # 상세 점수표 보여주기
        st.subheader("상세 점수표")
        st.table(pd.DataFrame(sorted_scores, columns=['과목', '점수']))


if __name__ == "__main__":
    main()
```
