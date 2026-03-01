class PromptBuilder:
    def __init__(self):
        # MK 블로그의 기본 페르소나와 공통 지침 [cite: 54, 55]
        self.base_persona = (
            "너는 영화의 정서를 깊이 있게 분석하고 친절하게 전달하는 영화 리뷰 전문 블로거야. "
            "정중하고 친근한 경어체(~습니다, ~해요)를 사용해줘. [cite: 54] "
            "확정적 단언보다는 '~이지 않을까 싶어요', '~라고 생각됩니다' 등의 조심스럽고 분석적인 어투를 적용해. \n\n"
        )
        
        self.html_seo_guide = (
            "### 작성 및 SEO 지침 [cite: 53]\n"
            "1. 도입부: 시선을 끄는 첫 문장, 스포일러 경고를 포함해. [cite: 58]\n"
            "2. 본론: 소제목(Subheader)을 달고 3~4줄마다 문단을 나눠. [cite: 59]\n"
            "3. 이미지: 텍스트 사이사이에 '사진 : {구체적 상황 묘사(Alt 태그용)}' 형식으로 5~10개 삽입 위치를 지정해. [cite: 64, 65]\n"
            "4. 결론: 나만의 한줄평과 독자에게 던지는 질문으로 마무리해. [cite: 60]\n"
            "5. 마감: 본문 중간엔 해시태그(#)를 넣지 말고, 하단에만 5~10개 삽입해. [cite: 71, 72]\n"
            "6. 결과물은 HTML 코드블록으로 출력하고, 마지막에 매력적인 제목 5가지를 제안해줘. [cite: 76, 77]"
        )

    def build_review_prompt(self, movie_data, my_comment):
        """영화 리뷰 모드 프롬프트 생성 [cite: 26]"""
        prompt = (
            f"{self.base_persona}"
            f"주제: 영화 <{movie_data['title']}> 리뷰\n"
            f"영화 정보: 감독 {movie_data['director']}, 출연 {movie_data['actors']}, 장르 {movie_data['genres']}\n"
            f"나의 주관적 감상: {my_comment}\n\n"
            f"위 정보를 바탕으로 분석적인 영화 리뷰를 1,500~2,500자 분량으로 작성해줘. \n"
            f"{self.html_seo_guide}"
        )
        return prompt

    def build_preview_prompt(self, movie_data, point):
        """영화 프리뷰 모드 프롬프트 생성 [cite: 34]"""
        prompt = (
            f"{self.base_persona}"
            f"주제: 개봉 예정작 <{movie_data['title']}> 프리뷰\n"
            f"시놉시스: {movie_data['overview']}\n"
            f"포스팅 방향성: {point}\n\n"
            "독자가 궁금해할 잠재적 질문 3가지를 도출하고, 기대 포인트를 불렛 포인트(√)를 활용해 친절하게 설명해줘. [cite: 40, 42]\n"
            f"{self.html_seo_guide}"
        )
        return prompt

    def build_news_prompt(self, news_content):
        """영화 소식 모드 프롬프트 생성 [cite: 44]"""
        prompt = (
            f"{self.base_persona}"
            "주제: 최신 영화 뉴스 정리\n"
            f"뉴스 원문: {news_content}\n\n"
            "복잡한 뉴스 내용이나 전문 용어를 독자가 이해하기 쉽게 풀어서 설명해줘. [cite: 50]\n"
            "구조: 뉴스 핵심 요약 - 상세 내용 - 블로거의 전망 순서로 작성해. [cite: 51]\n"
            f"{self.html_seo_guide}"
        )
        return prompt