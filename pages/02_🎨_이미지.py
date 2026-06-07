import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MK 이미지 작업실", page_icon="🎨", layout="wide")

from mk_theme import inject_css
inject_css()

from navbar import render_navbar
render_navbar()


st.title("🎨 MK 이미지 작업실")

import os
_studio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "studio", "MK_STUDIO.html")
with open(_studio_path, "r", encoding="utf-8") as f:
    _studio_html = f.read()

components.html(_studio_html, height=900, scrolling=False)
