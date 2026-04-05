import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - 영화 인사이트", page_icon="🎬", layout="wide")

KOBIS_API_KEY = st.secrets.get("KOBIS_API_KEY") or os.getenv("KOBIS_API_KEY")

# --- API 호출 함수 ---

def get_daily_box_office():
    """어제 날짜 기준 박스오피스 전체 데이터 가져오기"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": KOBIS_API_KEY, "targetDt": yesterday}
    try:
        response = requests.get(url, params=params)
        data = response.json().get("boxOfficeResult", {})
        return data, yesterday
    except Exception as e:
        st.error(f"박스오피스 로드 실패: {e}")
        return {}, ""

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

def format_date(date_str):
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return "정보없음"

# --- UI 구현 섹션 ---
st.title("🎬 MK CINELAB : 영화 인사이트")

if not KOBIS_API_KEY:
    st.error("⚠️ API 키를 확인해 주세요.")
    st.stop()

# 공통 데이터 로드 (두 탭에서 공유)
box_office_result, target_date = get_daily_box_office()
box_office_list = box_office_result.get("dailyBoxOfficeList", [])

tab1, tab2 = st.tabs(["🔥 실시간 박스오피스", "🔍 영화 상세 검색"])

# --- [Tab 1: 박스오피스] ---
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
                    st.write(f"개봉일: {movie['openDt']} | 신규진입: {movie['rankOldAndNew']}")
                with c3:
                    st.write(f"**누적 관객:** {int(movie['audiAcc']):,}")
                    st.write(f"**당일 관객:** {int(movie['audiCnt']):,}")
                st.divider()

# --- [Tab 2: 영화 상세 검색] ---
with tab2:
    search_query = st.text_input("영화 제목을 입력하세요", placeholder="예: 파묘, 범죄도시, 괴물", key="search_input")

    if search_query:
        movies = get_movie_list(search_query)
        if movies:
            movie_options = {f"{m['movieNm']} ({m['prdtYear']})": m['movieCd'] for m in movies}
            selected_label = st.selectbox("상세 정보를 볼 영화 선택", options=list(movie_options.keys()))
            
            if selected_label:
                m_code = movie_options[selected_label]
                detail = get_movie_detail(m_code)
                
                if detail:
                    st.divider()
                    # 1. 기본 정보 섹션
                    col1, col2 = st.columns([1, 1.5])
                    with col1:
                        st.subheader("📌 기본 정보")
                        st.write(f"**영화명:** {detail['movieNm']}")
                        st.write(f"**국가:** {detail['nations'][0]['nationNm'] if detail['nations'] else '정보없음'}")
                        st.write(f"**상영시간:** {detail['showTm']}분")
                        st.write(f"**장르:** {', '.join([g['genreNm'] for g in detail['genres']])}")
                        grade = detail['audits'][0]['watchGradeNm'] if detail['audits'] else '정보없음'
                        st.write(f"**심의등급:** {grade}")
                    with col2:
                        st.subheader("👥 제작진 및 출연")
                        st.write(f"**감독:** {', '.join([d['peopleNm'] for d in detail['directors']])}")
                        actors = [a['peopleNm'] for a in detail['actors'][:10]]
                        st.write(f"**주요 출연:** {', '.join(actors) if actors else '정보없음'}")

                    # 2. 실시간 흥행 통계 섹션 (박스오피스 데이터 매칭)
                    # 현재 검색한 영화가 박스오피스 리스트에 있는지 확인
                    stats = next((item for item in box_office_list if item["movieCd"] == m_code), None)
                    
                    st.divider()
                    st.subheader("📊 실시간 흥행 및 통계 정보")
                    
                    if stats:
                        st.success(f"현재 박스오피스 **{stats['rank']}위**에 랭크되어 있는 영화입니다. (조회 일자: {format_date(target_date)})")
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("박스오피스 순위", f"{stats['rank']}위", f"{stats['rankInten']} ({stats['rankOldAndNew']})")
                        m2.metric("당일 관객수", f"{int(stats['audiCnt']):,}명", f"{stats['audiChange']}%")
                        m3.metric("누적 관객수", f"{int(stats['audiAcc']):,}명", f"+{int(stats['audiInten']):,}명")
                        m4.metric("매출 점유율", f"{stats['salesShare']}%", f"{stats['salesChange']}%")

                        with st.expander("📝 상세 통계 지표 보기"):
                            st.write(f"**조회 종류:** {box_office_result.get('boxofficeType')}")
                            st.write(f"**조회 범위:** {box_office_result.get('showRange')}")
                            st.write(f"**당일 매출액:** {int(stats['salesAmt']):,}원 (전일 대비 {int(stats['salesInten']):,}원 증감)")
                            st.write(f"**누적 매출액:** {int(stats['salesAcc']):,}원")
                            st.write(f"**상영 스크린 수:** {stats['scrnCnt']}개")
                            st.write(f"**상영 횟수:** {stats['showCnt']}회")
                    else:
                        st.info("이 영화는 현재 박스오피스 TOP 10 밖이거나 최신 흥행 통계 데이터가 존재하지 않습니다.")

if st.button("🔄 앱 초기화"):
    st.rerun()