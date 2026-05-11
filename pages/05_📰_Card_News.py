import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="카드뉴스 메이커", page_icon="📰", layout="wide")

CARD_NEWS_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MK CINELAB 카드뉴스 메이커</title>
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
  :root {
    --bg: #0c0b0a;
    --surface: #161412;
    --surface2: #1e1b18;
    --border: rgba(255,255,255,0.08);
    --accent: #d4a574;
    --accent2: #e8c49a;
    --text: #f0ebe4;
    --text-muted: rgba(240,235,228,0.5);
    --text-dim: rgba(240,235,228,0.25);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Pretendard', -apple-system, sans-serif;
    min-height: 100vh;
  }

  .app {
    display: grid;
    grid-template-columns: 380px 1fr;
    min-height: 100vh;
  }

  /* SIDEBAR */
  .sidebar {
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 28px 24px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .sidebar-logo {
    font-size: 13px;
    letter-spacing: 3px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  .sidebar-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 28px;
    line-height: 1.3;
  }

  .section { margin-bottom: 24px; }

  .section-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-label::after {
    content: '';
    flex: 1;
    height: 0.5px;
    background: var(--border);
  }

  .field { margin-bottom: 10px; }

  .field label {
    display: block;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 5px;
    letter-spacing: 0.3px;
  }

  .field input[type="text"],
  .field textarea,
  .field input[type="date"],
  .field input[type="time"] {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 9px 12px;
    color: var(--text);
    font-family: 'Pretendard', sans-serif;
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s;
    resize: vertical;
  }

  .field input[type="text"]:focus,
  .field textarea:focus,
  .field input[type="date"]:focus,
  .field input[type="time"]:focus {
    border-color: var(--accent);
  }

  .field textarea { min-height: 72px; }

  .field input[type="color"] {
    width: 100%;
    height: 36px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    padding: 2px 4px;
  }

  .upload-zone {
    border: 1.5px dashed var(--border);
    border-radius: 10px;
    padding: 18px 12px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
    position: relative;
  }
  .upload-zone:hover { border-color: var(--accent); background: rgba(212,165,116,0.04); }
  .upload-zone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  .upload-zone span { font-size: 11px; color: var(--text-muted); }
  .upload-zone .preview-img {
    width: 100%; border-radius: 8px; margin-top: 8px;
    max-height: 120px; object-fit: cover; display: none;
  }

  .card-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 20px;
    background: var(--surface2);
    border-radius: 10px;
    padding: 4px;
  }
  .tab-btn {
    flex: 1;
    background: none;
    border: none;
    padding: 7px 0;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    border-radius: 7px;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Pretendard', sans-serif;
  }
  .tab-btn.active {
    background: var(--accent);
    color: #1a0f00;
  }

  .tab-panel { display: none; }
  .tab-panel.active { display: block; }

  .sidebar-actions {
    margin-top: auto;
    padding-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .btn-download {
    width: 100%;
    padding: 12px;
    background: var(--accent);
    color: #1a0f00;
    border: none;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    font-family: 'Pretendard', sans-serif;
    letter-spacing: 0.3px;
    transition: opacity 0.2s;
  }
  .btn-download:hover { opacity: 0.88; }

  /* PREVIEW AREA */
  .preview-area {
    background: var(--bg);
    padding: 40px 32px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .preview-header {
    width: 100%;
    max-width: 900px;
    margin-bottom: 28px;
  }

  .preview-header-title {
    font-size: 13px;
    color: var(--text-muted);
    letter-spacing: 1px;
    font-weight: 400;
  }

  .cards-container {
    width: 100%;
    max-width: 900px;
    display: flex;
    flex-direction: column;
    gap: 32px;
    align-items: center;
  }

  .canvas-wrapper {
    width: 100%;
    max-width: 540px;
    position: relative;
  }

  .canvas-num {
    position: absolute;
    top: -22px;
    left: 0;
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .canvas-card {
    width: 100%;
    aspect-ratio: 4/5;
    border-radius: 0;
    overflow: hidden;
    position: relative;
    font-family: 'Pretendard', sans-serif;
  }

  /* CARD 1 - COVER */
  .card1 { background: #1a1510; }

  .card1-bg {
    position: absolute; inset: 0;
    background-size: cover;
    background-position: center;
    transition: opacity 0.4s;
  }

  .card1-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(
      to bottom,
      rgba(0,0,0,0.15) 0%,
      rgba(0,0,0,0.05) 25%,
      rgba(0,0,0,0.4) 55%,
      rgba(0,0,0,0.88) 100%
    );
  }

  .card1-logo {
    position: absolute;
    top: 4.5%; right: 5%;
    font-size: clamp(7px, 1.5vw, 11px);
    letter-spacing: 3px;
    color: rgba(255,255,255,0.75);
    border: 0.8px solid rgba(255,255,255,0.35);
    padding: 3px 10px;
    border-radius: 3px;
  }

  .card1-bottom {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 5% 6% 6%;
    display: flex;
    flex-direction: column;
  }

  .card1-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 0.8px solid rgba(212,165,116,0.7);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: clamp(7px, 1.2vw, 9.5px);
    color: var(--accent2);
    width: fit-content;
    margin-bottom: 3.5%;
    letter-spacing: 1px;
  }

  .badge-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .card1-eyebrow {
    font-size: clamp(7px, 1.3vw, 10px);
    color: rgba(212,165,116,0.8);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 2%;
    font-weight: 400;
  }

  .card1-title {
    font-size: clamp(18px, 5vw, 38px);
    font-weight: 700;
    color: #fff;
    line-height: 1.2;
    margin-bottom: 1%;
  }

  .card1-title-en {
    font-size: clamp(8px, 1.5vw, 11px);
    color: rgba(255,255,255,0.4);
    letter-spacing: 1px;
    margin-bottom: 4%;
  }

  .card1-divider {
    height: 0.5px;
    background: rgba(255,255,255,0.18);
    margin-bottom: 3.5%;
  }

  .card1-meta {
    display: flex;
    gap: 5%;
    flex-wrap: wrap;
  }

  .card1-meta-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: clamp(7px, 1.3vw, 10px);
    color: rgba(255,255,255,0.72);
  }

  .card1-meta-item svg {
    width: clamp(9px, 1.5vw, 12px);
    height: clamp(9px, 1.5vw, 12px);
    stroke: var(--accent);
    fill: none;
    flex-shrink: 0;
  }

  /* CARD 2 - INFO */
  .card2 { background: #0e0c0a; }

  .card2-photo {
    height: 42%;
    position: relative;
    overflow: hidden;
    background: #1e1a15;
  }

  .card2-photo-bg {
    position: absolute; inset: 0;
    background-size: cover;
    background-position: center;
  }

  .card2-photo-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.6));
  }

  .card2-photo-label {
    position: absolute;
    bottom: 5%; left: 5%;
    font-size: clamp(10px, 2.5vw, 18px);
    color: rgba(255,255,255,0.9);
  }

  .card2-body {
    height: 58%;
    padding: 5% 6%;
    display: flex;
    flex-direction: column;
  }

  .card2-eyebrow {
    font-size: clamp(7px, 1.1vw, 9px);
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 5%;
  }

  .card2-info-list {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .card2-info-row {
    display: flex;
    align-items: center;
    gap: 4%;
    padding: 3.5% 0;
    border-bottom: 0.5px solid rgba(255,255,255,0.06);
  }
  .card2-info-row:last-of-type { border-bottom: none; }

  .card2-info-icon {
    width: clamp(14px, 2.5vw, 20px);
    height: clamp(14px, 2.5vw, 20px);
    stroke: var(--accent);
    fill: none;
    flex-shrink: 0;
  }

  .card2-info-key {
    font-size: clamp(7px, 1.1vw, 9px);
    color: rgba(255,255,255,0.35);
    min-width: 15%;
    letter-spacing: 0.5px;
  }

  .card2-info-val {
    font-size: clamp(9px, 1.6vw, 12px);
    color: rgba(255,255,255,0.88);
    font-weight: 500;
    flex: 1;
    line-height: 1.4;
  }

  .card2-include {
    margin-top: auto;
    background: rgba(212,165,116,0.08);
    border: 0.5px solid rgba(212,165,116,0.25);
    border-radius: 8px;
    padding: 3% 4%;
    font-size: clamp(8px, 1.3vw, 10px);
    color: rgba(255,255,255,0.6);
    line-height: 1.6;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .card2-include svg {
    width: clamp(10px, 1.8vw, 14px);
    height: clamp(10px, 1.8vw, 14px);
    stroke: var(--accent);
    fill: none;
    flex-shrink: 0;
  }

  /* CARD 3 - 모임 소개 */
  .card3 { background: #0e0c0a; }

  .card3-photo {
    height: 35%;
    position: relative;
    overflow: hidden;
    background: #1a1510;
    flex-shrink: 0;
  }
  .card3-photo-bg {
    position: absolute; inset: 0;
    background-size: cover;
    background-position: center;
  }
  .card3-photo-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.7));
  }
  .card3-film-strip {
    position: absolute;
    bottom: 6%; left: 5%;
    display: flex; gap: 4px; align-items: center;
  }
  .film-dot {
    width: clamp(4px, 0.8vw, 6px);
    height: clamp(4px, 0.8vw, 6px);
    border-radius: 50%;
    background: rgba(212,165,116,0.6);
  }
  .film-dot:nth-child(2) { opacity: 0.4; }
  .film-dot:nth-child(3) { opacity: 0.2; }

  .card3-body {
    flex: 1;
    padding: 5% 6%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .card3-section-label {
    font-size: clamp(7px, 1.1vw, 9px);
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 5%;
  }
  .card3-items {
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  .card3-item {
    display: flex;
    align-items: flex-start;
    gap: 3%;
    padding: 3.5% 0;
    border-bottom: 0.5px solid rgba(255,255,255,0.06);
  }
  .card3-item:last-of-type { border-bottom: none; }
  .card3-item-dot {
    width: clamp(4px, 0.9vw, 6px);
    height: clamp(4px, 0.9vw, 6px);
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
    margin-top: clamp(4px, 0.9vw, 7px);
  }
  .card3-item-text {
    font-size: clamp(9px, 1.55vw, 12px);
    color: rgba(255,255,255,0.82);
    line-height: 1.5;
    font-weight: 400;
  }
  .card3-closing {
    padding-top: 4%;
    font-size: clamp(8px, 1.3vw, 10.5px);
    color: rgba(212,165,116,0.75);
    font-style: italic;
    letter-spacing: 0.3px;
    border-top: 0.5px solid rgba(255,255,255,0.08);
  }

  /* CARD 4 - CTA */
  .card4 { background: #0e0c0a; }

  .card4-photo {
    height: 50%;
    position: relative;
    overflow: hidden;
    background: #1a1510;
    flex-shrink: 0;
  }
  .card4-photo-bg {
    position: absolute; inset: 0;
    background-size: cover;
    background-position: center;
  }
  .card4-photo-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.65));
  }
  .card4-body {
    height: 50%;
    padding: 5% 6%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .card4-how-label {
    font-size: clamp(7px, 1.1vw, 9px);
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 3%;
  }
  .card4-how-text {
    font-size: clamp(9px, 1.5vw, 11.5px);
    color: rgba(255,255,255,0.65);
    line-height: 1.7;
  }
  .card4-divider {
    height: 0.5px;
    background: rgba(255,255,255,0.1);
    margin-bottom: 4%;
  }
  .card4-account-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4%;
  }
  .card4-account {
    font-size: clamp(10px, 1.8vw, 13px);
    font-weight: 700;
    color: rgba(255,255,255,0.8);
  }
  .card4-host {
    font-size: clamp(7px, 1.1vw, 9px);
    color: rgba(255,255,255,0.3);
  }
  .card4-cta {
    width: 100%;
    background: var(--accent);
    border-radius: 8px;
    padding: 4% 0;
    text-align: center;
    font-size: clamp(9px, 1.6vw, 12px);
    font-weight: 700;
    color: #1a0f00;
    letter-spacing: 1px;
    border: none;
    font-family: 'Pretendard', sans-serif;
  }

  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }

  .toast {
    position: fixed;
    bottom: 28px; right: 28px;
    background: var(--accent);
    color: #1a0f00;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    opacity: 0;
    transform: translateY(8px);
    transition: all 0.3s;
    pointer-events: none;
    z-index: 999;
  }
  .toast.show { opacity: 1; transform: translateY(0); }

  .color-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
