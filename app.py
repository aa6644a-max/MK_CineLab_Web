import streamlit as st

# 페이지 기본 설정 (넓은 화면 사용)
st.set_page_config(page_title="MK 작업실", page_icon="🛠️", layout="wide")

# ==========================================
# 1. 메인 환영 배너 (Hero Section)
# ==========================================
st.markdown("""
    <div style='text-align: center; padding: 2rem 0; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🛠️ MK's 통합 자동화 작업실</h1>
        <p style='font-size: 1.2rem; color: #555;'>영화 리뷰부터 일상 기록까지, 모든 창작을 스마트하게 연결하는 공간입니다.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. 메뉴 가이드 (카드 UI)
# ==========================================
st.markdown("### 🧭 사이드바 메뉴 가이드")
st.write("왼쪽 사이드바 메뉴에서 원하시는 작업을 선택해 주세요. (모바일의 경우 좌측 상단 **`>`** 버튼 클릭)")
st.write("") # 약간의 여백 추가

# 2x2 그리드 형태로 카드 배치
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### ⚙️ 00 Settings")
        st.write("**데이터 및 취향 관리**")
        st.caption("블로그 원문 데이터를 수집하고, 포스팅에 활용될 내 취향 데이터를 관리하는 기본 설정 공간입니다.")

with col2:
    with st.container(border=True):
        st.markdown("### ✍️ 01 Movie Blog")
        st.write("**영화 리뷰/프리뷰 자동화**")
        st.caption("TMDB와 네이버 뉴스를 바탕으로 영화 리뷰, 기대작 프리뷰, 큐레이션 포스팅을 자동 생성합니다.")

with col3:
    with st.container(border=True):
        st.markdown("### 📸 02 Daily Life")
        st.write("**일상 & 현장 기록**")
        st.caption("PDF 자료나 현장 사진을 업로드하여 나만의 감성이 담긴 일상, 맛집, 현장 일지를 작성합니다.")

with col4:
    with st.container(border=True):
        st.markdown("### 🔍 03 Movie Search & Play")
        st.write("**하이브리드 영화 대시보드 & 테스트룸**")
        st.caption("실시간 박스오피스 순위를 확인하고, 자유롭게 새로운 AI 프롬프트를 테스트해 보는 장난감 공간입니다.")

# ==========================================
# 3. 하단 꿀팁
# ==========================================
st.markdown("---")
st.info("💡 **Tip:** 스마트폰 브라우저(웨일, 크롬, 사파리)의 **'홈 화면에 추가'** 기능을 이용하시면 바탕화면 아이콘을 통해 앱처럼 바로 접속하실 수 있습니다!")