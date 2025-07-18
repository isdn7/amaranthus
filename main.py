import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="과목 유형 검사", page_icon="📚", layout="centered")

@st.cache_data
def load_data(file_path):
    """CSV 파일을 로드하고 데이터를 정리하는 함수"""
    try:
        df = pd.read_csv(file_path, dtype={'번호': str})
        
        # 컬럼명 및 데이터 공백 제거
        df.columns = df.columns.str.strip()
        if '관련교과군' in df.columns:
            df['관련교과군'] = df['관련교과군'].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # --- 핵심 수정 부분: 축약된 과목명을 전체 이름으로 변경 ---
        if '관련교과군' in df.columns:
            name_map = {
                '생명': '생명과학',
                '지구': '지구과학',
                '일사': '일반사회'
            }
            df['관련교과군'] = df['관련교과군'].replace(name_map)
            
        return df
    except Exception as e:
        st.error(f"CSV 파일 로드 중 오류: {e}")
        return None

# data.csv 파일을 읽도록 설정
df = load_data('data.csv')
required_columns = ['번호', '수정내용', '척도', '카테고리', '관련교과군']

if df is None or not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 컬럼명을 확인해주세요.")
    st.stop()

# 과목 순서 정의
SUBJECT_ORDER = [
    '국어', '수학', '영어', '독일어', '중국어', '일본어',
    '물리', '화학', '생명과학', '지구과학',
    '일반사회', '역사', '윤리', '지리'
]
# 섹션(카테고리) 순서 정의 및 생성
SECTION_ORDER = ['기초교과군', '제2외국어군', '과학군', '사회군']
section_list = [s for s in SECTION_ORDER if s in df['카테고리'].unique()]
if not section_list:
    st.error("CSV 파일의 '카테고리' 열 내용을 확인해주세요.")
    st.stop()

# 세션 상태 초기화
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}

st.title("📚 나의 과목 선호 유형 검사")
st.write("---")

def display_survey():
    section_index = st.session_state.current_section
    current_section_name = section_list[section_index]
    questions_df = df[df['카테고리'] == current_section_name].astype({'번호': str})
    
    st.progress((section_index + 1) / len(section_list), text=f"{section_index + 1}/{len(section_list)} 단계 진행 중")
    
    with st.form(key=f"section_{section_index}"):
        st.header(f"섹션 {section_index + 1}: {current_section_name}")
        st.write("각 문항을 읽고 자신과 가장 가깝다고 생각하는 정도를 선택해주세요.")
        
        for _, row in questions_df.iterrows():
            q_id_str = str(row['번호'])
            st.markdown(f"**{q_id_str}. {row['수정내용']}**")
            st.radio("1(전혀 그렇지 않다) ~ 5(매우 그렇다)", [1, 2, 3, 4, 5], key=f"q_{q_id_str}", horizontal=True, label_visibility="collapsed")
        
        is_last_section = (section_index == len(section_list) - 1)
        button_label = "결과 분석하기" if is_last_section else "다음 섹션으로"
        if st.form_submit_button(button_label):
            for _, row in questions_df.iterrows():
                q_id_str = str(row['번호'])
                st.session_state.responses[q_id_str] = st.session_state[f"q_{q_id_str}"]
            st.session_state.current_section += 1
            st.rerun()

def display_results():
    import plotly.express as px
    with st.spinner('결과를 분석하는 중입니다...'):
        scores = {subject: 0 for subject in df['관련교과군'].dropna().unique()}
        
        df_results = df.astype({'번호': str})

        for q_id, answer in st.session_state.responses.items():
            q_data_rows = df_results.loc[df_results['번호'] == q_id]
            
            if q_data_rows.empty: continue
            
            q_data = q_data_rows.iloc[0]
            scale = q_data['척도']
            subject = q_data['관련교과군']
            
            score_to_add = (6 - answer) if scale == '역' else answer
            
            if pd.notna(subject) and subject in scores:
                scores[subject] += score_to_add

        final_scores = {s: v for s, v in scores.items() if v > 0}
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)

    st.balloons()
    st.header("📈 최종 분석 결과")

    if sorted_scores:
        st.subheader("💡 나의 상위 선호 과목 Top 8")
        top_8_subjects = sorted_scores[:8]
        top_subjects_text = ", ".join([f"**{i+1}위**: {subject}" for i, (subject, score) in enumerate(top_8_subjects)])
        st.success(top_subjects_text)
        st.subheader("과목별 선호도 점수")
        
        scores_series = pd.Series(final_scores).reindex(SUBJECT_ORDER).fillna(0)
        chart_df = scores_series.reset_index()
        chart_df.columns = ['과목', '점수']

        fig = px.bar(chart_df, x='과목', y='점수')
        fig.update_xaxes(tickangle=0)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("분석 결과가 없습니다.")

    if st.button("검사 다시하기"):
        st.session_state.current_section = 0
        st.session_state.responses = {}
        st.rerun()

if st.session_state.current_section < len(section_list):
    display_survey()
else:
    display_results()
