import requests
import re

class TMDBClient:
    def __init__(self):
        # 1. 아래 값들에 절대 한글 주석을 달지 마세요.
        # 따옴표 안에 순수하게 키와 토큰만 넣으세요.
        raw_api_key = "민규님의_API_키"
        raw_token = "민규님의_액세스_토큰"
        
        self.base_url = "https://api.themoviedb.org/3"
        
        # 2. 정규표현식을 사용해 영어, 숫자, 마침표(.) 외의 모든 문자(한글 포함) 강제 제거
        # latin-1 인코딩 에러를 방지하는 가장 확실한 방패입니다.
        clean_api_key = re.sub(r'[^a-zA-Z0-9.]', '', raw_api_key)
        clean_token = re.sub(r'[^a-zA-Z0-9.]', '', raw_token)
        
        self.api_key = clean_api_key
        self.headers = {
            "Authorization": f"Bearer {clean_token}",
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
            
        # 32번째 줄: 이제 headers가 정제되어 에러가 나지 않습니다.
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