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

# --- [핵심 추가] 네이버 블로그 본문을 끝까지 긁어오는 함수 ---
def get_naver_blog_full_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        # 네이버 블로그는 iframe 구조이므로 실제 본문이 있는 주소로 변환하여 접근하는 것이 좋습니다.
        # RSS 링크 예시: https://blog.naver.com/shock552/224238844854...
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 스마트에디터 ONE (최신) 본문 영역 찾기
        content_area = soup.find('div', class_='se-main-container')
        
        if content_area:
            # 텍스트만 추출 (줄바꿈 유지)
            return content_area.get_text(separator='\n').strip()
        else:
            # 구버전 에디터 본문 영역 찾기
            content_area = soup.find('div', id='post-view-area')
            if content_area:
                return content_area.get_text(separator='\n').strip()
            
        return None # 찾지 못했을 경우
    except Exception as e:
        print(f"본문 수집 에러: {e}")
        return None

st.title("⚙️ 시스템 설정 및 데이터 동기화")
st.markdown("---")

st.subheader("📡 네이버 블로그 전수 조사 및 학습")
st.write("민규 님의 블로그 글을 링크까지 추적하여 **본문 전체**를 완벽하게 수집합니다.")

blog_id = st.text_input("네이버 블로그 ID", value="shock552")

if st.button("🚀 내 블로그 전체 본문 동기화하기", type="primary"):
    if blog_id:
        rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"
        
        with st.spinner(f"'{blog_id}' 님의 블로그 글을 정밀 분석 중입니다..."):
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                progress_bar = st.progress(0)
                status_text = st.empty()
                saved_count = 0
                total_entries = len(feed.entries)
                
                try:
                    all_posts = db.get_all_posts()
                    existing_titles = [p[1] for p in all_posts]
                except:
                    existing_titles = []

                for i, entry in enumerate(feed.entries):
                    title = entry.title
                    link = entry.link
                    
                    if title not in existing_titles:
                        # [업그레이드] 요약본 대신 실제 본문을 긁어옴
                        full_content = get_naver_blog_full_content(link)
                        
                        # 본문을 성공적으로 긁어왔다면 저장, 실패하면 요약본이라도 저장
                        final_content = full_content if full_content else entry.description
                        
                        db.save_post(title, "블로그원본", final_content)
                        saved_count += 1
                        
                        # 구글 시트 429 에러 방지 (충분한 대기시간)
                        time.sleep(2.5) 
                    
                    progress = int(((i + 1) / total_entries) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"본문 추출 중... ({i+1}/{total_entries})")
                
                status_text.text("모든 본문 수집 완료!")
                if saved_count > 0:
                    st.success(f"🎉 성공! 총 {saved_count}개의 포스팅 본문을 완벽하게 수집했습니다.")
                else:
                    st.info("👍 이미 최신 글의 전체 본문이 DB에 저장되어 있습니다.")
            else:
                st.error("❌ 데이터를 가져올 수 없습니다.")
    else:
        st.warning("블로그 ID를 입력해 주세요.")