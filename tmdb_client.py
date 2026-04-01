import requests

class TMDBClient:
    def __init__(self):
        # ⚠️ 여기 따옴표 안에 민규님의 API 키와 토큰을 '직접' 넣으세요.
        # ⚠️ 값 뒤에 한글 주석(# 어쩌구)이 붙어있다면 반드시 지워주세요!
        self.api_key = "민규님의_API_키"
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": "Bearer 민규님의_액세스_토큰",
            "accept": "application/json"
        }

    def search_movie(self, title):
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        # 이 줄에서 에러가 난다면 100% 위 Authorization의 토큰 값에 한글/공백이 섞인 겁니다.
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