</style>
</head>
<body>

<div class="app">

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="sidebar-logo">MK CINELAB</div>
    <div class="sidebar-title">카드뉴스 메이커</div>

    <div class="card-tabs">
      <button class="tab-btn active" onclick="switchTab(0)">카드 1</button>
      <button class="tab-btn" onclick="switchTab(1)">카드 2</button>
      <button class="tab-btn" onclick="switchTab(2)">카드 3</button>
      <button class="tab-btn" onclick="switchTab(3)">카드 4</button>
    </div>

    <!-- TAB 0: CARD 1 -->
    <div class="tab-panel active" id="tab0">
      <div class="section">
        <div class="section-label">배경 이미지</div>
        <div class="upload-zone">
          <input type="file" accept="image/*" onchange="loadImage(this, 'card1-bg', 'prev1')">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:rgba(255,255,255,0.2); margin-bottom:4px; display:block; margin:0 auto 4px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span>영화 스틸컷 / 포스터 업로드</span>
          <img class="preview-img" id="prev1">
        </div>
      </div>
      <div class="section">
        <div class="section-label">텍스트</div>
        <div class="field">
          <label>상단 레이블 (예: 5월 대구영화모임)</label>
          <input type="text" id="c1-eyebrow" value="5월 대구영화모임" oninput="update()">
        </div>
        <div class="field">
          <label>영화 제목 (한글)</label>
          <input type="text" id="c1-title" value="펀치 드렁크 러브" oninput="update()">
        </div>
        <div class="field">
          <label>영화 제목 (영문 + 연도)</label>
          <input type="text" id="c1-title-en" value="Punch-Drunk Love, 2002" oninput="update()">
        </div>
        <div class="field">
          <label>날짜</label>
          <input type="date" id="c1-date" value="2025-05-03" onchange="updateDates()">
        </div>
        <div class="field">
          <label>장소</label>
          <input type="text" id="c1-place" value="Lawns, 대구" oninput="update()">
        </div>
        <div class="field">
          <label>모집 뱃지 문구</label>
          <input type="text" id="c1-badge" value="인원 모집 중" oninput="update()">
        </div>
      </div>
    </div>

    <!-- TAB 1: CARD 2 -->
    <div class="tab-panel" id="tab1">
      <div class="section">
        <div class="section-label">배경 이미지</div>
        <div class="upload-zone">
          <input type="file" accept="image/*" onchange="loadImage(this, 'card2-photo-bg', 'prev2')">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:rgba(255,255,255,0.2); margin-bottom:4px; display:block; margin:0 auto 4px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span>장소 / 공간 분위기 사진</span>
          <img class="preview-img" id="prev2">
        </div>
      </div>
      <div class="section">
        <div class="section-label">모임 정보</div>
        <div class="field">
          <label>날짜</label>
          <input type="date" id="c2-date" value="2025-05-03" onchange="updateDates()">
        </div>
        <div class="field">
          <label>시작 시간</label>
          <input type="time" id="c2-time-start" value="19:00" onchange="updateDates()">
        </div>
        <div class="field">
          <label>종료 시간</label>
          <input type="time" id="c2-time-end" value="22:30" onchange="updateDates()">
        </div>
        <div class="field">
          <label>장소</label>
          <input type="text" id="c2-place" value="Lawns (론스)" oninput="update()">
        </div>
        <div class="field">
          <label>참가비</label>
          <input type="text" id="c2-fee" value="15,000원 / 1인" oninput="update()">
        </div>
        <div class="field">
          <label>신청 방법</label>
          <input type="text" id="c2-apply" value="인스타그램 DM 신청" oninput="update()">
        </div>
        <div class="field">
          <label>포함 사항</label>
          <input type="text" id="c2-include" value="웰컴 드링크 1잔 포함" oninput="update()">
        </div>
      </div>
    </div>

    <!-- TAB 2: CARD 3 -->
    <div class="tab-panel" id="tab2">
      <div class="section">
        <div class="section-label">배경 이미지</div>
        <div class="upload-zone">
          <input type="file" accept="image/*" onchange="loadImage(this, 'card3-photo-bg', 'prev3')">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:rgba(255,255,255,0.2); margin-bottom:4px; display:block; margin:0 auto 4px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span>감성 소품 / 공간 사진</span>
          <img class="preview-img" id="prev3">
        </div>
      </div>
      <div class="section">
        <div class="section-label">모임 소개 문구</div>
        <div class="field">
          <label>섹션 레이블</label>
          <input type="text" id="c3-label" value="이런 분들 오세요" oninput="update()">
        </div>
        <div class="field">
          <label>항목 1</label>
          <input type="text" id="c3-item1" value="다른 사람들과 영화에 대해 이야기하고 싶은 분" oninput="update()">
        </div>
        <div class="field">
          <label>항목 2</label>
          <input type="text" id="c3-item2" value="영화 한 편으로 다양한 이야기를 나누고 싶은 분" oninput="update()">
        </div>
        <div class="field">
          <label>항목 3</label>
          <input type="text" id="c3-item3" value="보고 싶었지만 혼자 보기 아쉬웠던 영화가 있는 분" oninput="update()">
        </div>
        <div class="field">
          <label>항목 4 (선택)</label>
          <input type="text" id="c3-item4" value="좋은 공간에서 편안하게 영화를 즐기고 싶은 분" oninput="update()">
        </div>
        <div class="field">
          <label>하단 한마디</label>
          <input type="text" id="c3-closing" value="영화를 좋아한다면, 그걸로 충분합니다." oninput="update()">
        </div>
      </div>
    </div>

    <!-- TAB 3: CARD 4 -->
    <div class="tab-panel" id="tab3">
      <div class="section">
        <div class="section-label">배경 이미지</div>
        <div class="upload-zone">
          <input type="file" accept="image/*" onchange="loadImage(this, 'card4-photo-bg', 'prev4')">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:rgba(255,255,255,0.2); margin-bottom:4px; display:block; margin:0 auto 4px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span>감성 소품 / 공간 사진</span>
          <img class="preview-img" id="prev4">
        </div>
      </div>
      <div class="section">
        <div class="section-label">신청 안내</div>
        <div class="field">
          <label>신청 안내 문구</label>
          <textarea id="c4-howtext">참가 신청은 인스타그램
