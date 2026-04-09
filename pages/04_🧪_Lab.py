import streamlit as st
import re
import io
from PIL import Image
from gemini_client import GeminiClient

st.set_page_config(page_title="실험실 - AI 사진 큐레이터", page_icon="🧪", layout="centered")

# ==========================================
# 💡 핵심 추가: 이미지 최적화 (다이어트) 클래스
# ==========================================
class OptimizedPhoto:
    """GeminiClient와 완벽하게 호환되도록 만든 가짜 파일 객체"""
    def __init__(self, byte_data, original_name):
        self.name = original_name
        self.type = "image/jpeg"
        self._data = io.BytesIO(byte_data)
        
    def read(self):
        return self._data.read()
        
    def seek(self, offset):
        self._data.seek(offset)

def optimize_image(uploaded_file):
    """사진을 AI 분석용(저용량 썸네일)으로 압축하는 함수"""
    img = Image.open(uploaded_file)
    # 아이폰 등에서 찍힌 사진의 색상 모드 오류 방지
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # 가로세로 최대 600px로 축소 (웹 렌더링 & API 전송 속도 극대화)
    img.thumbnail((600, 600))
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=80)
    
    return OptimizedPhoto(output.getvalue(), uploaded_file.name)

# ==========================================

# Gemini 엔진 가볍게 초기화
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
uploaded_photos_raw = st.file_uploader(
    "모임이나 현장에서 찍은 사진을 한꺼번에 올려보세요 (최대 50장 권장)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_photos_raw:
    st.info(f"총 {len(uploaded_photos_raw)}장의 사진이 업로드되었습니다. AI 분석을 위해 가볍게 최적화 중입니다...")
    
    # 💡 원본은 보존하고, AI 전송 및 미리보기용 '가벼운 사진' 리스트 생성
    uploaded_photos_lite = []
    for raw_photo in uploaded_photos_raw:
        uploaded_photos_lite.append(optimize_image(raw_photo))
    
    # 원본(을 축소한) 사진 작게 미리보기 (토글)
    with st.expander("업로드된 사진 전체 보기"):
        cols = st.columns(5)
        for i, photo_lite in enumerate(uploaded_photos_lite):
            photo_lite.seek(0) 
            cols[i % 5].image(photo_lite.read(), caption=f"No. {i+1}")
            photo_lite.seek(0) # 읽고 나서 다시 포인터를 처음으로 되돌림

    target_count = st.slider("이 중에서 몇 장을 추려낼까요?", min_value=3, max_value=20, value=7)
    
    if st.button("✨ 베스트 컷 자동 선별하기", type="primary"):
        with st.spinner(f"AI 에디터가 {len(uploaded_photos_lite)}장의 사진 흐름을 파악하는 중입니다... (10~30초 소요)"):
            
            prompt = f"""
            당신은 매거진의 수석 사진 편집자입니다.
            제가 총 {len(uploaded_photos_lite)}장의 오프라인 모임/행사 사진을 순서대로 제공했습니다.
            
            이 사진들 중에서 글의 '기승전결(장소 분위기 -> 모임 시작 -> 활동 모습 -> 결과물 및 단체샷)'을 
            가장 잘 보여줄 수 있는 핵심 사진 딱 {target_count}장만 선별해 주세요.
            구도가 너무 겹치거나 흔들린 사진은 피해주세요.

            [출력 규칙 - 절대 준수]
            오직 당신이 선택한 사진의 번호(1부터 시작)만 쉼표로 구분해서 적어주세요. 
            인사말, 설명, 기호 등 다른 텍스트는 일절 출력하지 마세요.
            예시: 1, 4, 12, 25, 30
            """
            
            try:
                # 무거운 원본 대신 가벼운 사진(lite)들을 Gemini로 전송
                result = gemini.generate_post(prompt, images=uploaded_photos_lite)
                
                # 결과 텍스트에서 숫자만 정규식으로 안전하게 추출
                numbers = re.findall(r'\d+', result)
                extracted_indices = [int(n) - 1 for n in numbers if 0 <= int(n) - 1 < len(uploaded_photos_lite)]
                
                # 중복 제거 및 오름차순 정렬
                extracted_indices = sorted(list(set(extracted_indices)))
                
                if not extracted_indices:
                    st.error("AI가 사진 번호를 제대로 추출하지 못했습니다. 결과가 텍스트로 섞여 나왔을 수 있습니다.")
                    st.write("AI 응답 원문:", result)
                else:
                    st.success(f"🎉 성공! AI가 총 {len(extracted_indices)}장의 베스트 컷을 골라냈습니다.")
                    
                    # 💡 최종 결과는 화질이 좋은 '원본(raw)' 사진으로 꺼내옵니다.
                    st.session_state.selected_photos = [uploaded_photos_raw[i] for i in extracted_indices]
                    st.session_state.selected_indices = extracted_indices
                    
            except Exception as e:
                st.error(f"사진 선별 중 통신 오류가 발생했습니다: {e}")

# 2. 선별 결과 출력
if st.session_state.get("selected_photos"):
    st.markdown("---")
    st.markdown("### 📸 AI가 픽한 스토리라인")
    st.caption("AI가 골라낸 사진들의 순서입니다. 이 흐름대로 포스팅하면 자연스럽습니다.")
    
    sel_cols = st.columns(3)
    for idx, (original_idx, raw_photo) in enumerate(zip(st.session_state.selected_indices, st.session_state.selected_photos)):
        sel_cols[idx % 3].image(raw_photo, caption=f"Original No. {original_idx + 1}")

    st.info("💡 선별된 사진 번호를 확인하셨나요? 해당 번호의 원본 사진들만 바탕화면에 따로 모아두신 후 **[02 Daily Life]의 모임 후기 탭**에 올려서 자동 포스팅을 진행하시면 완벽합니다!")