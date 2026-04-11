import streamlit as st
import base64
import re  
import pdfplumber  
from DailyPromptBuilder import DailyPromptBuilder
from gemini_client import GeminiClient
from rss_client import RSSClient
from html_formatter import HTMLFormatter
from naver_client import NaverClient  

# ✅ 수정: height, scrolling 파라미터 추가
def show_isolated_html(html_str, height=1000, scrolling=True):
    # 💡 AI 마크다운 기호 제거
    clean_html = html_str.replace("```html\n", "").replace("```html", "").replace("```", "")
    
    # scrolling 옵션을 overflow CSS로 처리
    overflow_style = "auto" if scrolling else "hidden"
    
    # 💡 components.html 대신 iframe 주입 방식 사용
    b64 = base64.b64encode(clean_html.encode('utf-8')).decode('utf-8')
    iframe_html = f'<iframe src="data:text/html;charset=utf-8;base64,{b64}" width="100%" height="{height}" style="border:none; overflow:{overflow_style};"></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)

# 페이지 기본 설정
st.set_page_config(page_title="일상 & 현장 기록", page_icon="🏠", layout="centered")

# 엔진 초기화
@st.cache_resource(show_spinner=False)
def init_daily_engines():
    return DailyPromptBuilder(), GeminiClient(), RSSClient(), HTMLFormatter(), NaverClient()

daily_builder, gemini, rss, formatter, naver_client = init_daily_engines()

st.title("🏠 민규의 일상 & 현장 기록")
st.markdown("---")

# ✅ 탭 이름 변경 (3개로 확장)
tab1, tab2, tab3 = st.tabs(["📄 PDF 요약 포스팅", "📸 사진 기반 포스팅", "🤝 모임 후기 포스팅"])

# 세션 스테이트 초기화 (3개 탭 모두 포함)
if "daily_html" not in st.session_state: st.session_state.daily_html = None

if "photo_preview_html" not in st.session_state: st.session_state.photo_preview_html = None
if "photo_copy_html" not in st.session_state: st.session_state.photo_copy_html = None
if "place_search_results" not in st.session_state: st.session_state.place_search_results = None
if "selected_place" not in st.session_state: st.session_state.selected_place = None

if "meeting_preview_html" not in st.session_state: st.session_state.meeting_preview_html = None
if "meeting_copy_html" not in st.session_state: st.session_state.meeting_copy_html = None
if "meeting_search_results" not in st.session_state: st.session_state.meeting_search_results = None
if "meeting_selected_place" not in st.session_state: st.session_state.meeting_selected_place = None

