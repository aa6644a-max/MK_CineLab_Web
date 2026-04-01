import requests
import re

class TMDBClient:
    def __init__(self):
        # ⚠️ 아래 따옴표 안에 키와 토큰만 넣으세요. (주석은 절대 달지 마세요!)
        raw_api_key = "민규님의_API_키"
        raw_token = "민규님의_ACCESS_TOKEN"
        
        self.base_url = "https://api.themoviedb.org/3"
        
        # 1. 정규표현식으로 영어, 숫자, 마침표(.) 외의 모든 문자(한글 포함) 강제 제거
        # latin-1 에러를 방지하는 가장 강력한 보호막입니다.
        self.api_key = re.sub(r'[^a-zA-Z0-9.]', '', str(raw_api_key))
        token = re.sub(r'[^a-zA-Z0-9.]', '', str(raw_token))
        
        # 2. 깨끗해진 토큰으로 헤더 구성
        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    def search_movie(self, title):
        """영화 제목만으로 검색하는 심플 모드"""
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        # 32번째 줄: 이제 headers가 완벽하게 깨끗해서 에러가 나지 않습니다.
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