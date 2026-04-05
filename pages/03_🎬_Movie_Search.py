import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - 평점 릴레이 테스트", page_icon="🧪")

# --- API 키 설정 ---
TMDB_API_KEY = (st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY") or "").strip().strip('\'"')
OMDB_API_KEY = (st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY") or "").strip().strip('\'"')

# 통신용 공통 헤더 (TMDB용)
tmdb_headers = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}

def fetch_tmdb_and_omdb(query):
    # [1구간] TMDB 영화 검색
    search_url = "https://api.themoviedb.org/3/search/movie"
    search_params = {"query": query, "language": "ko-KR"}
    
    try:
        search_res = requests.get(search_url, headers=tmdb_headers, params=search_params).json()
        results = search_res.get('results', [])
        
        if not results:
            return None, "TMDB에서 영화를 찾지 못했습니다.", None
            
        movie_id = results[0]['id']
        title = results[0]['title']
        poster_path = results[0]['poster_path']
        
        # [2구간] TMDB 상세 정보에서 IMDb ID 추출 (여기서도 headers 필수!)
        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        detail_params = {"append_to_response": "external_ids"}
        
        detail_res = requests.get(detail_url, headers=tmdb_headers, params=detail_params).json()
        imdb_id = detail_res.get('external_ids', {}).get('imdb_id')
        
        if not imdb_id:
            return title, "TMDB에 IMDb ID가 등록되지 않았습니다.", poster_path
            
        # [3구간] 추출한 IMDb ID로 OMDB 평점 조회 (OMDB는 헤더 없이 키만 파라미터로 전송)
        if not OMDB_API_KEY:
            return title, "❌ OMDB API 키가 설정되지 않았습니다.", poster_path
            
        omdb_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
        omdb_res = requests.get(omdb_url).json()
        
        if omdb_res.get('Response') == 'True':
            ratings = omdb_res.get('Ratings', [])
            return title, ratings, poster_path
        else:
            return title, f"OMDB 에러: {omdb_res.get('Error')}", poster_path
            
    except Exception as e:
        return None, f"통신 에러 발생: {e}", None

# --- UI ---
st.title("🧪 릴레이 테스트: TMDB 🏃‍♂️ OMDB")

if OMDB_API_KEY:
    st.info(f"🔑 OMDB 키 정상 로드됨: {OMDB_API_KEY[:3]}... (길이: {len(OMDB_API_KEY)})")
else:
    st.error("🔑 OMDB 키가 없습니다! Secrets 설정을 확인하세요.")

query = st.text_input("영화 제목을 입력하세요 (예: 파묘, 에이리언)", key="test_query")

if query:
    with st.spinner("TMDB와 OMDB를 바쁘게 오가는 중..."):
        title, result_data, poster = fetch_tmdb_and_omdb(query)
        
    st.divider()
    
    if title:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if poster:
                st.image(f"https://image.tmdb.org/t/p/w500{poster}", use_container_width=True)
            else:
                st.warning("포스터 없음")
                
        with col2:
            st.header(title)
            st.subheader("⭐ 글로벌 평점 리포트")
            
            # 평점 데이터가 정상적으로 리스트(List) 형태로 들어왔을 때
            if isinstance(result_data, list):
                if result_data:
                    for r in result_data:
                        st.metric(r['Source'], r['Value'])
                else:
                    st.info("OMDB에 등록된 평점이 아직 없습니다.")
            # 에러 메시지(문자열)가 들어왔을 때
            else:
                st.warning(result_data)
    else:
        st.error(result_data) # 검색 실패 메시지 출력