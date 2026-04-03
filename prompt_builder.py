import os
import webbrowser
from datetime import datetime

class PromptBuilder:
    def __init__(self):
        # 💡 객체 생성 시 현재 시간/계절 정보를 미리 세팅
        self.current_date = datetime.now()
        self.current_month = self.current_date.month
        self.current_year = self.current_date.year
        
        # 계절 판단 로직
        if 3 <= self.current_month <= 5:
            self.season = "봄"
        elif 6 <= self.current_month <= 8:
            self.season = "여름"
        elif 9 <= self.current_month <= 11:
            self.season = "가을"
        else:
            self.season = "겨울"

    def _get_base_guideline(self, post_type="review"):
        # 💡 현재 시점 텍스트 생성
        time_context = f"현재 시점은 {self.current_year}년 {self.current_month}월({self.season})입니다."

        # 🚨 [새로운 도입부 작성 공식] 포스팅 타입별 세분화 적용
        if post_type == "preview":
            intro_guideline = f"""- [서론 - 도입부 공식 절대 준수]: 
              1. "최근 영화 <[영화 제목]>의 개봉(또는 관련) 소식이 제 호기심을 자극했습니다." 혹은 이와 유사하게 시작하세요.
              2. 하단에 제공되는 [포스팅 계기/이유]를 녹여내어 이 영화를 프리뷰하게 된 명확한 동기를 밝히세요.
              3. "그래서 오늘은 개봉에 앞서 이 영화의 기대 포인트에 대해 미리 알아보도록 하겠습니다."로 본론을 여세요.
              4. 🚨 절대 "안녕하세요", "반갑습니다", "MK입니다" 혹은 "{self.season} 바람이 부는 요즘" 같은 상투적인 인사말은 금지입니다."""
            media_guideline = """- 제공된 [메인 포스터]와 [스틸컷 1~N개] HTML 코드는 본문에 모두 1번씩 그대로 복사하여 삽입해야 합니다.
            - 💡 [융통성 발휘]: 개봉 전 프리뷰이므로, 제공된 영화 스틸컷 외에 '실제 역사적 인물의 사진', '감독의 전작 포스터', '원작 책 표지' 등 문맥상 부가적인 정보 사진이 들어가면 좋은 위치에는 언제든지 `<p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{사진: 필요한 실제 사진/상황에 대한 구체적 설명}}</p>` 코드를 사용하여 회색 박스 자리를 자유롭게 만들어 주세요."""
        
        elif post_type == "review":
            intro_guideline = f"""- [서론 - 도입부 공식 절대 준수]:
              1. "최근 영화 <[영화 제목]>을(를) 관람했습니다." 혹은 이와 유사하게 흥미를 유발하며 시작하세요.
              2. 하단에 제공되는 [포스팅 계기/관람 이유]를 녹여내어 영화를 보게 된 동기나 강렬한 첫인상을 밝히세요.
              3. "그래서 오늘은 이 영화에 대한 솔직한 감상과 리뷰를 남겨보려 합니다."로 본론을 여세요. 서론 중간쯤에 [관람 인증샷] 코드를 자연스럽게 삽입하세요.
              4. 🚨 절대 "안녕하세요", "반갑습니다", "MK입니다" 혹은 계절 인사 같은 상투적인 인사말은 금지입니다."""
            media_guideline = """- 하단에 제공되는 이미지 HTML 코드 목록([메인 포스터], [관람 인증샷], [스틸컷 1~N개]) 전체를 무조건 한 번씩 본문에 1글자도 수정하지 말고 그대로 복사해서 배치해야 합니다.
            - 제미나이 임의로 이미지 태그를 줄이거나 생략하지 마세요. 제공된 코드는 반드시 모두 사용해야 합니다."""
        
        elif post_type == "news":
            intro_guideline = f"""- [서론 - 도입부 공식 절대 준수]:
              1. "최근 영화계에서 [관련 뉴스 주제]에 관한 흥미로운 소식을 접했습니다." 혹은 이와 유사하게 시작하세요.
              2. "그래서 오늘은 이 이슈가 어떤 의미를 가지는지 함께 알아보려 합니다."로 본론을 여세요.
              3. 🚨 절대 "안녕하세요", "반갑습니다", "MK입니다" 같은 상투적인 인사말은 금지입니다."""
            # ✅ 이 부분의 따옴표 충돌 문제를 수정했습니다 (""" 사용)
            media_guideline = """- 본문에 적절한 이미지가 들어갈 자리에 `<p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{사진: 문맥에 맞는 사진 설명}}</p>` 코드를 삽입하세요."""

        return f"""
        [작성 지침]
        {time_context} 

        1. 어조 및 페르소나 (Tone of Voice):
            - 정중하고 친근한 경어체("~습니다", "~해요", "~죠")를 자연스럽게 섞어 쓰세요.
            - 확정적 표현 대신 조심스러운 분석("~이지 않을까 싶어요", "~라고 생각됩니다", "~인 듯 보이기도 하며")을 사용하여 독자의 공감을 유도하세요.
            - 전문 용어나 복잡한 내용은 정보 전달자로서 친절하게 풀어서 설명하세요.
            - 영화의 정서를 다룰 때는 서정적이고 감성적인 어휘를 활용하여 분위기를 풍성하게 만드세요.

        2. 전체 분량 및 가독성 (Layout & Readability):
            - 정보의 밀도를 높여 공백 제외 1,500 ~ 2,000자 내외로 작성하세요.
            - 💡 [레이아웃 학습]: 기계적으로 단락을 나누지 마세요. 하단에 제공될 [나의 과거 레퍼런스 글]의 시각적인 호흡을 관찰하고, 그곳에 쓰인 짧은 문장 호흡과 문단 사이의 빈 줄(<p style="text-align: center;">&nbsp;</p>) 활용 방식을 새 글에도 똑같이 적용하세요.

        3. 포스팅 레이아웃 구조 (서론-본론-결론):
            - [최상단]: 시선 끄는 첫 문장으로 시작하고, 바로 아래에 [메인 포스터] HTML 코드를 삽입하세요. 스포일러 경고 문구도 잊지 마세요.
            {intro_guideline}
            - [본론]: H2, H3 태그를 활용해 소제목으로 단락을 구분하세요. 내용 흐름에 맞게 아래 제공된 [스틸컷] HTML 코드를 문단 사이사이에 전부 다 빠짐없이 골고루 흩뿌려서 삽입하세요.
            - [결론]: 전체적인 감상을 갈무리하며 나만의 한줄평과 기대평을 직관적으로 제시하세요.

        4. 멀티미디어 및 이미지 가이드 (🚨 절대 준수 사항):
            {media_guideline}

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

    def _generate_media_prompts(self, details, is_preview=False):
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
        
        if is_preview:
            return poster_html, stills_prompt_text, ""
        else:
            ticket_html = self._build_placeholder_html(f"{title} 영화관 관람 인증샷 (티켓 등)")
            return poster_html, stills_prompt_text, ticket_html

    def _get_reference_prompt(self, reference_posts):
        if not reference_posts:
            return ""
        return f"""
        [🚨 절대 준수: MK 문체 및 '시각적 구조' 완벽 복제 지침]
        아래 제공된 [나의 과거 레퍼런스 글]은 이 블로그의 주인장인 제가 직접 쓴 글입니다. 
        당신은 AI의 기계적인 작문 습관을 모두 버리고, 무조건 이 레퍼런스의 '말투', '단어 선택', '문장 끝맺음', '비유 방식'을 100% 똑같이 흉내 내서 빙의해야 합니다.

        * ⭕ 시각적 리듬 복제: 레퍼런스에서 한두 문장 만에 줄바꿈(엔터)을 하여 여백을 주었다면, 새 글에서도 그 짧고 속도감 있는 문단 구조를 똑같이 따라 하세요. 문장이 길어지기 전에 <p> 태그를 닫고 새로 열어주는 글쓴이 특유의 엔터 타이밍을 완벽히 파악하세요.
        * ❌ AI 금지어 (절대 사용 금지): "결론적으로", "요약하자면", "이 영화는 ~라는 점에서 큰 의미를 가집니다", "~의 향연", "~할 수밖에 없습니다", "과언이 아닙니다", "시각적 즐거움", "흥미로운".
        
        * 🚨 🚨 [초강력 경고: 내용 인용 금지] 🚨 🚨
        레퍼런스 글에 등장하는 **과거의 영화 제목, 배우 이름, 특정 사건 내용 등을 절대로, 단 하나도 새 글에 가져오거나 언급하지 마세요.**
        오직 **"말투와 글을 전개하는 방식"**이라는 껍데기만 훔쳐오고, 알맹이는 완전히 새로운 영화에 맞춰서 작성해야 합니다.

        [나의 과거 레퍼런스 글]
        {reference_posts}
        """

    def build_preview_prompt(self, details, point, reason="", latest_news="", reference_posts=""):
        base = self._get_base_guideline(post_type="preview")
        ref_prompt = self._get_reference_prompt(reference_posts)
        title = details.get('title', '')
        poster_html, stills_prompt_text, _ = self._generate_media_prompts(details, is_preview=True)

        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 아래 정보를 바탕으로 프리뷰 원고를 작성하세요.
        
        [영화 실제 데이터]
        - 제목: {title}
        - 개봉일: {details.get('release_date', '')}
        - 장르: {details.get('genres', '')}
        - 감독: {details.get('director', '')}
        - 출연: {details.get('actors', '')}
        - 줄거리: {details.get('overview', '')}
        
        [핵심 주제 및 강조 포인트]
        - {point}

        [포스팅 계기/이유]
        - {reason}

        [최신 네이버 뉴스 동향]
        {latest_news}
        
        {ref_prompt}

        [제공되는 실제 이미지 HTML 코드]
        - [메인 포스터]: {poster_html}
{stills_prompt_text}
        
        [특이사항]
        - 반드시 제공된 [영화 실제 데이터]를 바탕으로 작성하여 거짓 정보(할루시네이션)를 만들지 마세요.
        - [최신 네이버 뉴스 동향]의 내용을 본문에 반영하되, 출처를 암시하는 단어는 절대 쓰지 마세요.
        
        {base}
        """

    def build_review_prompt(self, details, comment, reason="", latest_news="", reference_posts=""):
        base = self._get_base_guideline(post_type="review")
        ref_prompt = self._get_reference_prompt(reference_posts)
        title = details.get('title', '')
        poster_html, stills_prompt_text, ticket_html = self._generate_media_prompts(details, is_preview=False)

        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 영화를 직접 관람한 후 작성하는 상세 리뷰 원고를 작성하세요.
        
        [영화 실제 데이터]
        - 제목: {title}
        - 개봉일: {details.get('release_date', '')}
        - 장르: {details.get('genres', '')}
        - 감독: {details.get('director', '')}
        - 출연: {details.get('actors', '')}
        - 줄거리: {details.get('overview', '')}
        
        [포스팅 계기/관람 이유]
        - {reason}

        [나의 주관적 감상평]
        {comment}

        [최신 네이버 뉴스 동향]
        {latest_news}
        
        {ref_prompt}

        [제공되는 실제 이미지 HTML 코드]
        - [메인 포스터]: {poster_html}
        - [관람 인증샷]: {ticket_html}
{stills_prompt_text}
        
        [특이사항]
        - 감상평에 담긴 저의 솔직한 감정을 본문에 자연스럽게 녹여내 주세요.
        
        {base}
        """

    def build_news_prompt(self, news_content, reference_posts=""):
        base = self._get_base_guideline(post_type="news")
        ref_prompt = self._get_reference_prompt(reference_posts)
        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 최신 영화 뉴스(기사)를 MK만의 시각으로 재해석한 포스팅을 작성하세요.
        
        [뉴스 원문 데이터]
        {news_content}
        
        {ref_prompt}

        [특이사항]
        - 단순히 기사를 요약하는 것이 아니라, 인플루언서로서 이 소식이 영화계나 팬들에게 어떤 의미가 있을지 의견을 덧붙여주세요.
        
        {base}
        """

    def build_html_conversion_prompt(self, raw_text):
        return f"""
        당신은 전문 HTML 포매터입니다. 
        아래 제공된 [원본 블로그 텍스트]의 **내용, 문체, 단어, 어투는 절대 단 한 글자도 수정하지 말고 그대로 복사해서 사용**하되, 
        MK CINELAB 블로그 포스팅 양식에 맞게 HTML 태그만 입혀서 출력하세요.

        [적용할 HTML 서식 규칙]
        1. 여백 및 구조: 원본 텍스트의 줄바꿈 리듬을 그대로 살리되, 문단 사이에 빈 줄(<p style="text-align: center;">&nbsp;</p>)을 삽입하여 가독성을 높이세요.
        2. 이미지 기획: 원본 텍스트의 흐름상 이미지가 들어가면 좋을 위치를 알아서 파악한 후, 아래의 회색 박스 코드를 삽입하세요.
           <p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{{{사진: 문맥에 맞는 사진 설명(예: 영화 포스터, 스틸컷 등)}}}}</p>

        [원본 블로그 텍스트]
        {raw_text}

        출력 형식: 설명이나 인사말 없이 오직 변환된 HTML 본문 코드만 출력하세요. (```html 마크다운은 제외할 것)
        """

    def build_curation_prompt(self, theme, movies_data_text, reference_posts=""):
        ref_prompt = self._get_reference_prompt(reference_posts)
        
        time_context = f"현재 시점은 {self.current_year}년 {self.current_month}월({self.season})입니다."
        
        return f"""
        당신은 네이버 영화 인플루언서 'MK'입니다. 여러 영화를 묶어서 소개하는 '영화 큐레이션(리스트형)' 블로그 포스팅을 작성하세요.

        {time_context}

        [포스팅 메인 테마 및 요청사항]
        - 테마: {theme}

        {ref_prompt}

        [수집된 영화 상세 데이터 (TMDB 정보 + 네이버 최신 뉴스 결합)]
        {movies_data_text}

        [🚨 큐레이션 작성 핵심 규칙 (글자 수 제한)]
        - 독자가 스크롤을 내리며 가볍게 읽을 수 있도록, 영화 1편당 설명은 매우 짧고 간결해야 합니다.
        - 정보 박스를 제외하고, '영화 소개글'과 '관전 포인트'를 모두 합쳐서 영화 1편당 공백 포함 200자 ~ 250자 내외로 타이트하게 요약하세요. 절대 장황하게 쓰지 마세요.

        [🚨 절대 준수: MK CINELAB 큐레이션 HTML 레이아웃]
        아래의 HTML 구조를 100% 동일하게 따라야 합니다. 제공된 영화 목록의 개수만큼 <영화 섹션>을 반복해서 생성하세요.

        <p>최근 <b>{theme}</b>에 관한 영화들이 눈길을 끕니다. 그래서 오늘은 이 주제에 맞는 영화들을 모아 소개해보려 합니다. [🚨 절대 "안녕하세요", "반갑습니다" 등의 인사는 금지]</p>
        <p style="text-align: center;">&nbsp;</p>

        <h2 style="border-bottom: 2px solid #333; padding-bottom: 5px;">[영화 제목]</h2>
        <p style="color: #666; font-weight: bold; font-size: 18px;">[영화의 분위기를 요약하는 감각적인 부제 1줄]</p>

        [수집된 영화 데이터에 포함된 <메인 포스터 HTML 코드>를 여기에 반드시 삽입]

        <div style="background: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <p style="margin: 0;">🏷️ 원제 : [Original Title]</p>
            <p style="margin: 0;">🌍 국가 : [Country]</p>
            <p style="margin: 0;">🎬 감독 : [Director]</p>
            <p style="margin: 0;">👤 출연 : [Actors (주연 위주로 2~3명)]</p>
            <p style="margin: 0;">📅 개봉일 : [Release Date]</p>
        </div>

        <p>[TMDB 줄거리를 바탕으로 하되, 아주 간결하게 압축한 영화 소개글. (1~2문장)]</p>

        <h3 style="color: #2e7d32; margin-top: 20px;">🔎 관전 포인트</h3>
        <p>[수집된 네이버 뉴스의 팩트와 MK의 주관적인 기대감을 섞은 핵심 관전 포인트. (1~2문장)]</p>

        <p style="text-align: center;">&nbsp;</p>
        <hr style="border: 0; border-top: 1px dashed #ccc; margin: 30px 0;">
        <p>[포스팅을 마무리하는 따뜻한 결론 인사말. 1~2문장]</p>
        
        출력 형식: 앞뒤의 부가 설명이나 인사말 없이 오직 완성된 HTML 본문 코드만 출력하세요. (```html 같은 마크다운 기호도 절대 쓰지 마세요.)
        """