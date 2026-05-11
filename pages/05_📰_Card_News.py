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

  .btn-download {
    width: 100%;
    max-width: 540px;
    padding: 15px;
    background: var(--accent);
    color: #1a0f00;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    font-family: 'Pretendard', sans-serif;
    letter-spacing: 0.5px;
    transition: opacity 0.2s;
    margin-top: 16px;
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
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .card-panel {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  .card-panel.active { display: flex; }

  .canvas-wrapper {
    width: 100%;
    max-width: 540px;
    position: relative;
    margin-top: 28px;
  }

  /* ── 모바일 반응형 ── */
  @media (max-width: 768px) {
    .app {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
      min-height: 100vh;
    }
    .sidebar {
      border-right: none;
      border-bottom: 1px solid var(--border);
      max-height: 56vh;
      overflow-y: auto;
      padding: 20px 16px;
    }
    .card-tabs {
      position: sticky;
      top: -20px;
      z-index: 10;
      background: var(--surface);
      padding: 8px 0 4px;
    }
    .preview-area {
      padding: 20px 16px 48px;
    }
    .canvas-wrapper {
      max-width: 100%;
    }
    .preview-header-title {
      font-size: 11px;
    }
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
          <input type="date" id="c1-date" onchange="updateDates()">
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

  </aside>

  <!-- PREVIEW -->
  <main class="preview-area">
    <div class="preview-header">
      <span class="preview-header-title">PREVIEW — 1080 × 1350 (4:5)</span>
    </div>

    <div class="cards-container">

      <!-- CARD 1 -->
      <div class="card-panel active" id="panel-0">
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
      </div><!-- /panel-0 -->

      <!-- CARD 2 -->
      <div class="card-panel" id="panel-1">
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
      </div><!-- /panel-1 -->

      <!-- CARD 3 -->
      <div class="card-panel" id="panel-2">
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
      </div><!-- /panel-2 -->

      <!-- CARD 4 -->
      <div class="card-panel" id="panel-3">
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
      </div><!-- /panel-3 -->

    </div>

    <button class="btn-download" onclick="downloadCurrent()">⬇ 이 카드 저장 (1080×1350)</button>

  </main>
</div>

<div class="toast" id="toast"></div>

<script>
let currentTab = 0;

function switchTab(i) {
  currentTab = i;
  document.querySelectorAll('.tab-btn').forEach((b,j)    => b.classList.toggle('active', i===j));
  document.querySelectorAll('.tab-panel').forEach((p,j)  => p.classList.toggle('active', i===j));
  document.querySelectorAll('.card-panel').forEach((p,j) => p.classList.toggle('active', i===j));
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

const CARD_LABELS = ['card1_cover','card2_info','card3_intro','card4_cta'];

// ── Pure Canvas Renderer (html2canvas 미사용) ──────────────────

function loadImg(src) {
  return new Promise(res => {
    const m = (src||'').match(/url\\("?(.+?)"?\\)/);
    const url = m ? m[1] : src;
    if (!url || url==='none') return res(null);
    const img = new Image();
    img.onload = ()=>res(img); img.onerror = ()=>res(null); img.src = url;
  });
}

function bgCover(ctx, img, x, y, w, h) {
  if (!img) return;
  const s = Math.max(w/img.width, h/img.height);
  ctx.save(); ctx.beginPath(); ctx.rect(x,y,w,h); ctx.clip();
  ctx.drawImage(img, x+(w-img.width*s)/2, y+(h-img.height*s)/2, img.width*s, img.height*s);
  ctx.restore();
}

function applyGrad(ctx, x, y, w, h, stops) {
  const g = ctx.createLinearGradient(x,y,x,y+h);
  stops.forEach(([p,c])=>g.addColorStop(p,c));
  ctx.fillStyle=g; ctx.fillRect(x,y,w,h);
}

function rr(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+r,r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
  ctx.arcTo(x,y+h,x,y+h-r,r); ctx.arcTo(x,y,x+r,y,r); ctx.closePath();
}

function wrapLines(ctx, text, maxW) {
  const res=[];
  for (const seg of (text||'').split('\\n')) {
    if (!seg.trim()) continue;
    if (ctx.measureText(seg).width<=maxW) { res.push(seg); continue; }
    const words=seg.split(' ');
    if (words.length>1) {
      let cur='';
      for (const w of words) {
        const t=cur?cur+' '+w:w;
        if(ctx.measureText(t).width<=maxW) cur=t;
        else { if(cur)res.push(cur); cur=w; }
      }
      if(cur)res.push(cur);
    } else {
      let cur='';
      for (const ch of seg) {
        if(ctx.measureText(cur+ch).width<=maxW)cur+=ch;
        else{res.push(cur);cur=ch;}
      }
      if(cur)res.push(cur);
    }
  }
  return res;
}

function getBg(id)  { return ((document.getElementById(id)||{style:{}}).style.backgroundImage)||''; }
function v(id)      { return (document.getElementById(id)||{}).value||''; }
function t(id)      { return ((document.getElementById(id)||{}).textContent||'').trim(); }
function getAc()    { return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()||'#d4a574'; }
function getAc2()   { return getComputedStyle(document.documentElement).getPropertyValue('--accent2').trim()||'#e8c49a'; }

const ICONS = {
  calendar(ctx,x,y,sz,col){
    const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
    ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.lineJoin='round';
    rr(ctx,3,4,18,18,2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(16,2);ctx.lineTo(16,6);ctx.moveTo(8,2);ctx.lineTo(8,6);ctx.moveTo(3,10);ctx.lineTo(21,10); ctx.stroke();
    ctx.restore();
  },
  pin(ctx,x,y,sz,col){
    const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
    ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.lineJoin='round';
    ctx.beginPath(); ctx.moveTo(21,10); ctx.bezierCurveTo(21,17,12,23,12,23); ctx.bezierCurveTo(12,23,3,17,3,10); ctx.bezierCurveTo(3,5,7,1,12,1); ctx.bezierCurveTo(17,1,21,5,21,10); ctx.closePath(); ctx.stroke();
    ctx.beginPath(); ctx.arc(12,10,3,0,Math.PI*2); ctx.stroke();
    ctx.restore();
  },
  clock(ctx,x,y,sz,col){
    const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
    ctx.strokeStyle=col; ctx.lineWidth=2/s;
    ctx.beginPath(); ctx.arc(12,12,10,0,Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(12,6);ctx.lineTo(12,12);ctx.lineTo(16,14); ctx.stroke();
    ctx.restore();
  },
  chat(ctx,x,y,sz,col){
    const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
    ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.lineJoin='round';
    ctx.beginPath(); ctx.moveTo(21,15); ctx.bezierCurveTo(21,16.1,20.1,17,19,17); ctx.lineTo(7,17); ctx.lineTo(3,21); ctx.lineTo(3,5); ctx.bezierCurveTo(3,3.9,3.9,3,5,3); ctx.lineTo(19,3); ctx.bezierCurveTo(20.1,3,21,3.9,21,5); ctx.closePath(); ctx.stroke();
    ctx.restore();
  },
  check(ctx,x,y,sz,col){
    const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
    ctx.strokeStyle=col; ctx.lineWidth=2/s;
    ctx.beginPath(); ctx.arc(12,12,10,0,Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(8,12);ctx.lineTo(10,14);ctx.lineTo(14,10); ctx.stroke();
    ctx.restore();
  },
};

async function renderCard(n) {
  // W=1080, H=1350 (4:5). CSS margin% = % of containing-block WIDTH(W), not height.
  const W=1080, H=1350, PX=W*0.06;   // PX=64.8px (6% horizontal pad)
  const cv=document.createElement('canvas'); cv.width=W; cv.height=H;
  const ctx=cv.getContext('2d');
  ctx.imageSmoothingEnabled=true; ctx.imageSmoothingQuality='high';
  const A=getAc(), A2=getAc2();
  // Font sizes = clamp-max * 2 (preview card ~540px → canvas 1080px = 2x)
  const F = (w,sz) => `${w} ${sz}px Pretendard,sans-serif`;

  if (n===0) {
    // ── Card 1: Cover ──
    ctx.fillStyle='#1a1510'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card1-bg')), 0,0,W,H);
    applyGrad(ctx,0,0,W,H,[[0,'rgba(0,0,0,0.15)'],[0.25,'rgba(0,0,0,0.05)'],[0.55,'rgba(0,0,0,0.4)'],[1,'rgba(0,0,0,0.88)']]);

    // Logo — top:4.5% right:5%, font clamp-max 11px×2=22px
    ctx.font=F('400',22);
    const ltxt='MK CINELAB', lw=ctx.measureText(ltxt).width+20, lh=36;
    const lx=W-W*0.05-lw, ly=H*0.045;
    ctx.strokeStyle='rgba(255,255,255,0.35)'; ctx.lineWidth=1.5;
    rr(ctx,lx,ly,lw,lh,4); ctx.stroke();
    ctx.fillStyle='rgba(255,255,255,0.75)'; ctx.fillText(ltxt,lx+10,ly+lh*0.69);

    // card1-bottom: padding 5% 6% 6% — all % = % of W
    // Build from bottom upward; cy = text baseline
    let cy = H - W*0.06;  // bottom padding = W×6% = 64.8px

    // Meta row — font 10px×2=20px, icon 12px×2=24px
    const ISZ=24;
    ctx.font=F('400',20); ctx.fillStyle='rgba(255,255,255,0.72)';
    const ds=t('d-c1-date'), ps=t('d-c1-place');
    ICONS.calendar(ctx,PX,cy-ISZ,ISZ,A); ctx.fillText(ds,PX+ISZ+8,cy-3);
    const dW=ctx.measureText(ds).width;
    ICONS.pin(ctx,PX+ISZ+8+dW+W*0.04,cy-ISZ,ISZ,A);
    ctx.fillText(ps,PX+ISZ+8+dW+W*0.04+ISZ+8,cy-3);
    cy -= ISZ + W*0.035;          // ↑ icon height + divider margin-bottom(3.5%W)

    // Divider — margin-bottom 3.5%W
    ctx.beginPath(); ctx.moveTo(PX,cy); ctx.lineTo(W-PX,cy);
    ctx.strokeStyle='rgba(255,255,255,0.18)'; ctx.lineWidth=1; ctx.stroke();
    cy -= W*0.04;                  // ↑ title-en margin-bottom(4%W)

    // English title — clamp-max 11px×2=22px, margin-bottom 4%W
    ctx.font=F('400',22); ctx.fillStyle='rgba(255,255,255,0.4)';
    ctx.fillText(v('c1-title-en'),PX,cy);
    cy -= 22 + W*0.01;             // ↑ text height + title margin-bottom(1%W)

    // Korean title — clamp-max 38px×2=76px, line-height 1.2
    const titleStr=v('c1-title'), maxTW=W-PX*2;
    let tSz=76;
    while(tSz>32){ctx.font=F('700',tSz); if(ctx.measureText(titleStr).width<=maxTW)break; tSz-=4;}
    ctx.font=F('700',tSz); ctx.fillStyle='#fff';
    const tLines=wrapLines(ctx,titleStr,maxTW);
    for(let i=tLines.length-1;i>=0;i--){ctx.fillText(tLines[i],PX,cy); cy-=tSz*1.2;}
    cy -= W*0.02;                  // ↑ eyebrow margin-bottom(2%W)

    // Eyebrow — clamp-max 10px×2=20px
    ctx.font=F('400',20); ctx.fillStyle=A+'cc';
    ctx.fillText((v('c1-eyebrow')||'').toUpperCase(),PX,cy);
    cy -= 20 + W*0.035;            // ↑ text height + badge margin-bottom(3.5%W)

    // Badge — clamp-max 9.5px×2=19px, padding 3px 12px
    const bStr=v('c1-badge'); ctx.font=F('400',19);
    const bTW=ctx.measureText(bStr).width, bH=34, bP=W*0.011, dR=6;
    const bX=PX, bY=cy-bH;
    ctx.strokeStyle=A+'b3'; ctx.lineWidth=1.5;
    rr(ctx,bX,bY,bTW+bP*2+dR*2+14,bH,bH/2); ctx.stroke();
    ctx.fillStyle=A; ctx.beginPath(); ctx.arc(bX+bP+dR,bY+bH/2,dR,0,Math.PI*2); ctx.fill();
    ctx.fillStyle=A2; ctx.fillText(bStr,bX+bP+dR*2+14,bY+bH*0.69);

  } else if (n===1) {
    // ── Card 2: Info ──
    const PH=H*0.42, BH=H-H*0.42;
    ctx.fillStyle='#0e0c0a'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card2-photo-bg')),0,0,W,PH);
    applyGrad(ctx,0,0,W,PH,[[0,'rgba(0,0,0,0.1)'],[1,'rgba(0,0,0,0.6)']]);

    // body padding 5% 6% (W-based)
    const bPT=W*0.05, bPB=W*0.06;
    const py=PH+bPT;
    // icon: clamp(14,2.5vw,20)×2=40px — cap at 36 for visual balance
    const ISZ=36;
    // flex gap: 4%W, key min-width: 15%W
    const GAP=W*0.04, KEY_W=W*0.15;
    const KEY_X=PX+ISZ+GAP, VAL_X=KEY_X+KEY_W+GAP;

    // Eyebrow — clamp-max 9px×2=18px, margin-bottom 5%W
    ctx.font=F('700',18); ctx.fillStyle=A; ctx.fillText('모임 정보',PX,py+18);

    const rStart=py+18+W*0.05;
    const incH=W*0.13;
    const avail=BH-bPT-18-W*0.05-incH-bPB;
    const rH=avail/4;

    const rows=[
      {icon:'calendar',key:'일시',val:t('d-c2-datetime')},
      {icon:'pin',     key:'장소',val:t('d-c2-place')},
      {icon:'clock',   key:'비용',val:t('d-c2-fee')},
      {icon:'chat',    key:'신청',val:t('d-c2-apply')},
    ];
    rows.forEach((row,i)=>{
      const ry=rStart+i*rH, mid=ry+rH/2;
      if(i<rows.length-1){ctx.beginPath();ctx.moveTo(PX,ry+rH);ctx.lineTo(W-PX,ry+rH);ctx.strokeStyle='rgba(255,255,255,0.06)';ctx.lineWidth=1;ctx.stroke();}
      ICONS[row.icon](ctx,PX,mid-ISZ/2,ISZ,A);
      ctx.font=F('400',18); ctx.fillStyle='rgba(255,255,255,0.35)'; ctx.fillText(row.key,KEY_X,mid+6);
      ctx.font=F('500',24); ctx.fillStyle='rgba(255,255,255,0.88)'; ctx.fillText(row.val,VAL_X,mid+9);
    });

    // Include box — padding 3%W, icon clamp-max 14px×2=28px
    const incY=PH+BH-bPB-incH;
    const ISZ2=28, incPad=W*0.04;
    ctx.fillStyle=A+'14'; rr(ctx,PX,incY,W-PX*2,incH,10); ctx.fill();
    ctx.strokeStyle=A+'40'; ctx.lineWidth=1; rr(ctx,PX,incY,W-PX*2,incH,10); ctx.stroke();
    ICONS.check(ctx,PX+incPad,incY+(incH-ISZ2)/2,ISZ2,A);
    ctx.font=F('400',20); ctx.fillStyle='rgba(255,255,255,0.6)';
    ctx.fillText(t('d-c2-include'),PX+incPad+ISZ2+10,incY+incH/2+7);

  } else if (n===2) {
    // ── Card 3: Intro ──
    const PH=H*0.35, BH=H-H*0.35;
    ctx.fillStyle='#0e0c0a'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card3-photo-bg')),0,0,W,PH);
    applyGrad(ctx,0,0,W,PH,[[0,'rgba(0,0,0,0.1)'],[1,'rgba(0,0,0,0.7)']]);

    // Film dots — bottom 6% of photo, left 5%
    const dotY=PH-PH*0.06;
    [1,0.4,0.2].forEach((op,i)=>{
      ctx.fillStyle=`rgba(212,165,116,${op*0.6})`;
      ctx.beginPath(); ctx.arc(PX+i*22,dotY,8,0,Math.PI*2); ctx.fill();
    });

    // body padding 5% 6% (W-based)
    const bPT=W*0.05, bPB=W*0.05;
    const py=PH+bPT;

    // Section label — clamp-max 9px×2=18px, margin-bottom 5%W
    ctx.font=F('700',18); ctx.fillStyle=A;
    ctx.fillText((t('d-c3-label')||'').toUpperCase(),PX,py+18);

    const items=[t('d-c3-item1'),t('d-c3-item2'),t('d-c3-item3'),t('d-c3-item4')].filter(x=>x.trim());
    const closH=W*0.08+24;
    const iStart=py+18+W*0.05;
    const avail=BH-bPT-18-W*0.05-closH-bPB;
    const iH=avail/items.length;
    // item text: clamp-max 12px×2=24px, dot: clamp-max 6px → radius=6
    const itemFSz=24, dotR=6;

    items.forEach((item,i)=>{
      const iy=iStart+i*iH, mid=iy+iH/2;
      if(i<items.length-1){ctx.beginPath();ctx.moveTo(PX,iy+iH);ctx.lineTo(W-PX,iy+iH);ctx.strokeStyle='rgba(255,255,255,0.06)';ctx.lineWidth=1;ctx.stroke();}
      // dot aligned to first text line
      ctx.fillStyle=A; ctx.beginPath(); ctx.arc(PX+dotR,iy+W*0.033+dotR,dotR,0,Math.PI*2); ctx.fill();
      ctx.font=F('400',itemFSz); ctx.fillStyle='rgba(255,255,255,0.82)';
      const ls=wrapLines(ctx,item,W-PX*2-dotR*2-14);
      const lineH=itemFSz*1.5;
      const startY=mid-ls.length*lineH/2+lineH*0.75;
      ls.forEach((l,li)=>ctx.fillText(l,PX+dotR*2+14,startY+li*lineH));
    });

    // Closing — border-top + italic text
    const cY=PH+BH-bPB;
    ctx.beginPath(); ctx.moveTo(PX,cY-closH+4); ctx.lineTo(W-PX,cY-closH+4);
    ctx.strokeStyle='rgba(255,255,255,0.08)'; ctx.lineWidth=1; ctx.stroke();
    ctx.font=`italic 400 22px Pretendard,sans-serif`; ctx.fillStyle=A+'bf';
    ctx.fillText(t('d-c3-closing'),PX,cY-4);

  } else if (n===3) {
    // ── Card 4: CTA ──
    const PH=H*0.5, BH=H-H*0.5;
    ctx.fillStyle='#0e0c0a'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card4-photo-bg')),0,0,W,PH);
    applyGrad(ctx,0,0,W,PH,[[0,'rgba(0,0,0,0.1)'],[1,'rgba(0,0,0,0.65)']]);

    // body padding 5% 6% (W-based)
    let cy=PH+W*0.05;

    // How-to label — clamp-max 9px×2=18px
    ctx.font=F('700',18); ctx.fillStyle=A; ctx.fillText('신청 방법',PX,cy+18);
    cy += 18 + W*0.03;

    // How-to text — clamp-max 11.5px×2=23→24px
    const howLines=v('c4-howtext').split(/\\r?\\n/).filter(l=>l.trim());
    const howFSz=24;
    ctx.font=F('400',howFSz); ctx.fillStyle='rgba(255,255,255,0.65)';
    howLines.forEach(line=>{ctx.fillText(line,PX,cy); cy+=howFSz*1.7;});

    // Divider at 73% of body height
    const divY=PH+BH*0.73;
    ctx.beginPath(); ctx.moveTo(PX,divY); ctx.lineTo(W-PX,divY);
    ctx.strokeStyle='rgba(255,255,255,0.1)'; ctx.lineWidth=1; ctx.stroke();

    // Account + host — account 13px×2=26px, host 9px×2=18px
    const accY=divY+BH*0.1;
    ctx.font=F('700',26); ctx.fillStyle='rgba(255,255,255,0.8)'; ctx.fillText(t('d-c4-account'),PX,accY);
    const hostStr=t('d-c4-host');
    ctx.font=F('400',18); ctx.fillStyle='rgba(255,255,255,0.3)';
    ctx.fillText(hostStr,W-PX-ctx.measureText(hostStr).width,accY);

    // CTA button — clamp-max 12px×2=24→26px for legibility
    const ctaY=accY+BH*0.1, ctaH=BH*0.18;
    ctx.fillStyle=A; rr(ctx,PX,ctaY,W-PX*2,ctaH,10); ctx.fill();
    const ctaStr=t('d-c4-cta'), ctaSz=26;
    ctx.font=F('700',ctaSz); ctx.fillStyle='#1a0f00';
    ctx.fillText(ctaStr,(W-ctx.measureText(ctaStr).width)/2,ctaY+ctaH/2+ctaSz*0.36);
  }

  return cv;
}

async function downloadCurrent() {
  await document.fonts.ready;
  const label = CARD_LABELS[currentTab];
  showToast(`카드 ${currentTab+1} 저장 중...`);
  try {
    const cv = await renderCard(currentTab);
    const link = document.createElement('a');
    link.download = `mkcinelab_${label}.png`;
    link.href = cv.toDataURL('image/png');
    link.click();
    showToast(`카드 ${currentTab+1} 저장 완료! (1080×1350)`);
  } catch(e) {
    showToast('저장 실패 — 콘솔 확인');
    console.error(e);
  }
}

const today = new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD
document.getElementById('c1-date').value = today;

update();
updateDates();
</script>
</body>
</html>"""

components.html(CARD_NEWS_HTML, height=3200, scrolling=False)
