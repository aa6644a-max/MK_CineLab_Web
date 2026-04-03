import feedparser
from bs4 import BeautifulSoup

class RSSClient:
    def __init__(self, blog_id="shock552"):
        # 민규 님의 네이버 블로그 RSS 주소
        self.rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"

    def get_latest_posts_text(self, limit=3):
        """
        RSS에서 최신 글을 가져와 제미나이가 읽기 좋게 순수 텍스트로 변환합니다.
        limit: 제미나이의 토큰(기억력) 한도를 고려해 최신 글 3~5개만 가져오는 것이 좋습니다.
        """
        try:
            feed = feedparser.parse(self.rss_url)
            posts_text = []
            
            # 최신 글부터 limit 개수만큼 반복
            for entry in feed.entries[:limit]:
                title = entry.title
                
                # 네이버 블로그 RSS는 description 안에 HTML 형태로 본문이 들어있음
                # BeautifulSoup을 이용해 HTML 태그를 싹 발라내고 순수 텍스트만 추출
                soup = BeautifulSoup(entry.description, 'html.parser')
                pure_text = soup.get_text(separator=' ', strip=True)
                
                posts_text.append(f"[제목: {title}]\n{pure_text}\n")
            
            # 여러 개의 글을 하나의 긴 텍스트로 합쳐서 반환
            return "\n\n---다음 글---\n\n".join(posts_text)
            
        except Exception as e:
            print(f"RSS 크롤링 중 에러 발생: {e}")
            return ""