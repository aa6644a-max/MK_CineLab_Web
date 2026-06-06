import streamlit as st

st.set_page_config(page_title="MK Studio", page_icon="✦", layout="wide")

if st.query_params.get("goto") == "posting":
    st.switch_page("pages/01_📝_포스팅.py")

from mk_theme import inject_css
inject_css()

# Full-width override for landing page
st.markdown("""<style>
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
</style>""", unsafe_allow_html=True)

LANDING = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
*{box-sizing:border-box;}
.mk{font-family:'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,sans-serif;color:#2C2010;background:#FAF7F0;}

/* ── NAV ── */
.mk-nav{
  position:sticky;top:0;z-index:999;
  background:rgba(250,247,240,0.96);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(150,120,60,0.18);
  padding:0 6%;height:66px;
  display:flex;align-items:center;justify-content:space-between;
}
.mk-logo{font-size:15px;font-weight:800;color:#C09030;letter-spacing:3px;text-transform:uppercase;text-decoration:none;}
.mk-nav-links{display:flex;gap:28px;align-items:center;}
.mk-nav-links a{color:rgba(44,32,16,0.6);text-decoration:none;font-size:14px;font-weight:500;transition:color .2s;}
.mk-nav-links a:hover{color:#C09030;}

/* ── BUTTONS ── */
.btn-fill{
  display:inline-block;background:#C09030;color:#fff !important;
  padding:10px 24px;border-radius:9px;font-size:13px;font-weight:700;
  text-decoration:none !important;letter-spacing:.4px;transition:background .2s;
  border:none;cursor:pointer;font-family:'Pretendard Variable','Pretendard',-apple-system,sans-serif;
}
.btn-fill:hover{background:#a87820;}
.btn-outline{
  display:inline-block;background:transparent;color:#C09030 !important;
  border:1.5px solid #C09030;padding:10px 24px;border-radius:9px;
  font-size:13px;font-weight:600;text-decoration:none !important;
  letter-spacing:.4px;transition:all .2s;
  font-family:'Pretendard Variable','Pretendard',-apple-system,sans-serif;
}
.btn-outline:hover{background:rgba(192,144,48,.08);}

/* ── HERO ── */
.mk-hero{
  min-height:88vh;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;
  padding:80px 6%;
  background:linear-gradient(165deg,#FAF7F0 55%,#F2EAD6 100%);
  position:relative;overflow:hidden;
}
.mk-hero::before{
  content:'';position:absolute;
  width:700px;height:700px;
  background:radial-gradient(circle,rgba(192,144,48,.07) 0%,transparent 70%);
  top:-150px;right:-150px;border-radius:50%;pointer-events:none;
}
.mk-hero::after{
  content:'';position:absolute;
  width:400px;height:400px;
  background:radial-gradient(circle,rgba(192,144,48,.05) 0%,transparent 70%);
  bottom:-80px;left:-80px;border-radius:50%;pointer-events:none;
}
.hero-badge{
  display:inline-block;
  background:rgba(192,144,48,.12);color:#C09030;
  border:1px solid rgba(192,144,48,.3);
  border-radius:100px;padding:5px 18px;
  font-size:11px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;margin-bottom:28px;
}
.mk-hero h1{
  font-size:clamp(2.4rem,5.5vw,4rem);font-weight:800;
  color:#2C2010;line-height:1.12;
  margin-bottom:20px;letter-spacing:-.5px;
}
.mk-hero h1 em{font-style:normal;color:#C09030;}
.mk-hero p{
  font-size:clamp(1rem,1.8vw,1.15rem);
  color:rgba(44,32,16,.62);max-width:500px;
  line-height:1.75;margin-bottom:40px;
}
.hero-btns{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:56px;}
.hero-btns a{font-size:14px;padding:13px 32px;}

/* stats row */
.hero-stats{
  display:flex;gap:56px;justify-content:center;flex-wrap:wrap;
  padding-top:36px;
  border-top:1px solid rgba(150,120,60,.15);
}
.stat{text-align:center;}
.stat-n{font-size:1.9rem;font-weight:800;color:#C09030;line-height:1;}
.stat-l{font-size:11px;color:rgba(44,32,16,.45);margin-top:5px;letter-spacing:.5px;}

/* ── DIVIDER ── */
.mk-hr{height:1px;background:rgba(150,120,60,.15);}

/* ── SECTIONS ── */
.mk-section{padding:96px 8%;max-width:1320px;margin:0 auto;}
.sec-badge{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#C09030;margin-bottom:12px;}
.sec-title{font-size:clamp(1.7rem,3vw,2.5rem);font-weight:800;color:#2C2010;letter-spacing:-.3px;margin-bottom:14px;}
.sec-sub{font-size:.95rem;color:rgba(44,32,16,.58);max-width:500px;line-height:1.75;margin-bottom:52px;}

/* ── FEATURES ── */
.feat-bg{background:#F2EAD6;}
.feat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px;}
.feat-card{
  background:#FAF7F0;border:1px solid rgba(150,120,60,.2);
  border-radius:16px;padding:32px 28px;
  transition:transform .25s,box-shadow .25s;
}
.feat-card:hover{transform:translateY(-5px);box-shadow:0 16px 48px rgba(150,120,60,.13);}
.feat-icon{font-size:2rem;margin-bottom:16px;display:block;}
.feat-title{font-size:1.05rem;font-weight:700;color:#2C2010;margin-bottom:10px;}
.feat-desc{font-size:.875rem;color:rgba(44,32,16,.58);line-height:1.7;}

/* ── HOW IT WORKS ── */
.steps{display:flex;gap:0;flex-wrap:wrap;position:relative;}
.step{flex:1;min-width:220px;text-align:center;padding:0 28px;position:relative;}
.step:not(:last-child)::after{
  content:'→';position:absolute;right:-10px;top:22px;
  font-size:1.5rem;color:rgba(192,144,48,.35);
}
.step-num{
  width:58px;height:58px;
  background:rgba(192,144,48,.1);border:2px solid rgba(192,144,48,.28);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:1.25rem;font-weight:800;color:#C09030;
  margin:0 auto 20px;
}
.step-title{font-size:1rem;font-weight:700;color:#2C2010;margin-bottom:8px;}
.step-desc{font-size:.875rem;color:rgba(44,32,16,.58);line-height:1.65;}

/* ── PRICING ── */
.price-bg{background:#F2EAD6;}
.price-wrap{display:flex;justify-content:center;gap:24px;flex-wrap:wrap;}
.price-card{
  background:#FAF7F0;border:2px solid rgba(192,144,48,.25);
  border-radius:20px;padding:52px 56px;
  max-width:440px;text-align:center;
}
.coming-badge{
  display:inline-block;background:#C09030;color:#fff;
  border-radius:100px;padding:6px 20px;
  font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
  margin-bottom:24px;
}
.price-title{font-size:1.4rem;font-weight:800;color:#2C2010;margin-bottom:12px;}
.price-desc{font-size:.92rem;color:rgba(44,32,16,.58);line-height:1.75;margin-bottom:28px;}

/* ── BOTTOM CTA ── */
.cta-section{
  text-align:center;padding:96px 8%;
  background:linear-gradient(165deg,#FAF7F0 0%,#F2EAD6 100%);
}
.cta-section h2{font-size:clamp(1.7rem,3.5vw,2.6rem);font-weight:800;color:#2C2010;margin-bottom:14px;letter-spacing:-.3px;}
.cta-section p{font-size:1rem;color:rgba(44,32,16,.58);margin-bottom:36px;line-height:1.7;}

/* ── FOOTER ── */
.mk-footer{
  background:#F2EAD6;padding:28px 8%;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;
  border-top:1px solid rgba(150,120,60,.15);
}
.footer-logo{font-size:13px;font-weight:800;color:#C09030;letter-spacing:2px;text-transform:uppercase;}
.footer-copy{font-size:12px;color:rgba(44,32,16,.38);}
</style>

<div class="mk">

<!-- NAV -->
<nav class="mk-nav">
  <a class="mk-logo" href="/">✦ MK STUDIO</a>
  <div class="mk-nav-links">
    <a href="#features">기능</a>
    <a href="#how">작동방식</a>
    <a href="#pricing">가격</a>
    <a href="?goto=posting" class="btn-fill" style="padding:9px 20px;">포스팅 시작 →</a>
  </div>
</nav>

<!-- HERO -->
<section class="mk-hero" id="hero">
  <div class="hero-badge">AI Content Workspace</div>
  <h1>모든 콘텐츠 작업,<br><em>한 곳에서</em></h1>
  <p>AI가 글을 쓰고, 이미지를 만들고, 발행까지 합니다.<br>블로그 운영의 모든 과정을 MK Studio 하나로.</p>
  <div class="hero-btns">
    <a href="?goto=posting" class="btn-fill">무료로 시작하기 →</a>
    <a href="#features" class="btn-outline">기능 살펴보기</a>
  </div>
  <div class="hero-stats">
    <div class="stat"><div class="stat-n">10x</div><div class="stat-l">작업 속도 향상</div></div>
    <div class="stat"><div class="stat-n">3</div><div class="stat-l">핵심 도구</div></div>
    <div class="stat"><div class="stat-n">AI</div><div class="stat-l">자동화 엔진</div></div>
  </div>
</section>

<div class="mk-hr"></div>

<!-- FEATURES -->
<div class="feat-bg" id="features">
  <div class="mk-section">
    <div class="sec-badge">Features</div>
    <div class="sec-title">필요한 모든 기능이<br>여기 있습니다</div>
    <div class="sec-sub">복잡한 블로그 운영을 AI가 대신합니다. 검색부터 발행까지, 모든 단계를 자동화.</div>
    <div class="feat-grid">
      <div class="feat-card">
        <span class="feat-icon">✍️</span>
        <div class="feat-title">AI 포스팅 자동생성</div>
        <div class="feat-desc">영화·드라마 정보를 입력하면 네이버 최적화 블로그 글을 즉시 완성합니다. Claude AI 기반.</div>
      </div>
      <div class="feat-card">
        <span class="feat-icon">🎨</span>
        <div class="feat-title">이미지 카드 자동제작</div>
        <div class="feat-desc">썸네일, 인용구 카드, 카드뉴스 템플릿을 원클릭 생성. 블로그 포스팅 준비 완료.</div>
      </div>
      <div class="feat-card">
        <span class="feat-icon">🚀</span>
        <div class="feat-title">네이버 블로그 자동발행</div>
        <div class="feat-desc">완성된 글을 네이버 블로그에 직접 포스팅. 복사·붙여넣기 없이 원클릭으로 끝.</div>
      </div>
      <div class="feat-card">
        <span class="feat-icon">📡</span>
        <div class="feat-title">콘텐츠 자동큐레이션</div>
        <div class="feat-desc">TMDB·RSS 기반 최신 트렌딩 콘텐츠 자동 수집. 항상 새로운 소재가 준비됩니다.</div>
      </div>
    </div>
  </div>
</div>

<div class="mk-hr"></div>

<!-- HOW IT WORKS -->
<section id="how">
  <div class="mk-section">
    <div style="text-align:center;margin-bottom:56px;">
      <div class="sec-badge">How it works</div>
      <div class="sec-title">3단계로 끝나는<br>블로그 포스팅</div>
    </div>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-title">콘텐츠 선택</div>
        <div class="step-desc">영화·드라마·트렌딩 콘텐츠 중 원하는 소재를 선택하거나 직접 입력합니다.</div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-title">AI 자동생성</div>
        <div class="step-desc">Claude AI가 네이버 최적화 포스팅과 이미지 카드를 동시에 생성합니다.</div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-title">원클릭 발행</div>
        <div class="step-desc">검토 후 네이버 블로그에 바로 발행. 작업 시간 90% 단축됩니다.</div>
      </div>
    </div>
  </div>
</section>

<div class="mk-hr"></div>

<!-- PRICING -->
<div class="price-bg" id="pricing">
  <div class="mk-section" style="text-align:center;">
    <div class="sec-badge">Pricing</div>
    <div class="sec-title">합리적인 구독 플랜</div>
    <div class="sec-sub" style="margin:0 auto 48px;">현재 무료로 사용할 수 있습니다. 구독 플랜은 곧 공개됩니다.</div>
    <div class="price-wrap">
      <div class="price-card">
        <div class="coming-badge">Coming Soon</div>
        <div class="price-title">구독 플랜 준비 중</div>
        <div class="price-desc">더 많은 기능과 함께 프리미엄 플랜이 출시될 예정입니다.<br>지금은 무료로 모든 기능을 경험해보세요.</div>
        <a href="?goto=posting" class="btn-fill" style="font-size:14px;padding:12px 32px;">지금 무료로 시작하기</a>
      </div>
    </div>
  </div>
</div>

<div class="mk-hr"></div>

<!-- BOTTOM CTA -->
<div class="cta-section">
  <h2>지금 바로 시작하세요</h2>
  <p>설치 없이, 가입 없이.<br>지금 바로 AI 블로그 작업실을 경험하세요.</p>
  <a href="?goto=posting" class="btn-fill" style="font-size:15px;padding:14px 40px;">포스팅 시작하기 →</a>
</div>

<div class="mk-hr"></div>

<!-- FOOTER -->
<footer class="mk-footer">
  <div class="footer-logo">✦ MK STUDIO</div>
  <div class="footer-copy">© 2026 MK Studio. All rights reserved.</div>
</footer>

</div>
"""

st.markdown(LANDING, unsafe_allow_html=True)
