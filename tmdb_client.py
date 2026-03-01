import os
import requests
from dotenv import load_dotenv

# .env 파일에 저장된 API 키를 불러옵니다 [cite: 10, 94]
load_dotenv()

class TMDBClient:
    def __init__(self):
        # 가이드북 권장사항: v4 Read Access Token을 사용합니다 [cite: 105]
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json;charset=utf-8"
        }

    def search_movie(self, title):
        """영화 제목으로 검색하여 첫 번째 영화의 정보를 가져옵니다 [cite: 31, 39]"""
        url = f"{self.base_url}/search/movie"
        params = {"query": title, "language": "ko-KR"}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            results = response.json().get('results')
            return results[0] if results else None
        return None

    def get_movie_details(self, movie_id):
        """영화 ID를 이용해 상세 정보(감독, 출연진 등)를 수집합니다 [cite: 31, 39]"""
        url = f"{self.base_url}/movie/{movie_id}"
        # 출연진(credits) 정보를 포함하여 요청합니다
        params = {"language": "ko-KR", "append_to_response": "credits"}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # 감독 정보 추출
            director = next((m['name'] for m in data['credits']['crew'] if m['job'] == 'Director'), "정보 없음")
            # 출연진 상위 3명 추출
            actors = [m['name'] for m in data['credits']['cast'][:3]]
            
            return {
                "title": data.get("title"),
                "release_date": data.get("release_date"),
                "genres": [g['name'] for g in data.get("genres", [])],
                "director": director,
                "actors": ", ".join(actors),
                "overview": data.get("overview")
            }
        return None