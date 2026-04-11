import streamlit as st
import base64
import re  
import pdfplumber  
# 💡 경고 예방을 위해 components import는 제거하고 iframe 방식을 사용합니다.
from DailyPromptBuilder import DailyPromptBuilder
from gemini_client import GeminiClient
from rss_client import RSSClient
from html_formatter import HTMLFormatter
from naver_client import NaverClient  

def show_isolated_html(html_str, height=1000, scrolling=True):
    """
    💡 TypeError를 방지하기 위해 매개변수를 확장했습니다.
    st.components.v1.html 대신 iframe 주입 방식을 사용합니다.
    """
    if not html_str:
        return
        
    # AI 마크다운 기호 제거
    clean_html = html_str.replace("```html\n", "").replace("```html", "").replace("```", "")
    
    # 스크롤 여부 설정
    scroll_attr = "yes" if scrolling else "no"
    
    # 2026년 이후에도 안전한 Base64 iframe 방식
    try:
        b64 = base64.b64encode(clean_html.encode('utf-8')).decode('utf-8')
        iframe_html = f'<iframe src="data:text/html;charset=utf-8;base64,{b64}" width="100%" height="{height}" scrolling="{scroll_attr}" style="border:none;"></iframe>'
        st.markdown(iframe_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"미리보기 생성 중 오류 발생: {e}")

# 페이지 기본 설정
st.set_page_config(page_title="일상 & 현장 기록", page_icon="🏠", layout="centered")

# 엔진 초기화
@st.cache_resource(show_spinner=False)
def init_daily_engines():
    return DailyPromptBuilder(), GeminiClient(), RSSClient(), HTMLFormatter(), NaverClient()

daily_builder, gemini, rss, formatter, naver_client = init_daily_engines()

st.title("🏠 민규의 일상 & 현장 기록")
st.markdown("---")

# ✅ 탭 구성
tab1, tab2, tab3 = st.tabs(["📄 PDF 요약 포스팅", "📸 사진 기반 포스팅", "🤝 모임 후기 포스팅"])

