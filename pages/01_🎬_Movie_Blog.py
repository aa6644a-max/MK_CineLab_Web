import streamlit as st
import streamlit.components.v1 as components
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient
from db_manager import DBManager
from rss_client import RSSClient  # 💡 1. 새로 만든 RSSClient를 불러옵니다!

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="centered")

@st.cache_resource
def init_engines():
    # 💡 2. 초기화할 때 RSSClient도 같이 실행해 줍니다.
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter(), NaverClient(), DBManager(), RSSClient()

tmdb, gemini, builder, formatter, naver, db, rss = init_engines() # 💡 3. rss 변수 추가

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

# 탭 순서 변경
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식", "🎬 큐레이션 리스트", "📝 내 글 직접 등록"])

if "rev_data" not in st.session_state: st.session_state.rev_data = None
if "pre_data" not in st.session_state: st.session_state.pre_data = None
if "news_data" not in st.session_state: st.session_state.news_data = None
if "converted_html" not in st.session_state: st.session_state.converted_html = None
if "cur_data" not in st.session_state: st.session_state.cur_data = None 

# 기존 DB에서 가져오던 함수 (필요할 때를 대비해 남겨둠)
def get_recent_references(post_type_filter, limit=2):
    try:
        all_posts = db.get_all_posts()
        filtered_posts = [p[3] for p in all_posts if p[2] == post_type_filter]
        if not filtered_posts:
            return ""
        recent_posts = filtered_posts[-limit:]
        return "\n\n---\n[이전 글 구분선]\n---\n\n".join(recent_posts)
    except Exception as e:
        print(f"DB 참조 실패: {e}")
        return ""

