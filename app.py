import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Known Space Explorer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu, header, footer { visibility: hidden; }
    .stApp { background: #000; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    iframe { display: block; }
</style>
""", unsafe_allow_html=True)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Known Space Explorer</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }

  html, body {
    background:#000; font-family:'Exo 2',sans-serif; color:#fff;
    width:100%; height:100%; overflow:hidden; touch-action:manipulation;
  }

  #stars { position:fixed; inset:0; pointer-events:none; z-index:0; }
  .star {
    position:absolute; background:#fff; border-radius:50%;
    animation:twinkle var(--d,3s) infinite alternate;
  }
  @keyframes twinkle {
    from { opacity:.15; transform:scale(1); }
    to   { opacity:1;   transform:scale(1.5); }
  }

  .scene {
    position:fixed; inset:0;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    z-index:10; transition:opacity .7s ease;
  }
  .scene.hidden { opacity:0; pointer-events:none; }

  /* ── LAUNCH SCENE ── */
  #scene-launch {
    background:linear-gradient(to top, #060620 0%, #000 55%);
    justify-content:flex-start;
  }
  .launch-title {
    text-align:center; padding:0 20px;
    margin-top:9vh; flex-shrink:0;
  }
  .launch-title h1 {
    font-family:'Orbitron',monospace;
    font-size:clamp(1.6rem,7vw,3rem); font-weight:900; letter-spacing:.12em;
    background:linear-gradient(135deg,#fff,#88aaff,#fff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  }
  .launch-title p {
    margin-top:8px; font-size:clamp(.62rem,2.5vw,.8rem);
    color:#88aaff88; letter-spacing:.2em; text-transform:uppercase;
  }

  /* drag hint */
  .drag-hint {
    margin-top: 14px;
    font-size: clamp(.7rem, 3vw, .85rem);
    color: #88aaff99;
    letter-spacing: .1em;
    animation: hintPulse 2s ease-in-out infinite;
    user-select: none;
  }
  @keyframes hintPulse {
    0%,100% { opacity:.5; transform:translateY(0); }
    50%      { opacity:1;  transform:translateY(4px); }
  }

  /* rocket area fills remaining space */
  .rocket-area {
    flex:1; display:flex; flex-direction:column;
    align-items:center; justify-content:flex-end;
    position:relative; width:100%; overflow:hidden;
  }
  .ground {
    position:absolute; bottom:0; left:0; right:0;
    height:22vh; min-height:110px; max-height:200px;
    background:radial-gradient(ellipse 130% 60% at 50% 100%,#1a472a 0%,#0d2818 50%,#050f08 100%);
    border-top:1px solid #2d7a3a33;
  }
  .launchpad {
    position:absolute; bottom:22vh; left:50%; transform:translateX(-50%);
    width:min(90px,20vw); height:12px;
    background:#555; border-radius:3px 3px 0 0; border:1px solid #777;
  }

  /* ROCKET — draggable */
  #rocketWrap {
    position:absolute;
    bottom:calc(22vh + 12px);
    left:50%; transform:translateX(-50%);
    display:flex; flex-direction:column; align-items:center;
    cursor:grab; touch-action:none; user-select:none;
    z-index:20;
    transition: filter .2s;
  }
  #rocketWrap:active { cursor:grabbing; }
  #rocketWrap.launching {
    animation:liftoff 3s ease-in forwards;
    pointer-events:none;
  }
  @keyframes liftoff {
    0%   { transform:translateX(-50%) translateY(0)      scale(1); filter:none; }
    15%  { transform:translateX(-50%) translateY(-20px)  scale(1); }
    100% { transform:translateX(-50%) translateY(-130vh) scale(.18); opacity:0; }
  }

  /* pull-down elastic visual */
  #rocketWrap.pulling {
    transition: none;
  }

  /* charge bar */
  .charge-wrap {
    position:absolute; bottom:calc(22vh + 90px); left:50%; transform:translateX(-50%);
    width:min(160px,40vw); height:6px;
    background:#ffffff11; border-radius:3px; overflow:hidden;
    opacity:0; transition:opacity .2s;
  }
  .charge-wrap.visible { opacity:1; }
  #chargeFill {
    height:100%; width:0%; border-radius:3px;
    background:linear-gradient(90deg,#3b82f6,#88aaff);
    transition:width .05s linear, background .2s;
  }
  #chargeFill.ready { background:linear-gradient(90deg,#22cc66,#88ffbb); }

  /* flame shown while pulling */
  .rocket-flame-idle {
    width:10px; height:0;
    border-left:5px solid transparent; border-right:5px solid transparent;
    border-top:0px solid #ff6600;
    transition: border-top-width .1s;
  }

  #rocketWrap.launching .rocket-flame-idle {
    animation:burnFlame 3s ease-in forwards;
  }
  @keyframes burnFlame {
    0%   { border-top-width:28px; border-top-color:#ff6600; opacity:1; }
    50%  { border-top-width:50px; border-top-color:#ffaa00; opacity:1; }
    100% { border-top-width:6px;  border-top-color:#ffdd00; opacity:.1; }
  }

  .rocket-nose {
    width:0; height:0;
    border-left:13px solid transparent; border-right:13px solid transparent;
    border-bottom:50px solid #d0d0d0;
    filter:drop-shadow(0 0 6px #88aaff55);
    pointer-events:none;
  }
  .rocket-body {
    width:26px; height:36px;
    background:linear-gradient(180deg,#ddd,#aaa); border-radius:2px; position:relative;
    pointer-events:none;
  }
  .rocket-body::before, .rocket-body::after {
    content:''; position:absolute; top:8px;
    width:11px; height:16px; background:#888; border-radius:0 0 5px 5px;
  }
  .rocket-body::before { left:-10px; }
  .rocket-body::after  { right:-10px; }

  .smoke-ring {
    position:absolute; bottom:calc(22vh + 12px); left:50%; transform:translateX(-50%);
    width:0; height:0; opacity:0; border-radius:50%; pointer-events:none;
  }
  .smoke-ring.active { animation:smokeOut 2.6s ease-out forwards; }
  @keyframes smokeOut {
    0%   { width:8px;   height:8px;   opacity:.7; background:#888; }
    100% { width:200px; height:200px; opacity:0;  background:#333; }
  }

  /* ── SHARED BUTTONS ── */
  .btn-primary {
    background:linear-gradient(135deg,#1e3a8a,#3b82f6); border:none; color:#fff;
    font-family:'Orbitron',monospace; font-size:clamp(.85rem,4vw,1rem);
    font-weight:700; letter-spacing:.12em; padding:16px 32px;
    cursor:pointer; border-radius:8px; min-height:52px;
    text-transform:uppercase; -webkit-appearance:none; transition:opacity .2s;
  }
  .btn-primary:active { opacity:.75; }
  .btn-ghost {
    background:transparent; border:1px solid #88aaff55; color:#88aaff99;
    font-family:'Exo 2',sans-serif; font-size:clamp(.85rem,4vw,.95rem);
    padding:14px 24px; cursor:pointer; border-radius:8px; min-height:52px;
    -webkit-appearance:none; transition:all .2s;
  }
  .btn-ghost:active { border-color:#88aaff; color:#88aaff; }
  .btn-row { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }

  /* ── SPACE SCENE ── */
  #scene-space { background:radial-gradient(ellipse at 78% 82%,#001833 0%,#000 55%); }
  .earth-globe {
    position:absolute; bottom:-14vw; right:-14vw;
    width:min(72vw,320px); height:min(72vw,320px); border-radius:50%;
    background:radial-gradient(circle at 35% 35%,#1e90ff,#006994,#003d5b,#001a2e);
    box-shadow:0 0 50px #1e90ff33,inset -18px -18px 45px #00000077;
  }
  .shuttle-float {
    position:absolute; top:26%; left:12%;
    font-size:clamp(2rem,8vw,3rem);
    animation:floatShuttle 5s ease-in-out infinite;
    filter:drop-shadow(0 0 10px #88aaff66);
  }
  @keyframes floatShuttle {
    0%,100% { transform:translateY(0) rotate(-10deg); }
    50%      { transform:translateY(-14px) rotate(-10deg); }
  }
  .prompt-card {
    background:#ffffff08; border:1px solid #88aaff33;
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    border-radius:18px; padding:clamp(22px,5vw,38px) clamp(18px,5vw,40px);
    text-align:center; max-width:min(88vw,440px);
    animation:fadeSlideUp .7s ease forwards;
  }
  @keyframes fadeSlideUp {
    from { opacity:0; transform:translateY(24px); }
    to   { opacity:1; transform:translateY(0); }
  }
  .prompt-card h2 { font-family:'Orbitron',monospace; font-size:clamp(1rem,4.5vw,1.35rem); margin-bottom:10px; }
  .prompt-card p  { color:#aabfe0; font-size:clamp(.8rem,3.3vw,.93rem); line-height:1.65; margin-bottom:22px; }

  /* ── SOLAR SYSTEM ── */
  #scene-solar {
    background:radial-gradient(ellipse at 50% 50%,#080318 0%,#000 65%);
    overflow:hidden; justify-content:center;
  }
  .solar-header {
    position:absolute; top:14px;
    font-family:'Orbitron',monospace; font-size:clamp(.6rem,2.5vw,.85rem);
    letter-spacing:.28em; color:#88aaff55; text-transform:uppercase;
  }
  #solarSystem { position:relative; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
  .sun {
    position:absolute; border-radius:50%;
    background:radial-gradient(circle,#fff7aa,#ffcc00,#ff8800,#ff4400);
    box-shadow:0 0 20px #ffcc0077,0 0 50px #ff880033; z-index:5;
    animation:pulse 3s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { box-shadow:0 0 20px #ffcc0077,0 0 50px #ff880033; }
    50%      { box-shadow:0 0 36px #ffcc00aa,0 0 80px #ff880055; }
  }
  .orbit { position:absolute; border-radius:50%; border:1px solid #ffffff09; pointer-events:none; }
  .planet-wrap { position:absolute; top:50%; left:50%; transform-origin:0 0; }
  .planet { border-radius:50%; cursor:pointer; position:relative; transition:transform .15s; }
  .planet:active { transform:scale(1.5); }
  .planet-label {
    position:absolute; top:calc(100% + 3px); left:50%; transform:translateX(-50%);
    font-size:clamp(6px,1.5vw,8px); color:#ffffff55; white-space:nowrap; pointer-events:none;
  }
  .saturn-ring {
    position:absolute; width:155%; height:28%; border-radius:50%;
    border:2px solid #c8a96477; top:36%; left:-27.5%;
    transform:rotateX(68deg); pointer-events:none;
  }
  .float-prompt {
    position:absolute; bottom:16px; left:50%; transform:translateX(-50%);
    background:#000000cc; border:1px solid #88aaff33;
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    border-radius:14px; padding:16px 20px; text-align:center;
    width:min(92vw,370px); animation:fadeSlideUp .8s ease 1s both;
  }
  .float-prompt p { color:#aabfe0; font-size:clamp(.76rem,3vw,.86rem); margin-bottom:14px; line-height:1.5; }

  /* ── PLANET INFO ── */
  .info-overlay {
    position:fixed; inset:0; background:#00000077;
    backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
    z-index:100; display:flex; align-items:flex-end; justify-content:center;
    animation:fadeIn .25s ease;
  }
  .info-overlay.hidden { display:none; }
  @keyframes fadeIn { from{opacity:0;} to{opacity:1;} }
  .info-card {
    background:linear-gradient(160deg,#0b1030,#050818); border:1px solid #88aaff33;
    border-radius:22px 22px 0 0; padding:26px 20px 40px;
    width:100%; max-width:540px;
    animation:slideUp .36s cubic-bezier(.16,1,.3,1) forwards; max-height:78vh; overflow-y:auto;
  }
  @keyframes slideUp { from{transform:translateY(100%);} to{transform:translateY(0);} }
  .info-card-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
  #infoName { font-family:'Orbitron',monospace; font-size:clamp(1.2rem,5.5vw,1.8rem); font-weight:700; }
  .info-close {
    background:#ffffff11; border:1px solid #ffffff22; color:#fff;
    width:40px; height:40px; border-radius:50%; cursor:pointer; font-size:1rem;
    display:flex; align-items:center; justify-content:center; flex-shrink:0; -webkit-appearance:none;
  }
  .info-close:active { background:#ffffff33; }
  .info-stats { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px; }
  .info-stat { background:#ffffff07; border-radius:10px; padding:12px 13px; }
  .info-stat-label { font-size:clamp(.58rem,2.3vw,.68rem); color:#88aaff88; text-transform:uppercase; letter-spacing:.08em; margin-bottom:4px; }
  .info-stat-value { font-size:clamp(.8rem,3.3vw,.93rem); font-weight:600; color:#dde8ff; }
  .info-fact {
    background:#88aaff09; border-left:3px solid #88aaff44;
    border-radius:0 8px 8px 0; padding:12px 14px;
    font-size:clamp(.78rem,3vw,.87rem); color:#aabfe0; line-height:1.65;
  }

  /* ── UNIVERSE ── */
  #scene-universe { background:#000; }
  .universe-wrap { display:flex; flex-direction:column; align-items:center; gap:24px; padding:16px 20px; }
  .universe-sphere {
    width:min(76vw,76vh,360px); height:min(76vw,76vh,360px); border-radius:50%;
    background:radial-gradient(circle at 40% 40%,#ffffff07 0%,#4444ff11 22%,#220044 42%,#110022 62%,#050010 82%,#000 100%);
    box-shadow:0 0 70px #4444ff22,0 0 140px #22004488,inset 0 0 70px #00000077;
    position:relative; overflow:hidden; flex-shrink:0;
    animation:universePulse 8s ease-in-out infinite;
  }
  @keyframes universePulse {
    0%,100% { box-shadow:0 0 70px #4444ff22,0 0 140px #22004488; }
    50%      { box-shadow:0 0 110px #6666ff44,0 0 220px #330055bb; }
  }
  .galaxy-cluster {
    position:absolute; border-radius:50%;
    background:radial-gradient(circle,#ffffff44,transparent);
    animation:clusterFloat var(--d) ease-in-out infinite alternate;
  }
  @keyframes clusterFloat {
    from { transform:translate(0,0) scale(1); opacity:.35; }
    to   { transform:translate(var(--tx),var(--ty)) scale(1.2); opacity:.75; }
  }
  .earth-dot {
    position:absolute; bottom:22%; right:26%;
    width:5px; height:5px; background:#4af; border-radius:50%;
    box-shadow:0 0 8px #4af; animation:dotPulse 2s ease-in-out infinite;
  }
  @keyframes dotPulse { 0%,100%{transform:scale(1);opacity:1;} 50%{transform:scale(2.2);opacity:.55;} }
  .you-are-here {
    position:absolute; bottom:calc(22% + 9px); right:calc(26% - 26px);
    font-size:clamp(6px,1.8vw,9px); color:#4af; white-space:nowrap; letter-spacing:.08em;
  }
  .universe-text { text-align:center; max-width:min(90vw,460px); animation:fadeSlideUp .9s ease .4s both; padding:0 8px; }
  .universe-text h2 { font-family:'Orbitron',monospace; font-size:clamp(.9rem,3.8vw,1.2rem); margin-bottom:10px; letter-spacing:.06em; }
  .universe-text p { color:#8899bb; font-size:clamp(.76rem,3vw,.88rem); line-height:1.75; }

  #zoomOverlay { position:fixed; inset:0; background:#000; z-index:200; opacity:0; pointer-events:none; transition:opacity .5s ease; }
  #zoomOverlay.active { opacity:1; pointer-events:all; }
</style>
</head>
<body>

<div id="stars"></div>
<div id="zoomOverlay"></div>

<!-- SCENE 1: LAUNCH -->
<div class="scene hidden" id="scene-launch">
  <div class="launch-title">
    <h1>KNOWN SPACE</h1>
    <p>A journey through the observable universe</p>
    <div class="drag-hint">↓ &nbsp;pull the rocket down to launch&nbsp; ↓</div>
  </div>

  <div class="rocket-area">
    <!-- charge bar -->
    <div class="charge-wrap" id="chargeWrap">
      <div id="chargeFill"></div>
    </div>

    <div class="ground"></div>
    <div class="launchpad"></div>

    <div id="rocketWrap">
      <div class="rocket-nose"></div>
      <div class="rocket-body"></div>
      <div class="rocket-flame-idle" id="idleFlame"></div>
    </div>

    <div class="smoke-ring" id="smoke"></div>
  </div>
</div>

<!-- SCENE 2: SPACE -->
<div class="scene" id="scene-space">
  <div class="earth-globe"></div>
  <div class="shuttle-float">🚀</div>
  <div class="prompt-card">
    <h2>You've entered space.</h2>
    <p>Earth drifts behind you. The silence of the cosmos stretches in every direction. Ready to explore our Solar System?</p>
    <div class="btn-row">
      <button class="btn-primary" id="btnGoSolar">Explore Solar System →</button>
    </div>
  </div>
</div>

<!-- SCENE 3: SOLAR SYSTEM -->
<div class="scene hidden" id="scene-solar">
  <div class="solar-header">Our Solar System</div>
  <div id="solarSystem"></div>
  <div class="float-prompt" id="floatPrompt">
    <p>Ready to see the full Observable Universe?</p>
    <div class="btn-row">
      <button class="btn-primary" id="btnGoUniverse">Zoom out →</button>
      <button class="btn-ghost" id="btnStay">Stay here</button>
    </div>
  </div>
</div>

<!-- SCENE 4: UNIVERSE -->
<div class="scene hidden" id="scene-universe">
  <div class="universe-wrap">
    <div class="universe-sphere" id="universeSphere"></div>
    <div class="universe-text">
      <h2>The Observable Universe</h2>
      <p>93 billion light-years across &middot; 2 trillion galaxies &middot; 13.8 billion years old.<br><br>Every star you've ever seen sits inside the Milky Way — one of those 2 trillion galaxies.</p>
    </div>
  </div>
</div>

<!-- PLANET INFO -->
<div class="info-overlay hidden" id="infoOverlay">
  <div class="info-card">
    <div class="info-card-header">
      <div id="infoName"></div>
      <button class="info-close" id="infoClose">✕</button>
    </div>
    <div class="info-stats">
      <div class="info-stat"><div class="info-stat-label">Distance from Sun</div><div class="info-stat-value" id="infoDistance"></div></div>
      <div class="info-stat"><div class="info-stat-label">Size vs Earth</div><div class="info-stat-value" id="infoSize"></div></div>
      <div class="info-stat"><div class="info-stat-label">Temperature</div><div class="info-stat-value" id="infoTemp"></div></div>
      <div class="info-stat"><div class="info-stat-label">Moons</div><div class="info-stat-value" id="infoMoons"></div></div>
    </div>
    <div class="info-fact" id="infoFact"></div>
  </div>
</div>

<script>
/* ── STARS ── */
const starsEl = document.getElementById('stars');
for (let i=0;i<180;i++){
  const s=document.createElement('div'); s.className='star';
  const sz=Math.random()*2+0.4;
  s.style.cssText=`width:${sz}px;height:${sz}px;top:${Math.random()*100}%;left:${Math.random()*100}%;--d:${(Math.random()*4+2).toFixed(1)}s;animation-delay:${(Math.random()*5).toFixed(1)}s;opacity:${(Math.random()*.5+.1).toFixed(2)}`;
  starsEl.appendChild(s);
}

/* ── DRAG TO LAUNCH ── */
const rocketWrap  = document.getElementById('rocketWrap');
const chargeWrap  = document.getElementById('chargeWrap');
const chargeFill  = document.getElementById('chargeFill');
const idleFlame   = document.getElementById('idleFlame');
const smokeEl     = document.getElementById('smoke');

const PULL_THRESHOLD = 90;   // px pulled down = 100% charge
let dragging = false, launched = false;
let startY = 0, currentPull = 0;

function getY(e){ return e.touches ? e.touches[0].clientY : e.clientY; }

function onDragStart(e){
  if (launched) return;
  dragging = true; startY = getY(e);
  rocketWrap.classList.add('pulling');
  chargeWrap.classList.add('visible');
  e.preventDefault();
}

function onDragMove(e){
  if (!dragging || launched) return;
  e.preventDefault();
  const dy = getY(e) - startY;          // positive = pulled down
  currentPull = Math.max(0, dy);        // only downward counts

  // elastic: rocket moves down half the pull, capped at 60px
  const visual = Math.min(currentPull * 0.55, 60);
  rocketWrap.style.transform = `translateX(-50%) translateY(${visual}px)`;

  // charge bar
  const pct = Math.min(currentPull / PULL_THRESHOLD * 100, 100);
  chargeFill.style.width = pct + '%';

  // flame grows with charge
  const flameH = Math.round(pct * 0.32);
  idleFlame.style.borderTopWidth = flameH + 'px';
  idleFlame.style.borderTopColor = pct < 60 ? '#ff6600' : '#ffcc00';
  idleFlame.style.borderTopStyle = 'solid';

  if (pct >= 100) chargeFill.classList.add('ready');
  else            chargeFill.classList.remove('ready');
}

function onDragEnd(e){
  if (!dragging || launched) return;
  dragging = false;
  rocketWrap.classList.remove('pulling');

  if (currentPull >= PULL_THRESHOLD) {
    // LAUNCH!
    launched = true;
    chargeWrap.classList.remove('visible');
    rocketWrap.style.transform = '';
    rocketWrap.classList.add('launching');
    smokeEl.classList.add('active');
    setTimeout(()=> transition('scene-space', 340), 2500);
  } else {
    // snap back
    rocketWrap.style.transition = 'transform .4s cubic-bezier(.34,1.56,.64,1)';
    rocketWrap.style.transform  = 'translateX(-50%) translateY(0)';
    setTimeout(()=>{ rocketWrap.style.transition=''; }, 420);
    chargeFill.style.width = '0%';
    chargeFill.classList.remove('ready');
    idleFlame.style.borderTopWidth = '0px';
    chargeWrap.classList.remove('visible');
    currentPull = 0;
  }
}

// mouse
rocketWrap.addEventListener('mousedown',  onDragStart);
window.addEventListener('mousemove',  onDragMove);
window.addEventListener('mouseup',    onDragEnd);

// touch
rocketWrap.addEventListener('touchstart', onDragStart, {passive:false});
window.addEventListener('touchmove',  onDragMove,  {passive:false});
window.addEventListener('touchend',   onDragEnd);

/* ── PLANET DATA ── */
const planets = [
  { name:'Mercury', color:'#b5b5b5', relSize:.38, orbitFrac:.16, speed:4.7,  distance:'57.9M km',  sizeRel:'0.38× Earth', temp:'-180 to 430°C', moons:'0',   fact:'Mercury has no atmosphere, so temperatures swing wildly — scorching by day and freezing by night.' },
  { name:'Venus',   color:'#e8c56a', relSize:.95, orbitFrac:.22, speed:3.5,  distance:'108.2M km', sizeRel:'0.95× Earth', temp:'465°C avg',      moons:'0',   fact:'Venus has the thickest atmosphere in the Solar System — crushing pressure 90x Earth\'s, with perpetual acid clouds.' },
  { name:'Earth',   color:'#3a7bd5', relSize:1,   orbitFrac:.28, speed:2.9,  distance:'149.6M km', sizeRel:'1x (home)',   temp:'15°C avg',       moons:'1',   fact:'The only known planet in the universe to harbour life — from deep-sea vents to the highest mountain peaks.' },
  { name:'Mars',    color:'#c1440e', relSize:.53, orbitFrac:.34, speed:2.4,  distance:'227.9M km', sizeRel:'0.53× Earth', temp:'-60°C avg',      moons:'2',   fact:'Olympus Mons on Mars is the tallest volcano in the Solar System — nearly 3x the height of Mount Everest.' },
  { name:'Jupiter', color:'#c88b3a', relSize:2.8, orbitFrac:.44, speed:1.3,  distance:'778.5M km', sizeRel:'11.2× Earth', temp:'-110°C clouds',  moons:'95',  fact:'Jupiter\'s Great Red Spot is a storm raging for 350+ years, wider than Earth itself.' },
  { name:'Saturn',  color:'#e4d191', relSize:2.4, orbitFrac:.56, speed:.97,  distance:'1.43B km',  sizeRel:'9.45× Earth', temp:'-140°C',         moons:'146', fact:'Saturn\'s rings span 282,000 km but are only a few hundred metres thick, made of billions of ice and rock fragments.', ring:true },
  { name:'Uranus',  color:'#7de8e8', relSize:1.9, orbitFrac:.68, speed:.68,  distance:'2.87B km',  sizeRel:'4× Earth',    temp:'-195°C',         moons:'27',  fact:'Uranus rotates on its side with a 98 degree tilt — its poles experience 42 years of continuous sunlight or darkness.' },
  { name:'Neptune', color:'#3f54ba', relSize:1.8, orbitFrac:.80, speed:.54,  distance:'4.5B km',   sizeRel:'3.88× Earth', temp:'-200°C',         moons:'16',  fact:'Neptune has the fastest winds in the Solar System — up to 2,100 km/h, faster than the speed of sound on Earth.' },
];

/* ── BUILD SOLAR SYSTEM ── */
function buildSolarSystem(){
  const solar=document.getElementById('solarSystem');
  solar.innerHTML='';
  document.querySelectorAll('style[data-orb]').forEach(el=>el.remove());
  const vw=window.innerWidth,vh=window.innerHeight;
  const size=Math.min(vw*.92,vh*.58,500);
  solar.style.width=size+'px'; solar.style.height=size+'px';
  const cx=size/2, sunSize=Math.max(16,size*.072);
  const sun=document.createElement('div'); sun.className='sun';
  sun.style.cssText=`width:${sunSize}px;height:${sunSize}px;top:${cx-sunSize/2}px;left:${cx-sunSize/2}px;`;
  solar.appendChild(sun);

  planets.forEach((p,i)=>{
    const orbitR=size*p.orbitFrac/2;
    const pxSize=Math.max(9,Math.round(sunSize*.4*p.relSize));
    const orb=document.createElement('div'); orb.className='orbit';
    orb.style.cssText=`width:${orbitR*2}px;height:${orbitR*2}px;top:${cx-orbitR}px;left:${cx-orbitR}px;`;
    solar.appendChild(orb);
    const sa=(i/planets.length)*360;
    const kf=document.createElement('style'); kf.setAttribute('data-orb','1');
    kf.textContent=`@keyframes orb${i}{from{transform:rotate(${sa}deg) translateX(${orbitR}px) rotate(-${sa}deg);}to{transform:rotate(${sa+360}deg) translateX(${orbitR}px) rotate(-${sa+360}deg);}}`;
    document.head.appendChild(kf);
    const wrap=document.createElement('div'); wrap.className='planet-wrap';
    wrap.style.cssText=`top:${cx}px;left:${cx}px;animation:orb${i} ${(11/p.speed).toFixed(1)}s linear infinite;`;
    const planet=document.createElement('div'); planet.className='planet';
    planet.style.cssText=`width:${pxSize}px;height:${pxSize}px;background:radial-gradient(circle at 35% 35%,${lighten(p.color)},${p.color},${darken(p.color)});box-shadow:0 0 ${pxSize*.5}px ${p.color}55;margin-left:-${pxSize/2}px;margin-top:-${pxSize/2}px;`;
    const hit=document.createElement('div');
    hit.style.cssText='position:absolute;inset:-14px;border-radius:50%;cursor:pointer;z-index:2;';
    planet.appendChild(hit);
    const lbl=document.createElement('div'); lbl.className='planet-label'; lbl.textContent=p.name;
    planet.appendChild(lbl);
    if(p.ring){const r=document.createElement('div');r.className='saturn-ring';planet.appendChild(r);}
    wrap.appendChild(planet); solar.appendChild(wrap);
    const openInfo=e=>{e.preventDefault();e.stopPropagation();showInfo(p,wrap);};
    hit.addEventListener('click',openInfo);
    hit.addEventListener('touchend',openInfo,{passive:false});
  });
}

function lighten(hex){return '#'+hex.slice(1).replace(/../g,m=>Math.min(255,parseInt(m,16)+45).toString(16).padStart(2,'0'));}
function darken(hex) {return '#'+hex.slice(1).replace(/../g,m=>Math.max(0,  parseInt(m,16)-40).toString(16).padStart(2,'0'));}

/* ── UNIVERSE ── */
function buildUniverse(){
  const sphere=document.getElementById('universeSphere');
  for(let i=0;i<55;i++){
    const cl=document.createElement('div'); cl.className='galaxy-cluster';
    const s=Math.random()*26+4;
    cl.style.cssText=`width:${s}px;height:${s}px;top:${Math.random()*83+5}%;left:${Math.random()*83+5}%;--d:${(Math.random()*6+4).toFixed(1)}s;--tx:${(Math.random()*16-8).toFixed(0)}px;--ty:${(Math.random()*16-8).toFixed(0)}px;animation-delay:${(Math.random()*6).toFixed(1)}s;`;
    sphere.appendChild(cl);
  }
  const dot=document.createElement('div'); dot.className='earth-dot';
  const yah=document.createElement('div'); yah.className='you-are-here'; yah.textContent='← you are here';
  sphere.appendChild(dot); sphere.appendChild(yah);
}
buildUniverse();

/* ── SCENE TRANSITIONS ── */
const overlay=document.getElementById('zoomOverlay');
function showScene(id){
  document.querySelectorAll('.scene').forEach(s=>s.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}
function transition(toScene,delay=560){
  overlay.classList.add('active');
  setTimeout(()=>{
    showScene(toScene);
    if(toScene==='scene-solar') buildSolarSystem();
    overlay.classList.remove('active');
  }, delay);
}

document.getElementById('btnGoSolar').addEventListener('click',()=>transition('scene-solar'));
document.getElementById('btnGoUniverse').addEventListener('click',()=>transition('scene-universe',760));
document.getElementById('btnStay').addEventListener('click',()=>{document.getElementById('floatPrompt').style.display='none';});
window.addEventListener('resize',()=>{if(!document.getElementById('scene-solar').classList.contains('hidden'))buildSolarSystem();});

/* ── PLANET INFO ── */
let activeWrap=null;
function showInfo(p,wrap){
  if(activeWrap) activeWrap.style.animationPlayState='running';
  activeWrap=wrap; wrap.style.animationPlayState='paused';
  document.getElementById('infoName').textContent=p.name;
  document.getElementById('infoName').style.color=p.color;
  document.getElementById('infoDistance').textContent=p.distance;
  document.getElementById('infoSize').textContent=p.sizeRel;
  document.getElementById('infoTemp').textContent=p.temp;
  document.getElementById('infoMoons').textContent=p.moons;
  document.getElementById('infoFact').textContent=p.fact;
  document.getElementById('infoOverlay').classList.remove('hidden');
}
const closeInfo=()=>{
  document.getElementById('infoOverlay').classList.add('hidden');
  if(activeWrap){activeWrap.style.animationPlayState='running';activeWrap=null;}
};
document.getElementById('infoClose').addEventListener('click',closeInfo);
document.getElementById('infoOverlay').addEventListener('click',e=>{if(e.target===document.getElementById('infoOverlay'))closeInfo();});
</script>
</body>
</html>"""

components.html(html_content, height=820, scrolling=False)
