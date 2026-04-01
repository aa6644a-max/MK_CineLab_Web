import requests

class TMDBClient:
    def __init__(self):
        # 본인의 API 키와 헤더 설정을 여기에 유지하세요
        self.api_key = "본인의_API_키" 
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer 본인의_액세스_토큰",
            "accept": "application/json"
        }

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
            
            # 1. 감독명 필터링이 필요한 경우
            if director_name:
                director_name_clean = director_name.replace(" ", "").lower()
                for movie in results[:5]:  # 상위 5개 검색 결과 확인
                    details = self.get_movie_details(movie['id'])
                    # get_movie_details에서 반환하는 'director' 키값을 확인
                    target_director = details.get('director', '').replace(" ", "").lower()
                    
                    if director_name_clean in target_director:
                        return movie
            
            # 2. 감독명이 없거나 일치하는 게 없으면 제목 매칭 우선
            for movie in results:
                if movie.get('title') == title:
                    return movie
            return results[0]
        return None

    def get_movie_details(self, movie_id):
        """영화 상세 정보 및 감독 정보를 가져옵니다."""
        # 기존에 작성하신 get_movie_details 코드를 여기에 유지하세요.
        # 감독 정보를 'director' 키에 담아 반환해야 위 search_movie가 작동합니다.
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"language": "ko-KR", "append_to_response": "credits"}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # 감독 찾기 로직
            director = ""
            credits = data.get("credits", {})
            for crew in credits.get("crew", []):
                if crew.get("job") == "Director":
                    director = crew.get("name")
                    break
            
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "release_date": data.get("release_date"),
                "director": director,
                "overview": data.get("overview"),
                "poster_path": data.get("poster_path")
            }
        return {}