import streamlit as st
import pandas as pd

# --- 1. 초기 설정 및 데이터 로드 ---

# 페이지 기본 설정
st.set_page_config(page_title="과목 유형 검사", page_icon="📚", layout="centered")

@st.cache_data # 데이터 로딩은 캐시에 저장하여 성능 향상
def load_data(file_path):
    """엑셀 파일을 로드하고 기본 전처리를 수행하는 함수"""
    try:
        df = pd.read_excel(file_path)
        # 필수 컬럼 확인
        required_columns = ['번호', '수정내용', '척도', '카테고리', '관련교과군']
        if not all(col in df.columns for col in required_columns):
            st.error(f"엑셀 파일에 필수 컬럼({required_columns})이 모두 포함되어 있는지 확인해주세요.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 엑셀 파일을 넣어주세요.")
        return None
    except Exception as e:
        st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
        return None

# 데이터 로드
# 엑셀 파일 이름을 'data.xlsx'로 가정합니다.
df = load_data('data.xlsx')

# 데이터 로드에 실패하면 앱 실행 중지
if df is None:
    st.stop()

# 교과군(섹션) 순서 정의
SECTION_ORDER = ['기초교과군', '제2외국어군', '과학군', '사회군']
# 엑셀 파일에 있는 교과군만 순서에 맞게 필터링
section_list = [s for s in SECTION_ORDER if s in df['관련교과군'].unique()]

# --- 2. 세션 상태(Session State) 초기화 ---
# 세션 상태를 사용해 사용자의 진행 단계와 답변을 저장합니다.

# 현재 진행 중인 섹션 번호 (0부터 시작)
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0

# 전체 답변을 저장할 딕셔너리
if 'responses' not in st.session_state:
    st.session_state.responses = {}

# --- 3. UI 및 로직 구현 ---

# 제목
st.title("📚 나의 과목 선호 유형 검사")
st.write("---")

def display_survey():
    """현재 섹션의 설문을 표시하고 답변을 처리하는 함수"""
    
    # 현재 섹션 번호와 이름 가져오기
    section_index = st.session_state.current_section
    current_section_name = section_list[section_index]
    
    # 현재 섹션에 해당하는 문항들 필터링
    questions_df = df[df['관련교과군'] == current_section_name]
    
    # 진행 상태 표시
    st.progress((section_index + 1) / len(section_list), text=f"{section_index + 1}/{len(section_list)} 단계 진행 중")
    
    # 폼(Form)을 사용하여 현재 섹션의 모든 답변을 한 번에 제출
    with st.form(key=f"section_{section_index}"):
        st.header(f"섹션 {section_index + 1}: {current_section_name}")
        st.write("각 문항을 읽고 자신과 가장 가깝다고 생각하는 정도를 선택해주세요.")
        
        # 현재 섹션의 모든 문항을 반복하며 라디오 버튼 생성
        for _, row in questions_df.iterrows():
            question_id = row['번호']
            question_text = row['수정내용']
            st.markdown(f"**{question_id}. {question_text}**")
            # st.radio의 key를 고유하게 설정하여 답변이 섞이지 않도록 함
            st.radio(
                "1(전혀 그렇지 않다) ~ 5(매우 그렇다)",
                options=[1, 2, 3, 4, 5],
                key=f"q_{question_id}", # 고유 키
                horizontal=True,
                label_visibility="collapsed"
            )
        
        # '다음' 또는 '결과 분석하기' 버튼
        is_last_section = (section_index == len(section_list) - 1)
        button_label = "결과 분석하기" if is_last_section else "다음 섹션으로"
        submitted = st.form_submit_button(button_label)

        if submitted:
            # 현재 폼의 답변들을 세션 상태에 저장
            for _, row in questions_df.iterrows():
                question_id = row['번호']
                st.session_state.responses[question_id] = st.session_state[f"q_{question_id}"]
            
            # 다음 섹션으로 이동
            st.session_state.current_section += 1
            st.rerun() # 페이지를 새로고침하여 다음 섹션을 표시

def display_results():
    """모든 설문 완료 후 결과를 계산하고 표시하는 함수"""
    with st.spinner('결과를 분석하는 중입니다...'):
        # 과목별 점수 초기화
        all_subjects = df['카테고리'].unique()
        scores = {subject: 0 for subject in all_subjects}

        # 저장된 모든 답변을 바탕으로 점수 계산
        for question_id, user_answer in st.session_state.responses.items():
            question_data = df[df['번호'] == question_id].iloc[0]
            scale = question_data['척도']
            subject = question_data['카테고리']
            
            # 척도에 따라 점수 계산 ('역'인 경우 6에서 뺀다)
            score_to_add = (6 - user_answer) if scale == '역' else user_answer
            scores[subject] += score_to_add

        # 점수가 0인 과목은 제외
        final_scores = {subject: score for subject, score in scores.items() if score > 0}
        # 점수가 높은 순으로 정렬
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)

    st.balloons()
    st.header("📈 최종 분석 결과")

    if not sorted_scores:
        st.warning("분석 결과가 없습니다. 모든 문항에 답변했는지 확인해주세요.")
        return

    # 최고 선호 과목 표시
    top_subject = sorted_scores[0][0]
    st.success(f"### 🥇 당신의 최고 선호 과목 유형은 **{top_subject}** 입니다!")

    # 전체 점수 시각화
    st.subheader("과목별 선호도 점수")
    chart_data = pd.DataFrame.from_dict(final_scores, orient='index', columns=['점수'])
    st.bar_chart(chart_data)

    # 다시 시작하기 버튼
    if st.button("검사 다시하기"):
        # 세션 상태 초기화 후 새로고침
        st.session_state.current_section = 0
        st.session_state.responses = {}
        st.rerun()

# --- 4. 메인 로직 실행 ---
# 현재 진행 단계에 따라 설문 또는 결과 페이지를 표시
if st.session_state.current_section < len(section_list):
    display_survey()
else:
    display_results()
