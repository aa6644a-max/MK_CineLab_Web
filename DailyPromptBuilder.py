from datetime import datetime

class DailyPromptBuilder:
    def __init__(self):
        self.current_date = datetime.now()
        self.current_month = self.current_date.month
        self.current_year = self.current_date.year
        self.season = "봄" if 3 <= self.current_month <= 5 else "여름" if 6 <= self.current_month <= 8 else "가을" if 9 <= self.current_month <= 11 else "겨울"

    def build_pdf_summary_prompt(self, pdf_text, user_context, reference_posts=""):
        """
        노트북LM 방식: 외부 검색 없이 오직 PDF와 사용자 입력값으로만 작성
        """
        time_context = f"현재 시점은 {self.current_year}년 {self.current_month}월({self.season})입니다."
        
        return f"""
        당신은 네이버 블로거 'MK'입니다. 
        제공된 [원본 데이터(PDF)]를 바탕으로, 당신만의 통찰력과 감성을 더해 블로그 포스팅을 작성하세요.
        
        [🚨 초강력 지침: 노트북LM 모드]
        1. 외부 영화 DB(TMDB)나 뉴스 검색 결과를 절대 사용하지 마세요.
        2. 오직 아래 제공된 [원본 데이터(PDF)]에 기술된 팩트만을 바탕으로 내용을 구성하세요.
        3. [나의 상황 및 기록 목적]을 글의 전반적인 감정선으로 삼으세요.

        [원본 데이터 (PDF 추출 텍스트)]
        {pdf_text}

        [나의 상황 및 기록 목적]
        {user_context}

        [작성 지침]
        {time_context}
        - 어조: 정중하고 다정한 경어체. (~해요, ~죠, ~생각됩니다)
        - 구성: 서론(계기) - 본론(PDF 내용 분석 및 MK의 생각) - 결론(마무리 감상)
        - 가독성: 3~4줄마다 <p> 태그 문단 나누기 및 빈 줄(<p style="text-align: center;">&nbsp;</p>) 삽입.
        
        [말투 레퍼런스 (학습용)]
        {reference_posts}

        [레이아웃 가이드]
        - 글의 흐름상 사진이 들어가면 좋을 위치에 아래 코드를 삽입하세요.
          <p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{{{사진: 문맥에 맞는 이미지 설명}}}}</p>

        출력 형식: 오직 HTML 본문 코드만 출력하세요. (마지막에 주석으로 제목 3개 제안)
        """