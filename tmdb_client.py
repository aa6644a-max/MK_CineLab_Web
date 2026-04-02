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
            # 💡 수정: images 탭을 추가로 요청하고, 언어 필터를 넓혀서 스틸컷을 다 가져옵니다.
            "append_to_response": "credits,images",
            "include_image_language": "ko,en,null"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # 감독, 배우, 장르 추출
                director = ""
                for crew in data.get("credits", {}).get("crew", []):
                    if crew.get("job") == "Director":
                        director = crew.get("name")
                        break
                
                actors = [cast.get("name") for cast in data.get("credits", {}).get("cast", [])[:3]]
                actors_str = ", ".join(actors) if actors else "정보 없음"
                
                genres = [g.get("name") for g in data.get("genres", [])]
                genres_str = ", ".join(genres) if genres else "정보 없음"

                # 🖼️ 포스터 추출
                poster_path = data.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

                # 🖼️ 스틸컷(Backdrops) 여러 장 추출 (최대 10장)
                backdrops = data.get("images", {}).get("backdrops", [])
                backdrop_urls = []
                for bd in backdrops[:10]:
                    if bd.get("file_path"):
                        backdrop_urls.append(f"https://image.tmdb.org/t/p/original{bd['file_path']}")
                
                # 만약 이미지가 하나도 없다면 기본 backdrop이라도 가져오기 시도
                if not backdrop_urls and data.get("backdrop_path"):
                    backdrop_urls.append(f"https://image.tmdb.org/t/p/original{data.get('backdrop_path')}")
                
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "release_date": data.get("release_date", "정보 없음"),
                    "director": director if director else "정보 없음",
                    "actors": actors_str,
                    "genres": genres_str,
                    "overview": data.get("overview") if data.get("overview") else "TMDB에 등록된 공식 줄거리가 없습니다.",
                    "poster_url": poster_url,
                    "backdrop_urls": backdrop_urls # 이제 URL이 여러 개 담긴 리스트(List)가 됩니다!
                }
        except Exception as e:
            print(f"TMDB Detail Error: {e}")
            
        return {}