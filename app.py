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
# 2. 메뉴 가이드 (카드 UI & 바로가기 버튼)
# ==========================================
st.markdown("### 🧭 작업실 바로가기")
st.write("아래의 버튼을 클릭하거나 왼쪽 사이드바를 통해 원하시는 작업실로 이동하세요!")
st.write("") 

# 2x3 그리드 형태로 카드 배치
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### ⚙️ 00 Settings")
        st.write("**데이터 및 취향 관리**")
        st.caption("블로그 원문 데이터를 수집하고, 내 취향 데이터를 관리하는 기본 설정 공간입니다.")
        st.write("") 
        try:
            st.page_link("pages/00_⚙️_Settings.py", label="Settings 이동하기", icon="⚙️")
        except:
            st.button("⚙️ 파일 경로를 맞춰주세요", disabled=True, use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("### ✍️ 01 Movie Blog")
        st.write("**영화 리뷰/프리뷰 자동화**")
        st.caption("TMDB와 네이버 뉴스를 바탕으로 영화 관련 포스팅을 자동 생성합니다.")
        st.write("") 
        st.page_link("pages/01_🎬_Movie_Blog.py", label="Movie Blog 이동하기", icon="🚀")

with col3:
    with st.container(border=True):
        st.markdown("### 📸 02 Daily Life")
        st.write("**일상 & 현장 기록**")
        st.caption("PDF 자료나 현장 사진을 업로드하여 나만의 감성이 담긴 현장 일지를 작성합니다.")
        st.write("") 
        st.page_link("pages/02_🏠_Daily_Life.py", label="Daily Life 이동하기", icon="🚀")

with col4:
    with st.container(border=True):
        st.markdown("### 🔍 03 Movie Search")
        st.write("**하이브리드 영화 대시보드**")
        st.caption("실시간 박스오피스 순위를 확인하고, 다양한 영화의 상세 정보를 검색합니다.")
        st.write("") 
        st.page_link("pages/03_🎬_Movie_Search.py", label="Movie Search 이동하기", icon="🚀")

with col5:
    with st.container(border=True):
        st.markdown("### 🎨 04 Thumbnail")
        st.write("**넷플릭스 스타일 블로그 썸네일**")
        st.caption("영화 스틸컷을 업로드하고 제목을 입력하면 넷플릭스 스타일 썸네일을 바로 다운로드할 수 있습니다.")
        st.write("")
        st.page_link("pages/04_🎨_Thumbnail.py", label="Thumbnail 이동하기", icon="🎨")

with col6:
    with st.container(border=True):
        st.markdown("### 📰 05 카드뉴스 메이커")
        st.write("**영화모임 카드뉴스 4종 세트**")
        st.caption("커버·정보·소개·신청 4장짜리 카드뉴스를 만들어 인스타그램에 바로 올릴 수 있습니다.")
        st.write("")
        st.page_link("pages/05_📰_Card_News.py", label="카드뉴스 메이커 이동하기", icon="📰")

# ==========================================
# 4. 하단 꿀팁
# ==========================================
st.markdown("---")
st.info("💡 **Tip:** 스마트폰 브라우저(웨일, 크롬, 사파리)의 **'홈 화면에 추가'** 기능을 이용하시면 바탕화면 아이콘을 통해 앱처럼 바로 접속하실 수 있습니다!")