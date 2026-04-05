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
    """TMDB에서 포스터, 줄거리, IMDb ID 가져오기"""
    if not TMDB_API_KEY: return None
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&language=ko-KR"
    if year: search_url += f"&year={year}"
    
    try:
        res = requests.get(search_url).json()
        if res.get('results'):
            movie_id = res['results'][0]['id']
            # 상세 정보(IMDb ID 포함) 요청
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids&language=ko-KR"
            return requests.get(detail_url).json()
    except: pass
    return None

def get_omdb_ratings(imdb_id):
    """OMDB에서 로튼토마토 및 IMDb 평점 가져오기"""
    if not OMDB_API_KEY or not imdb_id: return None
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        return requests.get(url).json()
    except: return None

def format_date(date_str):
    if len(date_str) == 8: return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return "정보없음"

# --- UI 구현 섹션 ---
st.title("🎬 MK CINELAB : 통합 영화 검색 시스템")

if not all([KOBIS_API_KEY, TMDB_API_KEY, OMDB_API_KEY]):
    st.warning("⚠️ 일부 API 키(TMDB 또는 OMDB)가 설정되지 않았습니다. 평점 및 포스터가 표시되지 않을 수 있습니다.")

box_office_result, target_date = get_daily_box_office()
box_office_list = box_office_result.get("dailyBoxOfficeList", [])

tab1, tab2 = st.tabs(["🔥 실시간 박스오피스", "🔍 영화 상세 검색"])

# [Tab 1: 박스오피스] - 기존과 동일 (생략 가능하나 유지)
with tab1:
    st.subheader(f"📅 {format_date(target_date)} 기준 인기 영화 TOP 10")
    if box_office_list:
        for movie in box_office_list:
            with st.container():
                c1, c2, c3 = st.columns([0.5, 2, 1.5])
                with c1:
                    st.header(movie['rank'])
                    change = int(movie['rankInten'])
                    st.caption(f"{'🔺' if change > 0 else '🔻' if change < 0 else '➖'} {abs(change) if change != 0 else ''}")
                with c2:
                    st.subheader(movie['movieNm'])
                    st.write(f"개봉일: {movie['openDt']}")
                with c3:
                    st.write(f"**누적 관객:** {int(movie['audiAcc']):,}")
                st.divider()

# [Tab 2: 영화 상세 검색] - 💡 대폭 강화된 섹션
with tab2:
    search_query = st.text_input("영화 제목을 입력하세요", placeholder="예: 파묘, 범죄도시, 괴물", key="search_input")

    if search_query:
        movies = get_movie_list(search_query)
        if movies:
            movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m for m in movies}
            selected_label = st.selectbox("상세 정보를 볼 영화 선택", options=list(movie_options.keys()))
            
            if selected_label:
                m_data = movie_options[selected_label]
                m_code = m_data['movieCd']
                
                with st.spinner("다양한 데이터 소스에서 정보를 통합하는 중..."):
                    k_detail = get_movie_detail(m_code)
                    t_detail = get_tmdb_info(m_data['movieNm'], m_data['prdtYear'])
                    
                    imdb_id = t_detail.get('external_ids', {}).get('imdb_id') if t_detail else None
                    o_detail = get_omdb_ratings(imdb_id) if imdb_id else None
                
                st.divider()
                
                # 상단 정보: 포스터 + 줄거리 + 평점
                top_col1, top_col2 = st.columns([1, 2])
                
                with top_col1:
                    if t_detail and t_detail.get('poster_path'):
                        st.image(f"https://image.tmdb.org/t/p/w500{t_detail['poster_path']}", use_container_width=True)
                    else:
                        st.info("포스터 이미지를 찾을 수 없습니다.")
                    
                    # ⭐ 평점 섹션 (OMDB)
                    if o_detail and o_detail.get('Response') == 'True':
                        st.markdown("### ⭐ 평점 리포트")
                        for r in o_detail.get('Ratings', []):
                            source = r['Source']
                            val = r['Value']
                            if source == "Internet Movie Database": st.metric("IMDb", val)
                            elif source == "Rotten Tomatoes": st.metric("Rotten Tomatoes", val)
                            elif source == "Metacritic": st.metric("Metacritic", val)
                
                with top_col2:
                    st.header(f"{m_data['movieNm']} ({m_data['prdtYear']})")
                    if t_detail and t_detail.get('tagline'):
                        st.markdown(f"*{t_detail['tagline']}*")
                    
                    st.markdown("#### 📖 줄거리")
                    overview = t_detail.get('overview') if t_detail else "줄거리 정보가 없습니다."
                    st.write(overview if overview else "국문 줄거리 정보가 준비 중입니다.")
                    
                    st.divider()
                    
                    # 기본 제작 정보 (KOBIS)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**🎬 감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                        st.write(f"**🎭 주연:** {', '.join([a['peopleNm'] for a in k_detail.get('actors', [])[:5]])}")
                    with c2:
                        st.write(f"**🎞️ 장르:** {', '.join([g['genreNm'] for g in k_detail.get('genres', [])])}")
                        st.write(f"**⏱️ 상영시간:** {k_detail.get('showTm', '0')}분")

                # 하단 정보: 흥행 통계 (KOBIS)
                stats = next((item for item in box_office_list if item["movieCd"] == m_code), None)
                
                st.divider()
                st.subheader("📊 영진위 공식 흥행 통계")
                
                if stats:
                    st.success(f"현재 박스오피스 **{stats['rank']}위** 기록 중")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("누적 관객수", f"{int(stats['audiAcc']):,}")
                    m2.metric("당일 관객수", f"{int(stats['audiCnt']):,}")
                    m3.metric("누적 매출액", f"₩{int(stats['salesAcc']):,}")
                    m4.metric("스크린 수", f"{stats['scrnCnt']}개")
                    
                    with st.expander("📝 실시간 상세 지표 확인"):
                        st.json(stats) # 사용자가 요청한 모든 필드를 JSON 형태로 깔끔하게 확인
                else:
                    st.info("이 영화는 현재 박스오피스 순위권 밖이거나 과거 개봉작입니다. 누적 관객수 등의 데이터는 영진위 홈페이지를 참고해 주세요.")

if st.button("🔄 앱 초기화"):
    st.rerun()