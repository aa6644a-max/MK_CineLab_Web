# app.py 의 탭 1 부분

with tab1:
    title = st.text_input("🎬 리뷰할 영화 제목", key="rev_title")
    
    # 연도와 감독명을 한 줄에 배치
    col_y, col_d = st.columns(2)
    with col_y:
        rev_year = st.text_input("📅 개봉 연도", placeholder="예: 2024", key="rev_year")
    with col_d:
        rev_director = st.text_input("👤 감독 이름", placeholder="예: 이강민", key="rev_dir")
    
    comment = st.text_area("✍️ 나의 주관적 감상평", height=150)
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            year_val = int(rev_year) if rev_year.isdigit() else None
            
            with st.spinner("감독명까지 대조하여 정보를 수집 중입니다..."):
                # 수정된 search_movie에 director_name 전달
                movie_info = tmdb.search_movie(title, year=year_val, director_name=rev_director)
                
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    # ... (이후 로직 동일)