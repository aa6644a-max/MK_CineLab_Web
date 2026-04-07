import requests
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class NaverClient:
    def __init__(self):
        # 기본값은 빈 문자열로 설정
        self.client_id = ""
        self.client_secret = ""

        # 1. Streamlit 웹 금고(secrets)에서 먼저 시도
        try:
            # .get()을 쓰면 키가 없어도 에러(KeyError)가 나지 않고 빈 문자열을 반환합니다.
            self.client_id = st.secrets.get("NAVER_CLIENT_ID", "")
            self.client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
        except FileNotFoundError:
            # 로컬 환경 등 secrets.toml 파일이 아예 없는 경우 에러를 무시하고 넘어갑니다.
            pass

        # 2. 웹 금고에서 값을 못 가져왔다면(빈 문자열이라면) 로컬(.env)에서 가져옵니다.
        if not self.client_id or not self.client_secret:
            self.client_id = os.getenv("NAVER_CLIENT_ID", "")
            self.client_secret = os.getenv("NAVER_CLIENT_SECRET", "")

    def search_movie_news(self, movie_title, display=3):
        """영화 제목으로 네이버 뉴스를 검색하여 핵심 요약 텍스트를 반환합니다."""
        url = "https://openapi.naver.com/v1/search/news.json"
        
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        # 정확도순(sim)으로 최상위 기사 3개(display=3)만 가져옵니다.
        params = {
            "query": f"{movie_title} 영화",
            "display": display,
            "sort": "sim"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                items = response.json().get('items', [])
                news_texts = []
                
                for item in items:
                    # 네이버는 검색어에 <b> 태그를 붙여서 주므로 깔끔하게 제거합니다.
                    title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                    desc = item['description'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                    news_texts.append(f"📰 기사 제목: {title}\n주요 내용: {desc}\n")
                
                return "\n".join(news_texts) if news_texts else "관련 최신 뉴스가 없습니다."
                
        except Exception as e:
            print(f"네이버 API 에러 발생: {e}")
            
        return "뉴스 검색에 실패했습니다."
            
    def search_local_place(self, query, display=5):
        """키워드로 네이버 지역(장소)을 검색하여 결과를 반환합니다."""
        url = "https://openapi.naver.com/v1/search/local.json"
        
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        params = {
            "query": query,
            "display": display
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"네이버 API 에러 발생: 상태 코드 {response.status_code}"}
                
        except Exception as e:
            return {"error": f"지역 검색 실패: {e}"}