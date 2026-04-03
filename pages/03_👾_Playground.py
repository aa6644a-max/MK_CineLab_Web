import streamlit as st
import random
import copy

# 페이지 기본 설정
st.set_page_config(page_title="장난감 공간 - 2048", page_icon="👾", layout="centered")

# --- 2048 게임 로직 함수들 ---
def init_game():
    st.session_state.board = [[0] * 4 for _ in range(4)]
    st.session_state.score = 0
    st.session_state.game_over = False
    add_new_tile()
    add_new_tile()

def add_new_tile():
    empty_cells = [(r, c) for r in range(4) for c in range(4) if st.session_state.board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        st.session_state.board[r][c] = 4 if random.random() < 0.1 else 2

def compress(board):
    new_board = [[0] * 4 for _ in range(4)]
    for r in range(4):
        pos = 0
        for c in range(4):
            if board[r][c] != 0:
                new_board[r][pos] = board[r][c]
                pos += 1
    return new_board

def merge(board):
    for r in range(4):
        for c in range(3):
            if board[r][c] != 0 and board[r][c] == board[r][c + 1]:
                board[r][c] *= 2
                st.session_state.score += board[r][c]
                board[r][c + 1] = 0
    return board

def reverse(board):
    new_board = []
    for r in range(4):
        new_board.append(list(reversed(board[r])))
    return new_board

def transpose(board):
    new_board = [[0] * 4 for _ in range(4)]
    for r in range(4):
        for c in range(4):
            new_board[r][c] = board[c][r]
    return new_board

def move(direction):
    board = st.session_state.board
    original_board = copy.deepcopy(board)

    if direction == 'LEFT':
        board = compress(board)
        board = merge(board)
        board = compress(board)
    elif direction == 'RIGHT':
        board = reverse(board)
        board = compress(board)
        board = merge(board)
        board = compress(board)
        board = reverse(board)
    elif direction == 'UP':
        board = transpose(board)
        board = compress(board)
        board = merge(board)
        board = compress(board)
        board = transpose(board)
    elif direction == 'DOWN':
        board = transpose(board)
        board = reverse(board)
        board = compress(board)
        board = merge(board)
        board = compress(board)
        board = reverse(board)
        board = transpose(board)

    st.session_state.board = board
    
    # 보드가 변했다면 새 타일 추가
    if board != original_board:
        add_new_tile()
        check_game_over()

def check_game_over():
    board = st.session_state.board
    # 빈칸이 있으면 게임 오버 아님
    if any(0 in row for row in board):
        return
    # 병합 가능한 타일이 있으면 게임 오버 아님
    for r in range(4):
        for c in range(3):
            if board[r][c] == board[r][c+1]: return
    for r in range(3):
        for c in range(4):
            if board[r][c] == board[r+1][c]: return
    st.session_state.game_over = True

# --- 타일 색상 매핑 ---
COLORS = {
    0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
}

# --- UI 렌더링 ---
st.title("👾 장난감 공간: 2048 게임")
st.markdown("모바일에서도 하단 버튼을 눌러 플레이할 수 있습니다!")

if 'board' not in st.session_state:
    init_game()

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader(f"점수: **{st.session_state.score}**")
with col2:
    if st.button("🔄 다시 시작"):
        init_game()
        st.rerun()

st.markdown("---")

# 보드판 그리기
board_html = "<div style='background-color:#bbada0; padding:10px; border-radius:10px; width:100%; max-width:400px; margin:auto;'>"
for row in st.session_state.board:
    board_html += "<div style='display:flex; justify-content:space-between; margin-bottom:10px;'>"
    for val in row:
        bg_color = COLORS.get(val, "#3c3a32") # 2048 이상은 어두운 색
        text_color = "#776e65" if val <= 4 else "#f9f6f2"
        display_val = val if val > 0 else ""
        board_html += f"<div style='background-color:{bg_color}; color:{text_color}; width:23%; aspect-ratio:1; display:flex; justify-content:center; align-items:center; font-size:24px; font-weight:bold; border-radius:5px;'>{display_val}</div>"
    board_html += "</div>"
board_html += "</div>"

st.markdown(board_html, unsafe_allow_html=True)

if st.session_state.game_over:
    st.error("💀 게임 오버! 더 이상 움직일 수 없습니다.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 모바일 조작 버튼 (화면 터치용) ---
st.markdown("<div style='text-align:center;'><b>조작 버튼</b></div>", unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3 = st.columns([1,1,1])
with btn_col2:
    if st.button("⬆️", use_container_width=True): move('UP')
    
btn_col4, btn_col5, btn_col6 = st.columns([1,1,1])
with btn_col4:
    if st.button("⬅️", use_container_width=True): move('LEFT')
with btn_col5:
    if st.button("⬇️", use_container_width=True): move('DOWN')
with btn_col6:
    if st.button("➡️", use_container_width=True): move('RIGHT')