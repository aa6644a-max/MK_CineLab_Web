import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - TMDB 테스트", page_icon="🧪")

# --- API 키 설정 ---
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

def search_tmdb_only(query):
    """오직 TMDB에서만 영화를 검색합니다."""
    if not TMDB_API_KEY:
        st.error("TMDB API 키가 없습니다.")
        return None

    # 한국어 세팅으로 검색
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=ko-KR"
    
    try:
        response = requests.get(url).json()
        results = response.get('results', [])
        
        if results:
            return results[0] # 가장 첫 번째 검색 결과 반환
        else:
            return None
    except Exception as e:
        st.error(f"API 호출 에러: {e}")
        return None

# --- UI ---
st.title("🧪 TMDB 순수 검색 테스트")
st.markdown("영진위 간섭 없이 오직 TMDB에 직접 쿼리를 날려 포스터를 가져오는지 확인합니다.")

query = st.text_input("영화 제목을 입력하세요 (예: 파묘, PROJECT HAIL MARY)", key="test_query")

if query:
    with st.spinner("TMDB 검색 중..."):
        movie_data = search_tmdb_only(query)
        
    if movie_data:
        st.success(f"TMDB에서 '{movie_data.get('title')}' 영화를 찾았습니다!")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            poster_path = movie_data.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                st.image(poster_url, use_container_width=True)
                st.caption(f"포스터 경로: {poster_path}")
            else:
                st.warning("영화는 찾았지만 TMDB에 등록된 포스터 이미지가 없습니다.")
                
        with col2:
            st.write(f"**원제:** {movie_data.get('original_title')}")
            st.write(f"**개봉일:** {movie_data.get('release_date')}")
            st.write(f"**TMDB 평점:** {movie_data.get('vote_average')}")
            st.write(f"**줄거리:** {movie_data.get('overview')}")
            
            with st.expander("원본 JSON 데이터 보기"):
                st.json(movie_data)
    else:
        st.error("TMDB에서 검색 결과가 전혀 나오지 않습니다. 영어/한국어 스펠링을 확인해 보세요.")