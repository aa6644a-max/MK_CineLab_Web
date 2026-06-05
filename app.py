import streamlit as st
from datetime import datetime

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="wide")

from mk_theme import inject_css
inject_css()

from tmdb_client import TMDBClient
from db_manager import DBManager

@st.cache_resource(show_spinner=False)
def init_home_engines():
    return TMDBClient(), DBManager()

tmdb, db = init_home_engines()

# ── 상단 바 ────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center;
            padding:0 0 20px; border-bottom:1px solid rgba(212,168,83,0.12); margin-bottom:32px;">
    <div style="display:flex; align-items:center; gap:14px;">
        <div style="width:36px; height:36px; background:#D4A853; border-radius:8px;
                    display:flex; align-items:center; justify-content:center;
                    font-size:18px;">🎬</div>
        <div>
            <div style="font-size:10px; letter-spacing:3px; color:#8B6F47; text-transform:uppercase;">MK CINELAB</div>
            <div style="font-size:16px; font-weight:700; color:#F5F0E8; line-height:1.1;">작업실</div>
        </div>
    </div>
    <div style="font-size:13px; color:rgba(245,240,232,0.4);">좌측 사이드바로 각 페이지 이동</div>
</div>
""", unsafe_allow_html=True)

# ── 메인 2열 레이아웃 ────────────────────────────────────────────────────
main_col, side_col = st.columns([5, 3], gap="large")

with main_col:
    # ── 히어로 배너 ────────────────────────────────────────────────────
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2E1F10 0%, #1C1410 50%, #0D0A07 100%);
        border: 1px solid rgba(212,168,83,0.2);
        border-radius: 16px;
        padding: 40px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position:absolute; top:0; right:0; width:280px; height:100%;
            background: radial-gradient(ellipse at 80% 50%, rgba(212,168,83,0.08) 0%, transparent 70%);
        "></div>
        <div style="
            position:absolute; top:-30px; right:40px;
            font-size:120px; opacity:0.04; line-height:1; user-select:none;
        ">🎬</div>
        <div style="position:relative;">
            <div style="
                display:inline-block; background:rgba(212,168,83,0.12);
                border:1px solid rgba(212,168,83,0.3); border-radius:20px;
                padding:4px 14px; font-size:10px; letter-spacing:2px;
                color:#D4A853; text-transform:uppercase; margin-bottom:16px;
            ">블로그 자동화 작업실</div>
            <h2 style="
                font-size:2rem; font-weight:700; color:#F5F0E8;
                margin:0 0 10px; line-height:1.25;
            ">MK만의 시선으로<br>영화를 기록하다.</h2>
            <p style="
                font-size:14px; color:rgba(245,240,232,0.5);
                margin:0; line-height:1.7; max-width:400px;
            ">PDF 조사부터 포스팅 생성, 썸네일 제작까지.<br>
            아래 작업실 중 원하는 곳으로 이동하세요.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 도구 카드 3종 ──────────────────────────────────────────────────
    t1, t2, t3 = st.columns(3, gap="small")

    CARD_STYLE = """
        background:{bg};
        border:1px solid {border};
        border-radius:14px;
        padding:22px 20px 18px;
        transition:border-color .2s;
        height:160px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
    """

    with t1:
        st.markdown(f"""
        <div style="{CARD_STYLE.format(bg='#241A14', border='rgba(212,168,83,0.18)')}">
            <div>
                <div style="font-size:26px; margin-bottom:8px;">📝</div>
                <div style="font-size:14px; font-weight:700; color:#F5F0E8; margin-bottom:4px;">포스팅 작업실</div>
                <div style="font-size:11px; color:rgba(245,240,232,0.4); line-height:1.5;">
                    PDF 요약 · 리뷰 · 프리뷰<br>큐레이션 · 사진 포스팅
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/01_📝_포스팅.py", label="작업실 열기 →")

    with t2:
        st.markdown(f"""
        <div style="{CARD_STYLE.format(bg='#1E1610', border='rgba(139,111,71,0.25)')}">
            <div>
                <div style="font-size:26px; margin-bottom:8px;">🎨</div>
                <div style="font-size:14px; font-weight:700; color:#F5F0E8; margin-bottom:4px;">이미지 작업실</div>
                <div style="font-size:11px; color:rgba(245,240,232,0.4); line-height:1.5;">
                    썸네일 메이커<br>카드뉴스 4종 세트
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/02_🎨_이미지.py", label="작업실 열기 →")

    with t3:
        st.markdown(f"""
        <div style="{CARD_STYLE.format(bg='#161210', border='rgba(212,168,83,0.1)')}">
            <div>
                <div style="font-size:26px; margin-bottom:8px;">⚙️</div>
                <div style="font-size:14px; font-weight:700; color:#F5F0E8; margin-bottom:4px;">설정</div>
                <div style="font-size:11px; color:rgba(245,240,232,0.4); line-height:1.5;">
                    블로그 데이터 동기화<br>취향 DB 관리
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/03_⚙️_설정.py", label="설정 열기 →")

    st.markdown("<div style='margin:28px 0 16px;'></div>", unsafe_allow_html=True)

    # ── TMDB 주간 트렌딩 ───────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:14px;">
        <span style="font-size:10px; letter-spacing:3px; color:#8B6F47; text-transform:uppercase;">TMDB</span>
        <span style="font-size:16px; font-weight:700; color:#F5F0E8;">이번 주 트렌딩</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        trending = tmdb.get_weekly_trending(limit=6)

    if trending:
        for row_start in range(0, 6, 3):
            cols = st.columns(3, gap="small")
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx >= len(trending):
                    break
                m = trending[idx]
                score_col = "#D4A853" if m["vote_average"] >= 7 else "rgba(245,240,232,0.35)"
                with col:
                    if m["poster_url"]:
                        st.image(m["poster_url"], width='stretch')
                    else:
                        st.markdown('<div style="width:100%;padding-top:150%;background:#241A14;border-radius:6px;"></div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="margin-top:6px;">
                        <div style="font-size:12px; font-weight:700; color:#F5F0E8; line-height:1.3; margin-bottom:2px;">{m['title']}</div>
                        <div style="font-size:10px; color:{score_col};">★ {m['vote_average']}
                            <span style="color:rgba(245,240,232,0.3); margin-left:4px;">{m['release_date']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.caption("트렌딩 데이터를 불러올 수 없습니다.")


# ── 오른쪽 사이드 패널 ─────────────────────────────────────────────────
with side_col:

    # ── DB 현황 ──────────────────────────────────────────────────────
    try:
        all_posts = db.get_all_posts()
        generated_posts = [p for p in all_posts if len(p) > 2 and p[2] != "블로그원본"]
        ref_count = len(all_posts) - len(generated_posts)
        type_counts = {}
        for p in generated_posts:
            t = p[2] if len(p) > 2 else "기타"
            type_counts[t] = type_counts.get(t, 0) + 1

        count_html = "".join(
            f'<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid rgba(212,168,83,0.06);">'
            f'<span style="font-size:12px; color:rgba(245,240,232,0.55);">{k}</span>'
            f'<span style="font-size:13px; font-weight:700; color:#D4A853;">{v}</span>'
            f'</div>'
            for k, v in type_counts.items()
        ) if type_counts else f'<div style="font-size:11px; color:rgba(245,240,232,0.3); padding:8px 0;">생성된 포스팅 없음</div>'

        st.markdown(f"""
        <div style="background:#1E1610; border:1px solid rgba(212,168,83,0.15);
                    border-radius:14px; padding:20px 18px; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <span style="font-size:10px; letter-spacing:2px; color:#8B6F47; text-transform:uppercase;">생성 포스팅</span>
                <span style="font-size:20px; font-weight:700; color:#D4A853;">{len(generated_posts)}<span style="font-size:11px; font-weight:400; color:rgba(245,240,232,0.3); margin-left:4px;">개</span></span>
            </div>
            {count_html}
            <div style="margin-top:10px; padding-top:10px; border-top:1px solid rgba(212,168,83,0.06);
                        font-size:10px; color:rgba(245,240,232,0.25);">
                블로그 원본 레퍼런스 {ref_count}개 별도 보관
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    # ── 최근 포스팅 ─────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:12px;">
        <span style="font-size:10px; letter-spacing:3px; color:#8B6F47; text-transform:uppercase;">RECENT</span>
        <span style="font-size:16px; font-weight:700; color:#F5F0E8;">최근 포스팅</span>
    </div>
    """, unsafe_allow_html=True)

    TYPE_COLOR = {
        "리뷰": "#D4A853", "프리뷰": "#8B6F47", "리스트": "#6B8E8B",
        "정주행": "#8B7B6B", "뉴스": "#6B7B8B", "블로그원본": "#5B5B5B",
    }

    try:
        all_posts = db.get_all_posts()
        # 블로그원본(스타일 레퍼런스용) 제외 — AI 생성 포스팅만 표시
        generated = [p for p in all_posts if len(p) > 2 and p[2] != "블로그원본"]
        recent = list(reversed(generated))[:12]
        if recent:
            items_html = ""
            for post in recent:
                _, title, post_type, date_str, _ = (list(post) + [None] * 5)[:5]
                color = TYPE_COLOR.get(post_type, "#8B6F47")
                try:
                    d = datetime.fromisoformat(str(date_str))
                    date_fmt = d.strftime("%m.%d")
                except Exception:
                    date_fmt = str(date_str)[:5] if date_str else "—"
                safe_title = str(title)[:28] + ("…" if len(str(title)) > 28 else "")
                items_html += f"""
                <div style="display:flex; align-items:center; gap:10px; padding:9px 0;
                            border-bottom:1px solid rgba(212,168,83,0.06);">
                    <div style="width:6px; height:6px; border-radius:50%;
                                background:{color}; flex-shrink:0;"></div>
                    <div style="flex:1; min-width:0;">
                        <div style="font-size:12px; color:#F5F0E8; white-space:nowrap;
                                    overflow:hidden; text-overflow:ellipsis;">{safe_title}</div>
                        <div style="font-size:10px; color:rgba(245,240,232,0.35); margin-top:1px;">{post_type}</div>
                    </div>
                    <div style="font-size:10px; color:rgba(245,240,232,0.25); white-space:nowrap;">{date_fmt}</div>
                </div>
                """
            st.markdown(f"""
            <div style="background:#1A1310; border:1px solid rgba(212,168,83,0.12);
                        border-radius:14px; padding:16px 16px 8px;">
                {items_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#1A1310; border:1px solid rgba(212,168,83,0.08);
                        border-radius:14px; padding:28px 20px; text-align:center;">
                <div style="font-size:24px; margin-bottom:8px; opacity:0.3;">📝</div>
                <div style="font-size:12px; color:rgba(245,240,232,0.35); line-height:1.6;">
                    아직 저장된 포스팅이 없습니다.<br>
                    포스팅 생성 후 💾 저장 버튼을 눌러주세요.
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"DB 오류: {e}")
