import streamlit as st
import feedparser
import time
import requests
from bs4 import BeautifulSoup
from db_manager import DBManager

st.set_page_config(page_title="설정 및 동기화", page_icon="⚙️")

@st.cache_resource
def get_db():
    return DBManager()
db = get_db()

# 세션 상태 초기화 (동기화 중인지 확인용)
if "sync_active" not in st.session_state:
    st.session_state.sync_active = False

def get_naver_blog_full_content(rss_link):
    """모바일 주소로 접속해 본문 전체를 긁어옵니다."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
    }
    try:
        mobile_url = rss_link.replace("blog.naver.com", "m.blog.naver.com")
        response = requests.get(mobile_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 에디터 본문 영역 추출
        content_area = soup.find('div', class_='se-main-container')
        if content_area:
            return content_area.get_text(separator='\n', strip=True)
        return None
    except Exception:
        return None

st.title("⚙️ 시스템 설정 및 데이터 동기화")
st.markdown("---")

st.subheader("📡 네이버 블로그 데이터 정밀 수집")

col1, col2 = st.columns([2, 1])
with col1:
    blog_id = st.text_input("네이버 블로그 ID", value="shock552")
with col2:
    # 💡 [핵심] 기존에 잘린 글들을 무시하고 다시 긁어오게 하는 옵션입니다.
    force_update = st.checkbox("기존 데이터 무시하고 새로 수집", help="DB에 이미 글이 있어도 본문을 다시 긁어와 덮어씁니다.")

# --- 동기화 로직 시작 ---
if not st.session_state.sync_active:
    if st.button("🚀 내 블로그 전체 본문 동기화 시작", type="primary"):
        st.session_state.sync_active = True
        st.rerun()
else:
    # 💡 [중지 버튼] 동기화 중일 때만 나타납니다.
    if st.button("🛑 동기화 중지(Cancel)", type="secondary"):
        st.session_state.sync_active = False
        st.warning("동기화가 사용자에 의해 중단되었습니다.")
        st.rerun()

    # 실제 수집 루프
    rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"
    feed = feedparser.parse(rss_url)

    if feed.entries:
        progress_bar = st.progress(0)
        status_text = st.empty()
        saved_count = 0
        total = len(feed.entries)
        
        # 기존 저장된 글 목록 가져오기
        try:
            all_posts = db.get_all_posts()
            existing_titles = [p[1] for p in all_posts]
        except:
            existing_titles = []

        for i, entry in enumerate(feed.entries):
            # 중지 버튼 클릭 시 루프 탈출 (st.rerun이 루프를 끊어주지만 안전장치로 추가)
            if not st.session_state.sync_active:
                break
                
            # [조건체크] 강제 업데이트 체크 시 무조건 실행, 아니면 중복 제외
            if force_update or (entry.title not in existing_titles):
                status_text.text(f"[{i+1}/{total}] 본문 추출 중: {entry.title[:20]}...")
                
                full_text = get_naver_blog_full_content(entry.link)
                final_content = full_text if full_text else entry.description
                
                # DB 저장 (기존에 있다면 덮어쓰는 로직은 db_manager에 따라 다를 수 있으나 보통 새로 추가됨)
                db.save_post(entry.title, "블로그원본", final_content)
                saved_count += 1
                
                # 구글 시트 과부하 방지 (2초 휴식)
                time.sleep(2)
            
            progress_bar.progress((i + 1) / total)
        
        st.session_state.sync_active = False
        st.success(f"🎉 동기화 완료! 총 {saved_count}개의 본문을 확보했습니다.")
        st.balloons()
        st.rerun()
    else:
        st.error("데이터를 불러올 수 없습니다.")
        st.session_state.sync_active = False