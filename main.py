import streamlit as st
import pandas as pd

# --------------------------------------------------------------------------
# 1. 초기 설정 및 데이터 로드
# --------------------------------------------------------------------------

# 페이지 기본 설정
st.set_page_config(page_title="과목 유형 검사", page_icon="📚", layout="centered")

@st.cache_data # 데이터 로딩은 캐시에 저장하여 성능 향상
def load_data(file_path):
    """엑셀 파일을 로드하고 기본 전처리를 수행하는 함수"""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다. main.py와 같은 폴더에 엑셀 파일을 넣어주세요.")
        return None
    except Exception as e:
        st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
        return None

# 데이터 로드 (엑셀 파일 이름을 'data.xlsx'로 가정)
df = load_data('data.xlsx')


# ==================================================================
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 디버깅 코드 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
#
# 이 부분에서 프로그램이 인식하는 실제 엑셀 컬럼명을 화면에 보여줍니다.
if df is not None:
    st.warning("코드가 현재 인식하고 있는 엑셀 컬럼명 리스트입니다:")
    st.write(list(df.columns))
#
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 디버깅 코드 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ==================================================================


# 필수 컬럼명 정의 (엑셀 파일과 정확히 일치해야 함)
required_columns = ['번호', '문항', '척도', '카테고리', '관련교과군']

# 데이터 또는 필수 컬럼이 없는 경우 앱 실행 중지
if df is None or not all(col in df.columns for col in required_columns):
    st.error(f"엑셀 파일에 필수 컬럼 {required_columns} 이(가) 모두 포함되어 있는지, 혹은 이름이 정확한지 위의 노란색 경고창과 비교하여 확인해주세요.")
    st.stop()


# 교과군(섹션) 순서 정의
SECTION_ORDER = ['기초교과군', '제2외국어군', '과학군', '사회군']
section_list = [s for s in SECTION_ORDER if s in df['관련교과군'].unique()]


# --------------------------------------------------------------------------
# 2. 세션 상태(Session State) 초기화
# --------------------------------------------------------------------------

# 현재 진행 중인 섹션 번호 (0부터 시작)
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0

# 전체 답변을 저장할 딕셔너리
if 'responses' not in st.session_state:
    st.session_state.responses = {}

# --------------------------------------------------------------------------
# 3. UI 및 로직 구현
# --------------------------------------------------------------------------

st.title("📚 나의 과목 선호 유형 검사")
st.write("---")

def display_survey():
    """현재 섹션의 설문을 표시하고 답변을 처리하는 함수"""
    section_index = st.session_state.current_section
    current_section_name = section_list[section_index]
    questions_df = df[df['관련교과군'] == current_section_name]
    
    st.progress((section_index + 1) / len(section_list), text=f"{section_index + 1}/{len(section_list)} 단계 진행 중")
    
    with st.form(key=f"section_{section_index}"):
        st.header(f"섹션 {section_index + 1}: {current_section_name}")
        st.write("각 문항을 읽고 자신과 가장 가깝다고 생각하는 정도를 선택해주세요.")
        
        for _, row in questions_df.iterrows():
            question_id = row['번호']
            question_text = row['수정내용']
            st.markdown(f"**{question_id}. {question_text}**")
            st.radio(
                "1(전혀 그렇지 않다) ~ 5(매우 그렇다)",
                options=[1, 2, 3, 4, 5],
                key=f"q_{question_id}",
                horizontal=True,
                label_visibility="collapsed"
            )
        
        is_last_section = (section_index == len(section_list) - 1)
        button_label = "결과 분석하기" if is_last_section else "다음 섹션으로"
        if st.form_submit_button(button_label):
            for _, row in questions_df.iterrows():
                question_id = row['번호']
                st.session_state.responses[question_id] = st.session_state[f"q_{question_id}"]
            
            st.session_state.current_section += 1
            st.rerun()

def display_results():
    """모든 설문 완료 후 결과를 계산하고 표시하는 함수"""
    with st.spinner('결과를 분석하는 중입니다...'):
        all_subjects = df['카테고리'].unique()
        scores = {subject: 0 for subject in all_subjects}

        for question_id, user_answer in st.session_state.responses.items():
            question_data = df[df['번호'] == question_id].iloc[0]
            scale = question_data['척도']
            subject = question_data['카테고리']
            
            score_to_add = (6 - user_answer) if scale == '역' else user_answer
            scores[subject] += score_to_add

        final_scores = {subject: score for subject, score in scores.items() if score > 0}
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)

    st.balloons()
    st.header("📈 최종 분석 결과")

    if not sorted_scores:
        st.warning("분석 결과가 없습니다. 모든 문항에 답변했는지 확인해주세요.")
    else:
        top_subject = sorted_scores[0][0]
        st.success(f"### 🥇 당신의 최고 선호 과목 유형은 **{top_subject}** 입니다!")
        st.subheader("과목별 선호도 점수")
        chart_data = pd.DataFrame.from_dict(final_scores, orient='index', columns=['점수'])
        st.bar_chart(chart_data)

    if st.button("검사 다시하기"):
        st.session_state.current_section = 0
        st.session_state.responses = {}
        st.rerun()

# --- 4. 메인 로직 실행 ---
if st.session_state.current_section < len(section_list):
    display_survey()
else:
    display_results()
