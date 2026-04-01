import requests

class TMDBClient:
    def __init__(self):
        # ⚠️ 아래 값들에 한글 주석(# 어쩌구)을 절대 달지 마세요!
        self.api_key = "민규님의_API_키"
        self.base_url = "https://api.themoviedb.org/3"
        
        # 토큰을 변수에 담고 strip()으로 눈에 안 보이는 공백을 지웁니다.
        token = "민규님의_ACCESS_TOKEN"
        token = token.strip() 
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    def search_movie(self, title):
        """영화 제목으로 검색 (가장 심플한 방식)"""
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
        """영화 상세 정보 가져오기"""
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