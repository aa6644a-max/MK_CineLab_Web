import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        # 환경변수에서 API 키를 가져옵니다. 
        # (만약 .env 파일 설정이 어렵다면, os.getenv(...) 부분을 지우고 "민규님의_API_키"를 직접 문자열로 넣으셔도 됩니다.)
        self.api_key = os.getenv("TMDB_API_KEY", "")
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie(self, title, year=None):
        url = f"{self.base_url}/search/movie"
        
        # 💡 핵심: headers를 아예 안 씁니다! params에 api_key를 직접 넣습니다.
        params = {
            "api_key": self.api_key.strip(),
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        
        if year:
            params["primary_release_year"] = year

        # headers=self.headers 부분이 삭제되었습니다. 에러 원천 차단!
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return results[0] if results else None
        return None

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}"
        
        # 💡 여기도 마찬가지로 params에 api_key를 넣습니다.
        params = {
            "api_key": self.api_key.strip(),
            "language": "ko-KR", 
            "append_to_response": "credits"
        }
        
        response = requests.get(url, params=params)
        
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