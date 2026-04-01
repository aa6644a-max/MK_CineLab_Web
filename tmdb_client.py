import requests

class TMDBClient:
    def __init__(self):
        # ⚠️ 중요: 아래 값들에 한글 주석을 달지 마세요.
        # 토큰을 따옴표("") 안에 공백 없이 정확히 붙여넣으세요.
        self.api_key = "여기에_API_키_입력" 
        self.base_url = "https://api.themoviedb.org/3"
        
        # 'Bearer ' 다음에 한 칸만 띄우고 바로 토큰이 와야 합니다.
        access_token = "여기에_액세스_토큰_입력"
        
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json"
        }

    def search_movie(self, title, year=None, director_name=None):
        """제목, 연도, 감독명을 조합해 최적의 영화를 찾습니다."""
        url = f"{self.base_url}/search/movie"
        
        # 한글 검색어는 requests가 알아서 인코딩해주지만, 확실히 하기 위해 params 구성
        params = {
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        if year:
            params["primary_release_year"] = year
            
        # 에러가 발생했던 지점입니다. headers가 깨끗해야 합니다.
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