import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(page_title="일상 & 현장 기록", page_icon="🏠", layout="centered")

# 대문 타이틀
st.title("🏠 민규의 일상 & 현장 기록")
st.markdown("---")

# 탭 구성: 첫 번째 탭을 'PDF 요약 포스팅'으로 설정
tab1, tab2 = st.tabs(["📄 PDF 요약 포스팅", "➕ 새 기능 추가 예정"])

with tab1:
    st.subheader("📄 PDF 자료 기반 블로그 초안 생성")
    st.write("메뉴판, 리플렛, 기획서 등 PDF 자료를 업로드하면 MK 스타일의 감성적인 포스팅으로 변환합니다.")
    
    # 1. 입력 영역 (Input Section)
    st.info("💡 PDF 속의 텍스트 정보와 민규님의 상황을 결합하여 풍성한 글을 만듭니다.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # PDF 업로드
        uploaded_file = st.file_uploader(
            "참고할 PDF 파일을 선택하세요", 
            type="pdf",
            key="daily_pdf_uploader"
        )
        
        # 추가 맥락 입력
        user_context = st.text_area(
            "이 기록에 담고 싶은 상황이나 생각", 
            placeholder="예: 남산동 카페 프로젝트 가구 조립 중에 잠시 쉬면서 읽어본 안내서입니다. 현장의 생생한 느낌을 담고 싶어요.",
            height=200,
            key="daily_context"
        )

    with col2:
        # 포스팅 테마 설정
        post_category = st.selectbox(
            "포스팅 카테고리",
            ["☕ 카페/맛집 탐방", "📍 장소/명소 리뷰", "🛠️ 작업/현장 기록", "📝 정보 공유/에세이"],
            key="daily_category"
        )
        
        # 문체 온도 조절
        writing_vibe = st.select_slider(
            "글의 감성 농도",
            options=["담백하게", "차분하게", "다정하게", "감성 가득", "위트 있게"],
            value="다정하게",
            key="daily_vibe"
        )
        
        st.write("---")
        # 생성 버튼
        generate_btn = st.button("✨ MK 스타일 포스팅 생성", type="primary", use_container_width=True)

    # 2. 결과 출력 영역 (Output Section)
    if generate_btn:
        if uploaded_file and user_context:
            with st.spinner("PDF 데이터를 분석하여 MK만의 문체로 다듬는 중..."):
                # 실제 로직 연결 예정 (Gemini + DailyPromptBuilder)
                st.session_state.daily_html = ""
                st.success("포스팅 초안 작성이 완료되었습니다!")
        else:
            st.warning("PDF 파일과 추가 맥락을 모두 입력해 주셔야 작성이 가능해요.")

    # 결과 표시 (데이터가 있을 때만)
    if "daily_html" in st.session_state:
        st.markdown("---")
        res_tab1, res_tab2 = st.tabs(["👁️ 블로그 미리보기", "📄 HTML 코드"])
        
        with res_tab1:
            st.info("네이버 블로그에 최적화된 레이아웃으로 미리보기를 제공합니다.")
            # components.html(st.session_state.daily_html, height=600, scrolling=True)
            
        with res_tab2:
            st.code(st.session_state.daily_html, language="html")
            
        if st.button("💾 이 포스팅을 일상 DB에 저장하기"):
            st.toast("민규님의 소중한 기록이 DB에 저장되었습니다!", icon="✅")

with tab2:
    st.empty()
    st.center_text = st.markdown("""
        <div style="text-align: center; padding: 50px; color: #888;">
            <h3>🛠️ 새로운 기능이 준비 중입니다</h3>
            <p>인스타그램 캡션 기반 글쓰기, 현장 사진 자동 일기 등<br>민규님의 일상을 기록할 더 다양한 방법을 고민하고 있어요.</p>
        </div>
    """, unsafe_allow_html=True)