import requests
import re

class TMDBClient:
    def __init__(self):
        # 1. 여기에 본인의 키와 토큰을 넣으세요.
        # 주의: 주석(#)을 달지 말고 값만 넣으세요.
        raw_api_key = "여기에_API_키"
        raw_token = "여기에_액세스_토큰"
        
        self.base_url = "https://api.themoviedb.org/3"
        
        # 2. 토큰에서 영어, 숫자, 마침표(.)를 제외한 모든 문자(한글 포함)를 강제로 제거
        # latin-1 에러를 방지하는 가장 확실한 방법입니다.
        self.api_key = re.sub(r'[^a-zA-Z0-9.]', '', raw_api_key)
        token = re.sub(r'[^a-zA-Z0-9.]', '', raw_token)
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    def search_movie(self, title, year=None, director_name=None):
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        if year:
            params["primary_release_year"] = year
            
        # ❱ 이 줄에서 터졌던 에러를 위에서 정제한 headers가 해결해줍니다.
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if not results:
                return None
            
            if director_name:
                search_dir = director_name.replace(" ", "").lower()
                for movie in results[:5]:
                    details = self.get_movie_details(movie['id'])
                    target_dir = details.get('director', '').replace(" ", "").lower()
                    if search_dir in target_dir:
                        return movie
            
            for movie in results:
                if movie.get('title') == title:
                    return movie
            return results[0]
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