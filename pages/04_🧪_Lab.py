import streamlit as st
import re
from gemini_client import GeminiClient

st.set_page_config(page_title="실험실 - AI 사진 큐레이터", page_icon="🧪", layout="centered")

# Gemini 엔진만 가볍게 초기화
@st.cache_resource(show_spinner=False)
def init_gemini():
    return GeminiClient()

gemini = init_gemini()

st.title("🧪 실험실: AI 사진 큐레이터")
st.markdown("블로그 포스팅 전, 찍어둔 **수십 장의 사진을 던져주고 베스트 컷만 추출해내는 기능**을 테스트합니다.")

# 세션 스테이트 초기화
if "selected_photos" not in st.session_state: st.session_state.selected_photos = None
if "selected_indices" not in st.session_state: st.session_state.selected_indices = None

# 1. 파일 업로드
uploaded_photos = st.file_uploader(
    "모임이나 현장에서 찍은 사진을 한꺼번에 올려보세요 (최대 50장 권장)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_photos:
    st.info(f"총 {len(uploaded_photos)}장의 사진이 업로드되었습니다.")
    
    # 원본 사진 작게 미리보기 (토글)
    with st.expander("업로드된 원본 사진 전체 보기"):
        cols = st.columns(5)
        for i, photo in enumerate(uploaded_photos):
            # 💡 수정 포인트: 컬럼 안에서는 알아서 꽉 차므로 width 설정을 제거했습니다.
            cols[i % 5].image(photo, caption=f"No. {i+1}")

    target_count = st.slider("이 중에서 몇 장을 추려낼까요?", min_value=3, max_value=20, value=7)
    
    # 💡 수정 포인트: 버튼은 경고가 뜨더라도 안전한 기존 방식(use_container_width)으로 둡니다.
    if st.button("✨ 베스트 컷 자동 선별하기", type="primary", use_container_width=True):
        with st.spinner(f"AI 에디터가 {len(uploaded_photos)}장의 사진을 눈으로 훑어보며 흐름을 짜는 중입니다... (10~20초 소요)"):
            
            prompt = f"""
            당신은 매거진의 수석 사진 편집자입니다.
            제가 총 {len(uploaded_photos)}장의 오프라인 모임/행사 사진을 순서대로 제공했습니다.
            
            이 사진들 중에서 글의 '기승전결(장소 분위기 -> 모임 시작 -> 활동 모습 -> 결과물 및 단체샷)'을 
            가장 잘 보여줄 수 있는 핵심 사진 딱 {target_count}장만 선별해 주세요.
            구도가 너무 겹치거나 흔들린 사진은 피해주세요.

            [출력 규칙 - 절대 준수]
            오직 당신이 선택한 사진의 번호(1부터 시작)만 쉼표로 구분해서 적어주세요. 
            인사말, 설명, 기호 등 다른 텍스트는 일절 출력하지 마세요.
            예시: 1, 4, 12, 25, 30
            """
            
            try:
                # Gemini Vision API 호출 (전체 이미지 전송)
                result = gemini.generate_post(prompt, images=uploaded_photos)
                
                # 결과 텍스트에서 숫자만 정규식으로 안전하게 추출
                numbers = re.findall(r'\d+', result)
                # 추출한 숫자를 실제 인덱스(0부터 시작)로 변환
                extracted_indices = [int(n) - 1 for n in numbers if 0 <= int(n) - 1 < len(uploaded_photos)]
                
                # 중복 제거 및 오름차순 정렬
                extracted_indices = sorted(list(set(extracted_indices)))
                
                if not extracted_indices:
                    st.error("AI가 사진 번호를 제대로 추출하지 못했습니다. 결과가 텍스트로 섞여 나왔을 수 있습니다.")
                    st.write("AI 응답 원문:", result)
                else:
                    st.success(f"🎉 성공! AI가 총 {len(extracted_indices)}장의 베스트 컷을 골라냈습니다.")
                    
                    st.session_state.selected_photos = [uploaded_photos[i] for i in extracted_indices]
                    st.session_state.selected_indices = extracted_indices
                    
            except Exception as e:
                st.error(f"사진 선별 중 통신 오류가 발생했습니다: {e}")

# 2. 선별 결과 출력
if st.session_state.get("selected_photos"):
    st.markdown("---")
    st.markdown("### 📸 AI가 픽한 스토리라인")
    st.caption("AI가 골라낸 사진들의 순서입니다. 이 흐름대로 포스팅하면 자연스럽습니다.")
    
    sel_cols = st.columns(3)
    for idx, (original_idx, photo) in enumerate(zip(st.session_state.selected_indices, st.session_state.selected_photos)):
        # 💡 수정 포인트: 여기도 image 태그에서 width 설정 제거
        sel_cols[idx % 3].image(photo, caption=f"Original No. {original_idx + 1}")

    st.info("💡 여기서 선별된 사진들이 마음에 든다면, 해당 사진들만 따로 빼두신 후 **[02 Daily Life]의 모임 후기 탭**에 올려서 자동 포스팅을 진행하시면 완벽합니다!")