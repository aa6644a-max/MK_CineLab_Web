import streamlit as st
import base64
#import streamlit.components.v1 as components
import pdfplumber  
from DailyPromptBuilder import DailyPromptBuilder
from gemini_client import GeminiClient
from rss_client import RSSClient
from html_formatter import HTMLFormatter

def show_isolated_html(html_str):
    b64 = base64.b64encode(html_str.encode('utf-8')).decode('utf-8')
    iframe_html = f'<iframe src="data:text/html;charset=utf-8;base64,{b64}" width="100%" height="800" style="border:none;"></iframe>'
    
    st.markdown(iframe_html, unsafe_allow_html=True)

# 페이지 기본 설정
st.set_page_config(page_title="일상 & 현장 기록", page_icon="🏠", layout="centered")

# 엔진 초기화
@st.cache_resource(show_spinner=False)
def init_daily_engines():
    return DailyPromptBuilder(), GeminiClient(), RSSClient(), HTMLFormatter()

daily_builder, gemini, rss, formatter = init_daily_engines()

st.title("🏠 민규의 일상 & 현장 기록")
st.markdown("---")

# ✅ 탭 이름 변경
tab1, tab2 = st.tabs(["📄 PDF 요약 포스팅", "📸 사진 기반 포스팅"])

if "daily_html" not in st.session_state: st.session_state.daily_html = None
if "photo_html" not in st.session_state: st.session_state.photo_html = None

# ==========================================
# [TAB 1] 기존 PDF 요약 포스팅 (그대로 유지)
# ==========================================
with tab1:
    st.subheader("📄 PDF 자료 기반 블로그 초안 생성")
    st.write("다양한 PDF 자료들을 업로드하면, 오직 그 내용들만 분석하여 MK 스타일로 요약해 드립니다.")
    
    st.info("💡 여러 개의 PDF를 한꺼번에 올릴 수 있습니다. 자료가 많을수록 더 정확한 분석이 가능해요.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "참고할 PDF 파일들을 선택하세요 (중복 선택 가능)", 
            type="pdf",
            accept_multiple_files=True,
            key="daily_pdf_uploader"
        )
        
        if uploaded_files:
            st.caption(f"📂 총 {len(uploaded_files)}개의 파일이 선택되었습니다.")

        user_context = st.text_area(
            "이 기록에 담고 싶은 상황이나 생각", 
            placeholder="예: 영화 살목지 개봉 전, 실제 장소에 대한 괴담 정보들만 모아서 정리하고 싶습니다. 영화 정보보다는 PDF 속 실화에 집중해 주세요.",
            height=200,
            key="daily_context"
        )

    with col2:
        post_category = st.text_input(
            "포스팅 카테고리 입력",
            placeholder="예: ☕ 카페 탐방, 🛠️ 현장 일지 등",
            key="daily_category_input"
        )
        
        writing_vibe = st.select_slider(
            "글의 감성 농도",
            options=["담백하게", "차분하게", "다정하게", "감성 가득", "위트 있게"],
            value="다정하게",
            key="daily_vibe"
        )
        
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
                    st.error("PDF에서텍스트를 추출할 수 없습니다. 이미지로 된 PDF인지 확인해 주세요.")
                else:
                    reference_posts = rss.get_latest_posts_text(limit=3)
                    
                    prompt = daily_builder.build_pdf_summary_prompt(
                        combined_text, 
                        f"[{post_category} / {writing_vibe} 분위기] {user_context}", 
                        reference_posts
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
# [TAB 2] 💡 신규 추가: 사진 기반 포스팅 UI
# ==========================================
with tab2:
    st.subheader("📸 사진 기반 일상/맛집/현장 포스팅")
    st.write("순서대로 사진을 업로드하고 짧은 캡션을 달아주세요. 알아서 흐름에 맞는 포스팅을 써드립니다.")

    # 1. 장소 검색 (현재는 UI만)
    st.markdown("#### 📍 1. 장소 정보 입력 (선택)")
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_query = st.text_input("상호명 또는 장소 검색", placeholder="예: 남산동 카페, 무촌리 현장 등", label_visibility="collapsed")
    with col_btn:
        st.button("네이버 검색", key="search_place_btn", use_container_width=True)
    st.info("※ 네이버 API 장소 검색 연동은 다음 단계에서 연결할 예정입니다!")

    st.markdown("---")

    # 2. 사진 업로드
    st.markdown("#### 🖼️ 2. 사진 업로드 및 메모")
    uploaded_photos = st.file_uploader(
        "포스팅에 들어갈 사진들을 순서대로 올려주세요.",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="photo_uploader"
    )

    photo_contexts = []
    if uploaded_photos:
        st.caption(f"총 {len(uploaded_photos)}장의 사진이 업로드되었습니다.")
        
        # 각 사진마다 썸네일과 텍스트 입력칸을 병렬 배치
        for i, photo in enumerate(uploaded_photos):
            col_img, col_text = st.columns([1, 3])
            
            with col_img:
                st.image(photo, use_container_width=True)
                
            with col_text:
                caption = st.text_area(
                    f"사진 {i+1} 설명", 
                    placeholder="예: 타설 전 철근 배근 완료 상태 / 우드톤 가구 조립 중 / 시그니처 메뉴인 전복 솥밥", 
                    height=100,
                    key=f"photo_cap_{i}"
                )
                photo_contexts.append({"photo": photo, "caption": caption})

    st.markdown("---")

    # 3. 포스팅 설정
    st.markdown("#### 📝 3. 포스팅 설정")
    col_cat, col_vibe = st.columns(2)
    with col_cat:
        photo_category = st.selectbox(
            "포스팅 카테고리",
            options=["🍽️ 맛집/카페 탐방", "🛠️ 현장/건축 일지", "🎬 일상 및 모임"],
            key="photo_category"
        )
    with col_vibe:
        photo_vibe = st.select_slider(
            "글의 감성 농도",
            options=["담백하게", "전문적으로", "차분하게", "다정하게", "위트 있게"],
            value="차분하게",
            key="photo_vibe"
        )

    st.write("") # 여백
    generate_photo_btn = st.button("📸 사진 포스팅 생성", type="primary", use_container_width=True)

    if generate_photo_btn:
        if not uploaded_photos:
            st.warning("먼저 사진을 업로드해 주세요!")
        else:
            # TODO: 다음 단계에서 Gemini 멀티모달 프롬프트 연동
            st.success("로직 연결은 다음 단계에서 진행됩니다! UI 레이아웃이 마음에 드는지 확인해 주세요 😉")