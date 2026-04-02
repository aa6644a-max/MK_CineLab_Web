import streamlit as st
import feedparser
import time
from db_manager import DBManager

st.set_page_config(page_title="설정 및 동기화", page_icon="⚙️")

# DB 연결
@st.cache_resource
def get_db():
    return DBManager()
db = get_db()

st.title("⚙️ 시스템 설정 및 데이터 동기화")
st.markdown("---")

st.subheader("📡 네이버 블로그 최신 글 자동 학습")
st.write("민규 님의 네이버 블로그 최신 글(최대 50개)을 긁어와 제미나이의 문체 학습용 DB에 저장합니다.")

# 블로그 ID 입력 (기본값으로 민규 님 ID 세팅)
blog_id = st.text_input("네이버 블로그 ID", value="shock552")

if st.button("🚀 내 블로그 최신 글 DB에 동기화하기", type="primary"):
    if blog_id:
        rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"
        
        with st.spinner(f"'{blog_id}' 님의 블로그에서 데이터를 수집하고 있습니다..."):
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                # 진행률 바 생성
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                saved_count = 0
                total_entries = len(feed.entries)
                
                # DB에 이미 있는 글 제목들을 미리 가져와서 중복 방지
                try:
                    all_posts = db.get_all_posts()
                    existing_titles = [p[1] for p in all_posts] # p[1]이 제목이라고 가정
                except:
                    existing_titles = []

                for i, entry in enumerate(feed.entries):
                    title = entry.title
                    content = entry.description # 본문 요약 내용
                    
                    # 중복되지 않은 새 글만 저장
                    if title not in existing_titles:
                        # 포스팅 종류를 '블로그원본'으로 통일해서 저장
                        db.save_post(title, "블로그원본", content)
                        saved_count += 1
                    
                    # 진행률 업데이트
                    progress = int(((i + 1) / total_entries) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"수집 진행 중... ({i+1}/{total_entries})")
                    time.sleep(0.05) # 너무 빠르면 진행률 바가 안 보여서 살짝 딜레이
                
                status_text.text("수집 완료!")
                if saved_count > 0:
                    st.success(f"🎉 성공! 총 {saved_count}개의 새로운 글을 찾아 DB에 저장했습니다.")
                else:
                    st.info("👍 이미 모든 최신 글이 DB에 저장되어 있습니다. (업데이트할 새 글이 없습니다.)")
            else:
                st.error("❌ 글을 가져오지 못했습니다. 블로그 ID를 다시 확인해 주세요.")
    else:
        st.warning("블로그 ID를 입력해 주세요.")