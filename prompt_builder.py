import os
import webbrowser
from BasePromptBuilder import BasePromptBuilder # 💡 베이스 빌더 불러오기

# 💡 BasePromptBuilder를 상속받습니다.
class PromptBuilder(BasePromptBuilder):
    def __init__(self):
        super().__init__() # 💡 부모의 날짜/계절 계산 로직 가져오기

    def _get_base_guideline(self, post_type="review"):
        time_context = f"현재 시점은 {self.current_year}년 {self.current_month}월({self.season})입니다."
        
        # ✅ [수정1] brand_color="#1a1a1a"로 BasePromptBuilder의 디자인 시스템 올바르게 호출
        # BasePromptBuilder._get_design_system()이 정의한 1x1 표(table) 타이틀 박스 방식이 적용됨
        design_system = self._get_design_system(brand_color="#1a1a1a")
        common_constraints = self._get_common_constraints()

        # 🚨 [새로운 도입부 작성 공식] 포스팅 타입별 세분화 적용
        if post_type == "preview":
            intro_guideline = f"""- [서론 - 도입부 공식 절대 준수]: 
              1. "최근 영화 <[영화 제목]>의 개봉(또는 관련) 소식이 제 호기심을 자극했습니다." 혹은 이와 유사하게 시작하세요.
              2. 하단에 제공되는 [포스팅 계기/이유]를 녹여내어 이 영화를 프리뷰하게 된 명확한 동기를 밝히세요.
              3. "그래서 오늘은 개봉에 앞서 이 영화의 기대 포인트에 대해 미리 알아보도록 하겠습니다."로 본론을 여세요."""
            media_guideline = """- 제공된 [메인 포스터]와 [스틸컷 1~N개] HTML 코드는 본문에 모두 1번씩 그대로 복사하여 삽입해야 합니다.
            - 💡 [융통성 발휘]: 개봉 전 프리뷰이므로, 부가적인 정보 사진이 들어가면 좋은 위치에는 언제든지 `<p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{사진: 필요한 실제 사진/상황에 대한 구체적 설명}}</p>` 코드를 사용하세요."""
        
        elif post_type == "review":
            # ✅ [수정2] 소제목 스타일을 BasePromptBuilder._get_design_system()의 
            # "1x1 표(table) 타이틀 박스" 방식과 일치하도록 수정.
            # 기존의 <div style="background:#1a1a1a..."> 방식을 제거하고
            # BasePromptBuilder가 정의한 table 구조로 통일합니다.
            intro_guideline = f"""- [서론 - 도입부 공식 절대 준수]:
              1. "최근 영화 <[영화 제목]>을(를) 관람했습니다." 혹은 이와 유사하게 흥미를 유발하며 시작하세요.
              2. 하단에 제공되는 [포스팅 계기/관람 이유]를 녹여내어 영화를 보게 된 동기나 강렬한 첫인상을 밝히세요.
              3. "그래서 오늘은 이 영화에 대한 솔직한 감상과 리뷰를 남겨보려 합니다."로 본론을 여세요.
              4. 서론 마지막 문장 직후에 아래 구분선 코드를 삽입하세요.
                 <p style="text-align:center; color:#bbb; letter-spacing: 8px;">• • • • •</p>
              5. 구분선 바로 아래에 [관람 인증샷] 코드를 삽입하세요.

            - [줄거리 요약 섹션 - 구분선+인증샷 직후 반드시 작성]:
              아래 HTML 소제목 스타일을 그대로 복사하여 줄거리 섹션을 여세요.
              (🚨 H2, H3 태그 및 border-bottom 방식 사용 절대 금지 — 반드시 아래 table 구조만 사용)
              <table width="100%" border="0" cellpadding="15" bgcolor="#1a1a1a"><tr><td><b style="color:#ffffff; font-size:18px;">■ 어떤 이야기인가요?</b></td></tr></table>
              - 제공된 [줄거리] 데이터를 바탕으로 결말·반전을 드러내지 않는 선에서 3~4문장으로 압축 정리합니다.
              - 영화의 배경, 주인공 상황, 핵심 갈등 구조만 간결하게 소개하세요.
              - 줄거리 요약 직후에 [스틸컷 1] 코드를 삽입하세요.

            - [본론 소제목 스타일 - 🚨 반드시 아래 table 형식만 사용]:
              모든 본론 소제목은 위 디자인 시스템(1번 항목)에서 정의한 table 구조를 그대로 사용하세요.
              H2, H3 태그 및 border-bottom 방식은 절대 사용 금지.
              <table width="100%" border="0" cellpadding="15" bgcolor="#1a1a1a"><tr><td><b style="color:#ffffff; font-size:18px;">[소제목 내용]</b></td></tr></table>

            - [본론 구성 - 소제목 내용은 AI 재량으로 자유롭게]:
              소제목 주제는 영화의 특성과 감상평에서 가장 강조할 포인트를 자유롭게 설정하세요. 단, 아래 조건은 반드시 지키세요.
              • 본론 소제목을 최소 3개 이상 사용하세요.
              • 각 소제목 아래에 3~5문장 단락을 구성하세요. (글자수 목표 달성을 위해 충분히 풍부하게 서술)
              • 복잡한 요소를 설명하는 구간에는 아래 인용구 박스를 1~2개 삽입하세요.
                <blockquote style="border-left:4px solid #333; margin:20px 0; padding:10px 20px; background:#f9f9f9; color:#444; font-size:15px;">
                  [핵심 분석 문장이나 인상적인 표현을 한 문장으로]
                </blockquote>
              • 🚨 [스틸컷 분산 배치 필수]: 스틸컷은 반드시 각 소제목 단락 사이에 1장씩 고르게 분산하세요.
                절대로 후반부에 연달아 몰아 배치하지 마세요. 스틸컷 2장 이상이 연속으로 붙어 있으면 안 됩니다.

            - [관전 포인트 섹션 - 본론 마지막에 반드시 삽입]:
              마지막 본론 스틸컷 이후, 결론 전에 아래 형식의 관전 포인트 박스를 삽입하세요.
              <div style="background:#f5f5f5; border:1px solid #ddd; border-radius:8px; padding:16px 20px; margin:30px 0;">
                <p style="margin:0 0 8px; font-size:13px; color:#e53e3e; font-weight:bold;">🔎 관전 포인트</p>
                <p style="margin:0; font-size:14px; color:#555;">[이 영화를 어떤 마음으로 보면 좋을지, 주목할 점, 추천 대상을 2~3문장으로 솔직하게 작성]</p>
              </div>"""

            # ✅ [수정3] 이미지 분산 배치 강제 지침 강화
            # 기존: "고르게 분산하세요" (권고) → 변경: 구체적인 배치 순서와 금지 조항 명시
            media_guideline = """- 하단에 제공되는 이미지 HTML 코드 목록([메인 포스터], [관람 인증샷], [스틸컷 1~N개]) 전체를 무조건 한 번씩 본문에 1글자도 수정하지 말고 그대로 복사해서 배치해야 합니다.
            - 🚨 [스틸컷 배치 순서 — 절대 준수]:
              • [스틸컷 1]은 줄거리 요약 섹션 직후에 배치하세요.
              • [스틸컷 2]부터는 반드시 각 본론 소제목 단락 아래에 1장씩 배치하세요.
              • 남은 스틸컷이 소제목 수보다 많을 경우, 긴 단락 중간에 1장씩 분산하세요.
              • 🚫 절대 금지: 스틸컷 2장 이상을 텍스트 없이 연속으로 배치하는 것은 엄격히 금지합니다.
              • 🚫 절대 금지: 글 후반부(결론 앞)에 스틸컷을 몰아서 배치하는 것은 엄격히 금지합니다.
            - 각 스틸컷 바로 아래에 해당 장면의 분위기나 연출 의도를 설명하는 1~2문장 캡션을 <p style="text-align:center; color:#666; font-size:14px; font-style:italic;"> 태그로 덧붙이세요.
            - AI 임의로 이미지 태그를 줄이거나 생략하지 마세요."""
        
        elif post_type == "news":
            intro_guideline = f"""- [서론 - 도입부 공식 절대 준수]:
              1. "최근 영화계에서 [관련 뉴스 주제]에 관한 흥미로운 소식을 접했습니다." 혹은 이와 유사하게 시작하세요.
              2. "그래서 오늘은 이 이슈가 어떤 의미를 가지는지 함께 알아보려 합니다."로 본론을 여세요."""
            media_guideline = """- 본문에 적절한 이미지가 들어갈 자리에 `<p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{사진: 문맥에 맞는 사진 설명}}</p>` 코드를 삽입하세요."""

        return f"""
        [작성 지침]
        {time_context} 
        
        {design_system}
        
        {common_constraints}

        1. 어조 및 페르소나 (Tone of Voice):
            - 정중하고 친근한 경어체("~습니다", "~해요", "~죠")를 자연스럽게 섞어 쓰세요.
            - 전문 용어나 복잡한 내용은 정보 전달자로서 친절하게 풀어서 설명하세요.
            - 영화의 정서를 다룰 때는 서정적이고 감성적인 어휘를 활용하여 분위기를 풍성하게 만드세요.

        2. 전체 분량 및 구조:
            - 🚨 [글자수 필수 준수]: 공백·HTML 태그·이미지 코드를 제외한 순수 텍스트 기준으로 반드시 2,000 ~ 2,500자를 채워야 합니다. 이는 네이버 블로그 상위노출 기준(공백 제외 최소 1,500자)을 충족하고 영화 리뷰 콘텐츠로서 신뢰도 있는 분량을 확보하기 위한 최소 기준입니다. 분량이 부족하다면 각 소제목 단락을 더 풍성하게 확장하세요.
            - [최상단]: 시선 끄는 첫 문장으로 시작하고, 바로 아래에 [메인 포스터] HTML 코드를 삽입하세요. 스포일러 경고 문구도 잊지 마세요.
            - 🚨 [영화 정보 박스 필수 삽입]: 메인 포스터 바로 밑에는 반드시 아래 HTML 형태의 정보 박스를 삽입하여 영화 기본 정보를 정리하세요. 부족한 정보(러닝타임, 쿠키영상 등)는 스스로 검색하여 정확히 채워 넣으세요.
              <div style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; border: 1px solid #eee; margin: 20px 0; font-size: 15px; line-height: 1.8;">
                <p style="margin: 0;">📽️ <b>원제</b> : [원제]</p>
                <p style="margin: 0;">🎞️ <b>장르</b> : [장르]</p>
                <p style="margin: 0;">🌍 <b>국가</b> : [제작 국가]</p>
                <p style="margin: 0;">🎬 <b>감독</b> : [감독]</p>
                <p style="margin: 0;">⏳ <b>러닝타임</b> : [러닝타임, 예: 125분]</p>
                <p style="margin: 0;">🔞 <b>관람등급</b> : [등급, 예: 12세 이상 관람가]</p>
                <p style="margin: 0;">📅 <b>개봉일</b> : [개봉일]</p>
                <p style="margin: 0;">🍪 <b>쿠키영상</b> : [있음 n개/없음/정보 없음]</p>
              </div>
            {intro_guideline}
            - [결론]: 전체적인 감상을 2~3문장으로 갈무리하세요. 결론 마지막에는 아래 두 가지를 순서대로 반드시 삽입하세요.
              ① 관련 포스팅 유도 박스:
              <div style="background:#f4f4f4; border-left: 4px solid #333; padding: 15px 20px; margin: 30px 0; border-radius: 0 8px 8px 0;">
                <p style="margin:0; font-size:13px; color:#888;">📌 함께 읽으면 좋은 글</p>
                <p style="margin:5px 0 0; font-weight:bold;">[이 영화와 연관된 이전 포스팅 주제 추천 1~2개 제안]</p>
              </div>
              ② MK CINELAB CTA 문구:
              <p style="text-align:center; color:#888; font-size:13px;">🎬 MK CINELAB의 다른 영화 이야기가 궁금하다면?</p>

        3. 멀티미디어 및 이미지 가이드 (🚨 절대 준수 사항):
            {media_guideline}

        4. SEO (검색 최적화):
            - 본문 서두와 제목에 메인 키워드를 자연스럽게 배치하되 과도한 반복은 피하세요.
            - 절대 본문 중간에 해시태그(#)를 넣지 마세요.
            - 글의 맨 마지막 영역에만 <p> 태그로 묶어서 연관 태그를 5~10개 삽입하세요.

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

        # ✅ [수정4] 스틸컷 최소 수량 조정: max(6, ...) → max(5, ...)
        # 기존 6개 강제 생성이 후반부 몰아붙이기의 원인이었으므로 5개로 줄이고,
        # 실제 URL이 있는 경우엔 그 수를 우선 따르도록 합니다.
        target_count = max(5, len(backdrop_urls))
        for i in range(len(stills_html_list), target_count):
            stills_html_list.append(self._build_placeholder_html(f"{title} 주요 장면 {i+1} (관련 텍스트 삽입)"))

        # ✅ [수정5] 스틸컷 배치 힌트를 프롬프트 텍스트에 직접 명시
        # 각 스틸컷 항목에 권장 배치 위치를 주석으로 추가하여 AI가 순서대로 분산 배치하도록 유도
        stills_prompt_parts = []
        for i, html in enumerate(stills_html_list):
            if i == 0:
                placement_hint = "(배치 위치: 줄거리 요약 직후)"
            else:
                placement_hint = f"(배치 위치: 본론 소제목 {i}번 단락 아래)"
            stills_prompt_parts.append(f"        - [스틸컷 {i+1}] {placement_hint}: {html}")
        
        stills_prompt_text = "\n".join(stills_prompt_parts)
        
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