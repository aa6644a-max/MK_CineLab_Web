import requests

class TMDBClient:
    def __init__(self):
        # 1. API 키 (따옴표 안에 영어/숫자만 딱 넣으세요. 주석 절대 금지!)
        self.api_key = "민규님의_API_키" 
        self.base_url = "https://api.themoviedb.org/3"
        
        # 2. 액세스 토큰 (여기도 주석 절대 금지!)
        token = "민규님의_ACCESS_TOKEN"
        
        # 3. 헤더 구성 (문자열 앞뒤 공백을 강제로 제거해서 latin-1 에러 방지)
        token = str(token).strip()
        self.headers = {
            "Authorization": "Bearer " + token,
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
        # 32번째 줄: headers가 완전히 정제된 상태로 요청을 보냅니다.
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