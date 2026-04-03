import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="일상 & 현장 기록", page_icon="🏠", layout="centered")

st.title("🏠 민규의 일상 & 현장 기록")
st.markdown("""
PDF 자료와 오늘의 이야기를 결합하여 **MK 스타일의 블로그 포스팅**을 완성합니다. 
카페, 장소, 현장 작업 등 어떤 일상도 좋습니다.
---
""")

# 1. 입력 영역 (Input Section)
st.subheader("📝 오늘의 기록 준비")
col1, col2 = st.columns([2, 1])

with col1:
    # PDF 업로드
    uploaded_file = st.file_uploader(
        "참고할 PDF 자료 (메뉴판, 기획서, 안내문 등)", 
        type="pdf",
        help="PDF 내의 텍스트를 분석하여 포스팅 정보로 활용합니다."
    )
    
    # 추가 맥락 입력
    user_context = st.text_area(
        "오늘의 상황이나 덧붙이고 싶은 생각", 
        placeholder="예: Namsan-dong 카페 현장에서 가구 조립을 마친 후 근처에서 발견한 조용한 카페입니다.",
        height=150
    )

with col2:
    # 포스팅 성격 선택
    post_type = st.selectbox(
        "포스팅 테마",
        ["☕ 카페/맛집 탐방", "📍 명소/장소 리뷰", "🛠️ 현장/작업 기록", "📝 일반 정보 공유", "🌿 일상 에세이"]
    )
    
    # 감성 온도 조절 (Gemini에게 전달할 힌트)
    vibe = st.select_slider(
        "글의 분위기",
        options=["담백한", "차분한", "다정한", "감성적인", "위트있는"],
        value="다정한"
    )

# 2. 실행 버튼
st.markdown("---")
if st.button("✨ MK 스타일 포스팅 생성하기", type="primary", use_container_width=True):
    if uploaded_file and user_context:
        with st.spinner("PDF를 분석하고 문장을 다듬는 중입니다..."):
            # TODO: PDF 텍스트 추출 및 Gemini 연동 로직
            st.session_state.daily_result = "현재 프롬프트 빌더 제작 전 단계입니다. 레이아웃 확인용 예시입니다."
    else:
        st.warning("PDF 파일과 추가 맥락을 모두 입력해 주세요.")

# 3. 결과 출력 영역 (Output Section)
if "daily_result" in st.session_state:
    st.subheader("✅ 완성된 포스팅 확인")
    
    # 저장 버튼
    if st.button("💾 이 기록을 DB에 저장하기"):
        st.toast("기록이 안전하게 저장되었습니다!", icon="🎉")

    # 결과물 탭 (코드 및 미리보기)
    res_tab1, res_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
    
    with res_tab1:
        st.code("", language="html")
        
    with res_tab2:
        # 미리보기 예시 (실제 구현 시 생성된 HTML 삽입)
        st.info("여기에 블로그에 실제로 올라갈 모습이 렌더링됩니다.")
        # components.html(st.session_state.daily_result, height=600, scrolling=True)

# 4. 최근 작성한 일상 목록 (간단한 히스토리)
with st.expander("📂 최근 작성한 일상 기록 보기"):
    st.write("- 2026-03-25: 남산동 카페 가구 조립 기록")
    st.write("- 2026-03-16: 거창 무촌리 건축 현장 일지")