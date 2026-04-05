import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - 영화 인사이트", page_icon="🎬", layout="wide")

# --- API 키 설정 ---
KOBIS_API_KEY = st.secrets.get("KOBIS_API_KEY") or os.getenv("KOBIS_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")

# --- API 호출 함수 ---

def get_daily_box_office():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": KOBIS_API_KEY, "targetDt": yesterday}
    try:
        response = requests.get(url, params=params)
        return response.json().get("boxOfficeResult", {}), yesterday
    except: return {}, ""

def get_movie_list(movie_nm):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {"key": KOBIS_API_KEY, "movieNm": movie_nm}
    try:
        response = requests.get(url, params=params)
        return response.json().get("movieListResult", {}).get("movieList", [])
    except: return []

def get_movie_detail(movie_cd):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": KOBIS_API_KEY, "movieCd": movie_cd}
    try:
        response = requests.get(url, params=params)
        return response.json().get("movieInfoResult", {}).get("movieInfo", {})
    except: return []

def get_tmdb_info(title, year=None):
    """TMDB 검색 강화: 연도 조건을 빼고 재시도하는 로직 추가"""
    if not TMDB_API_KEY: return None
    
    def search(query_title, query_year):
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query_title}&language=ko-KR"
        if query_year: url += f"&year={query_year}"
        res = requests.get(url).json()
        return res.get('results', [])

    results = search(title, year)
    if not results and year: # 연도 포함 검색 결과 없으면 제목으로만 재검색
        results = search(title, None)
    
    if results:
        movie_id = results[0]['id']
        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids&language=ko-KR"
        return requests.get(detail_url).json()
    return None

def get_omdb_ratings(imdb_id):
    if not OMDB_API_KEY or not imdb_id: return None
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        return requests.get(url).json()
    except: return None

# --- UI 구현 섹션 ---
st.title("🎬 MK CINELAB : 통합 영화 검색 시스템")

box_office_result, target_date = get_daily_box_office()
box_office_list = box_office_result.get("dailyBoxOfficeList", [])

tab1, tab2 = st.tabs(["🔥 실시간 박스오피스", "🔍 영화 상세 검색"])

with tab1:
    st.subheader(f"📅 {target_date[:4]}-{target_date[4:6]}-{target_date[6:]} 기준 인기 영화 TOP 10")
    if box_office_list:
        for movie in box_office_list:
            with st.container():
                c1, c2, c3 = st.columns([0.5, 2, 1.5])
                with c1: st.header(movie['rank'])
                with c2: st.subheader(movie['movieNm'])
                with c3: st.write(f"**누적:** {int(movie['audiAcc']):,}명")
                st.divider()

with tab2:
    search_query = st.text_input("영화 제목을 입력하세요", placeholder="예: 왕과 사는 남자, 파묘", key="search_input")

    if search_query:
        movies = get_movie_list(search_query)
        if movies:
            movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m for m in movies}
            selected_label = st.selectbox("정확한 영화를 선택하세요", options=list(movie_options.keys()))
            
            if selected_label:
                m_data = movie_options[selected_label]
                with st.spinner("정보를 통합하는 중..."):
                    k_detail = get_movie_detail(m_data['movieCd'])
                    t_detail = get_tmdb_info(m_data['movieNm'], m_data['prdtYear'])
                    imdb_id = t_detail.get('external_ids', {}).get('imdb_id') if t_detail else None
                    o_detail = get_omdb_ratings(imdb_id) if imdb_id else None
                
                st.divider()
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # 1. 포스터 예외 처리
                    if t_detail and t_detail.get('poster_path'):
                        st.image(f"https://image.tmdb.org/t/p/w500{t_detail['poster_path']}", use_container_width=True)
                    else:
                        st.warning("🖼️ TMDB에 등록된 포스터가 없습니다.")
                        st.caption("해외 DB 등록 전인 최신 한국 영화일 수 있습니다.")
                    
                    # 2. 평점 예외 처리
                    st.markdown("### ⭐ 평점 리포트")
                    if o_detail and o_detail.get('Response') == 'True':
                        for r in o_detail.get('Ratings', []):
                            st.metric(r['Source'], r['Value'])
                    else:
                        st.info("평점 정보를 찾을 수 없습니다. (IMDb/로튼토마토 미등록)")

                with col2:
                    st.header(f"{m_data['movieNm']} ({m_data['prdtYear']})")
                    st.markdown("#### 📖 줄거리")
                    st.write(t_detail.get('overview', "정보가 없습니다.") if t_detail else "TMDB에서 줄거리를 가져오지 못했습니다.")
                    
                    st.divider()
                    st.markdown("#### 📌 공식 흥행 지표")
                    stats = next((item for item in box_office_list if item["movieCd"] == m_data['movieCd']), None)
                    
                    if stats:
                        # 3. JSON 코드 대신 깔끔한 표/리스트로 출력
                        st.success(f"현재 박스오피스 {stats['rank']}위 기록 중")
                        res_col1, res_col2 = st.columns(2)
                        with res_col1:
                            st.write(f"**누적 관객:** {int(stats['audiAcc']):,}명")
                            st.write(f"**당일 관객:** {int(stats['audiCnt']):,}명")
                            st.write(f"**스크린 수:** {stats['scrnCnt']}개")
                        with res_col2:
                            st.write(f"**누적 매출:** ₩{int(stats['salesAcc']):,}")
                            st.write(f"**매출 점유율:** {stats['salesShare']}%")
                            st.write(f"**상영 횟수:** {stats['showCnt']}회")
                    else:
                        st.info("현재 박스오피스 순위권 밖입니다.")