import streamlit as st
import base64
import re
#import streamlit.components.v1 as components
from tmdb_client import TMDBClient
from claude_client import ClaudeClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient
from db_manager import DBManager
from rss_client import RSSClient

def show_isolated_html(html_str):
    b64 = base64.b64encode(html_str.encode('utf-8')).decode('utf-8')
    iframe_html = f'<iframe src="data:text/html;charset=utf-8;base64,{b64}" width="100%" height="800" style="border:none;"></iframe>'
    
    # 기존 코드 (삭제 또는 주석 처리)
    # st.html(iframe_html) 
    
    # 💡 새로운 코드 (이걸로 교체!)
    st.markdown(iframe_html, unsafe_allow_html=True)

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="centered")

# 🚨 해결의 핵심: 함수 이름을 v3로 변경하여 강제 캐시 초기화!
@st.cache_resource(show_spinner=False)
def init_engines_v3():
    return TMDBClient(), ClaudeClient(), PromptBuilder(), HTMLFormatter(), NaverClient(), DBManager(), RSSClient()

tmdb, gemini, builder, formatter, naver, db, rss = init_engines_v3()

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식", "🎬 큐레이션 리스트", "📺 정주행 추천", "📝 내 글 직접 등록"])

if "rev_data" not in st.session_state: st.session_state.rev_data = None
if "pre_data" not in st.session_state: st.session_state.pre_data = None
if "news_data" not in st.session_state: st.session_state.news_data = None
if "converted_html" not in st.session_state: st.session_state.converted_html = None
if "converted_titles" not in st.session_state: st.session_state.converted_titles = []
if "cur_data" not in st.session_state: st.session_state.cur_data = None
if "binge_data" not in st.session_state: st.session_state.binge_data = None

def parse_titles_from_html(html_text):
    match = re.search(r'<!--\s*TITLES:\s*(.+?)\s*-->', html_text, re.DOTALL)
    if not match:
        return []
    return [t.strip() for t in match.group(1).split('||') if t.strip()]

def get_recent_references(post_type_filter, limit=2):
    try:
        all_posts = db.get_all_posts()
        # p[2]=포스팅종류, p[4]=본문내용
        filtered_posts = [p[4] for p in all_posts if p[2] == post_type_filter and len(p) > 4 and p[4]]
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
    
    # 💡 1. 포스팅 계기 입력 칸 추가
    reason_input = st.text_input("영화를 보게 된 계기/관람 이유", placeholder="예: 평소 좋아하는 감독의 신작이라 개봉하자마자 아이맥스로 관람했습니다.", key="rev_reason")
    
    comment = st.text_area("나의 주관적 감상평", height=150, key="rev_comment")
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            with st.spinner("영화 정보, 최신 뉴스, 그리고 실시간 네이버 블로그(RSS) 데이터를 수집 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(title)
                    
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("리뷰")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts

                    # 💡 2. builder에 reason_input 전달
                    prompt = builder.build_review_prompt(details, comment, reason=reason_input, latest_news=latest_news, reference_posts=reference_posts)
                    result = gemini.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    st.session_state.rev_data = {"title": details['title'], "html": final_html, "titles": titles}
                else: st.error(f"'{title}' 영회를 찾을 수 없습니다.")
        else: st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.rev_data:
        st.success(f"'{st.session_state.rev_data['title']}' 리뷰 생성 완료!")
        titles = st.session_state.rev_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="rev_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 리뷰를 내 취향 DB에 저장하기", key="save_rev_btn"):
            if db.save_post(st.session_state.rev_data['title'], "리뷰", st.session_state.rev_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.rev_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.rev_data['html'])

