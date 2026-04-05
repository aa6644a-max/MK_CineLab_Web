import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="MK CINELAB - 영화 인사이트", page_icon="🎬", layout="wide")

# --- 설정 (API 키 관리) ---
if "KOBIS_API_KEY" in st.secrets:
    KOBIS_API_KEY = st.secrets["KOBIS_API_KEY"]
else:
    KOBIS_API_KEY = os.getenv("KOBIS_API_KEY")

# --- API 호출 함수 ---

def get_daily_box_office():
    """어제 날짜 기준 박스오피스 TOP 10 가져오기"""
    # 박스오피스는 보통 전날 데이터가 최신입니다.
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": KOBIS_API_KEY, "targetDt": yesterday}
    try:
        response = requests.get(url, params=params)
        return response.json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", []), yesterday
    except Exception as e:
        st.error(f"박스오피스 로드 실패: {e}")
        return [], ""

def get_movie_list(movie_nm):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {"key": KOBIS_API_KEY, "movieNm": movie_nm}
    try:
        response = requests.get(url, params=params)
        return response.json().get("movieListResult", {}).get("movieList", [])
    except Exception as e:
        st.error(f"목록 검색 중 오류: {e}")
        return []

def get_movie_detail(movie_cd):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": KOBIS_API_KEY, "movieCd": movie_cd}
    try:
        response = requests.get(url, params=params)
        return response.json().get("movieInfoResult", {}).get("movieInfo", {})
    except Exception as e:
        st.error(f"상세 정보 조회 중 오류: {e}")
        return []

def format_date(date_str):
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return "정보없음"

# --- UI 구현 섹션 ---
st.title("🎬 MK CINELAB : 영화 인사이트")

if not KOBIS_API_KEY:
    st.error("⚠️ API 키를 찾을 수 없습니다.")
    st.stop()

# 탭 구성
tab1, tab2 = st.tabs(["🔥 실시간 박스오피스", "🔍 영화 상세 검색"])

# --- [Tab 1: 박스오피스] ---
with tab1:
    box_office_list, target_date = get_daily_box_office()
    st.subheader(f"📅 {format_date(target_date)} 기준 인기 영화")
    
    if box_office_list:
        # 가독성을 위해 컬럼 구성
        for movie in box_office_list:
            with st.container():
                col_rank, col_info, col_audi = st.columns([0.5, 2, 1.5])
                
                with col_rank:
                    st.header(f"{movie['rank']}")
                    # 순위 변동 아이콘
                    rank_inten = int(movie['rankInten'])
                    if rank_inten > 0: st.caption(f"🔺{rank_inten}")
                    elif rank_inten < 0: st.caption(f"🔻{abs(rank_inten)}")
                    else: st.caption("➖")
                
                with col_info:
                    st.subheader(movie['movieNm'])
                    st.write(f"개봉일: {movie['openDt']}")
                
                with col_audi:
                    # 관객수 포맷팅 (쉼표 추가)
                    daily_audi = f"{int(movie['audiCnt']):,}"
                    acc_audi = f"{int(movie['audiAcc']):,}"
                    st.write(f"**오늘 관객:** {daily_audi}명")
                    st.write(f"**누적 관객:** {acc_audi}명")
                st.divider()
    else:
        st.info("박스오피스 데이터를 불러오는 중입니다...")

# --- [Tab 2: 영화 상세 검색] ---
with tab2:
    search_query = st.text_input("영화 제목을 입력하세요", placeholder="예: 파묘, 범죄도시, 괴물", key="search_input")

    if search_query:
        movies = get_movie_list(search_query)
        if not movies:
            st.warning("검색 결과가 없습니다.")
        else:
            movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m['movieCd'] for m in movies}
            selected_label = st.selectbox("상세 정보를 볼 영화 선택", options=list(movie_options.keys()))
            
            if selected_label:
                detail = get_movie_detail(movie_options[selected_label])
                if detail:
                    st.divider()
                    c1, c2 = st.columns([1, 1.5])
                    with c1:
                        st.subheader("📌 기본 정보")
                        st.write(f"**영화명:** {detail['movieNm']}")
                        st.write(f"**상영시간:** {detail['showTm']}분")
                        st.write(f"**장르:** {', '.join([g['genreNm'] for g in detail['genres']])}")
                        grade = detail['audits'][0]['watchGradeNm'] if detail['audits'] else '정보없음'
                        st.write(f"**심의등급:** {grade}")
                    with c2:
                        st.subheader("👥 제작진 및 출연")
                        directors = [d['peopleNm'] for d in detail['directors']]
                        st.write(f"**감독:** {', '.join(directors)}")
                        actors = [a['peopleNm'] for a in detail['actors'][:10]] # 상위 10명만
                        st.write(f"**주요 출연:** {', '.join(actors) if actors else '정보없음'}")

if st.button("🔄 앱 초기화"):
    st.rerun()