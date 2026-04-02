import os
import webbrowser

class PromptBuilder:
    def _get_base_guideline(self):
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
            - [최상단]: 시선 끄는 첫 문장으로 시작하고, 바로 아래에 [메인 포스터] HTML 코드를 삽입하세요. 스포일러 경고 문구도 잊지 마세요.
            - [서론]: 콘텐츠를 보게 된 계기나 첫인상을 적고, 그 직후(서론 중간)에 [관람 인증샷] HTML 코드를 전체 글의 두 번째 이미지로 자연스럽게 삽입하세요. 그 후 영화의 기본 정보 요약, 포스팅 목적을 밝히세요.
            - [본론]: H2, H3 태그를 활용해 소제목으로 단락을 구분하세요. 내용 흐름에 맞게 아래 제공된 [스틸컷 1] 부터 마지막 스틸컷까지의 HTML 코드를 문단 사이사이에 전부 다 빠짐없이 골고루 흩뿌려서 모두 삽입하세요.
            - [결론]: 전체적인 감상을 갈무리하며 나만의 한줄평과 별점을 직관적으로 제시하세요.

        4. 멀티미디어 및 이미지 가이드 (🚨 절대 준수 사항):
            - 하단에 제공되는 이미지 HTML 코드 목록([메인 포스터], [관람 인증샷], [스틸컷 1~N개]) 전체를 무조건 한 번씩 본문에 1글자도 수정하지 말고 그대로 복사해서 배치해야 합니다.
            - 제미나이 임의로 이미지 태그를 줄이거나 생략하지 마세요. 제공된 코드는 반드시 모두 사용해야 합니다.

        5. SEO (검색 최적화):
            - 본문 서두와 제목에 메인 키워드를 자연스럽게 배치하되 과도한 반복은 피하세요.
            - 절대 본문 중간에 해시태그(#)를 넣지 마세요.
            - 글의 맨 마지막 영역에만 <p> 태그로 묶어서 연관 태그(영화 제목, 감독, 배우, 장르 등)를 5~10개 삽입하세요.

        출력 형식: 오직 HTML 본문 코드만 출력하세요. 맨 마지막 줄에 HTML 주석() 형식으로 매력적인 제목 5개를 제안하세요.
        """

    def _build_image_html(self, url, alt_text):
        if not url:
            return ""
        return f'<div style="text-align: center; margin: 25px 0;"><img src="{url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></div>'

    def _build_placeholder_html(self, text):
        return f'<p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{{{사진: {text}}}}}</p>'

    def _generate_media_prompts(self, details):
        title = details.get('title', '')
        
        poster_html = self._build_image_html(details.get('poster_url'), f"{title} 메인 포스터")
        if not poster_html:
            poster_html = self._build_placeholder_html(f"영화 '{title}' 메인 포스터")
            
        backdrop_urls = details.get('backdrop_urls', [])
        stills_html_list = []
        
        for i, url in enumerate(backdrop_urls):
            stills_html_list.append(self._build_image_html(url, f"{title} 공식 스틸컷 {i+1}"))
            
        target_count = max(6, len(backdrop_urls))
        for i in range(len(stills_html_list), target_count):
            stills_html_list.append(self._build_placeholder_html(f"{title} 주요 장면 {i+1} (관련 텍스트 삽입)"))

        stills_prompt_text = "\n".join([f"        - [스틸컷 {i+1}]: {html}" for i, html in enumerate(stills_html_list)])
        
        ticket_html = self._build_placeholder_html(f"{title} 영화관 관람 인증샷 (티켓 등)")
        
        return poster_html, stills_prompt_text, ticket_html

    def build_preview_prompt(self, details, point, latest_news=""):
        base = self._get_base_guideline()
        title = details.get('title', '')
        
        poster_html, stills_prompt_text, ticket_html = self._generate_media_prompts(details)

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
        
        [제공되는 실제 이미지 HTML 코드 (🚨목록에 있는 코드를 하나도 빠짐없이 전부 복사해서 붙여넣으세요)]
        - [메인 포스터]: {poster_html}
        - [관람 인증샷]: {ticket_html}
{stills_prompt_text}
        
        [특이사항]
        - 반드시 제공된 [영화 실제 데이터]를 바탕으로 작성하여 거짓 정보(할루시네이션)를 만들지 마세요.
        - [최신 네이버 뉴스 동향]의 내용을 본문에 반영하되, 출처를 암시하는 단어는 절대 쓰지 마세요.
        
        {base}
        """

    def build_review_prompt(self, details, comment, latest_news=""):
        base = self._get_base_guideline()
        title = details.get('title', '')
        
        poster_html, stills_prompt_text, ticket_html = self._generate_media_prompts(details)

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
        
        [제공되는 실제 이미지 HTML 코드 (🚨목록에 있는 코드를 하나도 빠짐없이 전부 복사해서 붙여넣으세요)]
        - [메인 포스터]: {poster_html}
        - [관람 인증샷]: {ticket_html}
{stills_prompt_text}
        
        [특이사항]
        - 감상평에 담긴 저의 솔직한 감정을 본문에 자연스럽게 녹여내 주세요.
        - [최신 네이버 뉴스 동향]의 내용을 반영하되, 출처를 암시하는 단어는 절대 피하세요.
        
        {base}
        """

    def build_news_prompt(self, news_content):
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
        print(f"\\n[알림] 결과물을 브라우저에서 확인합니다: {file_path}")
        webbrowser.open(f"file://{file_path}")