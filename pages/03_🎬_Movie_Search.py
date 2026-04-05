import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="MK CINELAB - 영화 검색", page_icon="🎬", layout="wide")

# --- 설정 (API 키 관리) ---
# .env 파일에 KOBIS_API_KEY="본인의키" 형태로 저장되어 있어야 합니다.
KOBIS_API_KEY = os.getenv("KOBIS_API_KEY")

st.title("🎬 MK CINELAB : 영화 데이터베이스 검색")
st.markdown("영진위(KOBIS) API를 활용하여 대한민국 영화 DB의 표준 정보를 검색합니다.")

# API 키 누락 시 경고창 표시
if not KOBIS_API_KEY:
    st.error("⚠️ API 키를 찾을 수 없습니다. .env 파일에 'KOBIS_API_KEY'를 설정해 주세요.")
    st.stop()

st.markdown("---")

# --- API 호출 함수 ---
def get_movie_list(movie_nm):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {"key": KOBIS_API_KEY, "movieNm": movie_nm}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # HTTP 에러 체크
        return response.json().get("movieListResult", {}).get("movieList", [])
    except Exception as e:
        st.error(f"목록 검색 중 오류 발생: {e}")
        return []

def get_movie_detail(movie_cd):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": KOBIS_API_KEY, "movieCd": movie_cd}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("movieInfoResult", {}).get("movieInfo", {})
    except Exception as e:
        st.error(f"상세 정보 조회 중 오류 발생: {e}")
        return []

# 날짜 포맷 함수 (YYYYMMDD -> YYYY-MM-DD)
def format_date(date_str):
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return "정보없음"

# --- UI 구현 섹션 ---
search_query = st.text_input("영화 제목을 입력해 보세요", placeholder="예: 파묘, 범죄도시, 괴물")

if search_query:
    movies = get_movie_list(search_query)
    
    if not movies:
        st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다.")
    else:
        st.info(f"'{search_query}'(으)로 검색된 {len(movies)}개의 결과가 있습니다.")
        
        # 영화 선택
        movie_options = {f"{m['movieNm']} ({m['prdtYear']} | {m['genreAlt']})": m['movieCd'] for m in movies}
        selected_label = st.selectbox("상세 정보를 볼 영화를 선택하세요", options=list(movie_options.keys()))
        
        if selected_label:
            movie_cd = movie_options[selected_label]
            detail = get_movie_detail(movie_cd)
            
            if detail:
                st.divider()
                col1, col2 = st.columns([1, 1.5])
                
                with col1:
                    st.subheader("📌 기본 정보")
                    st.write(f"**영화명(국문):** {detail['movieNm']}")
                    st.write(f"**영화명(영문):** {detail['movieNmEn']}")
                    st.write(f"**상영시간:** {detail['showTm']}분")
                    # 개봉일 포맷팅 적용
                    open_date = format_date(detail.get('openDt', ''))
                    st.write(f"**개봉일:** {open_date}")
                    st.write(f"**장르:** {', '.join([g['genreNm'] for g in detail['genres']])}")
                    
                    grade = detail['audits'][0]['watchGradeNm'] if detail['audits'] else '정보없음'
                    st.write(f"**심의등급:** {grade}")
                
                with col2:
                    st.subheader("👥 제작진 및 출연")
                    directors = [d['peopleNm'] for d in detail['directors']]
                    st.write(f"**감독:** {', '.join(directors) if directors else '정보없음'}")
                    
                    actors = [a['peopleNm'] for a in detail['actors']]
                    if actors:
                        with st.expander(f"출연 배우 ({len(actors)}명) 전체 보기"):
                            st.write(", ".join(actors))
                    else:
                        st.write("**출연 배우:** 정보없음")
                    
                    companys = [f"{c['companyNm']}({c['companyPartNm']})" for c in detail['companys']]
                    if companys:
                        st.write(f"**관련 기업:** {', '.join(companys)}")

# 초기화 버튼
if st.button("🔄 검색 초기화"):
    st.rerun()