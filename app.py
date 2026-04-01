import streamlit as st
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter

# 페이지 설정
st.set_page_config(page_title="MK CINELAB 모바일", page_icon="🎬")

# 엔진 초기화
@st.cache_resource
def init_engines():
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter()

tmdb, gemini, builder, formatter = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.caption("대구 영화 인플루언서 MK님을 위한 모바일 작업실")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식"])

# --- 탭 1: 영화 리뷰 ---
with tab1:
    # 1. 영화 제목 입력
    title = st.text_input("리뷰할 영화 제목", key="rev_title")
    
    # 2. 개봉 연도 입력칸 추가 (이 부분이 없어서 화면에 안 나왔던 거예요!)
    rev_year = st.text_input("개봉 연도 (선택 사항)", placeholder="예: 2024", key="rev_year")
    
    # 3. 감상평 입력
    comment = st.text_area("나의 주관적 감상평", height=150)
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            # 연도 입력값 처리 (숫자만 추출)
            year_val = int(rev_year) if rev_year.isdigit() else None
            
            with st.spinner("정보를 수집하고 글을 작성 중입니다..."):
                # 검색 시 연도(year_val)를 함께 전달합니다.
                movie_info = tmdb.search_movie(title, year=year_val)
                
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    prompt = builder.build_review_prompt(details, comment)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    
                    st.success("생성 완료! 아래 코드를 복사하세요.")
                    st.code(final_html, language='html')
                else:
                    st.error("영화 정보를 찾을 수 없습니다. 제목과 연도를 확인해주세요.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

# --- 탭 2: 개봉 프리뷰 ---
with tab2:
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    
    # 프리뷰 탭에도 연도 검색 기능을 넣으면 훨씬 정확해집니다.
    p_year = st.text_input("개봉 연도 (선택 사항)", placeholder="예: 2025", key="pre_year")
    
    point = st.text_input("포스팅 강조 포인트 (예: 배우 중심)")
    
    if st.button("프리뷰 생성"):
        if p_title:
            year_val = int(p_year) if p_year.isdigit() else None
            with st.spinner("프리뷰 원고 작성 중..."):
                movie_info = tmdb.search_movie(p_title, year=year_val)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    prompt = builder.build_preview_prompt(details, point)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    
                    st.success("프리뷰 생성 완료!")
                    st.code(final_html, language='html')
                else:
                    st.error("영화 정보를 찾을 수 없습니다.")

# --- 탭 3: 영화 소식 ---
with tab3:
    news_content = st.text_area("뉴스 기사 원문", height=300)
    if st.button("뉴스 포스팅 생성"):
        if news_content:
            with st.spinner("뉴스 분석 및 포스팅 생성 중..."):
                prompt = builder.build_news_prompt(news_content)
                result = gemini.generate_post(prompt)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                st.code(final_html, language='html')