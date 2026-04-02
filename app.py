import streamlit as st
import streamlit.components.v1 as components
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient
from db_manager import DBManager  # 💡 추가 1: 방금 만든 DB 매니저를 불러옵니다.

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="centered")

@st.cache_resource
def init_engines():
    # 💡 추가 2: DB 매니저도 엔진 목록에 추가해서 켜줍니다.
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter(), NaverClient(), DBManager()

# 💡 추가 3: db 변수로 매니저를 받습니다.
tmdb, gemini, builder, formatter, naver, db = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

# 💡 핵심 추가: 스트림릿은 버튼을 누르면 화면이 초기화되므로, 생성된 글을 '메모리'에 기억시킵니다.
if "rev_data" not in st.session_state: st.session_state.rev_data = None
if "pre_data" not in st.session_state: st.session_state.pre_data = None
if "news_data" not in st.session_state: st.session_state.news_data = None

tab1, tab2, tab3 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식"])

# ==========================================
# 탭 1: 영화 리뷰
# ==========================================
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
            with st.spinner("영화 정보 및 네이버 최신 뉴스 수집 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(title)
                    prompt = builder.build_review_prompt(details, comment, latest_news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    
                    # 생성된 결과물을 메모리에 저장!
                    st.session_state.rev_data = {"title": details['title'], "html": final_html}
                else:
                    st.error(f"'{title}' 영화를 찾을 수 없습니다. 제목과 연도를 확인해 주세요.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    # 💡 메모리에 글이 있다면 화면에 뿌려주고 저장 버튼을 표시합니다.
    if st.session_state.rev_data:
        st.success(f"'{st.session_state.rev_data['title']}' 리뷰 생성 완료!")
        
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1:
            st.code(st.session_state.rev_data['html'], language='html')
        with sub_tab2:
            components.html(st.session_state.rev_data['html'], height=800, scrolling=True)
            
        st.divider()
        # 💾 DB 저장 버튼 추가
        if st.button("💾 리뷰 DB에 저장하기", key="save_rev"):
            db.save_post(movie_title=st.session_state.rev_data['title'], post_type="review", content=st.session_state.rev_data['html'])
            st.success(f"[{st.session_state.rev_data['title']}] 리뷰가 내 데이터베이스에 안전하게 저장되었습니다! 🎉")


# ==========================================
# 탭 2: 개봉 프리뷰
# ==========================================
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
                    latest_news = naver.search_movie_news(p_title)
                    prompt = builder.build_preview_prompt(details, point, latest_news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    
                    # 결과물 메모리 저장
                    st.session_state.pre_data = {"title": details['title'], "html": final_html}
                else:
                    st.error("해당하는 영화 정보가 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    # 💡 프리뷰 결과 출력 및 저장 버튼
    if st.session_state.pre_data:
        st.success("프리뷰 생성 완료!")
        
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1:
            st.code(st.session_state.pre_data['html'], language='html')
        with sub_tab2:
            components.html(st.session_state.pre_data['html'], height=800, scrolling=True)
            
        st.divider()
        if st.button("💾 프리뷰 DB에 저장하기", key="save_pre"):
            db.save_post(movie_title=st.session_state.pre_data['title'], post_type="preview", content=st.session_state.pre_data['html'])
            st.success(f"[{st.session_state.pre_data['title']}] 프리뷰가 내 데이터베이스에 안전하게 저장되었습니다! 🎉")


# ==========================================
# 탭 3: 최신 영화 뉴스
# ==========================================
with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    
    if st.button("뉴스 포스팅 생성", type="primary"):
        if news_content:
            with st.spinner("뉴스 분석 및 작성 중..."):
                prompt = builder.build_news_prompt(news_content)
                result = gemini.generate_post(prompt)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                
                # 결과물 메모리 저장
                st.session_state.news_data = {"title": "영화 뉴스 포스팅", "html": final_html}
        else:
            st.warning("뉴스 원문을 입력해 주세요.")

    # 💡 뉴스 결과 출력 및 저장 버튼
    if st.session_state.news_data:
        st.success("뉴스 포스팅 생성 완료!")
        
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1:
            st.code(st.session_state.news_data['html'], language='html')
        with sub_tab2:
            components.html(st.session_state.news_data['html'], height=800, scrolling=True)
            
        st.divider()
        if st.button("💾 뉴스 DB에 저장하기", key="save_news"):
            db.save_post(movie_title="영화 뉴스", post_type="news", content=st.session_state.news_data['html'])
            st.success("뉴스 포스팅이 내 데이터베이스에 안전하게 저장되었습니다! 🎉")