import streamlit as st
from gemini_client import GeminiClient

# 페이지 기본 설정
st.set_page_config(page_title="장난감 공간 - AI 방탈출", page_icon="👾", layout="centered")

st.title("👾 무한 텍스트 방탈출 (TRPG)")
st.markdown("제미나이(GM)가 만들어내는 미지의 공간에서 탈출해 보세요! 어떤 행동이든 텍스트로 자유롭게 입력할 수 있습니다.")
st.markdown("---")

# 1. 제미나이 엔진 초기화
@st.cache_resource(show_spinner=False)
def get_gemini():
    return GeminiClient()

gemini = get_gemini()

# 2. 게임 상태 및 대화 기록 보관소 (Session State)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
    # 게임 시작 상황 만들기 (첫 프롬프트)
    start_prompt = """
    당신은 텍스트 방탈출 게임의 게임 마스터(GM)입니다.
    플레이어는 방금 낯설고 어두운 방에서 눈을 떴습니다. 
    주변의 으스스하고 미스터리한 환경을 시각적으로 묘사하고, 플레이어가 당장 상호작용할 수 있는 사물 2~3가지를 제시해 주세요.
    절대 플레이어의 행동을 대신 결정하지 말고, 마지막엔 항상 "어떻게 하시겠습니까?"로 질문을 던지세요.
    답변은 너무 길지 않게 3~4문장으로 몰입감 있게 작성해 주세요.
    """
    
    with st.spinner("맵을 생성하는 중..."):
        initial_scene = gemini.generate_post(start_prompt)
        # GM의 첫 대사를 기록에 저장
        st.session_state.chat_history.append({"role": "assistant", "content": initial_scene})

# 3. 화면에 지금까지의 대화 기록 출력하기
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. 사용자 행동 입력 및 제미나이(GM)의 판정
if user_action := st.chat_input("행동을 입력하세요 (예: 책상을 살펴본다, 문을 발로 찬다)"):
    
    # 사용자가 입력한 행동을 화면에 바로 띄우고 기록에 저장
    st.session_state.chat_history.append({"role": "user", "content": user_action})
    with st.chat_message("user"):
        st.markdown(user_action)

    # 제미나이에게 상황을 이해시키기 위해 과거 대화 내용 묶어주기
    # (너무 길어지면 제미나이가 헷갈릴 수 있으니 최근 6개 대화만 전달)
    history_text = "당신은 방탈출 게임의 게임 마스터(GM)입니다. 이전 상황들을 참고하여 플레이어의 행동에 대한 결과를 판정하고 묘사해 주세요. 답변은 3~4문장으로 짧고 몰입감 있게 작성하세요.\n\n[이전 상황]\n"
    for m in st.session_state.chat_history[-6:]:
        speaker = "GM" if m["role"] == "assistant" else "Player"
        history_text += f"{speaker}: {m['content']}\n"
    
    history_text += "\n위 맥락을 이어서, Player의 마지막 행동에 대한 결과를 흥미롭게 묘사하고 다음 선택을 유도하세요."

    # 제미나이의 응답 받아오기
    with st.chat_message("assistant"):
        with st.spinner("GM이 행동의 결과를 판정 중입니다..."):
            response = gemini.generate_post(history_text)
            st.markdown(response)
    
    # GM의 판정 결과를 기록에 저장
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # 💡 초기화 버튼: 게임이 막혔을 때 처음부터 다시 시작
    st.button("🔄 게임 다시 시작하기", on_click=lambda: st.session_state.pop("chat_history"))