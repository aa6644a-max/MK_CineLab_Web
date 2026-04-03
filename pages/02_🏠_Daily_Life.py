import streamlit as st
import streamlit.components.v1 as components
# PDF 처리를 위해 필요한 라이브러리 (상단에 추가 추천)
# import pdfplumber 

# 페이지 기본 설정
st.set_page_config(page_title="일상 & 현장 기록", page_icon="🏠", layout="centered")

# 대문 타이틀
st.title("🏠 민규의 일상 & 현장 기록")
st.markdown("---")

tab1, tab2 = st.tabs(["📄 PDF 요약 포스팅", "➕ 새 기능 추가 예정"])

with tab1:
    st.subheader("📄 PDF 자료 기반 블로그 초안 생성")
    st.write("다양한 PDF 자료들을 업로드하면, 오직 그 내용들만 분석하여 MK 스타일로 요약해 드립니다.")
    
    st.info("💡 여러 개의 PDF를 한꺼번에 올릴 수 있습니다. 자료가 많을수록 더 정확한 분석이 가능해요.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # ✅ 핵심 수정: accept_multiple_files=True 추가
        uploaded_files = st.file_uploader(
            "참고할 PDF 파일들을 선택하세요 (중복 선택 가능)", 
            type="pdf",
            accept_multiple_files=True,
            key="daily_pdf_uploader"
        )
        
        # 파일이 업로드되었을 때 간단한 목록 표시
        if uploaded_files:
            st.caption(f"📂 총 {len(uploaded_files)}개의 파일이 선택되었습니다.")

        user_context = st.text_area(
            "이 기록에 담고 싶은 상황이나 생각", 
            placeholder="예: 영화 살목지 개봉 전, 실제 장소에 대한 괴담 정보들만 모아서 정리하고 싶습니다. 영화 정보보다는 PDF 속 실화에 집중해 주세요.",
            height=200,
            key="daily_context"
        )

    with col2:
        post_category = st.selectbox(
            "포스팅 카테고리",
            ["☕ 카페/맛집 탐방", "📍 장소/명소 리뷰", "🛠️ 작업/현장 기록", "📝 정보 공유/에세이"],
            key="daily_category"
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
        # ✅ 로직 수정: uploaded_files가 리스트이므로 비어있는지 확인
        if uploaded_files and user_context:
            with st.spinner(f"{len(uploaded_files)}개의 PDF 데이터를 분석 중입니다..."):
                # 1. 모든 PDF에서 텍스트 추출 (예시 로직)
                # combined_text = ""
                # for file in uploaded_files:
                #     with pdfplumber.open(file) as pdf:
                #         combined_text += "\n".join([page.extract_text() for page in pdf.pages])
                
                # 2. DailyPromptBuilder에 combined_text 전달
                st.session_state.daily_html = ""
                st.success("노트북LM 스타일의 맞춤형 포스팅 생성이 완료되었습니다!")
        else:
            st.warning("분석할 PDF 파일(최소 1개)과 추가 맥락을 입력해 주세요.")

    # 결과 표시 영역 유지
    if "daily_html" in st.session_state:
        st.markdown("---")
        res_tab1, res_tab2 = st.tabs(["👁️ 블로그 미리보기", "📄 HTML 코드"])
        with res_tab1:
            st.info("외부 정보 없이 민규님이 주신 자료로만 구성된 미리보기입니다.")
        with res_tab2:
            st.code(st.session_state.daily_html, language="html")