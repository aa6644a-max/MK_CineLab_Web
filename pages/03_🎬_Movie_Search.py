import streamlit as st
import requests
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - 영화 검색 시스템", page_icon="🎬", layout="wide")

# --- [1] API 키 로드 및 클리닝 ---
KOBIS_API_KEY = (st.secrets.get("KOBIS_API_KEY") or os.getenv("KOBIS_API_KEY") or "").strip().strip('\'"')
TMDB_API_KEY = (st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY") or "").strip().strip('\'"')
OMDB_API_KEY = (st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY") or "").strip().strip('\'"')
NAVER_CLIENT_ID = (st.secrets.get("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID") or "").strip().strip('\'"')
NAVER_CLIENT_SECRET = (st.secrets.get("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET") or "").strip().strip('\'"')

# --- [2] 데이터 통신 함수 ---

def fetch_kobis_search(query):
    if not KOBIS_API_KEY: return []
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOBIS_API_KEY}&movieNm={query}"
    try:
        return requests.get(url).json().get("movieListResult", {}).get("movieList", [])
    except: return []

def fetch_kobis_detail_and_boxoffice(movie_cd):
    detail_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={KOBIS_API_KEY}&movieCd={movie_cd}"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    box_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={yesterday}"
    
    try:
        detail = requests.get(detail_url).json().get("movieInfoResult", {}).get("movieInfo", {})
        box_list = requests.get(box_url).json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        stats = next((i for i in box_list if i["movieCd"] == movie_cd), None)
        return detail, stats
    except: return {}, None

def fetch_tmdb_data(movie_nm, movie_en, year):
    if not TMDB_API_KEY: return None, None, "", 0, 0
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}", "accept": "application/json"}
    queries = [q for q in [movie_nm, movie_en] if q]
    
    for query in queries:
        for lang in ["ko-KR", "en-US"]:
            for y in [year, ""]:
                url = "https://api.themoviedb.org/3/search/movie"
                params = {"query": query, "language": lang}
                if y: params["year"] = y
                
                try:
                    res = requests.get(url, headers=headers, params=params).json().get('results', [])
                    if res:
                        movie_id = res[0]['id']
                        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                        d_params = {"append_to_response": "external_ids", "language": "ko-KR"}
                        detail = requests.get(detail_url, headers=headers, params=d_params).json()
                        
                        poster = f"https://image.tmdb.org/t/p/w500{detail.get('poster_path')}" if detail.get('poster_path') else None
                        overview = detail.get('overview', "")
                        imdb_id = detail.get('external_ids', {}).get('imdb_id')
                        vote_avg = detail.get('vote_average', 0)
                        vote_cnt = detail.get('vote_count', 0)
                        return poster, imdb_id, overview, vote_avg, vote_cnt
                except: continue
    return None, None, "", 0, 0

def fetch_naver_plot_fallback(movie_nm):
    if not NAVER_CLIENT_ID: return ""
    url = f"https://openapi.naver.com/v1/search/encyc.json?query={movie_nm}+영화&display=1"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            return re.sub('<[^<]+?>', '', res['items'][0].get('description', ""))
    except: pass
    return "등록된 줄거리 정보가 없습니다."

def fetch_omdb_ratings(imdb_id):
    if not OMDB_API_KEY or not imdb_id: return []
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    try:
        res = requests.get(url).json()
        return res.get('Ratings', []) if res.get('Response') == 'True' else []
    except: return []

# --- 숫자 포맷팅 헬퍼 함수 ---
def format_money(amount_str):
    """긴 매출액을 보기 편하게 억 단위로 변환"""
    try:
        amount = int(amount_str)
        if amount >= 100000000:
            return f"{amount // 100000000:,}억 {(amount % 100000000) // 10000:,}만 원"
        return f"₩{amount:,}"
    except: return "정보 없음"


# --- [3] UI 렌더링 ---

st.title("🎬 MK CINELAB : 하이브리드 영화 대시보드")
st.markdown("정확한 영화 식별을 위해 **검색 후 드롭다운**에서 조회할 영화를 선택해 주세요.")

search_query = st.text_input("🔍 영화 제목 입력", placeholder="예: 파묘, 에이리언, 프로젝트 헤일메리")

