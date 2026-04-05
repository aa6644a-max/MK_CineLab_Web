import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - 통합 영화 검색", page_icon="🎬", layout="wide")

# --- [1] API 키 로드 ---
KOBIS_API_KEY = st.secrets.get("KOBIS_API_KEY") or os.getenv("KOBIS_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET")

# --- [2] 각 데이터 소스별 전담 함수 ---

def fetch_kobis_data(movie_nm, movie_cd):
    """[영진위] 공식 통계 및 상세 정보 담당"""
    # 1. 상세 정보 (감독, 배우 등)
    detail_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={KOBIS_API_KEY}&movieCd={movie_cd}"
    # 2. 박스오피스 통계 (누적 관객수 등)
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    box_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={yesterday}"
    
    try:
        detail = requests.get(detail_url).json().get("movieInfoResult", {}).get("movieInfo", {})
        box_office = requests.get(box_url).json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        stats = next((item for item in box_office if item["movieCd"] == movie_cd), None)
        return detail, stats
    except: return {}, None

def fetch_tmdb_poster(movie_nm):
    """[TMDB] 오직 포스터 이미지와 IMDb ID 추출 담당"""
    if not TMDB_API_KEY: return None, None
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_nm}&language=ko-KR"
    try:
        res = requests.get(url).json().get('results', [])
        if res:
            movie_id = res[0]['id']
            # IMDb ID를 얻기 위해 외부 ID 추가 호출
            ext_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
            detail = requests.get(ext_url).json()
            poster_url = f"https://image.tmdb.org/t/p/w500{detail.get('poster_path')}" if detail.get('poster_path') else None
            return poster_url, detail.get('external_ids', {}).get('imdb_id')
    except: pass
    return None, None

def fetch_naver_plot(movie_nm):
    """[네이버] 지식백과 검색을 통한 공식 줄거리 추출 담당"""
    if not NAVER_CLIENT_ID: return "네이버 API 설정이 필요합니다."
    # 영화 정보는 지식백과(encyc)가 가장 정확합니다.
    url = f"https://openapi.naver.com/v1/search/encyc.json?query={movie_nm}+영화+줄거리&display=1"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            description = res['items'][0].get('description')
            # HTML 태그 제거 및 정리
            import re
            clean_plot = re.sub('<[^<]+?>', '', description)
            return clean_plot
    except: pass
    return "네이버에서 줄거리를 찾을 수 없습니다."

def fetch_omdb_ratings(imdb_id):
    """[OMDB] 오직 로튼토마토 및 IMDb 평점 담당"""
    if not OMDB_API_KEY or not imdb_id: return []
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        res = requests.get(url).json()
        return res.get('Ratings', []) if res.get('Response') == 'True' else []
    except: return []

# --- [3] UI 구성 ---

st.title("🎬 MK CINELAB : 하이브리드 영화 분석기")
st.caption("영진위(통계) | TMDB(포스터) | 네이버(줄거리) | OMDB(평점)")

query = st.text_input("분석할 영화 제목을 입력하세요", placeholder="예: 프로젝트 헤일메리")

if query:
    # 1단계: 영진위에서 기본 목록 검색
    search_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOBIS_API_KEY}&movieNm={query}"
    movies = requests.get(search_url).json().get("movieListResult", {}).get("movieList", [])
    
    if movies:
        movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m for m in movies}
        selected_label = st.selectbox("정확한 영화를 선택하세요", options=list(movie_options.keys()))
        
        if selected_label:
            target = movie_options[selected_label]
            m_nm, m_cd = target['movieNm'], target['movieCd']
            
            with st.spinner("각 데이터 소스에서 최적의 정보를 수집 중..."):
                # 독립적으로 각 API 호출 (역할 분담)
                k_detail, k_stats = fetch_kobis_data(m_nm, m_cd)
                poster_url, imdb_id = fetch_tmdb_poster(m_nm)
                naver_plot = fetch_naver_plot(m_nm)
                omdb_ratings = fetch_omdb_ratings(imdb_id)
            
            st.divider()
            
            # --- 레이아웃 출력 ---
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # [TMDB 전담] 포스터
                if poster_url: st.image(poster_url, use_container_width=True)
                else: st.warning("🖼️ TMDB 포스터 없음")
                
                # [OMDB 전담] 평점
                st.markdown("### ⭐ 평점 리포트")
                if omdb_ratings:
                    for r in omdb_ratings:
                        st.metric(r['Source'], r['Value'])
                else: st.info("글로벌 평점 정보 없음")

            with col2:
                st.header(f"{m_nm} ({target['prdtYear']})")
                
                # [네이버 전담] 줄거리
                st.markdown("#### 📖 줄거리 (Naver)")
                st.write(naver_plot)
                
                st.divider()
                
                # [영진위 전담] 흥행 지표
                st.markdown("#### 📊 영진위 공식 흥행 통계")
                if k_stats:
                    st.success(f"현재 박스오피스 {k_stats['rank']}위 기록 중")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"✅ **누적 관객:** {int(k_stats['audiAcc']):,}명")
                        st.write(f"✅ **당일 관객:** {int(k_stats['audiCnt']):,}명")
                    with c2:
                        st.write(f"✅ **누적 매출:** ₩{int(k_stats['salesAcc']):,}")
                        st.write(f"✅ **상영 횟수:** {k_stats['showCnt']}회")
                else:
                    st.info("현재 박스오피스 순위권 밖입니다.")

                with st.expander("👥 제작진 및 출연진 상세"):
                    st.write(f"**감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                    st.write(f"**배우:** {', '.join([a['peopleNm'] for a in k_detail.get('actors', [])[:10]])}")

if st.button("🔄 앱 초기화"):
    st.rerun()