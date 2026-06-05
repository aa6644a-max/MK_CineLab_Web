import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MK 이미지 작업실", page_icon="🎨", layout="wide")

from mk_theme import inject_css
inject_css()

THUMBNAIL_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Noto Sans KR', sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
    padding: 20px 16px 60px;
  }
  h1 { text-align:center; font-size:18px; font-weight:700; margin-bottom:4px; }
  .subtitle { text-align:center; font-size:12px; color:rgba(255,255,255,0.4); margin-bottom:18px; }

  .preview-wrap { width:100%; max-width:480px; margin:0 auto 18px; }
  .preview-box {
    width:100%; aspect-ratio:1/1;
    position:relative; overflow:hidden;
    border-radius:8px; background:#1a1a1a;
    cursor:grab;
  }
  .preview-box:active { cursor:grabbing; }
  #preview-canvas { position:absolute; inset:0; width:100%; height:100%; display:block; }

  #drag-hint {
    position:absolute; inset:0;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    gap:8px; color:rgba(255,255,255,0.3); font-size:13px;
    pointer-events:none;
  }
  #drag-hint svg { opacity:.35; }
  #drag-hint.hidden { display:none; }

  #move-hint {
    position:absolute; bottom:50px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.65); color:rgba(255,255,255,0.75);
    font-size:11px; padding:5px 12px; border-radius:20px;
    pointer-events:none; white-space:nowrap;
    transition:opacity 1.2s;
  }
  #move-hint.fade { opacity:0; }

  .form-card {
    background:#161616; border:1px solid rgba(255,255,255,0.08);
    border-radius:12px; padding:20px 16px;
    max-width:480px; margin:0 auto;
    display:flex; flex-direction:column; gap:16px;
  }
  .field label {
    display:block; font-size:11px; font-weight:600;
    color:rgba(255,255,255,0.45); margin-bottom:6px;
    text-transform:uppercase; letter-spacing:.6px;
  }
  .field input[type=text] {
    width:100%; padding:10px 12px;
    border-radius:6px; border:1px solid rgba(255,255,255,0.12);
    background:rgba(255,255,255,0.05); color:#fff;
    font-size:15px; font-family:'Noto Sans KR',sans-serif;
    outline:none; transition:border-color .2s;
  }
  .field input[type=text]:focus { border-color:rgba(255,255,255,0.35); }
  .field input[type=text]::placeholder { color:rgba(255,255,255,0.22); }

  .slider-row { display:flex; align-items:center; gap:12px; }
  .slider-row input[type=range] {
    flex:1; -webkit-appearance:none; height:3px;
    background:rgba(255,255,255,0.15); border-radius:2px; outline:none;
  }
  .slider-row input[type=range]::-webkit-slider-thumb {
    -webkit-appearance:none; width:18px; height:18px;
    border-radius:50%; background:#e50914; cursor:pointer;
  }
  .slider-row input[type=range]::-moz-range-thumb {
    width:18px; height:18px; border-radius:50%; background:#e50914; border:none; cursor:pointer;
  }
  .slider-val { min-width:36px; text-align:right; font-size:13px; color:rgba(255,255,255,0.55); }

  .upload-btn {
    width:100%; padding:12px;
    border:1.5px dashed rgba(255,255,255,0.2); border-radius:8px;
    background:transparent; color:rgba(255,255,255,0.55);
    font-size:14px; font-family:'Noto Sans KR',sans-serif;
    cursor:pointer; text-align:center; transition:all .2s;
  }
  .upload-btn:hover { border-color:rgba(255,255,255,0.5); color:#fff; background:rgba(255,255,255,0.04); }
  #file-input { display:none; }
  #file-name { font-size:11px; color:rgba(255,255,255,0.3); text-align:center; margin-top:4px; }

  .size-row { display:flex; gap:8px; }
  .size-btn {
    flex:1; padding:8px 4px; border-radius:6px;
    border:1px solid rgba(255,255,255,0.12); background:transparent;
    color:rgba(255,255,255,0.45); font-size:12px;
    font-family:'Noto Sans KR',sans-serif; cursor:pointer; transition:all .2s;
  }
  .size-btn.active { border-color:#e50914; color:#fff; background:rgba(229,9,20,0.12); }

  .dl-btn {
    width:100%; padding:14px; background:#e50914; color:#fff;
    border:none; border-radius:8px; font-size:16px; font-weight:700;
    font-family:'Noto Sans KR',sans-serif; cursor:pointer;
    transition:background .2s, transform .1s;
  }
  .dl-btn:hover { background:#c8060f; }
  .dl-btn:active { transform:scale(.98); }
  .tip { font-size:11px; color:rgba(255,255,255,0.28); text-align:center; }
</style>
</head>
<body>

<h1>🎬 블로그 썸네일 메이커</h1>
<p class="subtitle">넷플릭스 스타일 썸네일을 쉽게 만들어 보세요</p>

<div class="preview-wrap">
  <div class="preview-box" id="preview-box">
    <canvas id="preview-canvas"></canvas>
    <div id="drag-hint">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <circle cx="8.5" cy="8.5" r="1.5"/>
        <polyline points="21 15 16 10 5 21"/>
      </svg>
      <span>이미지를 업로드해 주세요</span>
    </div>
    <div id="move-hint" style="display:none;">✥ 드래그해서 이미지 위치 조정</div>
  </div>
</div>

<div class="form-card">
  <div class="field">
    <label>제목</label>
    <input type="text" id="inp-title" placeholder="예: 악마는 프라다를 입는다2">
  </div>
  <div class="field">
    <label>부제목</label>
    <input type="text" id="inp-sub" placeholder="예: 20년만의 속편 보기전 꼭 알아야 할 정보">
  </div>
  <div class="field">
    <label>배경 이미지 — 업로드 후 미리보기에서 드래그로 위치 조정</label>
    <button class="upload-btn" onclick="document.getElementById('file-input').click()">
      📁 이미지 선택 (JPG, PNG)
    </button>
    <input type="file" id="file-input" accept="image/*">
    <div id="file-name">선택된 파일 없음</div>
  </div>
  <div class="field">
    <label>재생 위치 조절</label>
    <div class="slider-row">
      <input type="range" id="progress-slider" min="0" max="100" value="20" step="1">
      <span class="slider-val" id="progress-val">20%</span>
    </div>
  </div>
  <div class="field">
    <label>저장 크기</label>
    <div class="size-row">
      <button class="size-btn active" data-size="1080">1080×1080</button>
      <button class="size-btn" data-size="800">800×800</button>
      <button class="size-btn" data-size="600">600×600</button>
    </div>
  </div>
  <button class="dl-btn" id="dl-btn">⬇ 썸네일 다운로드</button>
  <p class="tip">PNG 파일로 저장됩니다</p>
</div>

<script>
let loadedImage  = null;
let imgOffsetX   = 0.5;
let imgOffsetY   = 0.5;
let selectedSize = 1080;
let progressPct  = 20;
let titleText    = '제목을 입력하세요';
let subText      = '부제목을 입력하세요';

const box      = document.getElementById('preview-box');
const pCanvas  = document.getElementById('preview-canvas');
const pCtx     = pCanvas.getContext('2d');
const dragHint = document.getElementById('drag-hint');
const moveHint = document.getElementById('move-hint');

function renderThumb(ctx, S) {
  ctx.clearRect(0, 0, S, S);
  if (loadedImage) {
    const iw = loadedImage.naturalWidth, ih = loadedImage.naturalHeight;
    const sc = Math.max(S / iw, S / ih);
    const sw = iw * sc, sh = ih * sc;
    ctx.globalAlpha = 0.75;
    ctx.drawImage(loadedImage, (S - sw) * imgOffsetX, (S - sh) * imgOffsetY, sw, sh);
    ctx.globalAlpha = 1;
  } else {
    ctx.fillStyle = '#1a1a1a'; ctx.fillRect(0, 0, S, S);
  }
  const grad = ctx.createLinearGradient(0, 0, 0, S);
  grad.addColorStop(0,    'rgba(0,0,0,0.38)');
  grad.addColorStop(0.45, 'rgba(0,0,0,0.08)');
  grad.addColorStop(1,    'rgba(0,0,0,0.72)');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, S, S);
  ctx.textBaseline = 'alphabetic';
  const leftX = S * 0.05, maxW = S * 0.90;
  let curY = S * 0.13;
  let titleFs = Math.round(S * 0.088);
  const minTitleFs = Math.round(S * 0.030);
  ctx.fillStyle = '#fff';
  ctx.shadowColor = 'rgba(0,0,0,0.75)'; ctx.shadowBlur = S * 0.016;
  ctx.font = `900 ${titleFs}px "Noto Sans KR",sans-serif`;
  while (titleFs > minTitleFs && ctx.measureText(titleText).width > maxW) {
    titleFs -= 2;
    ctx.font = `900 ${titleFs}px "Noto Sans KR",sans-serif`;
  }
  ctx.fillText(titleText, leftX, curY + titleFs);
  curY += titleFs + S * 0.018;
  let subFs = Math.round(S * 0.034);
  const minSubFs = Math.round(S * 0.014);
  ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.shadowBlur = S * 0.009;
  ctx.font = `500 ${subFs}px "Noto Sans KR",sans-serif`;
  while (subFs > minSubFs && ctx.measureText(subText).width > maxW) {
    subFs--;
    ctx.font = `500 ${subFs}px "Noto Sans KR",sans-serif`;
  }
  ctx.fillText(subText, leftX, curY + subFs);
  curY += subFs + S * 0.028;
  ctx.shadowBlur = 0;
  const btnH = S * 0.05, btnR = S * 0.01, btnFs = Math.round(S * 0.022);
  ctx.font = `700 ${btnFs}px "Noto Sans KR",sans-serif`;
  const playLabel = '▶  감상 하기';
  const playW = ctx.measureText(playLabel).width + S * 0.038;
  ctx.fillStyle = '#fff'; roundRect(ctx, leftX, curY, playW, btnH, btnR); ctx.fill();
  ctx.fillStyle = '#111'; ctx.fillText(playLabel, leftX + S * 0.018, curY + btnH * 0.665);
  const infoLabel = 'ⓘ  More Info';
  const infoW = ctx.measureText(infoLabel).width + S * 0.038;
  ctx.fillStyle = 'rgba(80,80,80,0.78)';
  roundRect(ctx, leftX + playW + S * 0.014, curY, infoW, btnH, btnR); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.fillText(infoLabel, leftX + playW + S * 0.014 + S * 0.018, curY + btnH * 0.665);
  const pbH = Math.max(2, Math.round(S * 0.004));
  const pbY = S * 0.918, pbL = S * 0.04, pbW = S * 0.92;
  const fillW = pbW * (progressPct / 100);
  ctx.fillStyle = 'rgba(255,255,255,0.28)'; ctx.fillRect(pbL, pbY, pbW, pbH);
  ctx.fillStyle = '#e50914'; ctx.fillRect(pbL, pbY, fillW, pbH);
  ctx.beginPath();
  ctx.arc(pbL + fillW, pbY + pbH / 2, Math.max(4, S * 0.007), 0, Math.PI * 2);
  ctx.fill();
  drawCtrlBar(ctx, S);
}

function drawCtrlBar(ctx, S) {
  const sz  = S * 0.027;
  const cy  = S * 0.955;
  const gap = S * 0.050;
  const lx  = S * 0.040;
  const rx  = S - S * 0.040;
  const k   = sz / 24;
  ctx.save();
  ctx.shadowBlur  = 0;
  ctx.fillStyle   = 'rgba(255,255,255,0.90)';
  ctx.strokeStyle = 'rgba(255,255,255,0.90)';
  function at(cx, fn) {
    ctx.save();
    ctx.translate(cx - sz / 2, cy - sz / 2);
    ctx.scale(k, k);
    ctx.lineWidth = 2.2 / k;
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    fn();
    ctx.restore();
  }
  at(lx, () => {
    ctx.fillRect(5.5, 4, 4.5, 16);
    ctx.fillRect(14, 4, 4.5, 16);
  });
  at(lx + gap, () => {
    ctx.beginPath();
    ctx.arc(12, 12.5, 8, 0.55, Math.PI * 1.45, false);
    ctx.stroke();
    const a = Math.PI * 1.45;
    const px = 12 + 8 * Math.cos(a), py = 12.5 + 8 * Math.sin(a);
    const tdx = Math.sin(a), tdy = -Math.cos(a);
    ctx.beginPath();
    ctx.moveTo(px + tdx * 3, py + tdy * 3);
    ctx.lineTo(px - tdy * 2.5, py + tdx * 2.5);
    ctx.lineTo(px + tdy * 2.5, py - tdx * 2.5);
    ctx.closePath(); ctx.fill();
    ctx.font = 'bold 7px sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('10', 12, 12.5);
  });
  at(lx + gap * 2, () => {
    ctx.beginPath();
    ctx.arc(12, 12.5, 8, Math.PI - 0.55, -Math.PI * 0.45, true);
    ctx.stroke();
    const a = -Math.PI * 0.45;
    const px = 12 + 8 * Math.cos(a), py = 12.5 + 8 * Math.sin(a);
    const tdx = -Math.sin(a), tdy = Math.cos(a);
    ctx.beginPath();
    ctx.moveTo(px + tdx * 3, py + tdy * 3);
    ctx.lineTo(px - tdy * 2.5, py + tdx * 2.5);
    ctx.lineTo(px + tdy * 2.5, py - tdx * 2.5);
    ctx.closePath(); ctx.fill();
    ctx.font = 'bold 7px sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('10', 12, 12.5);
  });
  at(lx + gap * 3, () => {
    ctx.beginPath();
    ctx.moveTo(11, 5); ctx.lineTo(6, 9); ctx.lineTo(2.5, 9);
    ctx.lineTo(2.5, 15); ctx.lineTo(6, 15); ctx.lineTo(11, 19);
    ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.arc(12.5, 12, 4,   -Math.PI * 0.5, Math.PI * 0.5, false); ctx.stroke();
    ctx.beginPath(); ctx.arc(12.5, 12, 7.5, -Math.PI * 0.5, Math.PI * 0.5, false); ctx.stroke();
  });
  at(rx - gap * 3, () => {
    ctx.beginPath();
    ctx.moveTo(4, 4); ctx.lineTo(17, 12); ctx.lineTo(4, 20);
    ctx.closePath(); ctx.fill();
    ctx.fillRect(18, 4, 2.5, 16);
  });
  at(rx - gap * 2, () => {
    [6, 12, 18].forEach(y => {
      ctx.beginPath(); ctx.arc(3.5, y, 1.5, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(8, y); ctx.lineTo(22, y); ctx.stroke();
    });
  });
  at(rx - gap, () => {
    ctx.beginPath();
    ctx.moveTo(4, 3.5); ctx.lineTo(20, 3.5);
    ctx.arcTo(22.5, 3.5, 22.5, 6, 2.5);
    ctx.lineTo(22.5, 16);
    ctx.arcTo(22.5, 18.5, 20, 18.5, 2.5);
    ctx.lineTo(14, 18.5); ctx.lineTo(10, 22); ctx.lineTo(10, 18.5);
    ctx.lineTo(4, 18.5);
    ctx.arcTo(1.5, 18.5, 1.5, 16, 2.5);
    ctx.lineTo(1.5, 6);
    ctx.arcTo(1.5, 3.5, 4, 3.5, 2.5);
    ctx.closePath(); ctx.stroke();
  });
  at(rx, () => {
    const d = 4.5, m = 2;
    ctx.beginPath(); ctx.moveTo(m + d, m); ctx.lineTo(m, m); ctx.lineTo(m, m + d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(24 - m - d, m); ctx.lineTo(24 - m, m); ctx.lineTo(24 - m, m + d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(m + d, 24 - m); ctx.lineTo(m, 24 - m); ctx.lineTo(m, 24 - m - d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(24 - m - d, 24 - m); ctx.lineTo(24 - m, 24 - m); ctx.lineTo(24 - m, 24 - m - d); ctx.stroke();
  });
  ctx.restore();
}

function drawPreview() { renderThumb(pCtx, pCanvas.width); }
function resizeCanvas() { pCanvas.width = box.offsetWidth; pCanvas.height = box.offsetHeight; drawPreview(); }
window.addEventListener('load', () => document.fonts.ready.then(resizeCanvas));
window.addEventListener('resize', resizeCanvas);

document.getElementById('inp-title').addEventListener('input', e => { titleText = e.target.value || '제목을 입력하세요'; drawPreview(); });
document.getElementById('inp-sub').addEventListener('input', e => { subText = e.target.value || '부제목을 입력하세요'; drawPreview(); });
document.getElementById('file-input').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  document.getElementById('file-name').textContent = file.name;
  const img = new Image();
  img.onload = () => {
    loadedImage = img; imgOffsetX = 0.5; imgOffsetY = 0.5;
    dragHint.classList.add('hidden');
    moveHint.style.display = 'block'; moveHint.style.opacity = '1';
    clearTimeout(window._hintTimer);
    window._hintTimer = setTimeout(() => moveHint.classList.add('fade'), 2500);
    drawPreview();
  };
  img.src = URL.createObjectURL(file);
});
document.getElementById('progress-slider').addEventListener('input', e => {
  progressPct = parseInt(e.target.value);
  document.getElementById('progress-val').textContent = progressPct + '%';
  drawPreview();
});
document.querySelectorAll('.size-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedSize = parseInt(btn.dataset.size);
  });
});
document.getElementById('dl-btn').addEventListener('click', async () => {
  await document.fonts.ready;
  const S = selectedSize;
  const canvas = document.createElement('canvas');
  canvas.width = S; canvas.height = S;
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  renderThumb(ctx, S);
  const title = document.getElementById('inp-title').value || 'thumbnail';
  const link = document.createElement('a');
  link.download = (title.slice(0, 20).replace(/[^\w가-힣]/g, '_') || 'thumbnail') + '_' + S + '.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
});
let isDragging = false, lastX = 0, lastY = 0;
function getXY(e) { return e.touches ? { x: e.touches[0].clientX, y: e.touches[0].clientY } : { x: e.clientX, y: e.clientY }; }
box.addEventListener('mousedown',  e => { if (!loadedImage) return; isDragging = true; const p = getXY(e); lastX = p.x; lastY = p.y; });
box.addEventListener('touchstart', e => { if (!loadedImage) return; isDragging = true; const p = getXY(e); lastX = p.x; lastY = p.y; }, { passive: true });
window.addEventListener('mousemove', e => {
  if (!isDragging || !loadedImage) return;
  const p = getXY(e), dx = p.x - lastX, dy = p.y - lastY;
  lastX = p.x; lastY = p.y;
  const S = pCanvas.width;
  const sc = Math.max(S / loadedImage.naturalWidth, S / loadedImage.naturalHeight);
  const rx = loadedImage.naturalWidth  * sc - S;
  const ry = loadedImage.naturalHeight * sc - S;
  if (rx > 0) imgOffsetX = Math.min(1, Math.max(0, imgOffsetX - dx / rx));
  if (ry > 0) imgOffsetY = Math.min(1, Math.max(0, imgOffsetY - dy / ry));
  drawPreview();
});
window.addEventListener('touchmove', e => {
  if (!isDragging || !loadedImage) return;
  if (e.cancelable) e.preventDefault();
  const p = getXY(e), dx = p.x - lastX, dy = p.y - lastY;
  lastX = p.x; lastY = p.y;
  const S = pCanvas.width;
  const sc = Math.max(S / loadedImage.naturalWidth, S / loadedImage.naturalHeight);
  const rx = loadedImage.naturalWidth  * sc - S;
  const ry = loadedImage.naturalHeight * sc - S;
  if (rx > 0) imgOffsetX = Math.min(1, Math.max(0, imgOffsetX - dx / rx));
  if (ry > 0) imgOffsetY = Math.min(1, Math.max(0, imgOffsetY - dy / ry));
  drawPreview();
}, { passive: false });
window.addEventListener('mouseup',  () => isDragging = false);
window.addEventListener('touchend', () => isDragging = false);
function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r); ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h); ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r); ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}
</script>
</body>
</html>"""

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
  body { background: var(--bg); color: var(--text); font-family: 'Pretendard', -apple-system, sans-serif; min-height: 100vh; }
  .app { display: grid; grid-template-columns: 380px 1fr; min-height: 100vh; }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 28px 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 0; }
  .sidebar-logo { font-size: 13px; letter-spacing: 3px; color: var(--accent); text-transform: uppercase; margin-bottom: 6px; }
  .sidebar-title { font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 28px; line-height: 1.3; }
  .section { margin-bottom: 24px; }
  .section-label { font-size: 9px; font-weight: 700; letter-spacing: 2px; color: var(--accent); text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
  .section-label::after { content: ''; flex: 1; height: 0.5px; background: var(--border); }
  .field { margin-bottom: 10px; }
  .field label { display: block; font-size: 11px; color: var(--text-muted); margin-bottom: 5px; letter-spacing: 0.3px; }
  .field input[type="text"], .field textarea, .field input[type="date"], .field input[type="time"] { width: 100%; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 9px 12px; color: var(--text); font-family: 'Pretendard', sans-serif; font-size: 13px; outline: none; transition: border-color 0.2s; resize: vertical; }
  .field input[type="text"]:focus, .field textarea:focus, .field input[type="date"]:focus, .field input[type="time"]:focus { border-color: var(--accent); }
  .field textarea { min-height: 72px; }
  .field input[type="color"] { width: 100%; height: 36px; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; cursor: pointer; padding: 2px 4px; }
  .upload-zone { border: 1.5px dashed var(--border); border-radius: 10px; padding: 18px 12px; text-align: center; cursor: pointer; transition: border-color 0.2s, background 0.2s; position: relative; }
  .upload-zone:hover { border-color: var(--accent); background: rgba(212,165,116,0.04); }
  .upload-zone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  .upload-zone span { font-size: 11px; color: var(--text-muted); }
  .upload-zone .preview-img { width: 100%; border-radius: 8px; margin-top: 8px; max-height: 120px; object-fit: cover; display: none; }
  .card-tabs { display: flex; gap: 4px; margin-bottom: 20px; background: var(--surface2); border-radius: 10px; padding: 4px; }
  .tab-btn { flex: 1; background: none; border: none; padding: 7px 0; font-size: 11px; font-weight: 500; color: var(--text-muted); border-radius: 7px; cursor: pointer; transition: all 0.2s; font-family: 'Pretendard', sans-serif; }
  .tab-btn.active { background: var(--accent); color: #1a0f00; }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }
  .btn-download { width: 100%; max-width: 540px; padding: 15px; background: var(--accent); color: #1a0f00; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; font-family: 'Pretendard', sans-serif; letter-spacing: 0.5px; transition: opacity 0.2s; margin-top: 16px; }
  .btn-download:hover { opacity: 0.88; }
  .preview-area { background: var(--bg); padding: 40px 32px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
  .preview-header { width: 100%; max-width: 900px; margin-bottom: 28px; }
  .preview-header-title { font-size: 13px; color: var(--text-muted); letter-spacing: 1px; font-weight: 400; }
  .cards-container { width: 100%; display: flex; flex-direction: column; align-items: center; }
  .card-panel { display: none; width: 100%; flex-direction: column; align-items: center; gap: 20px; }
  .card-panel.active { display: flex; }
  .canvas-wrapper { width: 100%; max-width: 540px; position: relative; margin-top: 28px; }
  @media (max-width: 768px) {
    .app { grid-template-columns: 1fr; grid-template-rows: auto 1fr; min-height: 100vh; }
    .sidebar { border-right: none; border-bottom: 1px solid var(--border); max-height: 56vh; overflow-y: auto; padding: 20px 16px; }
    .card-tabs { position: sticky; top: -20px; z-index: 10; background: var(--surface); padding: 8px 0 4px; }
    .preview-area { padding: 20px 16px 48px; }
    .canvas-wrapper { max-width: 100%; }
    .preview-header-title { font-size: 11px; }
  }
  .canvas-num { position: absolute; top: -22px; left: 0; font-size: 10px; color: var(--text-dim); letter-spacing: 2px; text-transform: uppercase; }
  .canvas-card { width: 100%; aspect-ratio: 4/5; border-radius: 0; overflow: hidden; position: relative; font-family: 'Pretendard', sans-serif; }
  .card1 { background: #1a1510; }
  .card1-bg { position: absolute; inset: 0; background-size: cover; background-position: center; transition: opacity 0.4s; }
  .card1-scrim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.05) 25%, rgba(0,0,0,0.4) 55%, rgba(0,0,0,0.88) 100%); }
  .card1-logo { position: absolute; top: 4.5%; right: 5%; font-size: clamp(7px, 1.5vw, 11px); letter-spacing: 3px; color: rgba(255,255,255,0.75); border: 0.8px solid rgba(255,255,255,0.35); padding: 3px 10px; border-radius: 3px; }
  .card1-bottom { position: absolute; bottom: 0; left: 0; right: 0; padding: 5% 6% 6%; display: flex; flex-direction: column; }
  .card1-badge { display: inline-flex; align-items: center; gap: 6px; border: 0.8px solid rgba(212,165,116,0.7); border-radius: 20px; padding: 3px 12px; font-size: clamp(7px, 1.2vw, 9.5px); color: var(--accent2); width: fit-content; margin-bottom: 3.5%; letter-spacing: 1px; }
  .badge-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); animation: pulse 2s ease-in-out infinite; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
  .card1-eyebrow { font-size: clamp(7px, 1.3vw, 10px); color: rgba(212,165,116,0.8); letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 2%; font-weight: 400; }
  .card1-title { font-size: clamp(18px, 5vw, 38px); font-weight: 700; color: #fff; line-height: 1.2; margin-bottom: 1%; }
  .card1-title-en { font-size: clamp(8px, 1.5vw, 11px); color: rgba(255,255,255,0.4); letter-spacing: 1px; margin-bottom: 4%; }
  .card1-divider { height: 0.5px; background: rgba(255,255,255,0.18); margin-bottom: 3.5%; }
  .card1-meta { display: flex; gap: 5%; flex-wrap: wrap; }
  .card1-meta-item { display: flex; align-items: center; gap: 5px; font-size: clamp(7px, 1.3vw, 10px); color: rgba(255,255,255,0.72); }
  .card1-meta-item svg { width: clamp(9px, 1.5vw, 12px); height: clamp(9px, 1.5vw, 12px); stroke: var(--accent); fill: none; flex-shrink: 0; }
  .card2 { background: #0e0c0a; }
  .card2-photo { height: 42%; position: relative; overflow: hidden; background: #1e1a15; }
  .card2-photo-bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
  .card2-photo-scrim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.6)); }
  .card2-body { height: 58%; padding: 5% 6%; display: flex; flex-direction: column; }
  .card2-eyebrow { font-size: clamp(7px, 1.1vw, 9px); font-weight: 700; letter-spacing: 2px; color: var(--accent); text-transform: uppercase; margin-bottom: 5%; }
  .card2-info-list { display: flex; flex-direction: column; flex: 1; }
  .card2-info-row { display: flex; align-items: center; gap: 4%; padding: 3.5% 0; border-bottom: 0.5px solid rgba(255,255,255,0.06); }
  .card2-info-row:last-of-type { border-bottom: none; }
  .card2-info-icon { width: clamp(14px, 2.5vw, 20px); height: clamp(14px, 2.5vw, 20px); stroke: var(--accent); fill: none; flex-shrink: 0; }
  .card2-info-key { font-size: clamp(7px, 1.1vw, 9px); color: rgba(255,255,255,0.35); min-width: 15%; letter-spacing: 0.5px; }
  .card2-info-val { font-size: clamp(9px, 1.6vw, 12px); color: rgba(255,255,255,0.88); font-weight: 500; flex: 1; line-height: 1.4; }
  .card2-include { margin-top: auto; background: rgba(212,165,116,0.08); border: 0.5px solid rgba(212,165,116,0.25); border-radius: 8px; padding: 3% 4%; font-size: clamp(8px, 1.3vw, 10px); color: rgba(255,255,255,0.6); line-height: 1.6; display: flex; align-items: center; gap: 6px; }
  .card2-include svg { width: clamp(10px, 1.8vw, 14px); height: clamp(10px, 1.8vw, 14px); stroke: var(--accent); fill: none; flex-shrink: 0; }
  .card3 { background: #0e0c0a; }
  .card3-photo { height: 35%; position: relative; overflow: hidden; background: #1a1510; flex-shrink: 0; }
  .card3-photo-bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
  .card3-photo-scrim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.7)); }
  .card3-film-strip { position: absolute; bottom: 6%; left: 5%; display: flex; gap: 4px; align-items: center; }
  .film-dot { width: clamp(4px, 0.8vw, 6px); height: clamp(4px, 0.8vw, 6px); border-radius: 50%; background: rgba(212,165,116,0.6); }
  .film-dot:nth-child(2) { opacity: 0.4; }
  .film-dot:nth-child(3) { opacity: 0.2; }
  .card3-body { flex: 1; padding: 5% 6%; display: flex; flex-direction: column; justify-content: space-between; }
  .card3-section-label { font-size: clamp(7px, 1.1vw, 9px); font-weight: 700; letter-spacing: 2px; color: var(--accent); text-transform: uppercase; margin-bottom: 5%; }
  .card3-items { display: flex; flex-direction: column; flex: 1; }
  .card3-item { display: flex; align-items: flex-start; gap: 3%; padding: 3.5% 0; border-bottom: 0.5px solid rgba(255,255,255,0.06); }
  .card3-item:last-of-type { border-bottom: none; }
  .card3-item-dot { width: clamp(4px, 0.9vw, 6px); height: clamp(4px, 0.9vw, 6px); border-radius: 50%; background: var(--accent); flex-shrink: 0; margin-top: clamp(4px, 0.9vw, 7px); }
  .card3-item-text { font-size: clamp(9px, 1.55vw, 12px); color: rgba(255,255,255,0.82); line-height: 1.5; font-weight: 400; }
  .card3-closing { padding-top: 4%; font-size: clamp(8px, 1.3vw, 10.5px); color: rgba(212,165,116,0.75); font-style: italic; letter-spacing: 0.3px; border-top: 0.5px solid rgba(255,255,255,0.08); }
  .card4 { background: #0e0c0a; }
  .card4-photo { height: 50%; position: relative; overflow: hidden; background: #1a1510; flex-shrink: 0; }
  .card4-photo-bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
  .card4-photo-scrim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.65)); }
  .card4-body { height: 50%; padding: 5% 6%; display: flex; flex-direction: column; justify-content: space-between; }
  .card4-how-label { font-size: clamp(7px, 1.1vw, 9px); font-weight: 700; letter-spacing: 2px; color: var(--accent); text-transform: uppercase; margin-bottom: 3%; }
  .card4-how-text { font-size: clamp(9px, 1.5vw, 11.5px); color: rgba(255,255,255,0.65); line-height: 1.7; }
  .card4-divider { height: 0.5px; background: rgba(255,255,255,0.1); margin-bottom: 4%; }
  .card4-account-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4%; }
  .card4-account { font-size: clamp(10px, 1.8vw, 13px); font-weight: 700; color: rgba(255,255,255,0.8); }
  .card4-host { font-size: clamp(7px, 1.1vw, 9px); color: rgba(255,255,255,0.3); }
  .card4-cta { width: 100%; background: var(--accent); border-radius: 8px; padding: 4% 0; text-align: center; font-size: clamp(9px, 1.6vw, 12px); font-weight: 700; color: #1a0f00; letter-spacing: 1px; border: none; font-family: 'Pretendard', sans-serif; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
  .toast { position: fixed; bottom: 28px; right: 28px; background: var(--accent); color: #1a0f00; padding: 10px 18px; border-radius: 8px; font-size: 13px; font-weight: 600; opacity: 0; transform: translateY(8px); transition: all 0.3s; pointer-events: none; z-index: 999; }
  .toast.show { opacity: 1; transform: translateY(0); }
  .color-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="sidebar-logo">MK CINELAB</div>
    <div class="sidebar-title">카드뉴스 메이커</div>
    <div class="card-tabs">
      <button class="tab-btn active" onclick="switchTab(0)">카드 1</button>
      <button class="tab-btn" onclick="switchTab(1)">카드 2</button>
      <button class="tab-btn" onclick="switchTab(2)">카드 3</button>
      <button class="tab-btn" onclick="switchTab(3)">카드 4</button>
    </div>
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
        <div class="field"><label>상단 레이블</label><input type="text" id="c1-eyebrow" value="5월 대구영화모임" oninput="update()"></div>
        <div class="field"><label>영화 제목 (한글)</label><input type="text" id="c1-title" value="펀치 드렁크 러브" oninput="update()"></div>
        <div class="field"><label>영화 제목 (영문 + 연도)</label><input type="text" id="c1-title-en" value="Punch-Drunk Love, 2002" oninput="update()"></div>
        <div class="field"><label>날짜</label><input type="date" id="c1-date" onchange="updateDates()"></div>
        <div class="field"><label>장소</label><input type="text" id="c1-place" value="Lawns, 대구" oninput="update()"></div>
        <div class="field"><label>모집 뱃지 문구</label><input type="text" id="c1-badge" value="인원 모집 중" oninput="update()"></div>
      </div>
    </div>
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
        <div class="field"><label>날짜</label><input type="date" id="c2-date" value="2025-05-03" onchange="updateDates()"></div>
        <div class="field"><label>시작 시간</label><input type="time" id="c2-time-start" value="19:00" onchange="updateDates()"></div>
        <div class="field"><label>종료 시간</label><input type="time" id="c2-time-end" value="22:30" onchange="updateDates()"></div>
        <div class="field"><label>장소</label><input type="text" id="c2-place" value="Lawns (론스)" oninput="update()"></div>
        <div class="field"><label>참가비</label><input type="text" id="c2-fee" value="15,000원 / 1인" oninput="update()"></div>
        <div class="field"><label>신청 방법</label><input type="text" id="c2-apply" value="인스타그램 DM 신청" oninput="update()"></div>
        <div class="field"><label>포함 사항</label><input type="text" id="c2-include" value="웰컴 드링크 1잔 포함" oninput="update()"></div>
      </div>
    </div>
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
        <div class="field"><label>섹션 레이블</label><input type="text" id="c3-label" value="이런 분들 오세요" oninput="update()"></div>
        <div class="field"><label>항목 1</label><input type="text" id="c3-item1" value="다른 사람들과 영화에 대해 이야기하고 싶은 분" oninput="update()"></div>
        <div class="field"><label>항목 2</label><input type="text" id="c3-item2" value="영화 한 편으로 다양한 이야기를 나누고 싶은 분" oninput="update()"></div>
        <div class="field"><label>항목 3</label><input type="text" id="c3-item3" value="보고 싶었지만 혼자 보기 아쉬웠던 영화가 있는 분" oninput="update()"></div>
        <div class="field"><label>항목 4 (선택)</label><input type="text" id="c3-item4" value="좋은 공간에서 편안하게 영화를 즐기고 싶은 분" oninput="update()"></div>
        <div class="field"><label>하단 한마디</label><input type="text" id="c3-closing" value="영화를 좋아한다면, 그걸로 충분합니다." oninput="update()"></div>
      </div>
    </div>
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
        <div class="field"><label>신청 안내 문구</label><textarea id="c4-howtext" oninput="update()">참가 신청은 인스타그램
DM으로 받습니다.
선착순 마감이니 서둘러주세요.</textarea></div>
        <div class="field"><label>인스타그램 계정</label><input type="text" id="c4-account" value="@daegu_movie" oninput="update()"></div>
        <div class="field"><label>기획·주최</label><input type="text" id="c4-host" value="기획·주최 MK CINELAB" oninput="update()"></div>
        <div class="field"><label>CTA 버튼 문구</label><input type="text" id="c4-cta" value="DM으로 신청하기" oninput="update()"></div>
      </div>
    </div>
    <div class="section" style="margin-top: 8px;">
      <div class="section-label">포인트 컬러</div>
      <div class="color-row">
        <div class="field"><label>메인 포인트</label><input type="color" id="color-accent" value="#d4a574" oninput="updateColor()"></div>
        <div class="field"><label>포인트 밝기</label><input type="color" id="color-accent2" value="#e8c49a" oninput="updateColor()"></div>
      </div>
    </div>
  </aside>
  <main class="preview-area">
    <div class="preview-header"><span class="preview-header-title">PREVIEW — 1080 × 1350 (4:5)</span></div>
    <div class="cards-container">
      <div class="card-panel active" id="panel-0">
      <div class="canvas-wrapper">
        <div class="canvas-num">01 — 모집 커버</div>
        <div class="canvas-card card1" id="canvas-card1">
          <div class="card1-bg" id="card1-bg"></div>
          <div class="card1-scrim"></div>
          <div class="card1-logo">MK CINELAB</div>
          <div class="card1-bottom">
            <div class="card1-badge"><div class="badge-dot"></div><span id="d-c1-badge">인원 모집 중</span></div>
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
      </div>
      <div class="card-panel" id="panel-1">
      <div class="canvas-wrapper">
        <div class="canvas-num">02 — 모임 정보</div>
        <div class="canvas-card card2" id="canvas-card2">
          <div class="card2-photo"><div class="card2-photo-bg" id="card2-photo-bg"></div><div class="card2-photo-scrim"></div></div>
          <div class="card2-body">
            <div class="card2-eyebrow">모임 정보</div>
            <div class="card2-info-list">
              <div class="card2-info-row"><svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg><span class="card2-info-key">일시</span><span class="card2-info-val" id="d-c2-datetime">5월 3일 (일)  19:00 ~ 22:30</span></div>
              <div class="card2-info-row"><svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg><span class="card2-info-key">장소</span><span class="card2-info-val" id="d-c2-place">Lawns (론스)</span></div>
              <div class="card2-info-row"><svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg><span class="card2-info-key">비용</span><span class="card2-info-val" id="d-c2-fee">15,000원 / 1인</span></div>
              <div class="card2-info-row"><svg class="card2-info-icon" viewBox="0 0 24 24" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg><span class="card2-info-key">신청</span><span class="card2-info-val" id="d-c2-apply">인스타그램 DM 신청</span></div>
            </div>
            <div class="card2-include"><svg viewBox="0 0 24 24" stroke-width="1.8"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M8 12l2 2 4-4"/></svg><span id="d-c2-include">웰컴 드링크 1잔 포함</span></div>
          </div>
        </div>
      </div>
      </div>
      <div class="card-panel" id="panel-2">
      <div class="canvas-wrapper">
        <div class="canvas-num">03 — 모임 소개</div>
        <div class="canvas-card card3" id="canvas-card3">
          <div class="card3-photo"><div class="card3-photo-bg" id="card3-photo-bg"></div><div class="card3-photo-scrim"></div><div class="card3-film-strip"><div class="film-dot"></div><div class="film-dot"></div><div class="film-dot"></div></div></div>
          <div class="card3-body">
            <div>
              <div class="card3-section-label" id="d-c3-label">이런 분들 오세요</div>
              <div class="card3-items">
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item1">다른 사람들과 영화에 대해 이야기하고 싶은 분</span></div>
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item2">영화 한 편으로 다양한 이야기를 나누고 싶은 싶은 분</span></div>
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item3">보고 싶었지만 혼자 보기 아쉬웠던 영화가 있는 분</span></div>
                <div class="card3-item"><div class="card3-item-dot"></div><span class="card3-item-text" id="d-c3-item4">좋은 공간에서 편안하게 영화를 즐기고 싶은 분</span></div>
              </div>
            </div>
            <div class="card3-closing" id="d-c3-closing">영화를 좋아한다면, 그걸로 충분합니다.</div>
          </div>
        </div>
      </div>
      </div>
      <div class="card-panel" id="panel-3">
      <div class="canvas-wrapper">
        <div class="canvas-num">04 — 신청 안내</div>
        <div class="canvas-card card4" id="canvas-card4">
          <div class="card4-photo"><div class="card4-photo-bg" id="card4-photo-bg"></div><div class="card4-photo-scrim"></div></div>
          <div class="card4-body">
            <div>
              <div class="card4-how-label">신청 방법</div>
              <div class="card4-how-text" id="d-c4-howtext">참가 신청은 인스타그램<br>DM으로 받습니다.<br>선착순 마감이니 서둘러주세요.</div>
            </div>
            <div>
              <div class="card4-divider"></div>
              <div class="card4-account-row"><div class="card4-account" id="d-c4-account">@daegu_movie</div><div class="card4-host" id="d-c4-host">기획·주최 MK CINELAB</div></div>
              <div class="card4-cta" id="d-c4-cta">DM으로 신청하기</div>
            </div>
          </div>
        </div>
      </div>
      </div>
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
  const file = input.files[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const url = e.target.result;
    document.getElementById(bgId).style.backgroundImage = `url(${url})`;
    const prev = document.getElementById(prevId); prev.src = url; prev.style.display = 'block';
  };
  reader.readAsDataURL(file);
}
function update() {
  const map = {'c1-eyebrow':'d-c1-eyebrow','c1-badge':'d-c1-badge','c1-title':'d-c1-title','c1-title-en':'d-c1-title-en','c1-place':'d-c1-place','c2-place':'d-c2-place','c2-fee':'d-c2-fee','c2-apply':'d-c2-apply','c2-include':'d-c2-include','c3-label':'d-c3-label','c3-item1':'d-c3-item1','c3-item2':'d-c3-item2','c3-item3':'d-c3-item3','c3-item4':'d-c3-item4','c3-closing':'d-c3-closing','c4-account':'d-c4-account','c4-host':'d-c4-host','c4-cta':'d-c4-cta'};
  for (const [src, dst] of Object.entries(map)) { const el = document.getElementById(src); if (el) document.getElementById(dst).textContent = el.value; }
  const howtext = document.getElementById('c4-howtext').value;
  document.getElementById('d-c4-howtext').innerHTML = howtext.replace(/\n/g, '<br>');
}
function updateDates() {
  const DAYS = ['일','월','화','수','목','금','토'];
  function fmtDate(id) { const v = document.getElementById(id).value; if (!v) return ''; const d = new Date(v + 'T00:00:00'); return `${d.getMonth()+1}월 ${d.getDate()}일 (${DAYS[d.getDay()]})`; }
  document.getElementById('d-c1-date').textContent = fmtDate('c1-date');
  const date2Str = fmtDate('c2-date'); const ts = document.getElementById('c2-time-start').value; const te = document.getElementById('c2-time-end').value;
  document.getElementById('d-c2-datetime').textContent = `${date2Str}  ${ts} ~ ${te}`;
}
function updateColor() {
  const a = document.getElementById('color-accent').value; const a2 = document.getElementById('color-accent2').value;
  document.documentElement.style.setProperty('--accent', a); document.documentElement.style.setProperty('--accent2', a2);
}
function showToast(msg) { const t = document.getElementById('toast'); t.textContent = msg; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 2400); }
const CARD_LABELS = ['card1_cover','card2_info','card3_intro','card4_cta'];
function loadImg(src) { return new Promise(res => { const m = (src||'').match(/url\("?(.+?)"?\)/); const url = m ? m[1] : src; if (!url || url==='none') return res(null); const img = new Image(); img.onload = ()=>res(img); img.onerror = ()=>res(null); img.src = url; }); }
function bgCover(ctx, img, x, y, w, h) { if (!img) return; const s = Math.max(w/img.width, h/img.height); ctx.save(); ctx.beginPath(); ctx.rect(x,y,w,h); ctx.clip(); ctx.drawImage(img, x+(w-img.width*s)/2, y+(h-img.height*s)/2, img.width*s, img.height*s); ctx.restore(); }
function applyGrad(ctx, x, y, w, h, stops) { const g = ctx.createLinearGradient(x,y,x,y+h); stops.forEach(([p,c])=>g.addColorStop(p,c)); ctx.fillStyle=g; ctx.fillRect(x,y,w,h); }
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+r,r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r); ctx.arcTo(x,y+h,x,y+h-r,r); ctx.arcTo(x,y,x+r,y,r); ctx.closePath(); }
function wrapLines(ctx, text, maxW) { const res=[]; for (const seg of (text||'').split('\n')) { if (!seg.trim()) continue; if (ctx.measureText(seg).width<=maxW) { res.push(seg); continue; } const words=seg.split(' '); if (words.length>1) { let cur=''; for (const w of words) { const t=cur?cur+' '+w:w; if(ctx.measureText(t).width<=maxW) cur=t; else { if(cur)res.push(cur); cur=w; } } if(cur)res.push(cur); } else { let cur=''; for (const ch of seg) { if(ctx.measureText(cur+ch).width<=maxW)cur+=ch; else{res.push(cur);cur=ch;} } if(cur)res.push(cur); } } return res; }
function getBg(id) { return ((document.getElementById(id)||{style:{}}).style.backgroundImage)||''; }
function v(id) { return (document.getElementById(id)||{}).value||''; }
function t(id) { return ((document.getElementById(id)||{}).textContent||'').trim(); }
function getAc() { return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()||'#d4a574'; }
function getAc2() { return getComputedStyle(document.documentElement).getPropertyValue('--accent2').trim()||'#e8c49a'; }
const ICONS = {
  calendar(ctx,x,y,sz,col){ const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.lineJoin='round'; rr(ctx,3,4,18,18,2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(16,2);ctx.lineTo(16,6);ctx.moveTo(8,2);ctx.lineTo(8,6);ctx.moveTo(3,10);ctx.lineTo(21,10); ctx.stroke(); ctx.restore(); },
  pin(ctx,x,y,sz,col){ const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.lineJoin='round'; ctx.beginPath(); ctx.moveTo(21,10); ctx.bezierCurveTo(21,17,12,23,12,23); ctx.bezierCurveTo(12,23,3,17,3,10); ctx.bezierCurveTo(3,5,7,1,12,1); ctx.bezierCurveTo(17,1,21,5,21,10); ctx.closePath(); ctx.stroke(); ctx.beginPath(); ctx.arc(12,10,3,0,Math.PI*2); ctx.stroke(); ctx.restore(); },
  clock(ctx,x,y,sz,col){ const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.beginPath(); ctx.arc(12,12,10,0,Math.PI*2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(12,6);ctx.lineTo(12,12);ctx.lineTo(16,14); ctx.stroke(); ctx.restore(); },
  chat(ctx,x,y,sz,col){ const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.lineJoin='round'; ctx.beginPath(); ctx.moveTo(21,15); ctx.bezierCurveTo(21,16.1,20.1,17,19,17); ctx.lineTo(7,17); ctx.lineTo(3,21); ctx.lineTo(3,5); ctx.bezierCurveTo(3,3.9,3.9,3,5,3); ctx.lineTo(19,3); ctx.bezierCurveTo(20.1,3,21,3.9,21,5); ctx.closePath(); ctx.stroke(); ctx.restore(); },
  check(ctx,x,y,sz,col){ const s=sz/24; ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle=col; ctx.lineWidth=2/s; ctx.beginPath(); ctx.arc(12,12,10,0,Math.PI*2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(8,12);ctx.lineTo(10,14);ctx.lineTo(14,10); ctx.stroke(); ctx.restore(); },
};
async function renderCard(n) {
  const W=1080, H=1350, PX=W*0.06;
  const cv=document.createElement('canvas'); cv.width=W; cv.height=H;
  const ctx=cv.getContext('2d'); ctx.imageSmoothingEnabled=true; ctx.imageSmoothingQuality='high';
  const A=getAc(), A2=getAc2();
  const F=(w,sz)=>`${w} ${sz}px Pretendard,sans-serif`;
  if (n===0) {
    ctx.fillStyle='#1a1510'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card1-bg')), 0,0,W,H);
    applyGrad(ctx,0,0,W,H,[[0,'rgba(0,0,0,0.15)'],[0.25,'rgba(0,0,0,0.05)'],[0.55,'rgba(0,0,0,0.4)'],[1,'rgba(0,0,0,0.88)']]);
    const logoFSz=22; ctx.font=F('400',logoFSz); const ltxt='MK CINELAB', ltxtW=ctx.measureText(ltxt).width;
    const lPX=26, lPY=14, lW=ltxtW+lPX*2, lH=logoFSz+lPY*2; const lx=W-W*0.05-lW, ly=H*0.045;
    ctx.strokeStyle='rgba(255,255,255,0.35)'; ctx.lineWidth=1.5; rr(ctx,lx,ly,lW,lH,4); ctx.stroke();
    ctx.fillStyle='rgba(255,255,255,0.75)'; ctx.fillText(ltxt,lx+lPX,ly+lH*0.7);
    let cy=H-W*0.06;
    const metaFSz=22, metaISZ=28; ctx.font=F('400',metaFSz); ctx.fillStyle='rgba(255,255,255,0.72)';
    const ds=t('d-c1-date'), ps=t('d-c1-place');
    ICONS.calendar(ctx,PX,cy-metaISZ,metaISZ,A); ctx.fillText(ds,PX+metaISZ+8,cy-2);
    const dW=ctx.measureText(ds).width; const pinX=PX+metaISZ+8+dW+W*0.05;
    ICONS.pin(ctx,pinX,cy-metaISZ,metaISZ,A); ctx.fillText(ps,pinX+metaISZ+8,cy-2);
    cy -= metaISZ + W*0.035;
    ctx.beginPath(); ctx.moveTo(PX,cy); ctx.lineTo(W-PX,cy); ctx.strokeStyle='rgba(255,255,255,0.18)'; ctx.lineWidth=1; ctx.stroke();
    cy -= W*0.04;
    const titleEnFSz=26; ctx.font=F('400',titleEnFSz); ctx.fillStyle='rgba(255,255,255,0.4)'; ctx.fillText(v('c1-title-en'),PX,cy);
    cy -= titleEnFSz + W*0.01;
    const titleStr=v('c1-title'), maxTW=W-PX*2; let tSz=86;
    while(tSz>44){ ctx.font=F('700',tSz); if(ctx.measureText(titleStr).width<=maxTW) break; tSz-=4; }
    ctx.font=F('700',tSz); ctx.fillStyle='#fff';
    const tLines=wrapLines(ctx,titleStr,maxTW);
    for(let i=tLines.length-1; i>=0; i--){ ctx.fillText(tLines[i],PX,cy); cy-=tSz*1.2; }
    cy -= W*0.02;
    ctx.font=F('400',24); ctx.fillStyle=A+'cc'; ctx.fillText((v('c1-eyebrow')||'').toUpperCase(),PX,cy);
    cy -= 24 + W*0.035;
    const badgeFSz=22; ctx.font=F('400',badgeFSz); const bStr=v('c1-badge'), bTW=ctx.measureText(bStr).width;
    const bPadX=W*0.012, bH=44, dotR=7, dotGap=12; const bTotalW=bPadX+dotR*2+dotGap+bTW+bPadX;
    const bX=PX, bY=cy-bH; ctx.strokeStyle=A+'b3'; ctx.lineWidth=1.5; rr(ctx,bX,bY,bTotalW,bH,bH/2); ctx.stroke();
    ctx.fillStyle=A; ctx.beginPath(); ctx.arc(bX+bPadX+dotR,bY+bH/2,dotR,0,Math.PI*2); ctx.fill();
    ctx.fillStyle=A2; ctx.fillText(bStr,bX+bPadX+dotR*2+dotGap,bY+bH*0.68);
  } else if (n===1) {
    const PH=H*0.42, BH=H*0.58; ctx.fillStyle='#0e0c0a'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card2-photo-bg')),0,0,W,PH);
    applyGrad(ctx,0,0,W,PH,[[0,'rgba(0,0,0,0.1)'],[1,'rgba(0,0,0,0.6)']]);
    const bPT=W*0.05, bPB=W*0.05; const bodyTop=PH+bPT, bodyBottom=PH+BH-bPB;
    ctx.font=F('700',19); ctx.fillStyle=A; ctx.fillText('모임 정보',PX,bodyTop+19);
    const ISZ2=26, incTextFSz=22, incPadY=W*0.03, incPadX=W*0.04; const incH=Math.max(ISZ2,incTextFSz)+incPadY*2; const incY=bodyBottom-incH;
    const ISZ=32, keyFSz=19, valFSz=24; const GAP=W*0.04, KEY_W=W*0.15; const KEY_X=PX+ISZ+GAP, VAL_X=KEY_X+KEY_W+GAP;
    const listTop=bodyTop+19+W*0.05; const rH=(incY-W*0.02-listTop)/4;
    const rows=[{icon:'calendar',key:'일시',val:t('d-c2-datetime')},{icon:'pin',key:'장소',val:t('d-c2-place')},{icon:'clock',key:'비용',val:t('d-c2-fee')},{icon:'chat',key:'신청',val:t('d-c2-apply')}];
    rows.forEach((row,i)=>{ const ry=listTop+i*rH, mid=ry+rH/2; if(i<rows.length-1){ ctx.beginPath();ctx.moveTo(PX,ry+rH);ctx.lineTo(W-PX,ry+rH); ctx.strokeStyle='rgba(255,255,255,0.06)';ctx.lineWidth=1;ctx.stroke(); } ICONS[row.icon](ctx,PX,mid-ISZ/2,ISZ,A); ctx.font=F('400',keyFSz); ctx.fillStyle='rgba(255,255,255,0.35)'; ctx.fillText(row.key,KEY_X,mid+keyFSz*0.38); ctx.font=F('500',valFSz); ctx.fillStyle='rgba(255,255,255,0.88)'; ctx.fillText(row.val,VAL_X,mid+valFSz*0.38); });
    ctx.fillStyle=A+'14'; rr(ctx,PX,incY,W-PX*2,incH,10); ctx.fill(); ctx.strokeStyle=A+'40'; ctx.lineWidth=1; rr(ctx,PX,incY,W-PX*2,incH,10); ctx.stroke();
    ICONS.check(ctx,PX+incPadX,incY+(incH-ISZ2)/2,ISZ2,A); ctx.font=F('400',incTextFSz); ctx.fillStyle='rgba(255,255,255,0.6)'; ctx.fillText(t('d-c2-include'),PX+incPadX+ISZ2+12,incY+incH/2+incTextFSz*0.38);
  } else if (n===2) {
    const PH=H*0.35, BH=H*0.65; ctx.fillStyle='#0e0c0a'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card3-photo-bg')),0,0,W,PH);
    applyGrad(ctx,0,0,W,PH,[[0,'rgba(0,0,0,0.1)'],[1,'rgba(0,0,0,0.7)']]);
    const filmDotR=6; [1,0.4,0.2].forEach((op,i)=>{ ctx.fillStyle=`rgba(212,165,116,${op*0.6})`; ctx.beginPath(); ctx.arc(PX+i*(filmDotR*2+10),PH-PH*0.06,filmDotR,0,Math.PI*2); ctx.fill(); });
    const bPT=W*0.05, bPB=W*0.05; const bodyTop=PH+bPT;
    ctx.font=F('700',19); ctx.fillStyle=A; ctx.fillText((t('d-c3-label')||'').toUpperCase(),PX,bodyTop+19);
    const closFSz=22, closPT=W*0.04; const closBaselineY=H-W*0.05; const closBorderY=closBaselineY-closFSz*1.2-closPT;
    const items=[t('d-c3-item1'),t('d-c3-item2'),t('d-c3-item3'),t('d-c3-item4')].filter(x=>x.trim());
    const iStart=bodyTop+19+W*0.05; const iH=(closBorderY-8-iStart)/Math.max(items.length,1);
    const itemFSz=24, dotR2=6;
    items.forEach((item,i)=>{ const iy=iStart+i*iH, mid=iy+iH/2; if(i<items.length-1){ ctx.beginPath();ctx.moveTo(PX,iy+iH);ctx.lineTo(W-PX,iy+iH); ctx.strokeStyle='rgba(255,255,255,0.06)';ctx.lineWidth=1;ctx.stroke(); } ctx.fillStyle=A; ctx.beginPath(); ctx.arc(PX+dotR2,mid-itemFSz*0.35,dotR2,0,Math.PI*2); ctx.fill(); ctx.font=F('400',itemFSz); ctx.fillStyle='rgba(255,255,255,0.82)'; const ls=wrapLines(ctx,item,W-PX*2-dotR2*2-W*0.03); const lineH=itemFSz*1.5; const startY=mid-ls.length*lineH/2+lineH*0.75; ls.forEach((l,li)=>ctx.fillText(l,PX+dotR2*2+W*0.03,startY+li*lineH)); });
    ctx.beginPath(); ctx.moveTo(PX,closBorderY); ctx.lineTo(W-PX,closBorderY); ctx.strokeStyle='rgba(255,255,255,0.08)'; ctx.lineWidth=1; ctx.stroke();
    ctx.font=`italic 400 ${closFSz}px Pretendard,sans-serif`; ctx.fillStyle=A+'bf'; ctx.fillText(t('d-c3-closing'),PX,closBaselineY);
  } else if (n===3) {
    const PH=H*0.5, BH=H*0.5; ctx.fillStyle='#0e0c0a'; ctx.fillRect(0,0,W,H);
    bgCover(ctx, await loadImg(getBg('card4-photo-bg')),0,0,W,PH);
    applyGrad(ctx,0,0,W,PH,[[0,'rgba(0,0,0,0.1)'],[1,'rgba(0,0,0,0.65)']]);
    const bPT=W*0.05, bPB=W*0.06; const bodyTop=PH+bPT, bodyBottom=PH+BH-bPB;
    const ctaFSz=26; const ctaH=Math.min(ctaFSz+W*0.08, BH*0.15); const ctaTopY=bodyBottom-ctaH;
    ctx.fillStyle=A; rr(ctx,PX,ctaTopY,W-PX*2,ctaH,10); ctx.fill(); ctx.font=F('700',ctaFSz); ctx.fillStyle='#1a0f00';
    const ctaStr=t('d-c4-cta'); ctx.fillText(ctaStr,(W-ctx.measureText(ctaStr).width)/2,ctaTopY+ctaH/2+ctaFSz*0.36);
    const accFSz=26, hostFSz=19; const accBaseline=ctaTopY-W*0.04;
    ctx.font=F('700',accFSz); ctx.fillStyle='rgba(255,255,255,0.8)'; ctx.fillText(t('d-c4-account'),PX,accBaseline);
    const hostStr=t('d-c4-host'); ctx.font=F('400',hostFSz); ctx.fillStyle='rgba(255,255,255,0.3)'; ctx.fillText(hostStr,W-PX-ctx.measureText(hostStr).width,accBaseline);
    const divY=accBaseline-accFSz-W*0.04; ctx.beginPath(); ctx.moveTo(PX,divY); ctx.lineTo(W-PX,divY); ctx.strokeStyle='rgba(255,255,255,0.1)'; ctx.lineWidth=1; ctx.stroke();
    ctx.font=F('700',19); ctx.fillStyle=A; ctx.fillText('신청 방법',PX,bodyTop+19);
    const howFSz=24; ctx.font=F('400',howFSz); ctx.fillStyle='rgba(255,255,255,0.65)';
    const howLines=v('c4-howtext').split(/\r?\n/).filter(l=>l.trim()); const howFirstY=bodyTop+19+W*0.03+howFSz;
    howLines.forEach((line,i)=>{ ctx.fillText(line,PX,howFirstY+i*howFSz*1.7); });
  }
  return cv;
}
async function downloadCurrent() {
  await document.fonts.ready;
  const label = CARD_LABELS[currentTab]; showToast(`카드 ${currentTab+1} 저장 중...`);
  try { const cv = await renderCard(currentTab); const link = document.createElement('a'); link.download = `mkcinelab_${label}.png`; link.href = cv.toDataURL('image/png'); link.click(); showToast(`카드 ${currentTab+1} 저장 완료! (1080×1350)`); }
  catch(e) { showToast('저장 실패 — 콘솔 확인'); console.error(e); }
}
const today = new Date().toLocaleDateString('en-CA');
document.getElementById('c1-date').value = today;
update();
updateDates();
</script>
</body>
</html>"""

st.title("🎨 MK 이미지 작업실")
st.markdown("---")

tab1, tab2 = st.tabs(["🎬 썸네일 메이커", "📰 카드뉴스 메이커"])

with tab1:
    components.html(THUMBNAIL_HTML, height=1600, scrolling=False)

with tab2:
    components.html(CARD_NEWS_HTML, height=3200, scrolling=False)