DM으로 받습니다.
선착순 마감이니 서둘러주세요.</textarea>
        </div>
        <div class="field">
          <label>인스타그램 계정</label>
          <input type="text" id="c4-account" value="@daegu_movie" oninput="update()">
        </div>
        <div class="field">
          <label>기획·주최</label>
          <input type="text" id="c4-host" value="기획·주최 MK CINELAB" oninput="update()">
        </div>
        <div class="field">
          <label>CTA 버튼 문구</label>
          <input type="text" id="c4-cta" value="DM으로 신청하기" oninput="update()">
        </div>
      </div>
    </div>

    <!-- 포인트 컬러 -->
    <div class="section" style="margin-top: 8px;">
      <div class="section-label">포인트 컬러</div>
      <div class="color-row">
        <div class="field">
          <label>메인 포인트</label>
          <input type="color" id="color-accent" value="#d4a574" oninput="updateColor()">
        </div>
        <div class="field">
          <label>포인트 밝기</label>
          <input type="color" id="color-accent2" value="#e8c49a" oninput="updateColor()">
        </div>
      </div>
    </div>

    <div class="sidebar-actions">
      <button class="btn-download" onclick="downloadAll()">전체 카드 이미지 저장 (4장)</button>
    </div>
  </aside>

  <!-- PREVIEW -->
  <main class="preview-area">
    <div class="preview-header">
      <span class="preview-header-title">PREVIEW — 1080 × 1350 (4:5)</span>
    </div>

    <div class="cards-container">

      <!-- CARD 1 -->
      <div class="canvas-wrapper">
        <div class="canvas-num">01 — 모집 커버</div>
        <div class="canvas-card card1" id="canvas-card1">
          <div class="card1-bg" id="card1-bg"></div>
          <div class="card1-scrim"></div>
          <div class="card1-logo">MK CINELAB</div>
          <div class="card1-bottom">
            <div class="card1-badge">
              <div class="badge-dot"></div>
              <span id="d-c1-badge">인원 모집 중</span>
            </div>
            <div class="card1-eyebrow" id="d-c1-eyebrow">5월 대구영화모임</div>
            <div class="card1-title" id="d-c1-title">펀치 드렁크 러브</div>
            <div class="card1-title-en" id="d-c1-title-en">Punch-Drunk Love, 2002</div>
            <div class="card1-divider"></div>
            <div class="card1-meta">
              <div class="card1-meta-item">
                <svg viewBox="0 0 24 24" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <span id="d-c1-date">5월 3일 (일)</span>
              </div>
              <div class="card1-meta-item">
                <svg viewBox="0 0 24 24" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                <span id="d-c1-place">Lawns, 대구</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CARD 2 -->
      <div class="canvas-wrapper">
        <div class="canvas-num">02 — 모임 정보</div>
        <div class="canvas-card card2" id="canvas-card2">
          <div class="card2-photo">
            <div class="card2-photo-bg" id="card2-photo-bg"></div>
            <div class="card2-photo-scrim"></div>
          </div>
          <div class="card2-body">
            <div class="card2-eyebrow">모임 정보</div>
            <div class="card2-info-list">
              <div class="card2-info-row">
                <svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <span class="card2-info-key">일시</span>
                <span class="card2-info-val" id="d-c2-datetime">5월 3일 (일)  19:00 ~ 22:30</span>
              </div>
              <div class="card2-info-row">
                <svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                <span class="card2-info-key">장소</span>
                <span class="card2-info-val" id="d-c2-place">Lawns (론스)</span>
              </div>
              <div class="card2-info-row">
                <svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                <span class="card2-info-key">비용</span>
                <span class="card2-info-val" id="d-c2-fee">15,000원 / 1인</span>
              </div>
              <div class="card2-info-row">
                <svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                <span class="card2-info-key">신청</span>
                <span class="card2-info-val" id="d-c2-apply">인스타그램 DM 신청</span>
              </div>
            </div>
            <div class="card2-include">
              <svg viewBox="0 0 24 24" stroke-width="1.8"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M8 12l2 2 4-4"/></svg>
              <span id="d-c2-include">웰컴 드링크 1잔 포함</span>
            </div>
          </div>
        </div>
      </div>

      <!-- CARD 3 -->
      <div class="canvas-wrapper">
        <div class="canvas-num">03 — 모임 소개</div>
        <div class="canvas-card card3" id="canvas-card3">
          <div class="card3-photo">
            <div class="card3-photo-bg" id="card3-photo-bg"></div>
            <div class="card3-photo-scrim"></div>
            <div class="card3-film-strip">
              <div class="film-dot"></div>
              <div class="film-dot"></div>
              <div class="film-dot"></div>
            </div>
          </div>
          <div class="card3-body">
            <div>
              <div class="card3-section-label" id="d-c3-label">이런 분들 오세요</div>
              <div class="card3-items">
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item1">다른 사람들과 영화에 대해 이야기하고 싶은 분</span></div>
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item2">영화 한 편으로 다양한 이야기를 나누고 싶은 분</span></div>
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item3">보고 싶었지만 혼자 보기 아쉬웠던 영화가 있는 분</span></div>
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item4">좋은 공간에서 편안하게 영화를 즐기고 싶은 분</span></div>
              </div>
            </div>
            <div class="card3-closing" id="d-c3-closing">영화를 좋아한다면, 그걸로 충분합니다.</div>
          </div>
        </div>
      </div>

      <!-- CARD 4 -->
      <div class="canvas-wrapper">
        <div class="canvas-num">04 — 신청 안내</div>
        <div class="canvas-card card4" id="canvas-card4">
          <div class="card4-photo">
            <div class="card4-photo-bg" id="card4-photo-bg"></div>
            <div class="card4-photo-scrim"></div>
          </div>
          <div class="card4-body">
            <div>
              <div class="card4-how-label">신청 방법</div>
              <div class="card4-how-text" id="d-c4-howtext">참가 신청은 인스타그램<br>DM으로 받습니다.<br>선착순 마감이니 서둘러주세요.</div>
            </div>
            <div>
              <div class="card4-divider"></div>
              <div class="card4-account-row">
                <div class="card4-account" id="d-c4-account">@daegu_movie</div>
                <div class="card4-host" id="d-c4-host">기획·주최 MK CINELAB</div>
              </div>
              <div class="card4-cta" id="d-c4-cta">DM으로 신청하기</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>
