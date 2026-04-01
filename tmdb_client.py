import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        # 💡 숨어있던 민규님의 진짜 TMDB API 키(v3)를 넣습니다!
        raw_key = "ed303aad7e82e47159f48e850f45eecf"
        self.api_key = re.sub(r'[^a-zA-Z0-9]', '', str(raw_key))
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie(self, title, year=None):
        url = f"{self.base_url}/search/movie"
        # 💡 핵심: headers 없이 params만 사용해 인코딩 에러를 100% 방지합니다.
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
                # 정확도 향상: 제목이 완전히 일치하는 영화 우선 찾기
                for movie in results:
                    if movie.get('title') == title:
                        return movie
                # 완전 일치가 없으면 검색 결과의 첫 번째 반환
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