if search_query:
    movies = fetch_kobis_search(search_query)
    
    if not movies:
        st.warning(f"영진위 DB에 '{search_query}'에 대한 검색 결과가 없습니다.")
    else:
        movie_options = {f"{m['movieNm']} ({m['prdtYear']} | {m['genreAlt']})": m for m in movies}
        selected = st.selectbox("🎯 정확한 영화를 선택하세요", options=["선택 안 함"] + list(movie_options.keys()))
        
        if selected != "선택 안 함":
            m_info = movie_options[selected]
            m_nm, m_en, m_cd, m_yr = m_info['movieNm'], m_info.get('movieNmEn', ''), m_info['movieCd'], m_info['prdtYear']
            
            with st.spinner("모든 데이터베이스를 조회 중입니다..."):
                k_detail, k_stats = fetch_kobis_detail_and_boxoffice(m_cd)
                poster_url, imdb_id, tmdb_overview, tmdb_vote, tmdb_cnt = fetch_tmdb_data(m_nm, m_en, m_yr)
                ratings = fetch_omdb_ratings(imdb_id)
                final_plot = tmdb_overview if tmdb_overview else fetch_naver_plot_fallback(m_nm)

            st.divider()
            col1, col2 = st.columns([1, 2.2])
            
            # [왼쪽 단] 포스터 및 평점
            with col1:
                if poster_url:
                    st.image(poster_url, use_container_width=True, caption="TMDB Database")
                else:
                    st.warning("🖼️ 포스터 이미지를 찾을 수 없습니다.")
                
                st.markdown("### ⭐ 글로벌 평점")
                if ratings:
                    for r in ratings:
                        icon = "🍅" if r['Source'] == "Rotten Tomatoes" else ("🎬" if r['Source'] == "Internet Movie Database" else "Ⓜ️")
                        st.metric(f"{icon} {r['Source']}", r['Value'])
                elif tmdb_vote and tmdb_cnt > 0:
                    st.info("OMDB 공식 평점 대신 TMDB 유저 평점을 제공합니다.")
                    st.metric("💠 TMDB User Rating", f"{tmdb_vote:.1f} / 10", f"{tmdb_cnt:,} votes")
                else:
                    st.info("등록된 평점 정보가 없습니다. (개봉 전 이거나 데이터 부족)")

            # [오른쪽 단] 정보 및 통계
            with col2:
                st.header(f"{m_nm} ({m_yr})")
                if m_en: st.caption(f"Original Title: {m_en}")
                
                c_head1, c_head2, c_head3 = st.columns(3)
                c_head1.write(f"⏱ **러닝타임:** {k_detail.get('showTm', '정보없음')}분")
                c_head2.write(f"🎞 **장르:** {', '.join([g['genreNm'] for g in k_detail.get('genres', [])])}")
                open_dt = k_detail.get('openDt', '')
                f_open_dt = f"{open_dt[:4]}-{open_dt[4:6]}-{open_dt[6:]}" if len(open_dt) == 8 else "미정"
                c_head3.write(f"📅 **개봉일:** {f_open_dt}")

                st.markdown("---")
                st.markdown("#### 📖 시놉시스 (Synopsis)")
                if final_plot:
                    st.write(final_plot)
                else:
                    st.info("등록된 공식 줄거리가 없습니다.")
                
                st.markdown("---")
                
                # 💡 [핵심 수정 구간] 2열 2행으로 배치하여 글자 짤림 방지
                st.markdown("#### 📊 영진위 실시간 통계")
                if k_stats:
                    st.success(f"🔥 현재 박스오피스 **{k_stats['rank']}위** 기록 중!")
                    
                    # 4개의 컬럼 대신 2개씩 2줄로 배치
                    row1_col1, row1_col2 = st.columns(2)
                    with row1_col1:
                        st.metric("누적 관객수", f"{int(k_stats['audiAcc']):,}명", f"+{int(k_stats['audiInten']):,}명 (전일 대비)")
                    with row1_col2:
                        st.metric("당일 관객수", f"{int(k_stats['audiCnt']):,}명")
                    
                    row2_col1, row2_col2 = st.columns(2)
                    with row2_col1:
                        # 172억 2500만원 형태로 포맷팅해서 자리 차지 줄임
                        st.metric("누적 매출액", format_money(k_stats['salesAcc']))
                    with row2_col2:
                        st.metric("스크린 수", f"{k_stats['scrnCnt']}개")
                else:
                    st.info("현재 박스오피스 TOP 10 진입작이 아닙니다. (과거 개봉작 또는 상영 전)")
                
                st.markdown("---")
                st.markdown("#### 👥 상세 제작 정보 (KOBIS Database)")
                
                with st.expander("🎬 감독 및 주요 출연진"):
                    st.write(f"**감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                    actors = [a['peopleNm'] for a in k_detail.get('actors', [])]
                    st.write(f"**출연진:** {', '.join(actors) if actors else '등록된 배우 정보가 없습니다.'}")
                
                with st.expander("🛠️ 주요 스태프 및 제작진"):
                    staffs = [f"{s['peopleNm']} ({s['staffRoleNm']})" for s in k_detail.get('staffs', [])]
                    st.write(", ".join(staffs) if staffs else "스태프 정보가 없습니다.")
                
                with st.expander("🏢 관련 회사 및 배급사"):
                    companies = [f"{c['companyNm']} ({c['companyPartNm']})" for c in k_detail.get('companys', [])]
                    for comp in companies:
                        st.write(f"- {comp}")
                        
                with st.expander("📋 심의 및 관람 등급"):
                    audits = [a['watchGradeNm'] for a in k_detail.get('audits', [])]
                    st.write(f"**심의 등급:** {', '.join(audits) if audits else '심의 정보 없음'}")
                    nations = [n['nationNm'] for n in k_detail.get('nations', [])]
                    st.write(f"**제작 국가:** {', '.join(nations) if nations else '정보 없음'}")