# --- Tab 2: 개봉 프리뷰 ---
with tab2:
    st.subheader("개봉 예정작 프리뷰")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트 (예: 배우 라인업, 감독의 전작 등)", key="pre_point")
    
    # 💡 3. 포스팅 계기 입력 칸 추가
    pre_reason_input = st.text_input("프리뷰를 쓰는 이유", placeholder="예: 예고편의 강렬한 분위기에 압도되어 개봉일만 손꼽아 기다리고 있습니다.", key="pre_reason")

    if st.button("프리뷰 생성", type="primary"):
        if p_title:
            with st.spinner("정보 및 실시간 블로그 취향 데이터 수집 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(p_title)
                    
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("프리뷰")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts

                    # 💡 4. builder에 reason=pre_reason_input 전달
                    prompt = builder.build_preview_prompt(details, point, reason=pre_reason_input, latest_news=latest_news, reference_posts=reference_posts)
                    result = gemini.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    st.session_state.pre_data = {"title": details['title'], "html": final_html, "titles": titles}
                else: st.error("해당하는 영화 정보가 없습니다.")
        else: st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.pre_data:
        st.success("프리뷰 생성 완료!")
        titles = st.session_state.pre_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="pre_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 프리뷰를 내 취향 DB에 저장하기", key="save_pre_btn"):
            if db.save_post(st.session_state.pre_data['title'], "프리뷰", st.session_state.pre_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.pre_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.pre_data['html'])

# --- Tab 3: 영화 뉴스 ---
with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    if st.button("뉴스 포스팅 생성", type="primary"):
        if news_content:
            with st.spinner("뉴스 분석 및 취향 데이터 반영 중..."):
                reference_posts = rss.get_latest_posts_text(limit=5)
                db_refs = get_recent_references("뉴스")
                if db_refs:
                    reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts
                prompt = builder.build_news_prompt(news_content, reference_posts)
                result = gemini.generate_post(prompt)
                titles = parse_titles_from_html(result)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                st.session_state.news_data = {"title": "영화 뉴스", "html": final_html, "titles": titles}
        else: st.warning("뉴스 원문을 입력해 주세요.")

    if st.session_state.news_data:
        st.success("뉴스 포스팅 생성 완료!")
        titles = st.session_state.news_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="news_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 뉴스를 내 취향 DB에 저장하기", key="save_news_btn"):
            if db.save_post(st.session_state.news_data['title'], "뉴스", st.session_state.news_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.news_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.news_data['html'])

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
                    st.info("Claude가 수집된 데이터를 바탕으로 MK 스타일 원고를 작성하고 있습니다...")
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("리스트")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts

                    prompt = builder.build_curation_prompt(cur_theme, movies_data_text, reference_posts)
                    result = gemini.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(cur_theme, result)

                    st.session_state.cur_data = {"title": cur_theme, "html": final_html, "titles": titles}
                else:
                    st.error("유효한 영화 정보를 하나도 수집하지 못했습니다. 제목을 정확히 확인해 주세요.")
        else:
            st.warning("테마와 영화 제목들을 모두 입력해 주세요.")
            
    if st.session_state.cur_data:
        st.success("큐레이션 리스트 포스팅 생성 완료!")
        titles = st.session_state.cur_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="cur_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 리스트를 내 취향 DB에 저장하기", key="save_cur_btn"):
            if db.save_post(st.session_state.cur_data['title'], "리스트", st.session_state.cur_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")

        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.cur_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.cur_data['html'])

