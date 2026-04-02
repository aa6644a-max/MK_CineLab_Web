import streamlit as st
import streamlit.components.v1 as components # 미리보기를 위한 컴포넌트 추가
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="centered")

@st.cache_resource
def init_engines():
    # 💡 수정 1: NaverClient()를 추가해서 리턴합니다.
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter(), NaverClient()

# 💡 수정 2: naver 변수로 네이버 엔진을 받습니다.
tmdb, gemini, builder, formatter, naver = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식"])

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
            # 💡 스피너 메시지도 조금 더 현실감 있게 바꿨습니다.
            with st.spinner("영화 정보 및 네이버 최신 뉴스 수집 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    
                    # 💡 수정 3: 네이버에서 최신 영화 뉴스를 검색해서 가져옵니다.
                    latest_news = naver.search_movie_news(title)
                    
                    # 💡 수정 4: 프롬프트를 만들 때 최신 뉴스를 같이 넘겨줍니다.
                    prompt = builder.build_review_prompt(details, comment, latest_news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    
                    st.success(f"'{details['title']}' 리뷰 생성 완료!")
                    
                    # --- 코드와 미리보기를 탭으로 분리 ---
                    sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
                    with sub_tab1:
                        st.code(final_html, language='html')
                    with sub_tab2:
                        components.html(final_html, height=800, scrolling=True)
                    # ------------------------------------------
                else:
                    st.error(f"'{title}' 영회를 찾을 수 없습니다. 제목과 연도를 확인해 주세요.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

with tab2:
    st.subheader("개봉 예정작 프리뷰")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트 (예: 배우 라인업, 감독의 전작 등)", key="pre_point")
    
    if st.button("프리뷰 생성", type="primary"):
        if p_title:
            with st.spinner("영화 정보 및 네이버 최신 뉴스 수집 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    
                    # 💡 수정 5: 프리뷰에서도 네이버 뉴스를 검색합니다.
                    latest_news = naver.search_movie_news(p_title)
                    
                    # 💡 수정 6: 프롬프트에 뉴스를 함께 넘깁니다.
                    prompt = builder.build_preview_prompt(details, point, latest_news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    
                    st.success("프리뷰 생성 완료!")
                    
                    # --- 미리보기 분리 ---
                    sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
                    with sub_tab1:
                        st.code(final_html, language='html')
                    with sub_tab2:
                        components.html(final_html, height=800, scrolling=True)
                    # -----------------
                else:
                    st.error("해당하는 영화 정보가 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    
    if st.button("뉴스 포스팅 생성", type="primary"):
        if news_content:
            with st.spinner("뉴스 분석 및 작성 중..."):
                prompt = builder.build_news_prompt(news_content)
                result = gemini.generate_post(prompt)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                
                st.success("뉴스 포스팅 생성 완료!")
                
                # --- 미리보기 분리 ---
                sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
                with sub_tab1:
                    st.code(final_html, language='html')
                with sub_tab2:
                    components.html(final_html, height=800, scrolling=True)
                # -----------------
        else:
            st.warning("뉴스 원문을 입력해 주세요.")