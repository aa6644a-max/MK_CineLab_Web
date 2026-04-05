import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- 페이지 설정 ---
st.set_page_config(page_title="MK CINELAB - 통합 검색", page_icon="🎬", layout="wide")

# --- API 키 설정 (Secrets 또는 .env) ---
KOBIS_API_KEY = st.secrets.get("KOBIS_API_KEY") or os.getenv("KOBIS_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET")

# --- [1] 데이터 요청 함수 정의 ---

def get_daily_box_office():
    """어제 날짜 박스오피스 TOP 10 로드"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": KOBIS_API_KEY, "targetDt": yesterday}
    try:
        res = requests.get(url, params=params).json()
        return res.get("boxOfficeResult", {}), yesterday
    except: return {}, ""

def get_movie_list(movie_nm):
    """영진위 제목 검색"""
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {"key": KOBIS_API_KEY, "movieNm": movie_nm}
    try:
        res = requests.get(url, params=params).json()
        return res.get("movieListResult", {}).get("movieList", [])
    except: return []

def get_movie_detail(movie_cd):
    """영진위 상세 정보(감독, 배우 등)"""
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": KOBIS_API_KEY, "movieCd": movie_cd}
    try:
        res = requests.get(url, params=params).json()
        return res.get("movieInfoResult", {}).get("movieInfo", {})
    except: return {}

def get_tmdb_info(title, prdt_year=None):
    """강화된 TMDB 검색: 연도 필터링 없이 1차 검색 후 가장 유사한 결과 반환"""
    if not TMDB_API_KEY: return None
    
    # 1. 제목으로만 검색 (가장 성공률 높음)
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&language=ko-KR"
    try:
        search_res = requests.get(search_url).json()
        results = search_res.get('results', [])
        
        if not results: return None
        
        # 제작 연도가 있다면 최대한 가까운 결과 선택, 없으면 첫 번째 결과
        target = results[0]
        if prdt_year:
            for r in results:
                if prdt_year in r.get('release_date', ''):
                    target = r
                    break
        
        # 상세 정보 및 IMDb ID 가져오기
        movie_id = target['id']
        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids&language=ko-KR"
        return requests.get(detail_url).json()
    except: return None

def get_omdb_ratings(imdb_id):
    """OMDB 평점 로드"""
    if not OMDB_API_KEY or not imdb_id: return None
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        return requests.get(url).json()
    except: return None

def get_naver_poster(movie_nm):
    """TMDB 실패 시 네이버 영화 포스터 이미지 검색"""
    if not NAVER_CLIENT_ID: return None
    url = f"https://openapi.naver.com/v1/search/movie.json?query={movie_nm}"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            return res['items'][0].get('image')
    except: return None

# --- [2] UI 메인 로직 ---

st.title("🎬 MK CINELAB : 통합 영화 분석기")

# 상단 탭 구성
tab1, tab2 = st.tabs(["🔥 실시간 박스오피스", "🔍 영화 심층 검색"])

box_office_res, target_date = get_daily_box_office()
box_office_list = box_office_res.get("dailyBoxOfficeList", [])

# [탭 1] 박스오피스 (간략 표기)
with tab1:
    st.subheader(f"📅 {target_date[:4]}-{target_date[4:6]}-{target_date[6:]} 박스오피스 TOP 10")
    if box_office_list:
        for m in box_office_list:
            st.write(f"**{m['rank']}위** | {m['movieNm']} (누적 {int(m['audiAcc']):,}명)")
    else: st.info("박스오피스 데이터를 불러올 수 없습니다.")

# [탭 2] 심층 검색 (TMDB + OMDB + KOBIS 통계)
with tab2:
    query = st.text_input("분석할 영화 제목을 입력하세요", placeholder="예: 왕과 사는 남자")
    
    if query:
        movies = get_movie_list(query)
        if movies:
            movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m for m in movies}
            selected = st.selectbox("영화를 선택하세요", options=list(movie_options.keys()))
            
            if selected:
                m_data = movie_options[selected]
                with st.spinner("다양한 DB에서 정보를 결합하는 중..."):
                    k_detail = get_movie_detail(m_data['movieCd'])
                    t_detail = get_tmdb_info(m_data['movieNm'], m_data['prdtYear'])
                    imdb_id = t_detail.get('external_ids', {}).get('imdb_id') if t_detail else None
                    o_detail = get_omdb_ratings(imdb_id)
                
                st.divider()
                
                # --- 레이아웃 설계 (2컬럼) ---
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # 포스터 출력 (TMDB 1순위, 네이버 2순위)
                    poster_url = f"https://image.tmdb.org/t/p/w500{t_detail['poster_path']}" if t_detail and t_detail.get('poster_path') else get_naver_poster(m_data['movieNm'])
                    
                    if poster_url: st.image(poster_url, use_container_width=True)
                    else: st.warning("🖼️ 포스터를 찾을 수 없습니다.")
                    
                    # 평점 리포트
                    st.markdown("### ⭐ 평점 리포트")
                    if o_detail and o_detail.get('Response') == 'True':
                        for r in o_detail.get('Ratings', []):
                            st.metric(r['Source'], r['Value'])
                    else: st.info("글로벌 평점이 아직 등록되지 않았습니다.")

                with col2:
                    st.header(f"{m_data['movieNm']} ({m_data['prdtYear']})")
                    if t_detail and t_detail.get('tagline'): st.write(f"*{t_detail['tagline']}*")
                    
                    st.markdown("#### 📖 줄거리")
                    st.write(t_detail.get('overview', "줄거리 정보가 없습니다.") if t_detail else "정보를 가져올 수 없습니다.")
                    
                    # 영진위 흥행 지표 (표 형태로 정리)
                    st.markdown("#### 📊 영진위 공식 흥행 통계")
                    stats = next((i for i in box_office_list if i["movieCd"] == m_data['movieCd']), None)
                    
                    if stats:
                        st.success(f"현재 박스오피스 **{stats['rank']}위** 기록 중")
                        s_c1, s_c2 = st.columns(2)
                        with s_c1:
                            st.write(f"✅ **누적 관객:** {int(stats['audiAcc']):,}명")
                            st.write(f"✅ **당일 관객:** {int(stats['audiCnt']):,}명")
                            st.write(f"✅ **스크린 수:** {stats['scrnCnt']}개")
                        with s_c2:
                            st.write(f"✅ **누적 매출:** ₩{int(stats['salesAcc']):,}")
                            st.write(f"✅ **매출 비율:** {stats['salesShare']}%")
                            st.write(f"✅ **상영 횟수:** {stats['showCnt']}회")
                    else:
                        st.info("이 영화는 현재 박스오피스 순위권 밖입니다.")
                    
                    with st.expander("👥 제작진 및 출연진 상세"):
                        st.write(f"**감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                        st.write(f"**배우:** {', '.join([a['peopleNm'] for a in k_detail.get('actors', [])[:15]])}")