# --- Tab 5: 정주행 추천 ---
with tab5:
    st.subheader("📺 정주행 추천 포스팅")
    st.markdown("애니메이션·드라마 등 시리즈물을 **정주행** 관점으로 소개하는 포스팅을 작성합니다.")

    binge_theme = st.text_input("포스팅 메인 테마", placeholder="예: 2025년 상반기 정주행 완료 애니 총결산", key="binge_theme")
    binge_titles_input = st.text_area("소개할 작품 제목들 (쉼표로 구분)", placeholder="예: 귀멸의 칼날, 프리렌, 던전밥", height=80, key="binge_titles_input")

    if st.button("정주행 추천 포스팅 생성", type="primary"):
        if binge_theme and binge_titles_input:
            title_list = [t.strip() for t in binge_titles_input.split(",") if t.strip()]

            with st.spinner(f"총 {len(title_list)}편의 시리즈 정보(TMDB)를 수집 중입니다..."):
                series_data_text = ""
                for s_title in title_list:
                    tv_info = tmdb.search_tv(s_title)
                    if tv_info:
                        details = tmdb.get_tv_details(tv_info['id'])
                        poster_html = builder._build_image_html(details.get('poster_url'), f"{details.get('title')} 포스터")
                        if not poster_html:
                            poster_html = builder._build_placeholder_html(f"'{details.get('title')}' 포스터")

                        series_data_text += f"""
[작품: {details.get('title')}]
- 원제: {details.get('original_title', '정보 없음')}
- 국가: {details.get('country', '정보 없음')}
- 방영 시작: {details.get('first_air_date', '정보 없음')}
- 총 화수: {details.get('number_of_episodes', '?')}화
- 시즌 수: {details.get('number_of_seasons', 1)}시즌
- 편당 러닝타임: 약 {details.get('episode_runtime', 24)}분
- 정주행 총 소요 시간: {details.get('total_watch_time', '정보 없음')}
- 장르: {details.get('genres', '')}
- 줄거리: {details.get('overview', '')}
- <포스터 HTML 코드>: {poster_html}
============================================
"""
                    else:
                        st.warning(f"'{s_title}' 정보를 찾을 수 없어 제외했습니다.")

                if series_data_text.strip():
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("정주행")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts

                    prompt = builder.build_binge_prompt(binge_theme, series_data_text, reference_posts)
                    result = gemini.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(binge_theme, result)
                    st.session_state.binge_data = {"title": binge_theme, "html": final_html, "titles": titles}
                else:
                    st.error("유효한 작품 정보를 하나도 수집하지 못했습니다. 제목을 확인해 주세요.")
        else:
            st.warning("테마와 작품 제목들을 모두 입력해 주세요.")

    if st.session_state.binge_data:
        st.success("정주행 추천 포스팅 생성 완료!")
        titles = st.session_state.binge_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="binge_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 포스팅을 내 취향 DB에 저장하기", key="save_binge_btn"):
            if db.save_post(st.session_state.binge_data['title'], "정주행", st.session_state.binge_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.binge_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.binge_data['html'])


# --- Tab 6: 내 글 직접 등록 ---
with tab6:
    st.subheader("📝 내 블로그 원문 직접 등록")
    st.markdown("Claude의 완벽한 문체 학습을 위해, 민규 님이 과거에 직접 쓰셨던 **진짜(Real) 블로그 포스팅 텍스트**를 넣어주세요.")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        manual_title = st.text_input("영화 제목 (또는 테마)", placeholder="예: 더 퍼스트 슬램덩크", key="manual_title")
    with col_b:
        manual_type = st.selectbox("포스팅 종류", ["리뷰", "프리뷰", "뉴스", "리스트", "정주행"], key="manual_type")
        
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
        if st.button("✨ (추천) Claude로 HTML 변환 후 확인하기", type="primary"):
            if manual_content:
                with st.spinner("원문 내용을 훼손하지 않고 예쁜 HTML 태그를 입히는 중..."):
                    prompt = builder.build_html_conversion_prompt(manual_content)
                    result = gemini.generate_post(prompt)
                    st.session_state.converted_titles = parse_titles_from_html(result)
                    st.session_state.converted_html = result
            else: st.warning("변환할 본문을 입력해 주세요.")
                
    if st.session_state.converted_html:
        st.markdown("---")
        st.subheader("🛠️ 변환된 HTML 코드 결과")
        titles = st.session_state.get("converted_titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="conv_title_select")
                st.code(selected, language=None)
        sub_t1, sub_t2 = st.tabs(["📄 변환된 HTML 코드", "👁️ 미리보기"])
        with sub_t1: st.code(st.session_state.converted_html, language='html')
        with sub_t2: show_isolated_html(st.session_state.converted_html)
        
        if st.button("💾 변환된 이 HTML 코드로 DB에 완벽하게 저장하기"):
            if manual_title:
                if db.save_post(manual_title, manual_type, st.session_state.converted_html):
                    st.success("✅ 포맷팅된 HTML 글이 DB에 등록되었습니다!")
                    st.session_state.converted_html = None
            else: st.warning("영화 제목을 입력해 주세요.")