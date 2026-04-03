import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="장난감 공간", page_icon="👾", layout="centered")

st.title("👾 민규만의 장난감 공간 (Playground)")
st.markdown("---")

st.write("여기는 새로운 AI 기능, 프롬프트, UI 등을 자유롭게 테스트해 보는 공간입니다.")

# 테스트용 탭 만들어두기
tab1, tab2 = st.tabs(["🧪 테스트 1", "🛠️ 테스트 2"])

with tab1:
    st.subheader("첫 번째 실험실")
    st.info("여기에 테스트할 코드를 자유롭게 작성하세요.")
    
with tab2:
    st.subheader("두 번째 실험실")
    st.write("새로운 기능을 덧붙일 때 사용하세요.")