</div>

<div class="toast" id="toast"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function switchTab(i) {
  document.querySelectorAll('.tab-btn').forEach((b,j) => b.classList.toggle('active', i===j));
  document.querySelectorAll('.tab-panel').forEach((p,j) => p.classList.toggle('active', i===j));
}

function loadImage(input, bgId, prevId) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const url = e.target.result;
    document.getElementById(bgId).style.backgroundImage = `url(${url})`;
    const prev = document.getElementById(prevId);
    prev.src = url;
    prev.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function update() {
  const map = {
    'c1-eyebrow':  'd-c1-eyebrow',
    'c1-badge':    'd-c1-badge',
    'c1-title':    'd-c1-title',
    'c1-title-en': 'd-c1-title-en',
    'c1-place':    'd-c1-place',
    'c2-place':    'd-c2-place',
    'c2-fee':      'd-c2-fee',
    'c2-apply':    'd-c2-apply',
    'c2-include':  'd-c2-include',
    'c3-label':    'd-c3-label',
    'c3-item1':    'd-c3-item1',
    'c3-item2':    'd-c3-item2',
    'c3-item3':    'd-c3-item3',
    'c3-item4':    'd-c3-item4',
    'c3-closing':  'd-c3-closing',
    'c4-account':  'd-c4-account',
    'c4-host':     'd-c4-host',
    'c4-cta':      'd-c4-cta',
  };
  for (const [src, dst] of Object.entries(map)) {
    const el = document.getElementById(src);
    if (el) document.getElementById(dst).textContent = el.value;
  }
  const howtext = document.getElementById('c4-howtext').value;
  document.getElementById('d-c4-howtext').innerHTML = howtext.replace(/\\n/g, '<br>');
}

