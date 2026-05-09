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

  .overlay-ui { position:absolute; inset:0; pointer-events:none; }
  .text-block { position:absolute; top:13%; left:5%; right:5%; overflow:hidden; }
  #prev-title {
    font-weight:900; color:#fff;
    line-height:1.18;
    text-shadow:0 2px 16px rgba(0,0,0,0.8);
    white-space:nowrap; overflow:hidden;
  }
  #prev-sub {
    font-size:clamp(11px,3.2vw,18px);
    font-weight:500; color:rgba(255,255,255,0.85);
    margin-top:8px;
    text-shadow:0 1px 8px rgba(0,0,0,0.9);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }
  .nf-btns {
    position:absolute; left:5%;
    display:flex; gap:8px; align-items:center;
  }
  .nf-btn {
    padding:4px 10px; border-radius:4px;
    font-size:clamp(7px,1.8vw,10px); font-weight:700;
    display:flex; align-items:center; gap:3px;
    font-family:'Noto Sans KR',sans-serif;
  }
  .nf-btn.play { background:#fff; color:#111; }
  .nf-btn.info { background:rgba(80,80,80,0.75); color:#fff; }

  .pb-wrap { position:absolute; bottom:38px; left:14px; right:14px; }
  .pb-track { height:3px; background:rgba(255,255,255,0.28); border-radius:2px; position:relative; }
  .pb-fill { height:100%; background:#e50914; border-radius:2px; position:relative; }
  .pb-dot { width:11px; height:11px; background:#e50914; border-radius:50%; position:absolute; right:-5.5px; top:-4px; }

  .ctrl-bar { position:absolute; bottom:10px; left:14px; right:14px; display:flex; align-items:center; justify-content:space-between; }
  .ctrl-side { display:flex; gap:10px; align-items:center; }
  .ctrl-icon svg { display:block; }

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
  #export-canvas { display:none; }
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

    <div class="overlay-ui">
      <div class="text-block">
        <div id="prev-title">제목을 입력하세요</div>
        <div id="prev-sub">부제목을 입력하세요</div>
      </div>
      <div class="nf-btns" id="nf-btns">
        <div class="nf-btn play">▶ 감상 하기</div>
        <div class="nf-btn info">ⓘ More Info</div>
      </div>
      <div class="pb-wrap">
        <div class="pb-track">
          <div class="pb-fill" id="pb-fill" style="width:20%"><div class="pb-dot"></div></div>
        </div>
      </div>
      <div class="ctrl-bar">
        <div class="ctrl-side">
          <span class="ctrl-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="white"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg></span>
          <span class="ctrl-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.62"/></svg></span>
          <span class="ctrl-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.49-3.62"/></svg></span>
          <span class="ctrl-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg></span>
        </div>
        <div class="ctrl-side">
          <span class="ctrl-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19"/></svg></span>
          <span class="ctrl-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg></span>
          <span class="ctrl-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
          <span class="ctrl-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg></span>
        </div>
      </div>
    </div>
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

<canvas id="export-canvas"></canvas>

<script>
let loadedImage  = null;
let imgOffsetX   = 0.5;
let imgOffsetY   = 0.5;
let selectedSize = 1080;
let progressPct  = 20;

const box      = document.getElementById('preview-box');
const pCanvas  = document.getElementById('preview-canvas');
const pCtx     = pCanvas.getContext('2d');
const dragHint = document.getElementById('drag-hint');
const moveHint = document.getElementById('move-hint');
const pbFill   = document.getElementById('pb-fill');
const titleEl  = document.getElementById('prev-title');
const subEl    = document.getElementById('prev-sub');
const nfBtns   = document.getElementById('nf-btns');

function resizeCanvas() {
  pCanvas.width  = box.offsetWidth;
  pCanvas.height = box.offsetHeight;
  drawPreview();
  positionButtons();
  autoFitTitle();
}
window.addEventListener('load', resizeCanvas);
window.addEventListener('resize', resizeCanvas);

function drawPreview() {
  const W = pCanvas.width, H = pCanvas.height;
  pCtx.clearRect(0, 0, W, H);
  if (loadedImage) {
    const iw = loadedImage.naturalWidth, ih = loadedImage.naturalHeight;
    const scale = Math.max(W/iw, H/ih);
    const sw = iw*scale, sh = ih*scale;
    const sx = (W - sw) * imgOffsetX;
    const sy = (H - sh) * imgOffsetY;
    pCtx.globalAlpha = 0.75;
    pCtx.drawImage(loadedImage, sx, sy, sw, sh);
    pCtx.globalAlpha = 1;
  }
  const grad = pCtx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0,    'rgba(0,0,0,0.38)');
  grad.addColorStop(0.45, 'rgba(0,0,0,0.08)');
  grad.addColorStop(1,    'rgba(0,0,0,0.72)');
  pCtx.fillStyle = grad;
  pCtx.fillRect(0, 0, W, H);
}

function positionButtons() {
  const topPx = box.offsetHeight * 0.13;
  nfBtns.style.top = (topPx + titleEl.offsetHeight + subEl.offsetHeight + 14) + 'px';
}

function autoFitTitle() {
  const maxW = box.offsetWidth * 0.90;
  let fs = Math.round(box.offsetWidth * 0.088);
  const minFs = 16;
  titleEl.style.fontSize = fs + 'px';
  while (fs > minFs && titleEl.scrollWidth > maxW) {
    fs--;
    titleEl.style.fontSize = fs + 'px';
  }
}

document.getElementById('inp-title').addEventListener('input', e => {
  titleEl.textContent = e.target.value || '제목을 입력하세요';
  autoFitTitle();
  positionButtons();
});
document.getElementById('inp-sub').addEventListener('input', e => {
  subEl.textContent = e.target.value || '부제목을 입력하세요';
  positionButtons();
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

let isDragging = false, lastX = 0, lastY = 0;
function getXY(e) {
  return e.touches ? { x: e.touches[0].clientX, y: e.touches[0].clientY }
                   : { x: e.clientX,             y: e.clientY };
}
box.addEventListener('mousedown',  e => { if (!loadedImage) return; isDragging=true; const p=getXY(e); lastX=p.x; lastY=p.y; });
box.addEventListener('touchstart', e => { if (!loadedImage) return; isDragging=true; const p=getXY(e); lastX=p.x; lastY=p.y; }, { passive:true });
window.addEventListener('mousemove', e => {
  if (!isDragging || !loadedImage) return;
  const p = getXY(e);
  const dx = p.x - lastX, dy = p.y - lastY;
  lastX = p.x; lastY = p.y;
  const W = pCanvas.width, H = pCanvas.height;
  const scale = Math.max(W/loadedImage.naturalWidth, H/loadedImage.naturalHeight);
  const sw = loadedImage.naturalWidth*scale, sh = loadedImage.naturalHeight*scale;
  const rx = sw - W, ry = sh - H;
  if (rx > 0) imgOffsetX = Math.min(1, Math.max(0, imgOffsetX - dx/rx));
  if (ry > 0) imgOffsetY = Math.min(1, Math.max(0, imgOffsetY - dy/ry));
  drawPreview();
});
window.addEventListener('touchmove', e => {
  if (!isDragging || !loadedImage) return;
  if (e.cancelable) e.preventDefault();
  const p = getXY(e);
  const dx = p.x - lastX, dy = p.y - lastY;
  lastX = p.x; lastY = p.y;
  const W = pCanvas.width, H = pCanvas.height;
  const scale = Math.max(W/loadedImage.naturalWidth, H/loadedImage.naturalHeight);
  const sw = loadedImage.naturalWidth*scale, sh = loadedImage.naturalHeight*scale;
  const rx = sw - W, ry = sh - H;
  if (rx > 0) imgOffsetX = Math.min(1, Math.max(0, imgOffsetX - dx/rx));
  if (ry > 0) imgOffsetY = Math.min(1, Math.max(0, imgOffsetY - dy/ry));
  drawPreview();
}, { passive:false });
window.addEventListener('mouseup',  () => isDragging = false);
window.addEventListener('touchend', () => isDragging = false);

document.getElementById('progress-slider').addEventListener('input', e => {
  progressPct = parseInt(e.target.value);
  document.getElementById('progress-val').textContent = progressPct + '%';
  pbFill.style.width = progressPct + '%';
});

document.querySelectorAll('.size-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedSize = parseInt(btn.dataset.size);
  });
});

document.getElementById('dl-btn').addEventListener('click', () => {
  const title = document.getElementById('inp-title').value || '제목을 입력하세요';
  const sub   = document.getElementById('inp-sub').value   || '부제목을 입력하세요';
  const size  = selectedSize;
  const canvas = document.getElementById('export-canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, size, size);

  if (loadedImage) {
    const iw = loadedImage.naturalWidth, ih = loadedImage.naturalHeight;
    const scale = Math.max(size/iw, size/ih);
    const sw = iw*scale, sh = ih*scale;
    const sx = (size - sw) * imgOffsetX;
    const sy = (size - sh) * imgOffsetY;
    ctx.globalAlpha = 0.75;
    ctx.drawImage(loadedImage, sx, sy, sw, sh);
    ctx.globalAlpha = 1;
  } else {
    ctx.fillStyle = '#1a1a1a'; ctx.fillRect(0,0,size,size);
  }

  const grad = ctx.createLinearGradient(0,0,0,size);
  grad.addColorStop(0,    'rgba(0,0,0,0.38)');
  grad.addColorStop(0.45, 'rgba(0,0,0,0.08)');
  grad.addColorStop(1,    'rgba(0,0,0,0.72)');
  ctx.fillStyle = grad; ctx.fillRect(0,0,size,size);

  const leftX = size*0.05, maxW = size*0.90;
  let curY = size*0.13;

  let titleFs = Math.round(size*0.078);
  const minTitleFs = Math.round(size*0.030);
  ctx.font = `900 ${titleFs}px "Noto Sans KR",sans-serif`;
  ctx.fillStyle = '#fff';
  ctx.shadowColor = 'rgba(0,0,0,0.75)'; ctx.shadowBlur = 18;
  while (titleFs > minTitleFs && ctx.measureText(title).width > maxW) {
    titleFs -= 2;
    ctx.font = `900 ${titleFs}px "Noto Sans KR",sans-serif`;
  }
  ctx.fillText(title, leftX, curY + titleFs);
  curY += titleFs + size*0.018;

  let subFs = Math.round(size*0.034);
  ctx.font = `500 ${subFs}px "Noto Sans KR",sans-serif`;
  ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.shadowBlur = 10;
  while (subFs > 14 && ctx.measureText(sub).width > maxW) {
    subFs--;
    ctx.font = `500 ${subFs}px "Noto Sans KR",sans-serif`;
  }
  ctx.fillText(sub, leftX, curY + subFs);
  curY += subFs + size*0.028;

  ctx.shadowBlur = 0;
  const btnH=size*0.038, btnR=size*0.01, btnFs=Math.round(size*0.018);
  ctx.font = `700 ${btnFs}px "Noto Sans KR",sans-serif`;
  const playLabel='▶  감상 하기';
  const playW = ctx.measureText(playLabel).width + size*0.038;
  ctx.fillStyle='#fff'; roundRect(ctx,leftX,curY,playW,btnH,btnR); ctx.fill();
  ctx.fillStyle='#111'; ctx.fillText(playLabel, leftX+size*0.018, curY+btnH*0.665);
  const infoLabel='ⓘ  More Info';
  const infoW = ctx.measureText(infoLabel).width + size*0.038;
  ctx.fillStyle='rgba(80,80,80,0.78)'; roundRect(ctx,leftX+playW+size*0.014,curY,infoW,btnH,btnR); ctx.fill();
  ctx.fillStyle='#fff'; ctx.fillText(infoLabel, leftX+playW+size*0.014+size*0.018, curY+btnH*0.665);

  const pbY=size*0.918, pbL=size*0.04, pbW=size*0.92;
  const fillW = pbW * (progressPct/100);
  ctx.fillStyle='rgba(255,255,255,0.28)'; ctx.fillRect(pbL,pbY,pbW,4);
  ctx.fillStyle='#e50914'; ctx.fillRect(pbL,pbY,fillW,4);
  ctx.beginPath(); ctx.arc(pbL+fillW, pbY+2, 7, 0, Math.PI*2); ctx.fill();

  const link = document.createElement('a');
  link.download = (title.slice(0,20).replace(/[^\\w가-힣]/g,'_')||'thumbnail')+'_'+size+'.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
});

function roundRect(ctx,x,y,w,h,r){
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.arcTo(x+w,y,x+w,y+r,r);
  ctx.lineTo(x+w,y+h-r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
  ctx.lineTo(x+r,y+h); ctx.arcTo(x,y+h,x,y+h-r,r);
  ctx.lineTo(x,y+r); ctx.arcTo(x,y,x+r,y,r); ctx.closePath();
}
</script>
</body>
</html>"""

components.html(THUMBNAIL_HTML, height=1750, scrolling=False)
