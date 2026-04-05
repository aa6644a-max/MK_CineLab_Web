import streamlit as st
import requests
import os
import re
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

# --- [2] 데이터 소스별 전담 함수 (로직 강화) ---

def fetch_tmdb_poster(movie_nm, year):
    """[전담: 포스터] 영진위 연도를 사용하여 정확한 영화의 포스터와 IMDb ID 추출"""
    if not TMDB_API_KEY: return None, None
    # 연도를 포함하여 검색 정확도를 높임
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_nm}&language=ko-KR&year={year}"
    try:
        res = requests.get(url).json().get('results', [])
        if not res: # 연도로 못 찾으면 제목으로만 재시도
            url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_nm}&language=ko-KR"
            res = requests.get(url).json().get('results', [])
            
        if res:
            movie_id = res[0]['id']
            ext_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
            detail = requests.get(ext_url).json()
            poster = f"https://image.tmdb.org/t/p/w500{detail.get('poster_path')}" if detail.get('poster_path') else None
            return poster, detail.get('external_ids', {}).get('imdb_id')
    except: pass
    return None, None

def fetch_naver_plot(movie_nm):
    """[전담: 줄거리] 지식백과 대신 '웹 검색'을 통해 실제 영화 시놉시스 추출"""
    if not NAVER_CLIENT_ID: return "네이버 키 설정 필요"
    # '지식백과'는 영화 단어 정의를 주는 경우가 많아 '웹 검색'으로 교체합니다.
    url = f"https://openapi.naver.com/v1/search/webkr.json?query={movie_nm}+영화+줄거리&display=1"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            desc = res['items'][0].get('description', "")
            clean_desc = re.sub('<[^<]+?>', '', desc) # HTML 태그 제거
            return clean_desc
    except: pass
    return "줄거리 정보를 찾을 수 없습니다."

def fetch_omdb_ratings(imdb_id):
    """[전담: 평점] IMDb ID를 기반으로 로튼토마토 및 IMDb 평점만 추출"""
    if not OMDB_API_KEY or not imdb_id: return []
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        res = requests.get(url).json()
        return res.get('Ratings', []) if res.get('Response') == 'True' else []
    except: return []

# --- [3] UI 및 메인 로직 ---

st.title("🎬 MK CINELAB : 하이브리드 영화 분석기")

query = st.text_input("영화 제목을 입력하세요", placeholder="예: 파묘, 프로젝트 헤일메리")

if query:
    # 1. 영진위 기본 검색 (이름 & 코드 & 연도 획득)
    k_list_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOBIS_API_KEY}&movieNm={query}"
    movies = requests.get(k_list_url).json().get("movieListResult", {}).get("movieList", [])
    
    if movies:
        movie_options = {f"{m['movieNm']} ({m['prdtYear']} | {m['genreAlt']})": m for m in movies}
        selected = st.selectbox("정확한 영화를 선택하세요", options=list(movie_options.keys()))
        
        if selected:
            m_info = movie_options[selected]
            m_nm, m_cd, m_yr = m_info['movieNm'], m_info['movieCd'], m_info['prdtYear']
            
            with st.spinner("분야별 데이터를 수집 중..."):
                # 분야별 독립 호출
                poster_url, imdb_id = fetch_tmdb_poster(m_nm, m_yr)
                plot_text = fetch_naver_plot(m_nm)
                ratings = fetch_omdb_ratings(imdb_id)
                
                # 영진위 상세/박스오피스 호출
                detail_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={KOBIS_API_KEY}&movieCd={m_cd}"
                k_detail = requests.get(detail_url).json().get("movieInfoResult", {}).get("movieInfo", {})
                
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
                box_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={yesterday}"
                box_list = requests.get(box_url).json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
                stats = next((i for i in box_list if i["movieCd"] == m_cd), None)

            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # [TMDB 전담] 포스터
                if poster_url: st.image(poster_url, use_container_width=True)
                else: st.warning("🖼️ TMDB 포스터 없음")
                
                # [OMDB 전담] 평점
                st.markdown("### ⭐ 평점 리포트")
                if ratings:
                    for r in ratings:
                        st.metric(r['Source'], r['Value'])
                else: st.info("글로벌 평점 정보 없음")

            with col2:
                st.header(f"{m_nm} ({m_yr})")
                
                # [네이버 전담] 줄거리
                st.markdown("#### 📖 줄거리 (Naver Web)")
                st.info(plot_text)
                
                st.divider()
                
                # [영진위 전담] 흥행 통계
                st.markdown("#### 📊 영진위 공식 흥행 통계")
                if stats:
                    st.success(f"현재 박스오피스 {stats['rank']}위 기록 중")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"✅ **누적 관객:** {int(stats['audiAcc']):,}명")
                    with c2:
                        st.write(f"✅ **누적 매출:** ₩{int(stats['salesAcc']):,}")
                else:
                    st.info("현재 박스오피스 순위권 밖입니다.")

                with st.expander("👥 제작진 정보"):
                    st.write(f"**감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                    st.write(f"**배우:** {', '.join([a['peopleNm'] for a in k_detail.get('actors', [])[:10]])}")

if st.button("🔄 앱 초기화"):
    st.rerun()