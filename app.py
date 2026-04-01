import streamlit as st
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter

st.set_page_config(page_title="MK CINELAB 모바일", page_icon="🎬")

@st.cache_resource
def init_engines():
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter()

tmdb, gemini, builder, formatter = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.caption("심플 모드: 영화 제목으로 리뷰 생성")

tab1, tab2, tab3 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식"])

with tab1:
    title = st.text_input("리뷰할 영화 제목", key="rev_title")
    comment = st.text_area("나의 주관적 감상평", height=200)
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            with st.spinner("영화 정보를 찾는 중..."):
                movie_info = tmdb.search_movie(title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    prompt = builder.build_review_prompt(details, comment)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    
                    st.success("생성 완료!")
                    st.code(final_html, language='html')
                else:
                    st.error("영화를 찾을 수 없습니다.")
        else:
            st.warning("제목을 입력해 주세요.")

# 프리뷰/뉴스 탭도 동일하게 심플 구조 유지
with tab2:
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트")
    if st.button("프리뷰 생성"):
        movie_info = tmdb.search_movie(p_title)
        if movie_info:
            details = tmdb.get_movie_details(movie_info['id'])
            prompt = builder.build_preview_prompt(details, point)
            result = gemini.generate_post(prompt)
            st.code(formatter.wrap_in_table(f"{details['title']} 프리뷰", result), language='html')

with tab3:
    news_content = st.text_area("뉴스 원문", height=300)
    if st.button("뉴스 생성"):
        prompt = builder.build_news_prompt(news_content)
        result = gemini.generate_post(prompt)
        st.code(formatter.wrap_in_table("최신 영화 뉴스", result), language='html')