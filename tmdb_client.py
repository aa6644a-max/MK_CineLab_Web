import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class TMDBClient:
    def __init__(self):
        # API Key (Read Access Token) 설정
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json;charset=utf-8"
        }

    def search_movie(self, title, year=None):
        """
        영화 제목으로 검색하여 최적의 결과를 반환합니다.
        year 인자를 추가하여 검색 정확도를 높일 수 있습니다.
        """
        url = f"{self.base_url}/search/movie"
        # region=KR을 추가하면 한국 개봉 데이터 기준으로 더 정확해집니다.
        params = {
            "query": title, 
            "language": "ko-KR", 
            "region": "KR"
        }
        
        if year:
            params["primary_release_year"] = year
            
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if not results:
                return None
            
            # 1순위: 제목이 토씨 하나 안 틀리고 정확히 일치하는 영화 찾기
            for movie in results:
                if movie.get('title') == title:
                    return movie
            
            # 2순위: 일치하는 게 없으면 가장 관련성 높은 첫 번째 결과 반환
            return results[0]
            
        return None

    def get_movie_details(self, movie_id):
        """영화 ID를 이용해 상세 정보(감독, 출연진 등)를 수집합니다."""
        url = f"{self.base_url}/movie/{movie_id}"
        # 출연진(credits) 정보를 포함하여 상세 데이터 요청
        params = {"language": "ko-KR", "append_to_response": "credits"}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # 감독(Director) 정보 추출
            credits = data.get('credits', {})
            crew = credits.get('crew', [])
            director = next((m['name'] for m in crew if m['job'] == 'Director'), "정보 없음")
            
            # 출연진(Cast) 상위 3명 추출
            cast = credits.get('cast', [])
            actors = [m['name'] for m in cast[:3]]
            
            # 블로그 포스팅에 필요한 핵심 데이터 정리
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "release_date": data.get("release_date"),
                "genres": [g['name'] for g in data.get("genres", [])],
                "director": director,
                "actors": ", ".join(actors),
                "overview": data.get("overview"),
                "poster_path": data.get("poster_path"), # 포스터 이미지 경로 추가
                "runtime": data.get("runtime")          # 러닝타임 추가
            }
        return None