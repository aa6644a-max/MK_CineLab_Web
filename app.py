# ... (상단 배너 코드는 동일) ...

# 2x2 그리드 형태로 카드 배치
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### ⚙️ 00 Settings")
        st.write("**데이터 및 취향 관리**")
        st.caption("블로그 원문 데이터를 수집하고, 내 취향 데이터를 관리하는 기본 설정 공간입니다.")
        st.write("") # 간격 띄우기
        
        # 💡 "pages/" 경로 추가! (실제 Settings 파일명에 맞춰주세요)
        try:
            st.page_link("pages/00_Settings.py", label="Settings 이동하기", icon="⚙️")
        except:
            st.button("⚙️ 파일 경로를 맞춰주세요", disabled=True, use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("### ✍️ 01 Movie Blog")
        st.write("**영화 리뷰/프리뷰 자동화**")
        st.caption("TMDB와 네이버 뉴스를 바탕으로 영화 관련 포스팅을 자동 생성합니다.")
        st.write("") # 간격 띄우기
        # 💡 "pages/" 경로 추가!
        st.page_link("pages/01_🎬_Movie_Blog.py", label="Movie Blog 이동하기", icon="🚀")

with col3:
    with st.container(border=True):
        st.markdown("### 📸 02 Daily Life")
        st.write("**일상 & 현장 기록**")
        st.caption("PDF 자료나 현장 사진을 업로드하여 나만의 감성이 담긴 현장 일지를 작성합니다.")
        st.write("") # 간격 띄우기
        # 💡 "pages/" 경로 추가!
        st.page_link("pages/02_🏠_Daily_Life.py", label="Daily Life 이동하기", icon="🚀")

with col4:
    with st.container(border=True):
        st.markdown("### 🔍 03 Movie Search")
        st.write("**하이브리드 영화 대시보드**")
        st.caption("실시간 박스오피스 순위를 확인하고, 다양한 영화의 상세 정보를 검색합니다.")
        st.write("") # 간격 띄우기
        # 💡 "pages/" 경로 추가!
        st.page_link("pages/03_🎬_Movie_Search.py", label="Movie Search 이동하기", icon="🚀")

# ... (하단 꿀팁 코드는 동일) ...