# --- Tab 1: 영화 리뷰 ---
with tab1:
    st.subheader("영화 리뷰 생성")
    col1, col2 = st.columns([3, 1])
    with col1: title = st.text_input("리뷰할 영화 제목", key="rev_title")
    with col2: year_input = st.text_input("개봉 연도 (선택)", placeholder="예: 2024", key="rev_year")
    comment = st.text_area("나의 주관적 감상평", height=150, key="rev_comment")
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            with st.spinner("영화 정보, 최신 뉴스, 그리고 실시간 네이버 블로그(RSS) 데이터를 수집 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(title)
                    
                    # 💡 [핵심 변경] 기존 DB 대신 RSS에서 진짜 최신 블로그 글 3개를 바로 긁어옵니다!
                    reference_posts = rss.get_latest_posts_text(limit=5) 
                    
                    prompt = builder.build_review_prompt(details, comment, latest_news, reference_posts)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    st.session_state.rev_data = {"title": details['title'], "html": final_html}
                else: st.error(f"'{title}' 영회를 찾을 수 없습니다.")
        else: st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.rev_data:
        st.success(f"'{st.session_state.rev_data['title']}' 리뷰 생성 완료!")
        if st.button("💾 이 리뷰를 내 취향 DB에 저장하기", key="save_rev_btn"):
            if db.save_post(st.session_state.rev_data['title'], "리뷰", st.session_state.rev_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.rev_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.rev_data['html'], height=800, scrolling=True)

# --- Tab 2: 개봉 프리뷰 ---
with tab2:
    st.subheader("개봉 예정작 프리뷰")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트 (예: 배우 라인업, 감독의 전작 등)", key="pre_point")
    if st.button("프리뷰 생성", type="primary"):
        if p_title:
            with st.spinner("정보 및 실시간 블로그 취향 데이터 수집 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(p_title)
                    
                    # 💡 RSS 적용
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    
                    prompt = builder.build_preview_prompt(details, point, latest_news, reference_posts)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    st.session_state.pre_data = {"title": details['title'], "html": final_html}
                else: st.error("해당하는 영화 정보가 없습니다.")
        else: st.warning("영화 제목을 입력해 주세요.")

    # ... (이하 프리뷰 저장 및 출력 코드는 동일)
    if st.session_state.pre_data:
        st.success("프리뷰 생성 완료!")
        if st.button("💾 이 프리뷰를 내 취향 DB에 저장하기", key="save_pre_btn"):
            if db.save_post(st.session_state.pre_data['title'], "프리뷰", st.session_state.pre_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.pre_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.pre_data['html'], height=800, scrolling=True)

# --- Tab 3: 영화 뉴스 ---
with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    if st.button("뉴스 포스팅 생성", type="primary"):
        if news_content:
            with st.spinner("뉴스 분석 및 취향 데이터 반영 중..."):
                # 💡 RSS 적용
                reference_posts = rss.get_latest_posts_text(limit=5)
                prompt = builder.build_news_prompt(news_content, reference_posts)
                result = gemini.generate_post(prompt)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                st.session_state.news_data = {"title": "영화 뉴스", "html": final_html}
        else: st.warning("뉴스 원문을 입력해 주세요.")

    # ... (이하 뉴스 저장 및 출력 코드는 동일)
    if st.session_state.news_data:
        st.success("뉴스 포스팅 생성 완료!")
        if st.button("💾 이 뉴스를 내 취향 DB에 저장하기", key="save_news_btn"):
            if db.save_post(st.session_state.news_data['title'], "뉴스", st.session_state.news_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.news_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.news_data['html'], height=800, scrolling=True)

# --- Tab 4: 큐레이션 리스트 ---
with tab4:
    st.subheader("🎬 영화 큐레이션 리스트 생성")
    st.markdown("여러 편의 영화를 특정 테마에 맞춰 한 번에 소개하는 포스팅을 작성합니다.")
    
    cur_theme = st.text_input("포스팅 메인 테마", placeholder="예: 다가오는 2026년 3월 개봉 예정 기대작 정리", key="cur_theme")
    cur_movies = st.text_area("소개할 영화 제목들 (쉼표로 구분)", placeholder="예: 프로젝트 헤일메리, 브라이드!, 호퍼스", height=100, key="cur_movies")
    
    if st.button("큐레이션 포스팅 생성", type="primary"):
        if cur_theme and cur_movies:
            movie_list = [m.strip() for m in cur_movies.split(",") if m.strip()]
            
            with st.spinner(f"총 {len(movie_list)}편의 영화 정보(TMDB)와 최신 뉴스(Naver)를 수집 중입니다..."):
                movies_data_text = ""
                # ... (중략: TMDB/Naver 데이터 수집 부분 동일)
                for m_title in movie_list:
                    m_info = tmdb.search_movie(m_title)
                    if m_info:
                        details = tmdb.get_movie_details(m_info['id'])
                        latest_news = naver.search_movie_news(m_title, display=2) 
                        
                        poster_html = builder._build_image_html(details.get('poster_url'), f"{details.get('title')} 포스터")
                        if not poster_html:
                            poster_html = builder._build_placeholder_html(f"영화 '{details.get('title')}' 메인 포스터")
                            
                        movies_data_text += f"""
                        [영화: {details.get('title')}]
                        - 원제: {details.get('original_title', '정보 없음')}
                        - 국가: {details.get('country', '정보 없음')}
                        - 감독: {details.get('director', '')}
                        - 출연: {details.get('actors', '')}
                        - 개봉일: {details.get('release_date', '')}
                        - 줄거리: {details.get('overview', '')}
                        - <메인 포스터 HTML 코드>: {poster_html}
                        - [최신 네이버 뉴스 동향]: 
                        {latest_news}
                        ============================================
                        """
                    else:
                        st.warning(f"'{m_title}' 정보를 찾을 수 없어 리스트에서 제외했습니다.")
                
                if movies_data_text.strip():
                    st.info("제미나이가 수집된 데이터를 바탕으로 MK 스타일 원고를 작성하고 있습니다...")
                    # 💡 RSS 적용
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    
                    prompt = builder.build_curation_prompt(cur_theme, movies_data_text, reference_posts)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(cur_theme, result)
                    
                    st.session_state.cur_data = {"title": cur_theme, "html": final_html}
                else:
                    st.error("유효한 영화 정보를 하나도 수집하지 못했습니다. 제목을 정확히 확인해 주세요.")
        else:
            st.warning("테마와 영화 제목들을 모두 입력해 주세요.")
            
    # ... (이하 리스트 저장 및 출력 코드는 동일)
    if st.session_state.cur_data:
        st.success("큐레이션 리스트 포스팅 생성 완료!")
        if st.button("💾 이 리스트를 내 취향 DB에 저장하기", key="save_cur_btn"):
            if db.save_post(st.session_state.cur_data['title'], "리스트", st.session_state.cur_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")

        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.cur_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.cur_data['html'], height=800, scrolling=True)

# --- Tab 5: 내 글 직접 등록 ---
# (이 부분은 민규 님이 올려주신 코드 원본과 100% 동일하게 유지합니다. 
# 잘못 붙여넣으신 하단 코드 덩어리만 제거했습니다.)
with tab5:
    st.subheader("📝 내 블로그 원문 직접 등록")
    st.markdown("제미나이의 완벽한 문체 학습을 위해, 민규 님이 과거에 직접 쓰셨던 **진짜(Real) 블로그 포스팅 텍스트**를 넣어주세요.")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        manual_title = st.text_input("영화 제목 (또는 테마)", placeholder="예: 더 퍼스트 슬램덩크", key="manual_title")
    with col_b:
        manual_type = st.selectbox("포스팅 종류", ["리뷰", "프리뷰", "뉴스", "리스트"], key="manual_type")
        
    manual_content = st.text_area("블로그 본문 텍스트", height=300, placeholder="과거 블로그 글을 그대로 복사해서 붙여넣으세요.", key="manual_content")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 (그대로) 텍스트만 DB에 바로 저장"):
            if manual_title and manual_content:
                with st.spinner("DB에 저장 중입니다..."):
                    if db.save_post(manual_title, manual_type, manual_content):
                        st.success("✅ 원본 글이 성공적으로 등록되었습니다!")
            else: st.warning("영화 제목과 블로그 본문을 모두 입력해 주세요.")
                
    with col_btn2:
        if st.button("✨ (추천) 제미나이로 HTML 변환 후 확인하기", type="primary"):
            if manual_content:
                with st.spinner("원문 내용을 훼손하지 않고 예쁜 HTML 태그를 입히는 중..."):
                    prompt = builder.build_html_conversion_prompt(manual_content)
                    st.session_state.converted_html = gemini.generate_post(prompt)
            else: st.warning("변환할 본문을 입력해 주세요.")
                
    if st.session_state.converted_html:
        st.markdown("---")
        st.subheader("🛠️ 변환된 HTML 코드 결과")
        sub_t1, sub_t2 = st.tabs(["📄 변환된 HTML 코드", "👁️ 미리보기"])
        with sub_t1: st.code(st.session_state.converted_html, language='html')
        with sub_t2: components.html(st.session_state.converted_html, height=400, scrolling=True)
        
        if st.button("💾 변환된 이 HTML 코드로 DB에 완벽하게 저장하기"):
            if manual_title:
                if db.save_post(manual_title, manual_type, st.session_state.converted_html):
                    st.success("✅ 포맷팅된 HTML 글이 DB에 등록되었습니다!")
                    st.session_state.converted_html = None
            else: st.warning("영화 제목을 입력해 주세요.")