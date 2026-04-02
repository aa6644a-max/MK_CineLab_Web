import feedparser

# 민규 님의 네이버 블로그 ID
blog_id = "shock552"
rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"

print(f"📡 '{blog_id}' 님의 네이버 블로그 글을 불러오는 중...\n")

# RSS 피드 파싱(분석)
feed = feedparser.parse(rss_url)

# 결과 출력
if feed.entries:
    print(f"✅ 성공! 총 {len(feed.entries)}개의 최신 글을 찾았습니다.\n")
    
    # 최신 글 5개만 뽑아서 제목과 링크 출력
    for i, entry in enumerate(feed.entries[:5], start=1):
        print(f"[{i}] 제목: {entry.title}")
        print(f"    링크: {entry.link}")
        print("-" * 40)
else:
    print("❌ 글을 가져오지 못했습니다. 블로그 ID나 비공개 설정을 확인해 주세요.")