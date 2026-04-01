import streamlit as st
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter

st.set_page_config(page_title="MK CINELAB", page_icon="🎬")

@st.cache_resource
def init_engines():
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter()

tmdb, gemini, builder, formatter = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")

title = st.text_input("영화 제목 입력")
comment = st.text_area("감상평 입력")

if st.button("리뷰 생성"):
    if title:
        with st.spinner("영화 찾는 중..."):
            movie_info = tmdb.search_movie(title)
            if movie_info:
                details = tmdb.get_movie_details(movie_info['id'])
                prompt = builder.build_review_prompt(details, comment)
                result = gemini.generate_post(prompt)
                st.code(formatter.wrap_in_table(details['title'], result), language='html')
            else:
                st.error("영화를 찾을 수 없습니다.")