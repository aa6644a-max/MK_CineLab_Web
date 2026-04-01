# tmdb_client.py

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
            
            # 감독명 필터링이 필요한 경우
            if director_name:
                director_name = director_name.replace(" ", "").lower()
                for movie in results[:5]:  # 상위 5개 검색 결과 확인
                    # 각 영화의 상세 정보(감독 확인용)를 가져옴
                    details = self.get_movie_details(movie['id'])
                    target_director = details.get('director', '').replace(" ", "").lower()
                    
                    if director_name in target_director:
                        return movie  # 감독명이 일치하면 해당 영화 반환
            
            # 감독명이 없거나 일치하는 게 없으면 제목 매칭 우선
            for movie in results:
                if movie.get('title') == title:
                    return movie
            return results[0]
        return None