# ==========================================
# [TAB 1] 기존 PDF 요약 포스팅
# ==========================================
with tab1:
    st.subheader("📄 PDF 자료 기반 블로그 초안 생성")
    st.write("다양한 PDF 자료들을 업로드하면, 오직 그 내용들만 분석하여 MK 스타일로 요약해 드립니다.")
    st.info("💡 여러 개의 PDF를 한꺼번에 올릴 수 있습니다. 자료가 많을수록 더 정확한 분석이 가능해요.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "참고할 PDF 파일들을 선택하세요 (중복 선택 가능)", 
            type="pdf", accept_multiple_files=True, key="daily_pdf_uploader"
        )
        if uploaded_files:
            st.caption(f"📂 총 {len(uploaded_files)}개의 파일이 선택되었습니다.")

        user_context = st.text_area(
            "이 기록에 담고 싶은 상황이나 생각", 
            placeholder="예: 영화 살목지 개봉 전, 실제 장소에 대한 괴담 정보들만 모아서 정리하고 싶습니다. 영화 정보보다는 PDF 속 실화에 집중해 주세요.",
            height=200, key="daily_context"
        )

    with col2:
        post_category = st.text_input("포스팅 카테고리 입력", placeholder="예: ☕ 카페 탐방, 🛠️ 현장 일지 등", key="daily_category_input")
        writing_vibe = st.select_slider("글의 감성 농도", options=["담백하게", "차분하게", "다정하게", "감성 가득", "위트 있게"], value="다정하게", key="daily_vibe")
        st.write("---")
        generate_btn = st.button("✨ MK 스타일 포스팅 생성", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_files and user_context and post_category:
            with st.spinner(f"{len(uploaded_files)}개의 PDF 데이터를 분석 중입니다..."):
                combined_text = ""
                for file in uploaded_files:
                    try:
                        with pdfplumber.open(file) as pdf:
                            combined_text += "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                    except Exception as e:
                        st.error(f"{file.name} 읽기 오류: {e}")

                if not combined_text.strip():
                    st.error("PDF에서 텍스트를 추출할 수 없습니다. 이미지로 된 PDF인지 확인해 주세요.")
                else:
                    reference_posts = rss.get_latest_posts_text(limit=3)
                    prompt = daily_builder.build_pdf_summary_prompt(
                        combined_text, f"[{post_category} / {writing_vibe} 분위기] {user_context}", reference_posts
                    )
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{post_category} 기록", result)
                    
                    st.session_state.daily_html = final_html
                    st.success("노트북LM 스타일의 맞춤형 포스팅 생성이 완료되었습니다!")
        else:
            st.warning("PDF 파일, 카테고리, 그리고 추가 맥락을 모두 입력해 주세요.")

    if st.session_state.daily_html:
        st.markdown("---")
        res_tab1, res_tab2 = st.tabs(["👁️ 블로그 미리보기", "📄 HTML 코드"])
        with res_tab1:
            st.info("외부 정보 없이 민규님이 주신 자료로만 구성된 미리보기입니다.")
            show_isolated_html(st.session_state.daily_html)
        with res_tab2:
            st.code(st.session_state.daily_html, language="html")

# ==========================================
# [TAB 2] 💡 사진 기반 포스팅
# ==========================================
with tab2:
    st.subheader("📸 사진 기반 일상/맛집/현장 포스팅")
    st.write("순서대로 사진을 업로드하고 짧은 캡션을 달아주세요. 알아서 흐름에 맞는 포스팅을 써드립니다.")

    # 1. 장소 검색
    st.markdown("#### 📍 1. 장소 정보 입력 (선택)")
    col_region, col_search, col_btn = st.columns([1.5, 3, 1])
    with col_region:
        region_list = ["직접 입력", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        region_option = st.selectbox("지역 선택", options=region_list, index=0, label_visibility="collapsed")
    with col_search:
        if region_option == "직접 입력":
            search_query = st.text_input("검색어", placeholder="지역명 + 상호명 (예: 제주 애월읍 카페)", label_visibility="collapsed")
            target_region = ""
        else:
            search_query = st.text_input("상호명 검색", placeholder=f"예: 남산동 스타벅스, 무촌리 철물점 등", label_visibility="collapsed")
            target_region = region_option

    with col_btn:
        search_place_btn = st.button("네이버 검색", key="search_place_btn", use_container_width=True)
    
    if search_place_btn and search_query:
        final_query = f"{target_region} {search_query}".strip()
        with st.spinner(f"'{final_query}'(으)로 네이버 지도를 뒤지는 중..."):
            results = naver_client.search_local_place(final_query)
            if "error" in results:
                st.error(results["error"])
            elif results.get("items"):
                st.session_state.place_search_results = results["items"]
                st.session_state.selected_place = None 
            else:
                st.warning("검색 결과가 없습니다. 검색어를 바꿔보세요!")

    if st.session_state.place_search_results and not st.session_state.selected_place:
        st.markdown("##### 📌 어느 곳인가요? (검색 결과)")
        with st.container(height=300):
            for i, item in enumerate(st.session_state.place_search_results):
                title = item['title'].replace('<b>', '').replace('</b>', '')
                category = item['category']
                address = item['roadAddress'] or item['address'] 
                
                col_info, col_sel = st.columns([5, 1])
                with col_info:
                    st.write(f"**{title}** \n<small>{category} | 📍 {address}</small>", unsafe_allow_html=True)
                with col_sel:
                    if st.button("선택", key=f"sel_place_{i}", use_container_width=True):
                        st.session_state.selected_place = {"title": title, "category": category, "address": address, "link": item.get('link', '')}
                        st.session_state.place_search_results = None
                        st.rerun()
        st.markdown("---")

    if st.session_state.selected_place:
        p = st.session_state.selected_place
        st.success(f"✅ **{p['title']}** 장소가 선택되었습니다! (📍 {p['address']})")
        if st.button("장소 다시 검색하기", key="reset_place_btn"):
            st.session_state.selected_place = None
            st.rerun()

    st.markdown("---")

    # 2. 사진 업로드
    st.markdown("#### 🖼️ 2. 사진 업로드 및 메모")
    uploaded_photos = st.file_uploader("포스팅에 들어갈 사진들을 순서대로 올려주세요.", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="photo_uploader")
    photo_contexts = []
    
    if uploaded_photos:
        st.caption(f"총 {len(uploaded_photos)}장의 사진이 업로드되었습니다.")
        for i, photo in enumerate(uploaded_photos):
            col_img, col_text = st.columns([1, 3])
            with col_img:
                st.image(photo, use_container_width=True)
            with col_text:
                caption = st.text_area(f"사진 {i+1} 설명", placeholder="예: 타설 전 철근 배근 완료 상태 / 우드톤 가구 조립 중", height=100, key=f"photo_cap_{i}")
                photo_contexts.append({"photo": photo, "caption": caption})

    st.markdown("---")

    # 3. 포스팅 설정
    st.markdown("#### 📝 3. 포스팅 설정")
    col_cat, col_vibe = st.columns(2)
    with col_cat:
        photo_category = st.selectbox("포스팅 카테고리", options=["🍽️ 맛집/카페 탐방", "🛠️ 현장/건축 일지", "🎬 일상 및 모임"], key="photo_category")
    with col_vibe:
        photo_vibe = st.select_slider("글의 감성 농도", options=["담백하게", "전문적으로", "차분하게", "다정하게", "위트 있게"], value="차분하게", key="photo_vibe")

    st.write("") 
    generate_photo_btn = st.button("📸 사진 포스팅 생성", type="primary", use_container_width=True)

    if generate_photo_btn:
        if not uploaded_photos:
            st.warning("먼저 사진을 업로드해 주세요!")
        else:
            with st.spinner("사진과 메모를 분석하여 포스팅을 작성 중입니다..."):
                place_info_text = ""
                if st.session_state.selected_place:
                    p = st.session_state.selected_place
                    place_info_text = f"[장소 정보]\n- 상호명: {p['title']}\n- 주소: {p['address']}\n- 카테고리: {p['category']}"
                
                photo_contexts_text = ""
                for i, ctx in enumerate(photo_contexts):
                    photo_contexts_text += f"- 사진 {i+1} 메모: {ctx['caption']}\n"
                
                reference_posts = rss.get_latest_posts_text(limit=3)
                prompt = daily_builder.build_photo_post_prompt(
                    category=photo_category, vibe=photo_vibe, place_info_text=place_info_text, photo_contexts_text=photo_contexts_text, reference_posts=reference_posts
                )

                result = gemini.generate_post(prompt, images=uploaded_photos)
                
                preview_html_raw = result
                for i, photo in enumerate(uploaded_photos):
                    photo.seek(0)
                    b64_data = base64.b64encode(photo.read()).decode('utf-8')
                    mime_type = photo.type if hasattr(photo, 'type') else 'image/jpeg'
                    preview_html_raw = preview_html_raw.replace(f"[PHOTO_{i+1}]", f"data:{mime_type};base64,{b64_data}")
                
                st.session_state.photo_preview_html = formatter.wrap_in_table(f"{photo_category} 기록", preview_html_raw)

                copy_html_raw = result
                for i in range(len(uploaded_photos)):
                    pattern = r'<div[^>]*>\s*<img[^>]*src="\[PHOTO_' + str(i+1) + r'\]"[^>]*>\s*</div>'
                    replacement = f'<p style="text-align: center; color: #e53e3e; font-weight: bold; margin: 30px 0;">[📸 블로그 에디터에서 이곳에 사진 {i+1}을 직접 업로드해주세요]</p>'
                    if re.search(pattern, copy_html_raw):
                        copy_html_raw = re.sub(pattern, replacement, copy_html_raw)
                    else:
                        fallback_pattern = r'<img[^>]*src="\[PHOTO_' + str(i+1) + r'\]"[^>]*>'
                        copy_html_raw = re.sub(fallback_pattern, replacement, copy_html_raw)

                st.session_state.photo_copy_html = formatter.wrap_in_table(f"{photo_category} 기록", copy_html_raw)
                st.success("사진 기반 맞춤형 포스팅 생성이 완료되었습니다!")

    if st.session_state.get("photo_preview_html"):
        st.markdown("---")
        res_tab1, res_tab2, res_tab3 = st.tabs(["👁️ 완벽 미리보기", "📋 블로그 복사용 화면", "📄 HTML 원본 코드"])
        with res_tab1:
            st.info("✨ 실제 사진들이 적용된 완벽한 미리보기입니다.")
            clean_html = st.session_state.photo_preview_html.replace("```html\n", "").replace("```html", "").replace("```", "")
            clean_html = clean_html.replace("MK CINELAB PREVIEW", "MK DAILY RECORD").replace("다른 영화 이야기가", "다른 일상/현장 이야기가")
            show_isolated_html(clean_html, height=1000, scrolling=True)
        with res_tab2:
            st.success("💡 아래 회색 네모 박스 안의 내용을 마우스로 쭉 드래그해서 복사(Ctrl+C)한 뒤 붙여넣기(Ctrl+V) 하세요!")
            clean_copy_html = st.session_state.photo_copy_html.replace("```html\n", "").replace("```html", "").replace("```", "")
            clean_copy_html = clean_copy_html.replace("MK CINELAB PREVIEW", "MK DAILY RECORD").replace("다른 영화 이야기가", "다른 일상/현장 이야기가")
            show_isolated_html(clean_copy_html, height=1000, scrolling=True)
        with res_tab3:
            st.warning("티스토리 등 HTML 소스코드 직접 입력이 가능한 곳을 위한 예비용 코드입니다.")
            clean_code_html = st.session_state.photo_copy_html.replace("MK CINELAB PREVIEW", "MK DAILY RECORD").replace("다른 영화 이야기가", "다른 일상/현장 이야기가")
            st.code(clean_code_html, language="html")

# ==========================================
# [TAB 3] 🤝 모임 후기 포스팅 (신규 추가!)
# ==========================================
with tab3:
    st.subheader("🤝 모임/행사 후기 포스팅")
    st.write("아이디어 랩, 워크숍, 소모임 등 사람들과 함께한 기록을 생생하게 정리해 드립니다.")

    # 1. 장소 검색 (탭 2와 분리된 key 사용)
    st.markdown("#### 📍 1. 모임 장소 검색 (선택)")
    col_region_m, col_search_m, col_btn_m = st.columns([1.5, 3, 1])
    
    with col_region_m:
        region_list_m = ["직접 입력", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        region_option_m = st.selectbox("지역 선택", options=region_list_m, index=0, key="meeting_region", label_visibility="collapsed")
        
    with col_search_m:
        if region_option_m == "직접 입력":
            search_query_m = st.text_input("검색어", placeholder="예: 활동그래, NFM 등", key="meeting_search_input", label_visibility="collapsed")
            target_region_m = ""
        else:
            search_query_m = st.text_input("상호명 검색", placeholder="예: 활동그래", key="meeting_search_input", label_visibility="collapsed")
            target_region_m = region_option_m

    with col_btn_m:
        search_place_btn_m = st.button("네이버 검색", key="meeting_search_btn", use_container_width=True)
    
    if search_place_btn_m and search_query_m:
        final_query_m = f"{target_region_m} {search_query_m}".strip()
        with st.spinner(f"'{final_query_m}' 검색 중..."):
            results_m = naver_client.search_local_place(final_query_m)
            if "error" in results_m:
                st.error(results_m["error"])
            elif results_m.get("items"):
                st.session_state.meeting_search_results = results_m["items"]
                st.session_state.meeting_selected_place = None 
            else:
                st.warning("검색 결과가 없습니다.")

    if st.session_state.meeting_search_results and not st.session_state.meeting_selected_place:
        st.markdown("##### 📌 어느 곳인가요?")
        with st.container(height=300):
            for i, item in enumerate(st.session_state.meeting_search_results):
                title = item['title'].replace('<b>', '').replace('</b>', '')
                category = item['category']
                address = item['roadAddress'] or item['address'] 
                
                col_info, col_sel = st.columns([5, 1])
                with col_info:
                    st.write(f"**{title}** <small>({category}) | 📍 {address}</small>", unsafe_allow_html=True)
                with col_sel:
                    if st.button("선택", key=f"sel_m_place_{i}", use_container_width=True):
                        st.session_state.meeting_selected_place = {"title": title, "category": category, "address": address}
                        st.session_state.meeting_search_results = None
                        st.rerun()
        st.markdown("---")

    if st.session_state.meeting_selected_place:
        p_m = st.session_state.meeting_selected_place
        st.success(f"✅ **{p_m['title']}** (📍 {p_m['address']})")
        if st.button("장소 다시 검색하기", key="reset_m_place_btn"):
            st.session_state.meeting_selected_place = None
            st.rerun()
    st.markdown("---")

    # 2. 모임 정보 및 사진 입력
    st.markdown("#### 📝 2. 모임 정보 및 사진")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        meeting_name = st.text_input("모임명", placeholder="예: 전주국제영화제 티셔츠 디자인 아이디어 랩")
        meeting_date = st.date_input("진행 날짜")
    with col_info2:
        participants = st.text_input("참석자", placeholder="예: 민규, jay, 징징이, 쥐톨, 샤카닝, 낙낙")
        mood = st.selectbox("전체 분위기", ["열정적이고 활기찬", "차분하고 진지한", "화기애애하고 편안한", "전문적이고 학술적인"])

    activities = st.text_area("주요 활동 내용", placeholder="예:\n- 티셔츠 디자인 브레인스토밍\n- 소형 열처리 프린팅 기기 시연\n- 굿즈 및 사은품 증정", height=120)

    uploaded_photos_m = st.file_uploader("현장 사진 업로드 (순서대로)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="meeting_photo_uploader")
    photo_contexts_m = []
    
    if uploaded_photos_m:
        st.caption(f"총 {len(uploaded_photos_m)}장의 사진이 업로드되었습니다.")
        for i, photo in enumerate(uploaded_photos_m):
            col_img, col_text = st.columns([1, 3])
            with col_img:
                st.image(photo, use_container_width=True)
            with col_text:
                caption = st.text_area(f"사진 {i+1} 설명", placeholder="예: 포스트잇으로 아이디어 도출 중인 모습", height=80, key=f"m_photo_cap_{i}")
                photo_contexts_m.append({"photo": photo, "caption": caption})

    st.markdown("---")
    
    generate_meeting_btn = st.button("✨ 모임 후기 포스팅 생성", type="primary", use_container_width=True)

    if generate_meeting_btn:
        if not meeting_name or not activities:
            st.warning("모임명과 주요 활동 내용은 필수입니다!")
        else:
            with st.spinner("모임 현장의 열기를 글로 옮기는 중입니다..."):
                place_info_text_m = ""
                if st.session_state.meeting_selected_place:
                    p = st.session_state.meeting_selected_place
                    place_info_text_m = f"[장소 정보]\n- 상호명: {p['title']}\n- 주소: {p['address']}\n- 카테고리: {p['category']}"
                
                photo_contexts_text_m = ""
                for i, ctx in enumerate(photo_contexts_m):
                    photo_contexts_text_m += f"- 사진 {i+1} 메모: {ctx['caption']}\n"
                
                reference_posts = rss.get_latest_posts_text(limit=3)

                prompt = daily_builder.build_meeting_review_prompt(
                    meeting_name=meeting_name,
                    date=str(meeting_date),
                    participants=participants,
                    activities=activities,
                    mood=mood,
                    place_info_text=place_info_text_m,
                    photo_contexts_text=photo_contexts_text_m,
                    reference_posts=reference_posts
                )

                if uploaded_photos_m:
                    result = gemini.generate_post(prompt, images=uploaded_photos_m)
                else:
                    result = gemini.generate_post(prompt)
                
                preview_html_raw = result
                if uploaded_photos_m:
                    for i, photo in enumerate(uploaded_photos_m):
                        photo.seek(0)
                        b64_data = base64.b64encode(photo.read()).decode('utf-8')
                        mime_type = photo.type if hasattr(photo, 'type') else 'image/jpeg'
                        preview_html_raw = preview_html_raw.replace(f"[PHOTO_{i+1}]", f"data:{mime_type};base64,{b64_data}")
                
                st.session_state.meeting_preview_html = formatter.wrap_in_table("🤝 모임 기록", preview_html_raw)

                copy_html_raw = result
                if uploaded_photos_m:
                    for i in range(len(uploaded_photos_m)):
                        pattern = r'<div[^>]*>\s*<img[^>]*src="\[PHOTO_' + str(i+1) + r'\]"[^>]*>\s*</div>'
                        replacement = f'<p style="text-align: center; color: #e53e3e; font-weight: bold; margin: 30px 0;">[📸 블로그 에디터에서 이곳에 사진 {i+1}을 직접 업로드해주세요]</p>'
                        if re.search(pattern, copy_html_raw):
                            copy_html_raw = re.sub(pattern, replacement, copy_html_raw)
                        else:
                            copy_html_raw = re.sub(r'<img[^>]*src="\[PHOTO_' + str(i+1) + r'\]"[^>]*>', replacement, copy_html_raw)

                st.session_state.meeting_copy_html = formatter.wrap_in_table("🤝 모임 기록", copy_html_raw)
                st.success("모임 후기 포스팅 생성이 완료되었습니다!")

    if st.session_state.get("meeting_preview_html"):
        st.markdown("---")
        res_tab1, res_tab2, res_tab3 = st.tabs(["👁️ 완벽 미리보기", "📋 블로그 복사용 화면", "📄 HTML 원본 코드"])
        
        with res_tab1:
            clean_html = st.session_state.meeting_preview_html.replace("```html\n", "").replace("```html", "").replace("```", "")
            show_isolated_html(clean_html, height=1000, scrolling=True)
            
        with res_tab2:
            st.success("💡 아래 회색 박스 내용을 복사(Ctrl+C)하여 네이버 블로그에 붙여넣기(Ctrl+V) 하세요!")
            clean_copy_html = st.session_state.meeting_copy_html.replace("```html\n", "").replace("```html", "").replace("```", "")
            show_isolated_html(clean_copy_html, height=1000, scrolling=True)

        with res_tab3:
            clean_code_html = st.session_state.meeting_copy_html
            st.code(clean_code_html, language="html")