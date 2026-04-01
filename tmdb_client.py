import requests
import re

class TMDBClient:
    def __init__(self):
        # ⚠️ 본인의 키와 토큰을 넣으세요 (주석 금지)
        raw_api_key = "민규님의_API_키"
        raw_token = "민규님의_액세스_토큰"
        
        self.base_url = "https://api.themoviedb.org/3"
        
        # 보안 및 인코딩 에러 방지를 위해 영어/숫자만 남김
        self.api_key = re.sub(r'[^a-zA-Z0-9.]', '', raw_api_key)
        token = re.sub(r'[^a-zA-Z0-9.]', '', raw_token)
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    def search_movie(self, title):
        """영화 제목만으로 가장 유사한 결과 하나를 찾습니다."""
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
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