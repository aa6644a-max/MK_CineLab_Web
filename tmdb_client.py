import requests
import os
import re
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        # 1. 웹 금고(secrets)에 있으면 가져오고, 없으면 로컬(.env)에서 가져옵니다.
        if "TMDB_API_KEY" in st.secrets:
            raw_key = st.secrets["TMDB_API_KEY"]
        else:
            raw_key = os.getenv("TMDB_API_KEY", "")

        # 🚨 2. 치명적 오류 방지: 만약 긴 토큰(eyJ...)이 들어왔거나 비어있으면 진짜 32자리 키로 강제 고정!
        if raw_key.startswith("eyJ") or not raw_key:
            raw_key = "ed303aad7e82e47159f48e850f45eecf"

        self.api_key = re.sub(r'[^a-zA-Z0-9]', '', str(raw_key))
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie(self, title, year=None):
        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "ko-KR",
            "region": "KR"
        }
        if year:
            params["primary_release_year"] = year

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for movie in results:
                    if movie.get('title') == title:
                        return movie
                return results[0] if results else None
        except Exception as e:
            print(f"TMDB Search Error: {e}")
            
        return None

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "language": "ko-KR", 
            # 💡 수정: images 탭을 추가로 요청하고, 언어 필터를 넓혀서 스틸컷을 다 가져옵니다.
            "append_to_response": "credits,images",
            "include_image_language": "ko,en,null"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # 감독, 배우, 장르 추출
                director = ""
                for crew in data.get("credits", {}).get("crew", []):
                    if crew.get("job") == "Director":
                        director = crew.get("name")
                        break
                
                actors = [cast.get("name") for cast in data.get("credits", {}).get("cast", [])[:3]]
                actors_str = ", ".join(actors) if actors else "정보 없음"
                
                genres = [g.get("name") for g in data.get("genres", [])]
                genres_str = ", ".join(genres) if genres else "정보 없음"

                # 💡 핵심 추가: 리스트 포스팅을 위한 '원제'와 '제작 국가' 추출
                original_title = data.get("original_title", "정보 없음")
                countries = [c.get("name") for c in data.get("production_countries", [])]
                country_str = ", ".join(countries) if countries else "정보 없음"

                # 🖼️ 포스터 추출
                poster_path = data.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

                # 🖼️ 스틸컷(Backdrops) 여러 장 추출 (최대 10장)
                backdrops = data.get("images", {}).get("backdrops", [])
                backdrop_urls = []
                for bd in backdrops[:10]:
                    if bd.get("file_path"):
                        backdrop_urls.append(f"https://image.tmdb.org/t/p/original{bd['file_path']}")
                
                # 만약 이미지가 하나도 없다면 기본 backdrop이라도 가져오기 시도
                if not backdrop_urls and data.get("backdrop_path"):
                    backdrop_urls.append(f"https://image.tmdb.org/t/p/original{data.get('backdrop_path')}")
                
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "original_title": original_title, # 새로 추가됨!
                    "country": country_str,           # 새로 추가됨!
                    "release_date": data.get("release_date", "정보 없음"),
                    "director": director if director else "정보 없음",
                    "actors": actors_str,
                    "genres": genres_str,
                    "overview": data.get("overview") if data.get("overview") else "TMDB에 등록된 공식 줄거리가 없습니다.",
                    "poster_url": poster_url,
                    "backdrop_urls": backdrop_urls
                }
        except Exception as e:
            print(f"TMDB Detail Error: {e}")
            
        return {}

    def get_weekly_trending(self, limit=6):
        url = f"{self.base_url}/trending/movie/week"
        params = {"api_key": self.api_key, "language": "ko-KR"}
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                results = res.json().get("results", [])[:limit]
                return [
                    {
                        "id": m.get("id"),
                        "title": m.get("title") or m.get("name", ""),
                        "release_date": (m.get("release_date") or "")[:4],
                        "vote_average": round(m.get("vote_average", 0), 1),
                        "overview": (m.get("overview") or "")[:80],
                        "poster_url": f"https://image.tmdb.org/t/p/w342{m['poster_path']}" if m.get("poster_path") else "",
                    }
                    for m in results
                ]
        except Exception as e:
            print(f"TMDB Trending Error: {e}")
        return []

    def search_tv(self, title):
        url = f"{self.base_url}/search/tv"
        params = {"api_key": self.api_key, "query": title, "language": "ko-KR"}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for item in results:
                    if item.get('name') == title:
                        return item
                return results[0] if results else None
        except Exception as e:
            print(f"TMDB TV Search Error: {e}")
        return None

    def get_tv_details(self, tv_id):
        url = f"{self.base_url}/tv/{tv_id}"
        params = {
            "api_key": self.api_key,
            "language": "ko-KR",
            "append_to_response": "credits,images",
            "include_image_language": "ko,en,null"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                runtimes = data.get("episode_run_time", [])
                avg_runtime = runtimes[0] if runtimes else 24
                total_episodes = data.get("number_of_episodes", 0)
                total_minutes = total_episodes * avg_runtime
                total_hours, remaining_mins = divmod(total_minutes, 60)
                if total_hours > 0:
                    total_time_str = f"{total_hours}시간 {remaining_mins}분" if remaining_mins else f"{total_hours}시간"
                else:
                    total_time_str = f"{total_minutes}분"

                genres = [g.get("name") for g in data.get("genres", [])]
                countries = [c.get("name") for c in data.get("production_countries", [])]
                cast = [c.get("name") for c in data.get("credits", {}).get("cast", [])[:3]]

                poster_path = data.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

                backdrops = data.get("images", {}).get("backdrops", [])
                backdrop_urls = [f"https://image.tmdb.org/t/p/original{bd['file_path']}"
                                 for bd in backdrops[:5] if bd.get("file_path")]
                if not backdrop_urls and data.get("backdrop_path"):
                    backdrop_urls.append(f"https://image.tmdb.org/t/p/original{data.get('backdrop_path')}")

                return {
                    "id": data.get("id"),
                    "title": data.get("name"),
                    "original_title": data.get("original_name", "정보 없음"),
                    "country": ", ".join(countries) if countries else "정보 없음",
                    "first_air_date": data.get("first_air_date", "정보 없음"),
                    "number_of_episodes": total_episodes,
                    "number_of_seasons": data.get("number_of_seasons", 1),
                    "episode_runtime": avg_runtime,
                    "total_watch_time": total_time_str,
                    "genres": ", ".join(genres) if genres else "정보 없음",
                    "overview": data.get("overview") or "TMDB에 등록된 공식 줄거리가 없습니다.",
                    "cast": ", ".join(cast) if cast else "정보 없음",
                    "poster_url": poster_url,
                    "backdrop_urls": backdrop_urls
                }
        except Exception as e:
            print(f"TMDB TV Detail Error: {e}")
        return {}