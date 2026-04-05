import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MK CINELAB - TMDB 테스트", page_icon="🧪")

TMDB_API_KEY = (st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY") or "").strip().strip('\'"')

def search_tmdb_only(query):
    # 1단계: 키가 제대로 들어왔는지 확인
    if not TMDB_API_KEY:
        st.error("❌ 코드에서 TMDB API 키를 전혀 찾지 못하고 있습니다! (.env 또는 Secrets 설정 확인 필요)")
        return None

    # 2단계: 한글 깨짐을 방지하기 위해 params 딕셔너리 사용
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ko-KR"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # 3단계: TMDB 서버가 보내는 '진짜' 에러 메시지 확인
        if "status_message" in data:
            st.error(f"🚨 TMDB 서버 에러 응답: {data['status_message']}")
            st.caption("주로 API 키가 틀렸거나 만료되었을 때 이 에러가 뜹니다.")
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

# 디버깅을 위해 현재 불러온 키의 일부분만 모자이크해서 보여주기
if TMDB_API_KEY:
    st.info(f"🔑 현재 로드된 TMDB 키: {TMDB_API_KEY[:5]}...{TMDB_API_KEY[-3:]} (길이: {len(TMDB_API_KEY)})")
else:
    st.error("🔑 현재 로드된 TMDB 키가 없습니다!")

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
        st.warning("결과가 없습니다. 위에 붉은색으로 뜬 에러 메시지를 확인해 주세요.")