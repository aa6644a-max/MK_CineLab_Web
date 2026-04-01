import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie_exact(self, title, year=None):
        search_url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "ko-KR",  # 한국어 결과 우선
            "region": "KR"        # 한국 개봉 데이터 기준
        }
        
        if year:
            params["primary_release_year"] = year

        response = requests.get(search_url, params=params)
        data = response.json()

        if not data.get('results'):
            return None

        # 정확도 향상을 위한 후처리: 제목이 완전히 일치하는 것 찾기
        for movie in data['results']:
            if movie['title'] == title:
                # 상세 정보(장르명 등)를 위해 한 번 더 조회하거나 그대로 반환
                return movie
        
        # 완전 일치가 없으면 가장 상단 결과 반환
        return data['results'][0]