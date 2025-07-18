import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="과목 유형 검사", page_icon="📚", layout="centered")

# @st.cache_data -> 캐시 기능을 잠시 비활성화하여 원인 분석
def load_data(file_path):
    """엑셀 파일을 로드하는 함수"""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
        return None

# 데이터 로드
df = load_data('data.xlsx')

# 필수 컬럼명 정의
required_columns = ['번호', '수정내용', '척도', '카테고리', '관련교과군']

# ==================================================================
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 정밀 디버깅 코드 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
if df is not None:
    st.error("--- 정밀 디버깅 모드 ---")
    
    st.write("**코드에서 요구하는 컬럼명:**")
    st.write(required_columns)
    
    actual_cols = list(df.columns)
    st.write("**엑셀에서 실제로 읽어온 컬럼명:**")
    st.write(actual_cols)
    
    st.write("**▼ 각 컬럼 일치 여부 상세 비교 ▼**")
    for req_col in required_columns:
        # 실제 컬럼 리스트와 타입을 비교하여 일치 여부 확인
        is_present = req_col in actual_cols
        st.info(f"코드의 '{req_col}' (타입: str)이(가) 엑셀에 있습니까?  👉  **{is_present}**")

    st.error("--- 디버깅 종료 ---")
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 정밀 디버깅 코드 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ==================================================================

# 데이터 또는 필수 컬럼이 없는 경우 앱 실행 중지
if df is None or not all(col in df.columns for col in required_columns):
    st.error("오류: 위 디버깅 결과를 확인하여, False로 나온 컬럼의 이름 또는 타입을 확인해주세요.")
    st.stop()

# --- 이하 코드는 동일 ---
st.title("📚 나의 과목 선호 유형 검사")
# (이하 나머지 코드는 생략, 이전 코드와 동일하게 유지)
# ...
