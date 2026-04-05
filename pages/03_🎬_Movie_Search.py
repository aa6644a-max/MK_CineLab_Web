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

# --- [2] 데이터 소스별 전담 함수 (검색 매칭률 극대화) ---

def fetch_tmdb_poster(movie_ko, movie_en, year, raw_query):
    """[전담: 포스터] 검색 후보를 늘리고 언어 장벽을 허문 완벽한 TMDB 검색"""
    if not TMDB_API_KEY: return None, None
    
    # 1. 검색어 후보 세팅 (국문 -> 영문 -> 사용자가 직접 입력한 원본 텍스트)
    queries = []
    for q in [movie_ko, movie_en, raw_query]:
        if q and q not in queries:
            queries.append(q)
            
    for query in queries:
        # 2. 언어 설정 (한국어로 찾고, 안 되면 영어 세팅으로 재검색)
        for lang in ["ko-KR", "en-US"]:
            # 3. 연도 설정 (연도 넣어서 정확히 찾고, 안 되면 연도 빼고 재검색)
            for y in [year, ""]:
                url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language={lang}"
                if y: url += f"&year={y}"
                
                try:
                    res = requests.get(url).json().get('results', [])
                    if res:
                        movie_id = res[0]['id']
                        # 상세 정보(IMDb ID 포함) 가져오기
                        ext_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
                        detail = requests.get(ext_url).json()
                        poster = f"https://image.tmdb.org/t/p/w500{detail.get('poster_path')}" if detail.get('poster_path') else None
                        return poster, detail.get('external_ids', {}).get('imdb_id')
                except:
                    continue
                    
    return None, None

def fetch_naver_plot(movie_nm):
    """[전담: 줄거리] 네이버 웹 문서 검색으로 줄거리 추출"""
    if not NAVER_CLIENT_ID: return "네이버 키 설정 필요"
    url = f"https://openapi.naver.com/v1/search/webkr.json?query={movie_nm}+영화+줄거리&display=1"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            desc = res['items'][0].get('description', "")
            clean_desc = re.sub('<[^<]+?>', '', desc) # <b> 등 HTML 태그 깔끔하게 제거
            return clean_desc
    except: pass
    return "줄거리 정보를 찾을 수 없습니다."

def fetch_omdb_ratings(imdb_id):
    """[전담: 평점] TMDB에서 넘겨받은 IMDb ID로 글로벌 평점 확보"""
    if not OMDB_API_KEY or not imdb_id: return []
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        res = requests.get(url).json()
        return res.get('Ratings', []) if res.get('Response') == 'True' else []
    except: return []

# --- [3] UI 및 메인 로직 ---

st.title("🎬 MK CINELAB : 하이브리드 영화 분석기")

query = st.text_input("영화 제목을 입력하세요 (국/영문 모두 가능)", placeholder="예: 파묘, PROJECT HAIL MARY")

if query:
    # 1. 영진위 기본 검색 (중앙 컨트롤 타워 역할)
    k_list_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOBIS_API_KEY}&movieNm={query}"
    movies = requests.get(k_list_url).json().get("movieListResult", {}).get("movieList", [])
    
    if movies:
        movie_options = {f"{m['movieNm']} ({m['prdtYear']} | {m['genreAlt']})": m for m in movies}
        selected = st.selectbox("정확한 영화를 선택하세요", options=list(movie_options.keys()))
        
        if selected:
            m_info = movie_options[selected]
            m_nm, m_en = m_info['movieNm'], m_info.get('movieNmEn', '')
            m_cd, m_yr = m_info['movieCd'], m_info['prdtYear']
            
            with st.spinner("분야별 데이터를 수집 중..."):
                # 💡 수정된 부분: query(사용자 입력값)를 TMDB 함수에 같이 넘겨줍니다!
                poster_url, imdb_id = fetch_tmdb_poster(m_nm, m_en, m_yr, query)
                plot_text = fetch_naver_plot(m_nm)
                ratings = fetch_omdb_ratings(imdb_id)
                # ... (아래는 기존과 동일) ...
                
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
                else: st.warning("🖼️ 글로벌 DB에서 포스터를 찾지 못했습니다.")
                
                # [OMDB 전담] 평점
                st.markdown("### ⭐ 평점 리포트")
                if ratings:
                    for r in ratings:
                        st.metric(r['Source'], r['Value'])
                else: st.info("글로벌 평점 정보 없음 (개봉 전 또는 미등록)")

            with col2:
                st.header(f"{m_nm} ({m_yr})")
                if m_en: st.caption(m_en) # 영문 제목이 있다면 부제로 표시
                
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
                    st.info("현재 박스오피스 순위권 밖이거나 상영 전입니다.")

                with st.expander("👥 제작진 정보"):
                    st.write(f"**감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                    st.write(f"**배우:** {', '.join([a['peopleNm'] for a in k_detail.get('actors', [])[:10]])}")

if st.button("🔄 앱 초기화"):
    st.rerun()