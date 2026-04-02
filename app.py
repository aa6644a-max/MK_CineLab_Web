import streamlit as st
import streamlit.components.v1 as components
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient
from db_manager import DBManager

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="centered")

@st.cache_resource
def init_engines():
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter(), NaverClient(), DBManager()

tmdb, gemini, builder, formatter, naver, db = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식"])

if "rev_data" not in st.session_state: st.session_state.rev_data = None
if "pre_data" not in st.session_state: st.session_state.pre_data = None
if "news_data" not in st.session_state: st.session_state.news_data = None

# 💡 과거 글을 가져오는 헬퍼 함수 추가
def get_recent_references(post_type_filter, limit=2):
    try:
        all_posts = db.get_all_posts()
        # 해당 타입(리뷰/프리뷰/뉴스)의 글만 필터링 (p[2]가 post_type)
        filtered_posts = [p[3] for p in all_posts if p[2] == post_type_filter]
        if not filtered_posts:
            return ""
        # 가장 최근 글(리스트의 맨 뒤) 2개를 묶어서 텍스트로 반환
        recent_posts = filtered_posts[-limit:]
        return "\n\n---\n[이전 글 구분선]\n---\n\n".join(recent_posts)
    except Exception as e:
        print(f"DB 참조 실패: {e}")
        return ""

with tab1:
    st.subheader("영화 리뷰 생성")
    col1, col2 = st.columns([3, 1])
    with col1:
        title = st.text_input("리뷰할 영화 제목", key="rev_title")
    with col2:
        year_input = st.text_input("개봉 연도 (선택)", placeholder="예: 2024", key="rev_year")
        
    comment = st.text_area("나의 주관적 감상평", height=150, key="rev_comment")
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            with st.spinner("영화 정보, 최신 뉴스, 그리고 나의 과거 취향 데이터(DB)를 수집 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(title)
                    
                    # 💡 DB에서 과거 리뷰 글을 불러옵니다!
                    reference_posts = get_recent_references("리뷰")
                    
                    prompt = builder.build_review_prompt(details, comment, latest_news, reference_posts)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    
                    st.session_state.rev_data = {"title": details['title'], "html": final_html}
                else:
                    st.error(f"'{title}' 영회를 찾을 수 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.rev_data:
        st.success(f"'{st.session_state.rev_data['title']}' 리뷰 생성 완료!")
        if st.button("💾 이 리뷰를 내 취향 DB에 저장하기", key="save_rev_btn"):
            if db.save_post(st.session_state.rev_data['title'], "리뷰", st.session_state.rev_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.rev_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.rev_data['html'], height=800, scrolling=True)

with tab2:
    st.subheader("개봉 예정작 프리뷰")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트 (예: 배우 라인업, 감독의 전작 등)", key="pre_point")
    
    if st.button("프리뷰 생성", type="primary"):
        if p_title:
            with st.spinner("정보 및 취향 데이터 수집 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(p_title)
                    
                    # 💡 DB에서 과거 프리뷰 글을 불러옵니다!
                    reference_posts = get_recent_references("프리뷰")
                    
                    prompt = builder.build_preview_prompt(details, point, latest_news, reference_posts)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    
                    st.session_state.pre_data = {"title": details['title'], "html": final_html}
                else:
                    st.error("해당하는 영화 정보가 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.pre_data:
        st.success("프리뷰 생성 완료!")
        if st.button("💾 이 프리뷰를 내 취향 DB에 저장하기", key="save_pre_btn"):
            if db.save_post(st.session_state.pre_data['title'], "프리뷰", st.session_state.pre_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.pre_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.pre_data['html'], height=800, scrolling=True)

with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    
    if st.button("뉴스 포스팅 생성", type="primary"):
        if news_content:
            with st.spinner("뉴스 분석 및 취향 데이터 반영 중..."):
                # 💡 DB에서 과거 뉴스 글을 불러옵니다!
                reference_posts = get_recent_references("뉴스")
                
                prompt = builder.build_news_prompt(news_content, reference_posts)
                result = gemini.generate_post(prompt)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                
                st.session_state.news_data = {"title": "영화 뉴스", "html": final_html}
        else:
            st.warning("뉴스 원문을 입력해 주세요.")

    if st.session_state.news_data:
        st.success("뉴스 포스팅 생성 완료!")
        if st.button("💾 이 뉴스를 내 취향 DB에 저장하기", key="save_news_btn"):
            if db.save_post(st.session_state.news_data['title'], "뉴스", st.session_state.news_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")

        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.news_data['html'], language='html')
        with sub_tab2: components.html(st.session_state.news_data['html'], height=800, scrolling=True)