import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="과목 유형 검사", page_icon="📚", layout="centered")

# @st.cache_data -> 캐시 기능을 잠시 비활성화
def load_data(file_path):
    """엑셀 파일을 로드하는 함수"""
    try:
        df = pd.read_excel(file_path)
        # 모든 컬럼명의 앞뒤 공백을 강제로 제거
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"엑셀 파일 로드 중 오류: {e}")
        return None

# 데이터 로드
df = load_data('data.xlsx')

# 필수 컬럼명 정의
required_columns = ['번호', '수정내용', '척도', '카테고리', '관련교과군']

st.title("최종 디버깅 모드")
st.write("---")

if df is not None:
    st.info("현재 엑셀에서 인식된 컬럼명: " + str(list(df.columns)))
    
    # --- 최종 검증 로직 ---
    st.subheader("▼▼▼ 최종 검증 결과 ▼▼▼")
    
    # 모든 필수 컬럼이 존재하는지 단 한 번만 검사
    all_columns_ok = all(col in df.columns for col in required_columns)
    
    if all_columns_ok:
        st.success("✅ 모든 필수 컬럼이 정상적으로 확인되었습니다.")
        st.write("오류가 발생해서는 안됩니다. 만약 이 메시지 아래에 오류가 보인다면, 앱 자체의 문제입니다.")
    else:
        st.error("❌ 필수 컬럼 중 일부가 일치하지 않습니다.")
        st.write("아래 상세 비교에서 `False`로 표시된 컬럼을 확인해주세요.")
        
        # 어떤 컬럼이 문제인지 상세 출력
        for req_col in required_columns:
            is_present = req_col in df.columns
            if not is_present:
                st.warning(f"'{req_col}' 컬럼을 찾을 수 없습니다. (일치 여부: {is_present})")

    st.write("---")
    # --- 검증 로직 종료 ---


    # 실제 앱 실행 로직 (검증 결과에 따라 실행)
    if not all_columns_ok:
        st.stop() # 검증 실패 시 앱 중지

    # (이하 정상 작동 로직)
    st.header("정상 진행")
    st.write("검사를 시작할 수 있습니다.")
    # 실제 설문 로직은 여기에 위치...

else:
    st.error("엑셀 파일 로드에 실패하여 검증을 진행할 수 없습니다.")
