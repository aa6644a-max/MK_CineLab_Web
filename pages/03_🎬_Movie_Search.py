import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - TMDB 테스트", page_icon="🧪")

TMDB_API_KEY = (st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY") or "").strip().strip('\'"')

def search_tmdb_only(query):
    if not TMDB_API_KEY:
        st.error("❌ TMDB API 키(토큰)를 찾지 못했습니다.")
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    
    # 💡 핵심 해결책: v4 토큰(eyJhb...)을 위한 인증 헤더(Headers) 추가
    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json"
    }
    
    # 💡 api_key는 파라미터에서 뺍니다.
    params = {
        "query": query,
        "language": "ko-KR"
    }
    
    try:
        # headers를 추가해서 통신을 요청합니다.
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if "status_message" in data and not data.get('success', True):
            st.error(f"🚨 TMDB 서버 에러 응답: {data['status_message']}")
            return None
            
        results = data.get('results', [])
        if results:
            return results[0]
        else:
            return None
    except Exception as e:
        st.error(f"🚨 파이썬 통신 에러: {e}")
        return None

# --- UI ---
st.title("🧪 TMDB 순수 검색 & 에러 추적기")

if TMDB_API_KEY:
    st.info(f"🔑 현재 로드된 TMDB 토큰: {TMDB_API_KEY[:5]}...{TMDB_API_KEY[-3:]} (길이: {len(TMDB_API_KEY)})")
else:
    st.error("🔑 현재 로드된 TMDB 토큰이 없습니다!")

query = st.text_input("영화 제목을 입력하세요", key="test_query")

if query:
    with st.spinner("TMDB 검색 중..."):
        movie_data = search_tmdb_only(query)
        
    if movie_data:
        st.success(f"🎉 성공! TMDB에서 '{movie_data.get('title')}' 영화를 찾았습니다!")
        poster_path = movie_data.get('poster_path')
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=300)
    else:
        st.warning("결과가 없습니다. 에러 메시지를 확인해 주세요.")