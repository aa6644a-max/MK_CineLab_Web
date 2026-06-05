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
            - 전문 용어는 정보 전달자로서 친절하게 풀어서 설명하세요.

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

        출력 형식: ```html, ``` 등 마크다운 코드블록 기호를 절대 포함하지 마세요. 오직 순수 HTML 본문 코드만 출력하세요.
        맨 마지막 줄에 아래 형식으로 네이버 SEO 최적화 제목 5개를 반드시 제안하세요:
        <!-- TITLES: 제목1||제목2||제목3||제목4||제목5 -->
        (제목 조건: 검색 노출에 유리한 핵심 키워드를 앞에 배치, 30자 이내, 클릭을 유도하는 감성적 표현 포함)
        """

    def build_photo_post_prompt(self, category, vibe, place_info_text, photo_contexts_text, reference_posts="", pdf_text=""):
        base_guideline = self._get_base_guideline()
        ref_prompt = self._get_reference_prompt(reference_posts)

        pdf_section = ""
        if pdf_text and pdf_text.strip():
            pdf_section = f"""
        [📄 사전 조사 자료 (PDF)]
        아래는 이 장소/주제에 대해 방문 전 직접 조사한 배경 자료입니다.
        글의 도입부와 배경 설명 단락을 작성할 때 이 내용을 적극적으로 활용하세요.
        단, 조사 내용을 나열하듯 쓰지 말고, 방문 경험과 자연스럽게 연결하세요.

        {pdf_text}
        """

        structure_guide = f"""
        [🗂️ MK 비평가 포스팅 구조 (반드시 이 순서로)]
        이 포스팅은 맛집/장소 소개 인플루언서 글이 아닙니다.
        MK는 어떤 장소나 경험을 '비평가의 시선'으로 기록합니다.

        1단계 — 배경과 소개 (전체의 약 25%):
           - 이 장소/가게/브랜드가 어떤 곳인지 PDF 조사 자료를 바탕으로 소개하세요.
           - "~라는 곳이 있다고 해서 찾아봤는데" 식의 발견 동기를 자연스럽게 녹이세요.
           - 홍보성 과장 표현('최고', '강추', '인생맛집') 절대 금지.

        2단계 — 방문 경위와 첫인상 (약 15%):
           - 왜, 어떤 계기로 갔는지 솔직하게 쓰세요 (집 근처라서, 궁금해서, 같이 간 사람이 있어서 등).
           - 공간의 첫인상, 동선, 분위기를 간결하게 묘사하세요.

        3단계 — 메뉴/경험 상세 기록 (약 45%):
           - 먹거나 경험한 것들을 사진 순서에 맞춰 구체적으로 기록하세요.
           - 맛/질감/온도/가격 등 실제 정보를 담되, '이게 맛있어요!'가 아니라 '이런 느낌이었다'로 쓰세요.
           - 비교 대상이나 기대치 대비 실제 경험 차이를 솔직하게 서술하세요.

        4단계 — MK의 총평 (약 15%):
           - 억지 별점이나 추천 멘트 없이 "또 가겠냐"에 대한 솔직한 결론.
           - 누구에게 어울릴 곳인지 구체적으로 (예: '영화 보고 가볍게 들르기 좋은 집').
        """

        return f"""
        당신은 네이버 블로거 'MK'입니다. 맛집 인플루언서가 아닌, 경험을 솔직하게 기록하는 비평가입니다.
        아래 제공된 [사전 조사 자료], [장소 정보], [사진 메모]를 바탕으로 포스팅을 작성하세요.

        [기록 기본 설정]
        - 포스팅 주제: {category}
        - 글의 전반적인 감성/어조: {vibe} 분위기로 작성

        {place_info_text}

        {pdf_section}

        [📸 제공된 사진 및 사용자 메모]
        실제 이미지 파일들이 순서대로 제공되었습니다.
        아래는 각 이미지에 남긴 메모입니다. 이미지의 시각 정보와 메모를 결합해 구체적인 문단을 만드세요.

        {photo_contexts_text}

        {structure_guide}

        ======================================
        💡 [MK CINELAB 베이스 지침 절대 적용]
        {base_guideline}
        ======================================

        [🎨 사진 포스팅 HTML 가이드]
        1. 전체 폰트: `<div style="font-family: 'Nanum Gothic', '나눔고딕', sans-serif; color: #333; line-height: 1.8;">` 로 전체를 감싸세요.
        2. 이미지 삽입 (절대 준수):
           - 글의 전개는 사진 순서를 그대로 따르세요.
           - 해당 사진이 보여야 할 문단 사이에 반드시 아래 형식으로 삽입:
             <div style="text-align: center; margin: 25px 0;"><img src="[PHOTO_번호]" alt="[사진 설명]" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></div>
           - 번호는 사진 순서(1부터)와 일치해야 합니다.
        3. 구분선: 단계 전환 시 `<div style="height: 2px; background: linear-gradient(to right, #ffffff, #a5d6a7, #ffffff); margin: 50px 0;"></div>` 1~2회 사용.

        {ref_prompt}

        출력 형식: 설명이나 인사말 없이 오직 완성된 HTML 본문 코드만 출력하세요. (```html 마크다운 기호 제외).
        맨 마지막 줄에 아래 형식으로 네이버 SEO 최적화 제목 5개를 반드시 제안하세요:
        <!-- TITLES: 제목1||제목2||제목3||제목4||제목5 -->
        (제목 조건: 검색 노출에 유리한 핵심 키워드를 앞에 배치, 30자 이내, 클릭을 유도하는 감성적 표현 포함)
        """
    
    def build_meeting_review_prompt(self, meeting_name, date, participants, activities, mood, place_info_text, photo_contexts_text, reference_posts=""):
        base_guideline = self._get_base_guideline()
        ref_prompt = self._get_reference_prompt(reference_posts)
        
        return f"""
        당신은 네이버 인플루언서 'MK'입니다. 사용자가 진행한 [오프라인 모임/행사] 정보와 [사진]들을 바탕으로 생생하고 몰입감 있는 블로그 포스팅 초안을 작성해야 합니다.

        [모임 기본 정보]
        - 모임명: {meeting_name}
        - 진행 날짜: {date}
        - 참석자: {participants}
        - 글의 전반적인 분위기: {mood}
        - 핵심 활동 내용:\n{activities}

        {place_info_text}

        [📸 제공된 현장 사진 및 메모]
        아래는 사용자가 업로드한 현장 사진에 대한 순서와 짧은 메모입니다. 이미지의 시각적 정보와 메모, 그리고 위의 '핵심 활동 내용'을 자연스럽게 엮어 스토리텔링하세요.
        
        {photo_contexts_text}

        ======================================
        💡 [MK CINELAB 베이스 지침 절대 적용]
        {base_guideline}
        ======================================

        [🤝 모임 후기 특화 가이드 (베이스 지침과 함께 적용)]
        1. 도입부: 왜 이 모임을 기획/참석하게 되었는지, 어떤 사람들과 모였는지({participants} 언급)에 대한 설렘을 담아 시작하세요.
        2. 공간의 분위기: 제공된 장소 정보({place_info_text})가 있다면, 그 공간이 모임에 어떤 에너지를 주었는지 묘사하세요.
        3. 전체 폰트: `<div style="font-family: 'Nanum Gothic', '나눔고딕', sans-serif; color: #333; line-height: 1.8;">` 로 전체를 감싸세요.
        4. 이미지 삽입 위치 (절대 준수): 
           - 글의 흐름에 맞춰 현장 분위기 -> 진행 과정 -> 결과물 순서로 사진을 배치하세요.
           - 본문 중 해당 사진이 보여야 할 위치에는 반드시 아래 형식의 이미지 태그를 삽입하세요.
             <div style="text-align: center; margin: 30px 0;"><img src="[PHOTO_번호]" alt="[현장 사진 설명]" style="max-width: 100%; border-radius: 8px;"></div>
           - 번호는 제공된 사진의 순서(1부터 시작)와 일치해야 합니다.
        5. 마무리: 모임을 통해 느낀 점과 다음을 기약하는 따뜻한 인사로 마무리하세요.
        
        {ref_prompt}

        출력 형식: 설명이나 인사말 없이 오직 완성된 HTML 본문 코드만 출력하세요. (```html 마크다운 기호 제외).
        맨 마지막 줄에 아래 형식으로 네이버 SEO 최적화 제목 5개를 반드시 제안하세요:
        <!-- TITLES: 제목1||제목2||제목3||제목4||제목5 -->
        (제목 조건: 검색 노출에 유리한 핵심 키워드를 앞에 배치, 30자 이내, 클릭을 유도하는 감성적 표현 포함)
        """