import os
import webbrowser

class PromptBuilder:
    def _get_base_guideline(self):
        """MK 블로그의 공통 지침을 반환합니다."""
        return """
        [작성 지침]
        1. 어조 및 페르소나 (Tone of Voice):
            - 정중하고 친근한 경어체("~습니다", "~해요")를 사용하여 예의와 친근함을 동시에 갖추세요.
            - 확정적 표현 대신 조심스러운 분석("~이지 않을까 싶어요", "~라고 생각됩니다", "~인 듯 보이기도 하며")을 사용하여 독자의 공감을 유도하세요.
            - 전문 용어나 복잡한 내용은 정보 전달자로서 친절하게 풀어서 설명하세요.
            - 영화의 정서를 다룰 때는 서정적이고 감성적인 어휘("공허한 마음을 채워 줄 수 있는" 등)를 활용하여 분위기를 풍성하게 만드세요.

        2. 전체 분량 및 가독성 (Layout & Readability):
            - 정보의 밀도를 높여 공백 제외 1,500 ~ 2,500자 내외로 작성하세요.
            - 모바일 가독성을 위해 3~4줄마다 반드시 문단을 나누고(<p> 태그 활용), 문단 사이에 빈 줄(<p style="text-align: center;">&nbsp;</p>)을 삽입하여 숨통을 트여주세요.

        3. 포스팅 레이아웃 구조 (서론-본론-결론):
            - [최상단]: 시선 끄는 첫 문장(핵심 메시지나 강렬한 감상평)으로 시작하고, 바로 아래에 [제공되는 실제 이미지 HTML 코드]의 '메인 포스터' 코드를 그대로 붙여넣으세요. 스포일러가 포함된 경우 명확히 경고 문구를 작성하세요.
            - [서론]: 콘텐츠를 보게 된 계기, 영화의 기본 정보 요약, 포스팅의 목적(무엇을 짚어볼 것인지)을 명확히 밝히세요.
            - [본론]: H2, H3 태그를 활용하여 핵심 내용을 요약한 소제목으로 단락을 구분하세요. 복잡한 이유나 특징은 불렛 포인트(•, -)를 사용하여 요약하세요. 그리고 본문 중간의 적절한 위치에 [제공되는 실제 이미지 HTML 코드]의 '스틸컷' 코드를 그대로 붙여넣으세요.
            - [결론]: 전체적인 감상을 갈무리하며 나만의 한줄평과 별점을 직관적으로 제시하세요. "이런 분들께 추천해요"라며 타겟 독자를 명시하고, 영화 상세 정보(장르, 감독, 개봉일 등)를 이모지와 함께 리스트 형식으로 정리하세요. 

        4. 멀티미디어 및 이미지 가이드 (🚨 절대 준수):
            - 본문 최상단과 중간에는 반드시 하단에 제공된 [제공되는 실제 이미지 HTML 코드]를 1글자도 수정하지 말고 그대로 복사해서 삽입하세요.
            - 위 2장의 진짜 이미지를 모두 삽입한 후, 추가로 관람 인증샷 등이 들어갈 자리가 필요할 때만 기존처럼 가짜 박스(<p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{사진: 관련 장면 묘사}}</p>)를 사용하세요.

        5. SEO (검색 최적화):
            - 본문 서두와 제목에 메인 키워드를 자연스럽게 배치하되 과도한 반복은 피하세요.
            - 절대 본문 중간에 해시태그(#)를 넣지 마세요.
            - 글의 맨 마지막 영역에만 <p> 태그로 묶어서 연관 태그(영화 제목, 감독, 배우, 장르 등)를 5~10개 삽입하세요.

        출력 형식: 오직 HTML 본문 코드만 출력하세요. 맨 마지막 줄에 HTML 주석() 형식으로 클릭을 유도하는 매력적인 제목 5개를 제안하세요.
        """

    def _build_image_html(self, url, alt_text):
        """이미지 URL이 있으면 완성된 HTML 태그를 반환하고, 없으면 빈 문자열을 반환합니다."""
        if not url:
            return ""
        return f'<div style="text-align: center; margin: 25px 0;"><img src="{url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></div>'

    def build_preview_prompt(self, details, point, latest_news=""):
        base = self._get_base_guideline()
        title = details.get('title', '')
        
        # 파이썬에서 미리 완벽한 HTML 태그를 만들어 버립니다.
        poster_html = self._build_image_html(details.get('poster_url'), f"{title} 메인 포스터")
        backdrop_html = self._build_image_html(details.get('backdrop_url'), f"{title} 공식 스틸컷")

        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 아래 정보를 바탕으로 프리뷰 원고를 작성하세요.
        
        [영화 실제 데이터]
        - 제목: {title}
        - 개봉일: {details.get('release_date', '')}
        - 장르: {details.get('genres', '')}
        - 감독: {details.get('director', '')}
        - 출연: {details.get('actors', '')}
        - 줄거리: {details.get('overview', '')}
        
        [강조 포인트]
        - {point}

        [최신 네이버 뉴스 동향]
        {latest_news}
        
        [제공되는 실제 이미지 HTML 코드]
        - 메인 포스터 (최상단에 배치할 것): {poster_html if poster_html else '제공된 이미지 없음'}
        - 스틸컷 (본론 중간에 배치할 것): {backdrop_html if backdrop_html else '제공된 이미지 없음'}
        
        [특이사항]
        - 반드시 제공된 [영화 실제 데이터]를 바탕으로 작성하여 거짓 정보(할루시네이션)를 만들지 마세요.
        - [최신 네이버 뉴스 동향]의 내용을 본문에 반영하되, "기사에 따르면", "최근 뉴스에서" 같은 출처를 암시하는 단어는 절대 쓰지 마세요.
        
        {base}
        """

    def build_review_prompt(self, details, comment, latest_news=""):
        base = self._get_base_guideline()
        title = details.get('title', '')
        
        poster_html = self._build_image_html(details.get('poster_url'), f"{title} 메인 포스터")
        backdrop_html = self._build_image_html(details.get('backdrop_url'), f"{title} 공식 스틸컷")

        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 영화를 직접 관람한 후 작성하는 상세 리뷰 원고를 작성하세요.
        
        [영화 실제 데이터]
        - 제목: {title}
        - 개봉일: {details.get('release_date', '')}
        - 장르: {details.get('genres', '')}
        - 감독: {details.get('director', '')}
        - 출연: {details.get('actors', '')}
        - 줄거리: {details.get('overview', '')}
        
        [나의 주관적 감상평]
        {comment}

        [최신 네이버 뉴스 동향]
        {latest_news}
        
        [제공되는 실제 이미지 HTML 코드]
        - 메인 포스터 (최상단에 배치할 것): {poster_html if poster_html else '제공된 이미지 없음'}
        - 스틸컷 (본론 중간에 배치할 것): {backdrop_html if backdrop_html else '제공된 이미지 없음'}
        
        [특이사항]
        - 감상평에 담긴 저의 솔직한 감정을 본문에 자연스럽게 녹여내 주세요.
        - [최신 네이버 뉴스 동향]의 내용을 반영하되, "뉴스에서", "동향을 보면" 등의 표현은 절대 피하세요.
        
        {base}
        """

    def build_news_prompt(self, news_content):
        # ... (이하 기존과 동일) ...
        base = self._get_base_guideline()
        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 최신 영화 뉴스(기사)를 MK만의 시각으로 재해석한 포스팅을 작성하세요.
        
        [뉴스 원문 데이터]
        {news_content}
        
        [특이사항]
        - 단순히 기사를 요약하는 것이 아니라, 인플루언서로서 이 소식이 영화계나 팬들에게 어떤 의미가 있을지 의견을 덧붙여주세요.
        
        {base}
        """

    def display_in_browser(self, html_content, filename="mk_blog_preview.html"):
        file_path = os.path.abspath(filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n[알림] 결과물을 브라우저에서 확인합니다: {file_path}")
        webbrowser.open(f"file://{file_path}")