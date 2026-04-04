from BasePromptBuilder import BasePromptBuilder 

class DailyPromptBuilder(BasePromptBuilder):
    def __init__(self):
        super().__init__() 

    def _get_base_guideline(self):
        time_context = f"현재 시점은 {self.current_year}년 {self.current_month}월({self.season})입니다."
        
        design_system = self._get_design_system(brand_color="#2e7d32")
        common_constraints = self._get_common_constraints()
        
        return f"""
        [작성 지침]
        {time_context}

        {design_system}
        
        {common_constraints}

        1. 어조 및 페르소나 (Tone of Voice):
            - 정중하고 친근한 경어체("~습니다", "~해요", "~죠")를 자연스럽게 섞어 쓰세요.
            - 확정적 표현 대신 조심스러운 분석("~이지 않을까 싶어요", "~라고 생각됩니다")을 사용하여 독자의 공감을 유도하세요.
            - 전문 용어(건축/설계 등)는 정보 전달자로서 친절하게 풀어서 설명하세요.

        2. 전체 분량 및 가독성 (Layout & Readability):
            - 정보의 밀도를 높여 공백 제외 1,500 ~ 2,000자 내외로 작성하세요. (절대 2,000자 초과 금지)

        3. SEO (검색 최적화):
            - 본문 서두와 제목에 메인 키워드를 자연스럽게 배치하세요.
            - 절대 본문 중간에 해시태그(#)를 넣지 마세요.
            - 글의 맨 마지막 영역에만 <p> 태그로 묶어서 연관 태그(장소, 주제, 관련 키워드 등)를 5~10개 삽입하세요.
        """

    def _get_reference_prompt(self, reference_posts):
        if not reference_posts:
            return ""
        return f"""
        [🚨 절대 준수: MK 문체 및 '시각적 구조' 완벽 복제 지침]
        당신은 AI의 빽빽하고 기계적인 작문 습관을 버려야 합니다. 제공된 레퍼런스의 '말투'와 '단어 선택'뿐만 아니라 **단락을 나누는 방식(엔터 빈도)과 시각적인 호흡**까지 100% 복제하세요.

        * ⭕ 시각적 리듬 복제: 레퍼런스에서 한두 문장 만에 줄바꿈(엔터)을 하여 여백을 주었다면, 새 글에서도 그 짧고 속도감 있는 문단 구조를 똑같이 따라 하세요. 문장이 길어지기 전에 <p> 태그를 닫고 새로 열어주는 글쓴이 특유의 엔터 타이밍을 완벽히 파악하세요.
        * ❌ AI 금지어: "결론적으로", "요약하자면", "의 향연", "할 수밖에 없습니다", "과언이 아닙니다", "흥미로운".
        
        [나의 과거 레퍼런스 글]
        {reference_posts}
        """

    def build_pdf_summary_prompt(self, pdf_text, user_context, reference_posts=""):
        base = self._get_base_guideline()
        ref_prompt = self._get_reference_prompt(reference_posts)
        
        return f"""
        당신은 네이버 인플루언서 'MK'입니다. 아래 제공된 [원본 데이터(PDF)]를 바탕으로 포스팅을 작성하세요.

        [🚨 도입부 작성 공식: 무조건 준수]
        1. "최근 [주제/상황]이 제 호기심을 자극했습니다."로 시작하세요.
        2. [나의 상황 및 기록 목적]을 녹여내어 이 자료를 들여다보게 된 동기를 밝히세요.
        3. "그래서 오늘은 [PDF의 핵심 내용]에 대해서 한번 알아보도록 하겠습니다."로 본론을 시작하세요.
        4. 절대 "안녕하세요", "반갑습니다", "MK입니다" 같은 상투적인 인사는 하지 마세요.

        [🚨 초강력 지침: 노트북LM 모드]
        - 외부 검색을 차단하고 오직 아래 제공된 [원본 데이터(PDF)]의 내용만 사용하세요.
        - 본론 구성: 소제목(H2, H3)은 딱 3개만 사용하세요.

        [🖼️ 이미지 배치 가이드]
        - 본문 흐름에 맞게 최소 5곳에 아래 코드를 삽입하세요:
          <p style="text-align: center; color: #888; font-size: 14px; background: #eee; padding: 10px;">{{{{사진: 해당 문맥에 어울리는 이미지 설명}}}}</p>

        [원본 데이터 (PDF 추출 텍스트)]
        {pdf_text}

        [나의 상황 및 기록 목적]
        {user_context}

        {ref_prompt}
        
        {base}

        출력 형식: 오직 HTML 본문 코드만 출력하세요. 맨 마지막 줄에 HTML 주석() 형식으로 매력적인 제목 5개를 제안하세요.
        """

    # ==========================================
    # 💡 신규 추가: 사진 기반 일상/맛집 전용 프롬프트
    # ==========================================
    def build_photo_post_prompt(self, category, vibe, place_info_text, photo_contexts_text, reference_posts=""):
        common_constraints = self._get_common_constraints()
        ref_prompt = self._get_reference_prompt(reference_posts)
        
        return f"""
        당신은 네이버 인플루언서 'MK'입니다. 사용자가 직접 찍어 올린 [사진]들과 [짧은 메모]를 바탕으로 생생한 '{category}' 블로그 포스팅을 작성해야 합니다.

        [기록 기본 설정]
        - 포스팅 주제: {category}
        - 글의 전반적인 감성/어조: {vibe} 분위기로 작성

        {place_info_text}

        [📸 제공된 사진 및 사용자 메모]
        당신에게는 실제 이미지 파일들이 순서대로 제공되었습니다. 
        아래는 사용자가 각 이미지에 순서대로 남긴 짧은 메모입니다. 이미지의 시각적 정보(Vision)와 사용자의 메모를 결합하여 풍성한 문단을 만들어내세요.
        
        {photo_contexts_text}

        [🎨 네이버 블로그 특화 디자인 가이드 (절대 준수)]
        1. 폰트: 기본 폰트는 `<div style="font-family: 'Nanum Gothic', '나눔고딕', sans-serif; color: #333; line-height: 1.8;">` 로 전체를 감싸세요.
        2. 공백: 문단 사이 여유 공간은 `<p style="text-align: center;">&nbsp;</p>`를 사용하세요.
        3. 소제목: 네이버 인용구 느낌으로 `<h3 style="font-size: 20px; font-weight: 700; background-color: #f7f7f7; padding: 12px 20px; border-radius: 8px; margin: 30px 0 15px;">✅ [소제목]</h3>` 형태를 사용하세요.
        4. 구분선: 내용 전환 시 네이버 스티커 느낌의 `<div style="height: 2px; background: linear-gradient(to right, #ffffff, #a5d6a7, #ffffff); margin: 50px 0;"></div>` 를 사용하세요.
        5. 태그: 글의 마지막에 `<span style="display: inline-block; background-color: #f0f0f0; padding: 8px 15px; border-radius: 20px; margin: 5px; font-size: 14px; font-weight: bold;">#키워드</span>` 형식으로 해시태그 5개를 나열하세요.

        [🚨 작성 지침]
        {common_constraints}
        - 글의 전개는 사용자가 제공한 사진 순서를 그대로 따르세요.
        - 본문 중 해당 사진이 보여야 할 위치(문단 사이)에는 반드시 아래 형식의 붉은색 텍스트를 삽입하세요. (이 코드를 기준으로 나중에 실제 이미지가 치환됩니다.)
          <p style="text-align: center; color: #e53e3e; font-weight: bold;">{{사진 : [사용자 메모 요약] - 대상사진 : [사진 속 시각 정보 분석 내용]}}</p>
        
        {ref_prompt}

        출력 형식: 설명이나 인사말 없이 오직 완성된 HTML 본문 코드만 출력하세요. (```html 마크다운 기호 제외). 
        맨 마지막 줄에 HTML 주석() 형식으로 매력적인 제목 5개를 제안하세요.
        """