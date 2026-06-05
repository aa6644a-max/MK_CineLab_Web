import streamlit as st
from datetime import datetime
import html as _html

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="wide")

from mk_theme import inject_css
inject_css()

from navbar import render_navbar
render_navbar()

from tmdb_client import TMDBClient
from db_manager import DBManager

@st.cache_resource(show_spinner=False)
def init_home_engines():
    return TMDBClient(), DBManager()

tmdb, db = init_home_engines()

# ── 메인 2열 레이아웃 ────────────────────────────────────────────────────
main_col, side_col = st.columns([5, 3], gap="large")

with main_col:
    st.markdown("""
<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:14px;">
<span style="font-size:10px;letter-spacing:3px;color:#8B6F47;text-transform:uppercase;">TMDB</span>
<span style="font-size:16px;font-weight:700;color:#F5F0E8;">이번 주 트렌딩</span>
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
                    st.markdown(
f'<div style="margin-top:6px;">'
f'<div style="font-size:12px;font-weight:700;color:#F5F0E8;line-height:1.3;margin-bottom:2px;">{_html.escape(m["title"])}</div>'
f'<div style="font-size:10px;color:{score_col};">★ {m["vote_average"]}'
f'<span style="color:rgba(245,240,232,0.3);margin-left:4px;">{m["release_date"]}</span>'
f'</div></div>',
                        unsafe_allow_html=True)
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
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(212,168,83,0.06);">'
            f'<span style="font-size:12px;color:rgba(245,240,232,0.55);">{k}</span>'
            f'<span style="font-size:13px;font-weight:700;color:#D4A853;">{v}</span>'
            f'</div>'
            for k, v in type_counts.items()
        ) if type_counts else '<div style="font-size:11px;color:rgba(245,240,232,0.3);padding:8px 0;">생성된 포스팅 없음</div>'

        st.markdown(
f'<div style="background:#1E1610;border:1px solid rgba(212,168,83,0.15);border-radius:14px;padding:20px 18px;margin-bottom:20px;">'
f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
f'<span style="font-size:10px;letter-spacing:2px;color:#8B6F47;text-transform:uppercase;">생성 포스팅</span>'
f'<span style="font-size:20px;font-weight:700;color:#D4A853;">{len(generated_posts)}<span style="font-size:11px;font-weight:400;color:rgba(245,240,232,0.3);margin-left:4px;">개</span></span>'
f'</div>'
f'{count_html}'
f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(212,168,83,0.06);font-size:10px;color:rgba(245,240,232,0.25);">블로그 원본 레퍼런스 {ref_count}개 별도 보관</div>'
f'</div>',
            unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"DB 연결 오류: {e}")

    # ── 최근 포스팅 ─────────────────────────────────────────────────
    st.markdown(
'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:12px;">'
'<span style="font-size:10px;letter-spacing:3px;color:#8B6F47;text-transform:uppercase;">RECENT</span>'
'<span style="font-size:16px;font-weight:700;color:#F5F0E8;">최근 포스팅</span>'
'</div>',
        unsafe_allow_html=True)

    TYPE_COLOR = {
        "리뷰": "#D4A853", "프리뷰": "#8B6F47", "리스트": "#6B8E8B",
        "정주행": "#8B7B6B", "뉴스": "#6B8E8B", "블로그원본": "#5B5B5B",
    }

    try:
        all_posts = db.get_all_posts()
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
                safe_title = _html.escape(str(title)[:28]) + ("…" if len(str(title)) > 28 else "")
                items_html += (
f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid rgba(212,168,83,0.06);">'
f'<div style="width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0;"></div>'
f'<div style="flex:1;min-width:0;">'
f'<div style="font-size:12px;color:#F5F0E8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{safe_title}</div>'
f'<div style="font-size:10px;color:rgba(245,240,232,0.35);margin-top:1px;">{post_type}</div>'
f'</div>'
f'<div style="font-size:10px;color:rgba(245,240,232,0.25);white-space:nowrap;">{date_fmt}</div>'
f'</div>'
                )
            st.markdown(
f'<div style="background:#1A1310;border:1px solid rgba(212,168,83,0.12);border-radius:14px;padding:16px 16px 8px;">{items_html}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
'<div style="background:#1A1310;border:1px solid rgba(212,168,83,0.08);border-radius:14px;padding:28px 20px;text-align:center;">'
'<div style="font-size:24px;margin-bottom:8px;opacity:0.3;">📝</div>'
'<div style="font-size:12px;color:rgba(245,240,232,0.35);line-height:1.6;">아직 저장된 포스팅이 없습니다.<br>포스팅 생성 후 💾 저장 버튼을 눌러주세요.</div>'
'</div>',
                unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"DB 오류: {e}")
