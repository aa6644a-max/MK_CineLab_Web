import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="블로그 썸네일 메이커", page_icon="🎨", layout="centered")

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

// ── 핵심 렌더러: 미리보기·저장 동일한 함수 사용 ─────────────────────
function renderThumb(ctx, S) {
  ctx.clearRect(0, 0, S, S);

  // 배경 이미지 (cover fit + drag offset)
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

  // 그라디언트 오버레이
  const grad = ctx.createLinearGradient(0, 0, 0, S);
  grad.addColorStop(0,    'rgba(0,0,0,0.38)');
  grad.addColorStop(0.45, 'rgba(0,0,0,0.08)');
  grad.addColorStop(1,    'rgba(0,0,0,0.72)');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, S, S);

  ctx.textBaseline = 'alphabetic';
  const leftX = S * 0.05, maxW = S * 0.90;
  let curY = S * 0.13;

  // 제목 — 자동 축소
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

  // 부제목 — 자동 축소
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

  // 버튼 (감상하기 / More Info)
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

  // 진행 바
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

  // 1. Pause
  at(lx, () => {
    ctx.fillRect(5.5, 4, 4.5, 16);
    ctx.fillRect(14, 4, 4.5, 16);
  });

  // 2. Skip back 10s (CW arc + arrowhead at end + "10")
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

  // 3. Skip forward 10s (CCW arc, mirror of skip-back)
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

  // 4. Volume (speaker polygon + two arc waves)
  at(lx + gap * 3, () => {
    ctx.beginPath();
    ctx.moveTo(11, 5); ctx.lineTo(6, 9); ctx.lineTo(2.5, 9);
    ctx.lineTo(2.5, 15); ctx.lineTo(6, 15); ctx.lineTo(11, 19);
    ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.arc(12.5, 12, 4,   -Math.PI * 0.5, Math.PI * 0.5, false); ctx.stroke();
    ctx.beginPath(); ctx.arc(12.5, 12, 7.5, -Math.PI * 0.5, Math.PI * 0.5, false); ctx.stroke();
  });

  // 5. Next episode (right-pointing triangle + vertical bar)
  at(rx - gap * 3, () => {
    ctx.beginPath();
    ctx.moveTo(4, 4); ctx.lineTo(17, 12); ctx.lineTo(4, 20);
    ctx.closePath(); ctx.fill();
    ctx.fillRect(18, 4, 2.5, 16);
  });

  // 6. Episode list (dots + horizontal lines)
  at(rx - gap * 2, () => {
    [6, 12, 18].forEach(y => {
      ctx.beginPath(); ctx.arc(3.5, y, 1.5, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(8, y); ctx.lineTo(22, y); ctx.stroke();
    });
  });

  // 7. Chat bubble
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

  // 8. Fullscreen (L-shapes at four corners)
  at(rx, () => {
    const d = 4.5, m = 2;
    ctx.beginPath(); ctx.moveTo(m + d, m); ctx.lineTo(m, m); ctx.lineTo(m, m + d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(24 - m - d, m); ctx.lineTo(24 - m, m); ctx.lineTo(24 - m, m + d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(m + d, 24 - m); ctx.lineTo(m, 24 - m); ctx.lineTo(m, 24 - m - d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(24 - m - d, 24 - m); ctx.lineTo(24 - m, 24 - m); ctx.lineTo(24 - m, 24 - m - d); ctx.stroke();
  });

  ctx.restore();
}

function drawPreview() {
  renderThumb(pCtx, pCanvas.width);
}

function resizeCanvas() {
  pCanvas.width  = box.offsetWidth;
  pCanvas.height = box.offsetHeight;
  drawPreview();
}

// 폰트 로드 완료 후 초기 렌더링
window.addEventListener('load', () => document.fonts.ready.then(resizeCanvas));
window.addEventListener('resize', resizeCanvas);

// ── 입력 이벤트 ──────────────────────────────────────────────────
document.getElementById('inp-title').addEventListener('input', e => {
  titleText = e.target.value || '제목을 입력하세요';
  drawPreview();
});
document.getElementById('inp-sub').addEventListener('input', e => {
  subText = e.target.value || '부제목을 입력하세요';
  drawPreview();
});

document.getElementById('file-input').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  document.getElementById('file-name').textContent = file.name;
  const img = new Image();
  img.onload = () => {
    loadedImage = img;
    imgOffsetX = 0.5; imgOffsetY = 0.5;
    dragHint.classList.add('hidden');
    moveHint.style.display = 'block';
    moveHint.style.opacity = '1';
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

// ── 다운로드 — renderThumb()로 고해상도 렌더링 ──────────────────────
document.getElementById('dl-btn').addEventListener('click', async () => {
  await document.fonts.ready;
  const S = selectedSize;
  const canvas = document.createElement('canvas');
  canvas.width = S; canvas.height = S;
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  renderThumb(ctx, S);
  const title = document.getElementById('inp-title').value || 'thumbnail';
  const link = document.createElement('a');
  link.download = (title.slice(0, 20).replace(/[^\\w가-힣]/g, '_') || 'thumbnail') + '_' + S + '.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
});

// ── 드래그로 이미지 위치 조정 ─────────────────────────────────────
let isDragging = false, lastX = 0, lastY = 0;
function getXY(e) {
  return e.touches ? { x: e.touches[0].clientX, y: e.touches[0].clientY }
                   : { x: e.clientX, y: e.clientY };
}
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

components.html(THUMBNAIL_HTML, height=1600, scrolling=False)
