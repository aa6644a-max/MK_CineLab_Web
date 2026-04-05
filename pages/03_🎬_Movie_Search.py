import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - 통합 검색", page_icon="🎬", layout="wide")

# --- API 키 설정 ---
KOBIS_API_KEY = st.secrets.get("KOBIS_API_KEY") or os.getenv("KOBIS_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET")

# --- [API 호출 함수] ---

def get_movie_list(movie_nm):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {"key": KOBIS_API_KEY, "movieNm": movie_nm}
    try:
        res = requests.get(url, params=params).json()
        return res.get("movieListResult", {}).get("movieList", [])
    except: return []

def get_movie_detail(movie_cd):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": KOBIS_API_KEY, "movieCd": movie_cd}
    try:
        res = requests.get(url, params=params).json()
        return res.get("movieInfoResult", {}).get("movieInfo", {})
    except: return {}

def get_tmdb_info(title):
    """제목으로만 검색하여 매칭 확률을 극대화합니다."""
    if not TMDB_API_KEY: return None
    # 연도(year) 파라미터를 제거하여 검색 범위를 넓힙니다.
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&language=ko-KR"
    try:
        res = requests.get(url).json()
        results = res.get('results', [])
        if results:
            movie_id = results[0]['id']
            # 상세 정보 및 IMDb ID 추출
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids&language=ko-KR"
            return requests.get(detail_url).json()
    except: pass
    return None

def get_naver_image_poster(movie_nm):
    """네이버 이미지 검색 API를 사용하여 포스터를 찾습니다."""
    if not NAVER_CLIENT_ID: return None
    url = f"https://openapi.naver.com/v1/search/image?query={movie_nm}+영화+포스터&display=1"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            return res['items'][0].get('link')
    except: return None

def get_omdb_ratings(imdb_id):
    if not OMDB_API_KEY or not imdb_id: return None
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        res = requests.get(url).json()
        return res if res.get('Response') == 'True' else None
    except: return None

# --- [UI 섹션] ---
st.title("🎬 MK CINELAB : 통합 영화 분석기")

# 박스오피스 데이터 로드 (Tab 1 생략, 로직용)
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
box_office_res = requests.get(f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={yesterday}").json()
box_office_list = box_office_res.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

tab1, tab2 = st.tabs(["🔥 실시간 박스오피스", "🔍 영화 심층 검색"])

with tab2:
    query = st.text_input("분석할 영화 제목을 입력하세요", placeholder="예: 프로젝트 헤일메리", key="search_input")
    
    if query:
        movies = get_movie_list(query)
        if movies:
            movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m for m in movies}
            selected = st.selectbox("영화를 선택하세요", options=list(movie_options.keys()))
            
            if selected:
                m_data = movie_options[selected]
                with st.spinner("모든 데이터를 통합하는 중..."):
                    k_detail = get_movie_detail(m_data['movieCd'])
                    t_detail = get_tmdb_info(m_data['movieNm']) # 연도 제외하고 검색
                    imdb_id = t_detail.get('external_ids', {}).get('imdb_id') if t_detail else None
                    o_detail = get_omdb_ratings(imdb_id)
                
                st.divider()
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # 포스터: TMDB -> 네이버 이미지 검색 순으로 시도
                    poster_path = t_detail.get('poster_path') if t_detail else None
                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", use_container_width=True)
                    else:
                        naver_poster = get_naver_image_poster(m_data['movieNm'])
                        if naver_poster:
                            st.image(naver_poster, caption="Source: Naver Image Search", use_container_width=True)
                        else:
                            st.warning("🖼️ 포스터를 찾을 수 없습니다.")
                    
                    st.markdown("### ⭐ 평점 리포트")
                    if o_detail:
                        for r in o_detail.get('Ratings', []):
                            st.metric(r['Source'], r['Value'])
                    else:
                        st.info("글로벌 평점 정보를 불러올 수 없습니다.")

                with col2:
                    st.header(f"{m_data['movieNm']} ({m_data['prdtYear']})")
                    st.markdown("#### 📖 줄거리")
                    st.write(t_detail.get('overview', "정보를 가져올 수 없습니다.") if t_detail else "TMDB에서 데이터를 찾지 못했습니다.")
                    
                    st.divider()
                    st.markdown("#### 📊 영진위 공식 흥행 통계")
                    stats = next((i for i in box_office_list if i["movieCd"] == m_data['movieCd']), None)
                    
                    if stats:
                        st.success(f"현재 박스오피스 **{stats['rank']}위** 기록 중")
                        s1, s2 = st.columns(2)
                        with s1:
                            st.write(f"✅ **누적 관객:** {int(stats['audiAcc']):,}명")
                            st.write(f"✅ **당일 관객:** {int(stats['audiCnt']):,}명")
                        with s2:
                            st.write(f"✅ **누적 매출:** ₩{int(stats['salesAcc']):,}")
                            st.write(f"✅ **스크린 수:** {stats['scrnCnt']}개")
                    else:
                        st.info("현재 박스오피스 순위권 밖입니다.")

if st.button("🔄 앱 초기화"):
    st.rerun()