# 세션 스테이트 초기화
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
# [TAB 1] PDF 요약 포스팅
# ==========================================
with tab1:
    st.subheader("📄 PDF 자료 기반 블로그 초안 생성")
    st.write("다양한 PDF 자료들을 업로드하면, 오직 그 내용들만 분석하여 MK 스타일로 요약해 드립니다.")
    st.info("💡 여러 개의 PDF를 한꺼번에 올릴 수 있습니다.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader("참고할 PDF 선택", type="pdf", accept_multiple_files=True, key="daily_pdf_uploader")
        user_context = st.text_area("맥락 입력", height=200, key="daily_context")
    with col2:
        post_category = st.text_input("카테고리", placeholder="예: 🛠️ 현장 일지", key="daily_category_input")
        writing_vibe = st.select_slider("감성 농도", options=["담백하게", "차분하게", "다정하게", "감성 가득", "위트 있게"], value="다정하게")
        generate_btn = st.button("✨ MK 스타일 생성", type="primary", use_container_width=True)

    if generate_btn and uploaded_files and user_context:
        with st.spinner("PDF 분석 중..."):
            combined_text = ""
            for file in uploaded_files:
                with pdfplumber.open(file) as pdf:
                    combined_text += "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            
            reference_posts = rss.get_latest_posts_text(limit=3)
            prompt = daily_builder.build_pdf_summary_prompt(combined_text, f"[{post_category}] {user_context}", reference_posts)
            result = gemini.generate_post(prompt)
            st.session_state.daily_html = formatter.wrap_in_table(f"{post_category} 기록", result)

    if st.session_state.daily_html:
        res_t1, res_t2 = st.tabs(["👁️ 블로그 미리보기", "📄 코드"])
        with res_t1: show_isolated_html(st.session_state.daily_html)
        with res_t2: st.code(st.session_state.daily_html, language="html")

# ==========================================
# [TAB 2] 사진 기반 포스팅
# ==========================================
with tab2:
    st.subheader("📸 사진 기반 일상/맛집/현장 포스팅")
    # 1. 장소 검색
    st.markdown("#### 📍 1. 장소 정보 입력")
    col_region, col_search, col_btn = st.columns([1.5, 3, 1])
    with col_region:
        region_list = ["직접 입력", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        region_option = st.selectbox("지역 선택", options=region_list, index=0, label_visibility="collapsed")
    with col_search:
        search_query = st.text_input("상호명", placeholder="예: 남산동 스타벅스", label_visibility="collapsed")
    with col_btn:
        if st.button("네이버 검색", key="search_place_btn", use_container_width=True):
            final_query = f"{region_option if region_option != '직접 입력' else ''} {search_query}".strip()
            results = naver_client.search_local_place(final_query)
            st.session_state.place_search_results = results.get("items", [])
            st.session_state.selected_place = None

    if st.session_state.place_search_results and not st.session_state.selected_place:
        with st.container(height=300):
            for i, item in enumerate(st.session_state.place_search_results):
                title = item['title'].replace('<b>', '').replace('</b>', '')
                if st.button(f"선택: {title}", key=f"sel_p_{i}"):
                    st.session_state.selected_place = {"title": title, "address": item['roadAddress'], "category": item['category']}
                    st.session_state.place_search_results = None
                    st.rerun()

    if st.session_state.selected_place:
        st.success(f"✅ 선택된 장소: {st.session_state.selected_place['title']}")
        if st.button("장소 초기화"):
            st.session_state.selected_place = None
            st.rerun()

    # 2. 사진 업로드
    st.markdown("#### 🖼️ 2. 사진 업로드 및 메모")
    uploaded_photos = st.file_uploader("사진들을 올려주세요", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="photo_uploader")
    photo_contexts = []
    if uploaded_photos:
        for i, photo in enumerate(uploaded_photos):
            col_img, col_text = st.columns([1, 3])
            with col_img: st.image(photo, use_container_width=True)
            with col_text: photo_contexts.append({"photo": photo, "caption": st.text_area(f"사진 {i+1} 설명", key=f"photo_cap_{i}")})

    if st.button("📸 사진 포스팅 생성", type="primary", use_container_width=True):
        if uploaded_photos:
            with st.spinner("포스팅 작성 중..."):
                place_info = f"[장소] {st.session_state.selected_place['title']}" if st.session_state.selected_place else ""
                photo_memo = "\n".join([f"- {c['caption']}" for c in photo_contexts])
                prompt = daily_builder.build_photo_post_prompt(category="일상", vibe="차분하게", place_info_text=place_info, photo_contexts_text=photo_memo, reference_posts="")
                result = gemini.generate_post(prompt, images=uploaded_photos)
                
                # Base64 이미지 변환 및 HTML 생성 로직
                preview_html = result
                for i, photo in enumerate(uploaded_photos):
                    photo.seek(0)
                    b64_data = base64.b64encode(photo.read()).decode('utf-8')
                    preview_html = preview_html.replace(f"[PHOTO_{i+1}]", f"data:image/jpeg;base64,{b64_data}")
                
                st.session_state.photo_preview_html = formatter.wrap_in_table("일상 기록", preview_html)
                st.session_state.photo_copy_html = formatter.wrap_in_table("일상 기록", result) # 복사용은 원본 유지

    if st.session_state.get("photo_preview_html"):
        st.markdown("---")
        res_tab1, res_tab2 = st.tabs(["👁️ 완벽 미리보기", "📄 코드"])
        with res_tab1:
            clean_html = st.session_state.photo_preview_html.replace("MK CINELAB PREVIEW", "MK DAILY RECORD")
            show_isolated_html(clean_html, height=1000, scrolling=True)
        with res_tab2: st.code(st.session_state.photo_copy_html, language="html")

# ==========================================
# [TAB 3] 모임 후기 포스팅
# ==========================================
with tab3:
    st.subheader("🤝 모임/행사 후기 포스팅")
    meeting_name = st.text_input("모임명", placeholder="예: 아이디어 랩")
    activities = st.text_area("주요 활동 내용", height=150)
    uploaded_photos_m = st.file_uploader("현장 사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="meeting_photo_uploader")
    
    if st.button("✨ 모임 후기 생성", type="primary", use_container_width=True):
        if meeting_name and activities:
            with st.spinner("작성 중..."):
                prompt = daily_builder.build_meeting_review_prompt(meeting_name=meeting_name, activities=activities, date="2026", participants="민규", mood="활기찬", place_info_text="", photo_contexts_text="", reference_posts="")
                result = gemini.generate_post(prompt, images=uploaded_photos_m)
                st.session_state.meeting_preview_html = formatter.wrap_in_table("🤝 모임 기록", result)
                st.session_state.meeting_copy_html = formatter.wrap_in_table("🤝 모임 기록", result)

    if st.session_state.get("meeting_preview_html"):
        res_m1, res_m2 = st.tabs(["👁️ 미리보기", "📄 코드"])
        with res_m1:
            show_isolated_html(st.session_state.meeting_preview_html, height=1000, scrolling=True)
        with res_m2: st.code(st.session_state.meeting_copy_html, language="html")