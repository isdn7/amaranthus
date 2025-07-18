import streamlit as st
import pandas as pd

st.header("🔬 데이터 정밀 진단")

try:
    # '번호' 열을 문자로 강제해서 CSV 파일 로드
    df = pd.read_csv('data.csv', dtype={'번호': str})
    st.success("data.csv 파일 로드 성공")
except Exception as e:
    st.error(f"파일 로드 실패: {e}")
    st.stop()

# 문제가 되는 '25'번 문항을 특정
test_id = '25'
st.info(f"'{test_id}'번 문항의 데이터를 검사합니다.")

# '번호' 열에서 '25'번을 찾음
q_data_rows = df.loc[df['번호'] == test_id]

st.write("---")

# --- 진단 결과 ---
st.subheader("1. '25'번으로 검색된 데이터:")
st.dataframe(q_data_rows)

st.subheader("2. 검색된 데이터의 개수:")
st.write(f"총 **{len(q_data_rows)}** 개의 행이 발견되었습니다.")

if not q_data_rows.empty:
    st.subheader("3. '척도' 컬럼의 내용:")
    scale_series = q_data_rows['척도']
    st.write(scale_series)

    st.subheader("4. '척도'가 '역'과 일치하는지 비교한 결과:")
    boolean_series = (scale_series == '역')
    st.write(boolean_series)
    st.warning("이 비교 결과가 True/False 하나가 아닌 여러 개로 나타나면 오류의 원인이 됩니다.")
