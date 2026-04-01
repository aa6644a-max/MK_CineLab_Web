import requests

class TMDBClient:
    def __init__(self):
        # 민규님의 실제 API 키와 토큰을 여기에 꼭 넣어주세요!
        self.api_key = "여기에_API_키"
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": "Bearer 여기에_액세스_토큰",
            "accept": "application/json"
        }

    # 핵심: 파라미터에 director_name=None 이 반드시 포함되어야 합니다.
    def search_movie(self, title, year=None, director_name=None):
        """제목, 연도, 감독명을 조합해 최적의 영화를 찾습니다."""
        url = f"{self.base_url}/search/movie"
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
            
            # 1. 감독명 필터링 로직
            if director_name:
                search_dir = director_name.replace(" ", "").lower()
                for movie in results[:5]:  # 상위 5개 결과 대조
                    details = self.get_movie_details(movie['id'])
                    target_dir = details.get('director', '').replace(" ", "").lower()
                    if search_dir in target_dir:
                        return movie
            
            # 2. 제목 매칭 우선순위
            for movie in results:
                if movie.get('title') == title:
                    return movie
            return results[0]
        return None

    def get_movie_details(self, movie_id):
        """영화 상세 및 감독 정보를 가져옵니다."""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"language": "ko-KR", "append_to_response": "credits"}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            director = ""
            # 감독(Director) 찾기 로직
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