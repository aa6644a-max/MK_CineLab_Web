import streamlit as st
import html as _html

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="wide")

from mk_theme import inject_css
inject_css()

from navbar import render_navbar
render_navbar()

from tmdb_client import TMDBClient

@st.cache_resource(show_spinner=False)
def init_home_engines():
    return TMDBClient()

tmdb = init_home_engines()

st.markdown(
'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:18px;">'
'<span style="font-size:10px;letter-spacing:3px;color:#8B6F47;text-transform:uppercase;">TMDB</span>'
'<span style="font-size:18px;font-weight:700;color:#F5F0E8;">이번 주 트렌딩</span>'
'</div>',
    unsafe_allow_html=True)

with st.spinner(""):
    trending = tmdb.get_weekly_trending(limit=6)

if trending:
    for row_start in range(0, 6, 3):
        cols = st.columns(3, gap="medium")
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
f'<div style="margin-top:8px;margin-bottom:16px;">'
f'<div style="font-size:13px;font-weight:700;color:#F5F0E8;line-height:1.3;margin-bottom:3px;">{_html.escape(m["title"])}</div>'
f'<div style="font-size:11px;color:{score_col};">★ {m["vote_average"]}'
f'<span style="color:rgba(245,240,232,0.3);margin-left:6px;">{m["release_date"]}</span>'
f'</div></div>',
                    unsafe_allow_html=True)
else:
    st.caption("트렌딩 데이터를 불러올 수 없습니다.")
