import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="과목 유형 검사", page_icon="📚", layout="centered")

@st.cache_data
def load_data(file_path):
    """엑셀 파일을 로드하고 컬럼명 공백을 제거하는 함수"""
    try:
        df = pd.read_excel(file_path)
        # 모든 컬럼명의 앞뒤 공백을 제거하여 안정성 확보
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"엑셀 파일 로드 중 오류: {e}")
        return None

# 데이터 로드
df = load_data('data.xlsx')

# 필수 컬럼 리스트
required_columns = ['번호', '수정내용', '척도', '카테고리', '관련교과군']

# 데이터 로드 실패 또는 필수 컬럼 부재 시 앱 중지
if df is None or not all(col in df.columns for col in required_columns):
    st.error("엑셀 파일을 확인해주세요. 필수 컬럼이 모두 존재해야 합니다.")
    st.stop()

# 교과군(섹션) 순서 정의 및 생성
SECTION_ORDER = ['기초교과군', '제2외국어군', '과학군', '사회군']
section_list = [s for s in SECTION_ORDER if s in df['관련교과군'].unique()]

# 생성된 섹션이 없을 경우 안내 후 중지
if not section_list:
    st.error("엑셀 파일의 '관련교과군' 열에 '기초교과군', '과학군' 등의 내용이 올바르게 입력되었는지 확인해주세요.")
    st.stop()

# --- 세션 상태 초기화 ---
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}

# --- UI 및 로직 함수 ---
st.title("📚 나의 과목 선호 유형 검사")
st.write("---")

def display_survey():
    """현재 섹션의 설문을 표시하는 함수"""
    section_index = st.session_state.current_section
    current_section_name = section_list[section_index]
    questions_df = df[df['관련교과군'] == current_section_name]
    
    st.progress((section_index + 1) / len(section_list), text=f"{section_index + 1}/{len(section_list)} 단계 진행 중")
    
    with st.form(key=f"section_{section_index}"):
        st.header(f"섹션 {section_index + 1}: {current_section_name}")
        st.write("각 문항을 읽고 자신과 가장 가깝다고 생각하는 정도를 선택해주세요.")
        
        for _, row in questions_df.iterrows():
            st.markdown(f"**{row['번호']}. {row['수정내용']}**")
            st.radio("1(전혀 그렇지 않다) ~ 5(매우 그렇다)", [1, 2, 3, 4, 5], key=f"q_{row['번호']}", horizontal=True, label_visibility="collapsed")
        
        is_last_section = (section_index == len(section_list) - 1)
        button_label = "결과 분석하기" if is_last_section else "다음 섹션으로"
        if st.form_submit_button(button_label):
            for _, row in questions_df.iterrows():
                st.session_state.responses[row['번호']] = st.session_state[f"q_{row['번호']}"]
            st.session_state.current_section += 1
            st.rerun()

def display_results():
    """결과를 계산하고 표시하는 함수"""
    with st.spinner('결과를 분석하는 중입니다...'):
        scores = {subject: 0 for subject in df['카테고리'].unique()}

        for q_id, answer in st.session_state.responses.items():
            q_data = df.loc[df['번호'] == q_id].iloc[0]
            score = (6 - answer) if q_data['척도'] == '역' else answer
            scores[q_data['카테고리']] += score

        final_scores = {s: v for s, v in scores.items() if v > 0}
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)

    st.balloons()
    st.header("📈 최종 분석 결과")

    if sorted_scores:
        st.success(f"### 🥇 당신의 최고 선호 과목 유형은 **{sorted_scores[0][0]}** 입니다!")
        st.subheader("과목별 선호도 점수")
        st.bar_chart(pd.DataFrame.from_dict(final_scores, orient='index', columns=['점수']))
    else:
        st.warning("분석 결과가 없습니다.")

    if st.button("검사 다시하기"):
        st.session_state.current_section = 0
        st.session_state.responses = {}
        st.rerun()

# --- 메인 로직 실행 ---
if st.session_state.current_section < len(section_list):
    display_survey()
else:
    display_results()
