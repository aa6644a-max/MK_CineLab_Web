import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="MK 작업실", page_icon="🛠️", layout="centered")

# 대문 화면 내용
st.title("🛠️ MK의 작업실에 오신 것을 환영합니다!")
st.markdown("---")

st.subheader("반갑습니다! 왼쪽 메뉴에서 원하는 작업을 선택해 주세요.")

st.info("""
👈 **왼쪽 사이드바를 확인해 보세요!**
- **00 Settings**: 블로그 원문 데이터 수집 및 포스팅 내용을 저장하고 관리하는 공간입니다.
- **01 Movie Blog**: 기존에 쓰시던 영화 리뷰, 프리뷰, 뉴스 자동화 프로그램입니다.
- **02 Daily Life**: 일상과 현장 기록 등 다양한 포스팅을 작성하는 공간입니다.
- **03 Playground**: 자유롭게 새로운 AI 기능이나 프롬프트를 테스트해 보는 민규님만의 장난감 공간입니다! 👾
""")