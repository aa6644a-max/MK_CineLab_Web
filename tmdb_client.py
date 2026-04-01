import requests
import os
import re
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        # 1. 웹 금고(secrets)에 있으면 가져오고, 없으면 로컬(.env)에서 가져옵니다.
        if "TMDB_API_KEY" in st.secrets:
            raw_key = st.secrets["TMDB_API_KEY"]
        else:
            raw_key = os.getenv("TMDB_API_KEY", "")

        # 🚨 2. 치명적 오류 방지: 만약 긴 토큰(eyJ...)이 들어왔거나 비어있으면 진짜 32자리 키로 강제 고정!
        if raw_key.startswith("eyJ") or not raw_key:
            raw_key = "ed303aad7e82e47159f48e850f45eecf"

        self.api_key = re.sub(r'[^a-zA-Z0-9]', '', str(raw_key))
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie(self, title, year=None):
        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        if year:
            params["primary_release_year"] = year

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for movie in results:
                    if movie.get('title') == title:
                        return movie
                return results[0] if results else None
        except Exception as e:
            print(f"TMDB Search Error: {e}")
            
        return None

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "language": "ko-KR", 
            "append_to_response": "credits"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                director = ""
                for crew in data.get("credits", {}).get("crew", []):
                    if crew.get("job") == "Director":
                        director = crew.get("name")
                        break
                
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "release_date": data.get("release_date"),
                    "director": director,
                    "overview": data.get("overview")
                }
        except Exception as e:
            print(f"TMDB Detail Error: {e}")
            
        return {}