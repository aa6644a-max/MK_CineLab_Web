import streamlit as st

def render_navbar():
    c0, c1, c2, c3, c4, _ = st.columns([3, 0.9, 1.2, 1.1, 0.9, 1.5])
    with c0:
        st.markdown(
            '<span style="font-size:15px;font-weight:800;color:#D4A853;'
            'letter-spacing:3px;line-height:36px;display:block;'
            'text-transform:uppercase;">🎬 MK CINELAB</span>',
            unsafe_allow_html=True,
        )
    with c1:
        st.page_link("app.py", label="홈")
    with c2:
        st.page_link("pages/01_📝_포스팅.py", label="포스팅")
    with c3:
        st.page_link("pages/02_🎨_이미지.py", label="이미지")
    with c4:
        st.page_link("pages/03_⚙️_설정.py", label="설정")
    st.markdown(
        '<div style="height:1px;background:rgba(212,168,83,0.15);'
        'margin:4px 0 20px;"></div>',
        unsafe_allow_html=True,
    )
