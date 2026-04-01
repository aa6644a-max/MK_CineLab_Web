import requests

class TMDBClient:
    def __init__(self):
        # 1. API 키와 토큰에서 '한글 주석'을 완전히 제거하세요.
        # 잘못된 예: self.api_key = "abc123" # 내 키
        # 올바른 예: self.api_key = "abc123"
        
        self.api_key = "민규님의_API_KEY" 
        self.base_url = "https://api.themoviedb.org/3"
        
        # 2. 토큰 값을 변수에 담을 때도 주석 없이 순수하게 문자열만 넣으세요.
        token = "민규님의_ACCESS_TOKEN" 
        
        # 3. 헤더 구성 (문자열 결합 시 불필요한 공백이나 특수문자가 없어야 함)
        self.headers = {
            "Authorization": f"Bearer {token.strip()}",
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
            
        # 여기서 self.headers가 깨끗하지 않으면 에러가 발생합니다.
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