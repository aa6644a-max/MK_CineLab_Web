import sys
from tmdb_client import TMDBClient
from gemini_client import GeminiClient

def main():
    print("🎬 [MK CINELAB] 자동 포스팅 생성기를 시작합니다.")
    print("-" * 40)

    # 1. 클라이언트 초기화
    tmdb = TMDBClient()
    gemini = GeminiClient()

    # 2. 사용자로부터 영화 정보 입력받기
    movie_title = input("📝 리뷰를 작성할 영화 제목을 입력하세요: ").strip()
    movie_year = input("📅 개봉 연도를 입력하세요 (모르면 엔터): ").strip()
    
    if not movie_title:
        print("❌ 영화 제목은 필수입니다.")
        return

    # 연도 입력이 있으면 숫자로 변환, 없으면 None
    year_val = int(movie_year) if movie_year.isdigit() else None

    # 3. TMDB에서 영화 검색
    print(f"\n🔍 TMDB에서 '{movie_title}' 정보를 찾는 중...")
    search_result = tmdb.search_movie(movie_title, year=year_val)

    if not search_result:
        print(f"❓ '{movie_title}'에 대한 검색 결과가 없습니다. 제목을 확인해주세요.")
        return

    # 4. 상세 정보 수집 (ID를 통해 감독, 배우, 줄거리 등 가져오기)
    movie_id = search_result['id']
    details = tmdb.get_movie_details(movie_id)
    
    if not details:
        print("❌ 상세 정보를 가져오는데 실패했습니다.")
        return

    print(f"✅ 확인된 영화: {details['title']} ({details['release_date']})")
    print(f"🎬 감독: {details['director']} | 주연: {details['actors']}")

    # 5. Gemini용 프롬프트 구성 (MK CINELAB 스타일 주입)
    # 팁: TMDB의 실제 데이터를 프롬프트에 넣어 할루시네이션(거짓말)을 방지합니다.
    prompt = f"""
    당신은 네이버 영화 인플루언서이자 'MK CINELAB'을 운영하는 전문 리뷰어 'MK'입니다.
    아래의 실제 영화 정보를 바탕으로 독창적이고 깊이 있는 블로그 리뷰 포스팅을 작성하세요.

    [영화 데이터]
    - 제목: {details['title']}
    - 개봉일: {details['release_date']}
    - 장르: {', '.join(details['genres'])}
    - 감독: {details['director']}
    - 출연: {details['actors']}
    - 줄거리: {details['overview']}

    [작성 규칙]
    1. 톤앤매너: 분석적이면서도 감성적인 문체를 사용하세요. (민규 님의 평소 스타일)
    2. 구조: 
       - 서론: 영화를 보게 된 계기나 첫인상
       - 본론: 영화가 던지는 철학적 질문(인간의 본질, 사회적 메시지 등)과 연출/연기 평
       - 결론: MK의 한줄평과 별점(5점 만점), 추천 대상
    3. 형식: HTML 태그를 적절히 사용하고, 이미지가 들어갈 자리는 '{{{{사진: 설명}}}}'으로 표시하세요.
    4. 반드시 제공된 '줄거리' 내용을 기반으로 작성하여 사실 관계를 유지하세요.
    """

    # 6. 블로그 포스팅 생성
    print("\n🤖 Gemini가 MK CINELAB 스타일로 글을 쓰는 중입니다. 잠시만 기다려주세요...")
    try:
        final_post = gemini.generate_post(prompt)
        
        print("\n" + "="*50)
        print("✨ 포스팅 생성 완료!")
        print("="*50 + "\n")
        print(final_post)
        
        # 7. (선택사항) 파일로 저장
        filename = f"review_{details['title'].replace(' ', '_')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_post)
        print(f"\n💾 결과가 '{filename}'으로 저장되었습니다.")

    except Exception as e:
        print(f"❌ 포스팅 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    main()