function updateDates() {
  const DAYS = ['일','월','화','수','목','금','토'];
  function fmtDate(id) {
    const v = document.getElementById(id).value;
    if (!v) return '';
    const d = new Date(v + 'T00:00:00');
    return `${d.getMonth()+1}월 ${d.getDate()}일 (${DAYS[d.getDay()]})`;
  }
  document.getElementById('d-c1-date').textContent = fmtDate('c1-date');

  const date2Str = fmtDate('c2-date');
  const ts = document.getElementById('c2-time-start').value;
  const te = document.getElementById('c2-time-end').value;
  document.getElementById('d-c2-datetime').textContent = `${date2Str}  ${ts} ~ ${te}`;
}

function updateColor() {
  const a  = document.getElementById('color-accent').value;
  const a2 = document.getElementById('color-accent2').value;
  document.documentElement.style.setProperty('--accent', a);
  document.documentElement.style.setProperty('--accent2', a2);
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2400);
}

function downloadAll() {
  const cards  = ['canvas-card1','canvas-card2','canvas-card3','canvas-card4'];
  const labels = ['card1_cover','card2_info','card3_intro','card4_cta'];
  const TARGET_W = 1080;
  const TARGET_H = 1350;
  let i = 0;

  function exportCard(el) {
    return new Promise(resolve => {
      const elW = el.offsetWidth  || 540;
      const elH = el.offsetHeight || 675;
      // 출력 목표 크기를 충족하는 최소 scale 계산 (최소 4배 보장)
      const scale = Math.max(4, Math.ceil(TARGET_W / elW) + 1);

      html2canvas(el, {
        scale,
        useCORS: true,
        allowTaint: true,
        backgroundColor: null,
        logging: false,
      }).then(raw => {
        // 정확히 1080×1350으로 리사이즈
        const out = document.createElement('canvas');
        out.width  = TARGET_W;
        out.height = TARGET_H;
        const ctx = out.getContext('2d');
        ctx.imageSmoothingEnabled  = true;
        ctx.imageSmoothingQuality  = 'high';
        ctx.drawImage(raw, 0, 0, TARGET_W, TARGET_H);
        resolve(out.toDataURL('image/png'));
      });
    });
  }

  function next() {
    if (i >= cards.length) { showToast('모든 카드 저장 완료! (1080×1350)'); return; }
    const el = document.getElementById(cards[i]);
    showToast(`카드 ${i+1}/4 저장 중...`);
    exportCard(el).then(dataUrl => {
      const link = document.createElement('a');
      link.download = `mkcinelab_${labels[i]}.png`;
      link.href = dataUrl;
      link.click();
      i++;
      setTimeout(next, 800);
    });
  }

  next();
}

update();
updateDates();
</script>
</body>
</html>"""

components.html(CARD_NEWS_HTML, height=3200, scrolling=False)
