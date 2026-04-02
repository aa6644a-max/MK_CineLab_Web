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
    # DBManager를 구글 시트용으로 초기화
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter(), NaverClient(), DBManager()

tmdb, gemini, builder, formatter, naver, db = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

# 세션 초기화
if "rev_data" not in st.session_state: st.session_state.rev_data = None
if "pre_data" not in st.session_state: st.session_state.pre_data = None
if "news_data" not in st.session_state: st.session_state.news_data = None

tab1, tab2, tab3, tab4 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식", "🗄️ 내 보물창고"])

# --- 탭 1: 영화 리뷰 ---
with tab1:
    st.subheader("영화 리뷰 생성")
    title = st.text_input("리뷰할 영화 제목", key="rev_title")
    comment = st.text_area("나의 주관적 감상평", key="rev_comment")
    
    if st.button("리뷰 생성", type="primary", key="btn_rev"):
        if title:
            with st.spinner("작성 중..."):
                movie_info = tmdb.search_movie(title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    news = naver.search_movie_news(title)
                    prompt = builder.build_review_prompt(details, comment, news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    st.session_state.rev_data = {"title": details['title'], "html": final_html}
        else:
            st.warning("제목을 입력하세요.")

    # 💡 데이터가 있을 때만 렌더링 (TypeError 방지)
    if st.session_state.rev_data and st.session_state.rev_data.get('html'):
        sub1, sub2 = st.tabs(["📄 코드", "👁️ 미리보기"])
        with sub1: st.code(st.session_state.rev_data['html'])
        with sub2: components.iframe(srcdoc=st.session_state.rev_data['html'], height=800, scrolling=True)
        
        if st.button("💾 구글 시트에 저장하기"):
            if db.save_post(st.session_state.rev_data['title'], "review", st.session_state.rev_data['html']):
                st.success("구글 스프레드시트에 저장되었습니다! 🎉")

# --- 탭 4: 내 보물창고 (구글 시트에서 불러오기) ---
with tab4:
    st.subheader("🗄️ 내 콘텐츠 보물창고")
    if st.button("새로고침"): st.rerun()
    
    posts = db.get_all_posts() 
    if not posts:
        st.info("시트에 저장된 포스팅이 없습니다.")
    else:
        post_options = {p[0]: f"[{p[2]}] {p[1]} ({p[3]})" for p in posts}
        sel_id = st.selectbox("포스팅 선택:", options=list(post_options.keys()), format_func=lambda x: post_options[x])
        if sel_id:
            content = db.get_post_content(sel_id)
            if content:
                components.iframe(srcdoc=content, height=800, scrolling=True)
                if st.button("🗑️ 삭제"):
                    if db.delete_post(sel_id): st.rerun()