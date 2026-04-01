import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        # 1. API 키와 토큰을 직접 문자열로 넣으세요 (에러 방지용)
        raw_token = "여기에_민규님의_TMDB_액세스_토큰_입력"
        
        # 2. 유니코드/latin-1 에러 원천 차단 (영어, 숫자, 점만 남김)
        token = re.sub(r'[^a-zA-Z0-9.]', '', str(raw_token))
        
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    def search_movie(self, title, year=None):
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        if year:
            params["primary_release_year"] = year

        # 에러가 나던 지점: 정제된 token을 쓰므로 이제 안전합니다.
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return results[0] if results else None
        return None

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"language": "ko-KR", "append_to_response": "credits"}
        response = requests.get(url, headers=self.headers, params=params)
        
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
        return {}