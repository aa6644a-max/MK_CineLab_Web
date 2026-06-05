import streamlit as st
from datetime import datetime

st.set_page_config(page_title="MK 작업실", page_icon="🎬", layout="wide")

from mk_theme import inject_css
inject_css()

from tmdb_client import TMDBClient
from db_manager import DBManager

@st.cache_resource(show_spinner=False)
def init_home_engines():
    return TMDBClient(), DBManager()

tmdb, db = init_home_engines()


# ── 헤더 ──────────────────────────────────────────────
st.markdown("""
<div style="padding:2.5rem 0 1.5rem; border-bottom:1px solid rgba(212,168,83,0.15); margin-bottom:2rem;">
    <p style="font-size:10px; letter-spacing:4px; color:#8B6F47; text-transform:uppercase; margin:0 0 6px;">MK CINELAB</p>
    <h1 style="font-size:2rem; font-weight:700; color:#F5F0E8; margin:0; border:none; padding:0;">작업실 대시보드</h1>
</div>
""", unsafe_allow_html=True)

# ── 빠른 이동 ──────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("**📝 포스팅 작업실**")
        st.caption("PDF 요약 · 리뷰 · 프리뷰 · 큐레이션 · 정주행 · 사진")
        st.page_link("pages/01_📝_포스팅.py", label="이동", icon="→")
with c2:
    with st.container(border=True):
        st.markdown("**🎨 이미지 작업실**")
        st.caption("썸네일 메이커 · 카드뉴스 4종")
        st.page_link("pages/02_🎨_이미지.py", label="이동", icon="→")
with c3:
    with st.container(border=True):
        st.markdown("**⚙️ 설정**")
        st.caption("네이버 블로그 데이터 동기화")
        st.page_link("pages/03_⚙️_설정.py", label="이동", icon="→")

st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)

# ── 본문: 2열 ─────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

# ── 왼쪽: TMDB 주간 트렌딩 ────────────────────────────
with left:
    st.markdown("""
    <p style="font-size:10px; letter-spacing:3px; color:#8B6F47; text-transform:uppercase; margin-bottom:4px;">TMDB</p>
    <h3 style="margin:0 0 16px; color:#F5F0E8;">이번 주 트렌딩</h3>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        trending = tmdb.get_weekly_trending(limit=6)

    if trending:
        g1, g2, g3 = st.columns(3)
        cols = [g1, g2, g3]
        for i, movie in enumerate(trending):
            with cols[i % 3]:
                score_color = "#D4A853" if movie["vote_average"] >= 7 else "rgba(245,240,232,0.45)"
                poster_html = (
                    f'<img src="{movie["poster_url"]}" style="width:100%;border-radius:6px;display:block;margin-bottom:8px;">'
                    if movie["poster_url"]
                    else '<div style="width:100%;padding-top:150%;background:#241A14;border-radius:6px;margin-bottom:8px;"></div>'
                )
                st.markdown(f"""
                <div style="margin-bottom:20px;">
                    {poster_html}
                    <div style="font-size:12px; font-weight:700; color:#F5F0E8; line-height:1.3; margin-bottom:4px;">
                        {movie['title']}
                    </div>
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span style="font-size:10px; color:{score_color};">★ {movie['vote_average']}</span>
                        <span style="font-size:10px; color:rgba(245,240,232,0.3);">{movie['release_date']}</span>
                    </div>
                    {f'<div style="font-size:10px; color:rgba(245,240,232,0.4); margin-top:4px; line-height:1.4;">{movie["overview"]}…</div>' if movie["overview"] else ""}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("트렌딩 데이터를 불러올 수 없습니다.")

# ── 오른쪽: 최근 포스팅 ───────────────────────────────
with right:
    st.markdown("""
    <p style="font-size:10px; letter-spacing:3px; color:#8B6F47; text-transform:uppercase; margin-bottom:4px;">DB</p>
    <h3 style="margin:0 0 16px; color:#F5F0E8;">최근 포스팅</h3>
    """, unsafe_allow_html=True)

    TYPE_BADGE = {
        "리뷰":    ("#D4A853", "#1a0f00"),
        "프리뷰":  ("#8B6F47", "#F5F0E8"),
        "리스트":  ("#2E2018", "#D4A853"),
        "정주행":  ("#2E2018", "#D4A853"),
        "뉴스":    ("#2E2018", "#8B6F47"),
        "블로그원본": ("#130E0A", "#8B6F47"),
    }

    try:
        all_posts = db.get_all_posts()
        recent = list(reversed(all_posts))[:10]

        if recent:
            for post in recent:
                _, title, post_type, date_str, _ = (post + [None] * 5)[:5]
                bg, fg = TYPE_BADGE.get(post_type, ("#2E2018", "#F5F0E8"))
                try:
                    d = datetime.fromisoformat(str(date_str))
                    date_fmt = d.strftime("%m.%d")
                except Exception:
                    date_fmt = str(date_str)[:5] if date_str else "—"
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:10px; padding:10px 0;
                            border-bottom:1px solid rgba(212,168,83,0.08);">
                    <span style="background:{bg}; color:{fg}; font-size:9px; font-weight:700;
                                 padding:2px 7px; border-radius:20px; white-space:nowrap;
                                 border:1px solid rgba(212,168,83,0.2);">{post_type}</span>
                    <span style="font-size:13px; color:#F5F0E8; flex:1; overflow:hidden;
                                 text-overflow:ellipsis; white-space:nowrap;">{title}</span>
                    <span style="font-size:10px; color:rgba(245,240,232,0.3); white-space:nowrap;">{date_fmt}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("저장된 포스팅이 없습니다.")
    except Exception as e:
        st.caption(f"DB 연결 오류: {e}")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── DB 요약 카운터 ─────────────────────────────────
    try:
        all_posts = db.get_all_posts()
        type_counts = {}
        for p in all_posts:
            t = p[2] if len(p) > 2 else "기타"
            type_counts[t] = type_counts.get(t, 0) + 1

        st.markdown(f"""
        <div style="background:#241A14; border:1px solid rgba(212,168,83,0.15);
                    border-radius:10px; padding:16px;">
            <p style="font-size:10px; letter-spacing:2px; color:#8B6F47;
                      text-transform:uppercase; margin:0 0 12px;">포스팅 DB 현황</p>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                {"".join(
                    f'<span style="background:#2E2018; color:#D4A853; font-size:11px; padding:4px 10px; border-radius:20px;">{k} {v}</span>'
                    for k, v in type_counts.items()
                )}
            </div>
            <p style="font-size:12px; color:rgba(245,240,232,0.45); margin:12px 0 0;">
                총 {len(all_posts)}개 기록
            </p>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass
