import requests

class TMDBClient:
    def __init__(self):
        # ⚠️ 아래 큰따옴표("") 안에 한글이 절대 없어야 합니다.
        # ⚠️ Bearer 뒤에 한글 주석을 달지 마세요.
        
        # 1. API 키 입력
        self.api_key = "민규님의_TMDB_API_KEY"
        self.base_url = "https://api.themoviedb.org/3"
        
        # 2. 액세스 토큰 입력 (주석 없이 값만 딱 넣으세요)
        token = "민규님의_ACCESS_TOKEN"
        
        # 3. 헤더 구성 (strip()으로 앞뒤 공백까지 완벽 제거)
        clean_token = token.strip()
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
            
        # ❱ 이 줄에서 에러가 났던 겁니다. headers가 순수한 영어/숫자여야 합니다.
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