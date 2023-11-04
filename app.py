import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Known Space Explorer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Strip ALL streamlit chrome so the iframe fills the whole viewport
st.markdown("""
<style>
  #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; }
  .stApp { background: #000 !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
  section[data-testid="stSidebar"] { display: none !important; }
  iframe { display: block !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Everything below is one self-contained HTML/CSS/JS app.
# Key engineering decisions:
#   1. No window-level event listeners for drag — use document-level with
#      pointer events (pointerdown/pointermove/pointerup) which work
#      identically on touch and mouse and don't get blocked by touch-action.
#   2. Rocket position managed purely in JS via CSS custom property --ry
#      so transform stays `translateX(-50%) translateY(var(--ry))` always.
#   3. iframe height = 100vh trick: set height to a large number (10000) and
#      let Streamlit clip, OR use scrolling=False + large height. We use
#      window.innerHeight detection inside JS to size things correctly.
#   4. All interactive elements use pointer-events model.
# ─────────────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Known Space Explorer</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:ital,wght@0,300;0,400;0,600&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════ */
*, *::before, *::after {
  margin: 0; padding: 0; box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}
html {
  height: 100%; background: #000;
}
body {
  height: 100%; width: 100%; overflow: hidden;
  background: #000; color: #fff;
  font-family: 'Exo 2', sans-serif;
  /* do NOT set touch-action on body — let children control it */
}

/* ═══════════════════════════════════════════════
   STARS (background layer)
═══════════════════════════════════════════════ */
#stars {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 0;
  overflow: hidden;
}
.star {
  position: absolute; background: #fff; border-radius: 50%;
  animation: twinkle var(--d, 3s) infinite alternate;
  animation-delay: var(--del, 0s);
}
@keyframes twinkle {
  from { opacity: .1; transform: scale(1); }
  to   { opacity: .9; transform: scale(1.6); }
}

/* ═══════════════════════════════════════════════
   SCENES
═══════════════════════════════════════════════ */
.scene {
  position: fixed; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: flex-start;
  z-index: 10;
  opacity: 1; pointer-events: auto;
  transition: opacity .6s ease;
  overflow: hidden;
}
.scene.hidden {
  opacity: 0; pointer-events: none;
}

/* ═══════════════════════════════════════════════
   SCENE 1 — LAUNCH
═══════════════════════════════════════════════ */
#scene-launch {
  background: linear-gradient(to top, #060625 0%, #000010 60%, #000 100%);
}

.launch-header {
  text-align: center;
  padding: 0 24px;
  margin-top: 8vh;
  flex-shrink: 0;
  user-select: none;
}
.launch-header h1 {
  font-family: 'Orbitron', monospace;
  font-size: clamp(1.7rem, 7vw, 3.2rem);
  font-weight: 900; letter-spacing: .1em;
  background: linear-gradient(135deg, #fff 0%, #88aaff 50%, #fff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.launch-header .sub {
  margin-top: 6px;
  font-size: clamp(.6rem, 2.5vw, .82rem);
  color: #88aaff77; letter-spacing: .22em; text-transform: uppercase;
}
.launch-header .hint {
  margin-top: 16px;
  font-size: clamp(.72rem, 3vw, .9rem);
  color: #88aaffbb; letter-spacing: .08em;
  animation: hintBob 1.8s ease-in-out infinite;
}
@keyframes hintBob {
  0%, 100% { transform: translateY(0);   opacity: .6; }
  50%       { transform: translateY(5px); opacity: 1;  }
}

/* The rocket stage: fills remaining vertical space */
.launch-stage {
  flex: 1;
  position: relative;
  width: 100%;
  overflow: hidden;
  /* needed so absolute children position relative to this */
}

/* Ground */
.ground {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 22vh; min-height: 100px; max-height: 220px;
  background: radial-gradient(ellipse 140% 60% at 50% 100%,
    #1a472a 0%, #0d2818 55%, #040d06 100%);
  border-top: 1px solid #2d7a3a22;
}

/* Launchpad */
.launchpad {
  position: absolute;
  bottom: 22vh; left: 50%;
  transform: translateX(-50%);
  width: clamp(70px, 18vw, 100px); height: 11px;
  background: linear-gradient(180deg, #777, #444);
  border-radius: 3px 3px 0 0;
  border: 1px solid #999;
  box-shadow: 0 0 12px #ffffff11;
}

/* Charge bar — sits above launchpad */
#chargeBar {
  position: absolute;
  bottom: calc(22vh + 130px);
  left: 50%; transform: translateX(-50%);
  width: clamp(130px, 35vw, 180px);
  height: 7px;
  background: #ffffff0f;
  border: 1px solid #ffffff1a;
  border-radius: 4px;
  overflow: hidden;
  opacity: 0;
  transition: opacity .25s;
  pointer-events: none;
}
#chargeBar.visible { opacity: 1; }
#chargeFill {
  height: 100%; width: 0%;
  border-radius: 4px;
  background: linear-gradient(90deg, #2255cc, #88aaff);
  transition: background .3s;
}
#chargeFill.ready {
  background: linear-gradient(90deg, #11aa55, #66ffaa);
  box-shadow: 0 0 8px #66ffaa88;
}
#chargeLabel {
  position: absolute;
  bottom: calc(22vh + 142px);
  left: 50%; transform: translateX(-50%);
  font-size: .65rem; color: #88aaff88;
  letter-spacing: .15em; text-transform: uppercase;
  pointer-events: none;
  opacity: 0; transition: opacity .25s;
}
#chargeLabel.visible { opacity: 1; }

/* ── ROCKET ── */
/* We use a wrapper that is positioned absolute, horizontally centred.
   The vertical offset is controlled ONLY by JS via --ry custom property
   so transform is always: translateX(-50%) translateY(var(--ry,0px))
   This prevents the "jump to left" bug. */
#rocket {
  position: absolute;
  bottom: calc(22vh + 11px);   /* sits on launchpad */
  left: 50%;
  --ry: 0px;
  transform: translateX(-50%) translateY(var(--ry));
  display: flex; flex-direction: column; align-items: center;
  cursor: grab;
  touch-action: none;   /* critical: lets pointer events work on touch */
  user-select: none;
  z-index: 30;
  will-change: transform;
}
#rocket:active { cursor: grabbing; }

/* Rocket SVG-style shapes */
.r-nose {
  width: 0; height: 0;
  border-left: 14px solid transparent;
  border-right: 14px solid transparent;
  border-bottom: 54px solid #d8d8d8;
  filter: drop-shadow(0 0 6px #88aaff66);
  pointer-events: none;
}
.r-body {
  width: 28px; height: 40px;
  background: linear-gradient(180deg, #e0e0e0 0%, #aaa 100%);
  border-radius: 2px;
  position: relative;
  pointer-events: none;
}
/* fins */
.r-body::before, .r-body::after {
  content: '';
  position: absolute; bottom: 4px;
  width: 13px; height: 20px;
  background: linear-gradient(180deg, #999, #666);
  border-radius: 0 0 6px 6px;
}
.r-body::before { left: -12px; }
.r-body::after  { right: -12px; }
/* window */
.r-body .r-window {
  position: absolute; top: 8px; left: 50%;
  transform: translateX(-50%);
  width: 10px; height: 10px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #aadeff, #226688);
  border: 1px solid #ffffff44;
  pointer-events: none;
}
/* flame */
.r-flame {
  width: 0; height: 0;
  border-left: 9px solid transparent;
  border-right: 9px solid transparent;
  border-top: 0px solid #ff6600;
  pointer-events: none;
  transition: border-top-width .08s, border-top-color .15s;
}

/* smoke puff */
#smoke {
  position: absolute;
  bottom: 22vh; left: 50%;
  transform: translateX(-50%);
  width: 0; height: 0;
  border-radius: 50%;
  background: radial-gradient(circle, #aaa, #444);
  opacity: 0;
  pointer-events: none;
}
#smoke.active {
  animation: smokePuff 2.4s ease-out forwards;
}
@keyframes smokePuff {
  0%   { width: 10px; height: 10px; opacity: .8; }
  100% { width: 260px; height: 260px; opacity: 0; }
}

/* liftoff animation — applied by JS */
@keyframes liftoff {
  0%   { bottom: calc(22vh + 11px); --ry: 0px; opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  10%  { transform: translateX(-50%) translateY(-30px) scale(1); }
  100% { transform: translateX(-50%) translateY(-150vh) scale(.15); opacity: 0; }
}
#rocket.launching {
  animation: liftoff 2.8s ease-in forwards;
  pointer-events: none;
  cursor: default;
}
#rocket.launching .r-flame {
  animation: launchFlame 2.8s ease-in forwards;
}
@keyframes launchFlame {
  0%   { border-top-width: 30px; border-top-color: #ff6600; }
  40%  { border-top-width: 60px; border-top-color: #ffaa00; }
  100% { border-top-width: 10px; border-top-color: #ffee66; opacity: .2; }
}

/* ═══════════════════════════════════════════════
   SCENE 2 — SPACE
═══════════════════════════════════════════════ */
#scene-space {
  background: radial-gradient(ellipse at 75% 90%, #001830 0%, #000 55%);
  justify-content: center;
}
.earth-orb {
  position: absolute; bottom: -18vw; right: -18vw;
  width: clamp(200px, 65vw, 340px);
  height: clamp(200px, 65vw, 340px);
  border-radius: 50%;
  background: radial-gradient(circle at 33% 33%,
    #2299ff, #006699, #003355, #001122);
  box-shadow: 0 0 50px #1e90ff33, inset -20px -20px 50px #00000066;
  pointer-events: none;
}
.floating-rocket {
  position: absolute; top: 24%; left: 10%;
  font-size: clamp(2rem, 9vw, 3.4rem);
  animation: floatR 5s ease-in-out infinite;
  filter: drop-shadow(0 0 10px #88aaff55);
  pointer-events: none; user-select: none;
}
@keyframes floatR {
  0%, 100% { transform: translateY(0) rotate(-12deg); }
  50%       { transform: translateY(-16px) rotate(-12deg); }
}

/* ═══════════════════════════════════════════════
   SHARED CARD / PROMPT STYLES
═══════════════════════════════════════════════ */
.glass-card {
  background: #ffffff07;
  border: 1px solid #88aaff2a;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 20px;
  padding: clamp(24px, 5vw, 42px) clamp(20px, 5vw, 44px);
  text-align: center;
  max-width: min(88vw, 450px);
  animation: cardIn .7s cubic-bezier(.16,1,.3,1) forwards;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}
.glass-card h2 {
  font-family: 'Orbitron', monospace;
  font-size: clamp(1rem, 4.5vw, 1.4rem);
  margin-bottom: 10px; color: #fff;
}
.glass-card p {
  font-size: clamp(.8rem, 3.3vw, .95rem);
  color: #aac4e0; line-height: 1.7;
  margin-bottom: 22px;
}

/* ═══════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════ */
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  min-height: 52px; padding: 0 28px;
  border-radius: 8px; border: none;
  font-family: 'Orbitron', monospace;
  font-size: clamp(.78rem, 3.5vw, .95rem);
  font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; cursor: pointer;
  -webkit-appearance: none; touch-action: manipulation;
  transition: opacity .15s, transform .15s;
  user-select: none;
}
.btn:active { opacity: .75; transform: scale(.96); }
.btn-primary {
  background: linear-gradient(135deg, #1a3080, #3b82f6);
  color: #fff;
  box-shadow: 0 4px 20px #3b82f633;
}
.btn-ghost {
  background: transparent;
  border: 1px solid #88aaff44;
  color: #88aaff99;
  font-family: 'Exo 2', sans-serif; font-weight: 600;
}
.btn-ghost:active { border-color: #88aaff; color: #88aaff; }
.btn-row { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }

/* ═══════════════════════════════════════════════
   SCENE 3 — SOLAR SYSTEM
═══════════════════════════════════════════════ */
#scene-solar {
  background: radial-gradient(ellipse at 50% 50%, #080215 0%, #000 70%);
  justify-content: center;
}
.solar-label {
  position: absolute; top: 14px;
  font-family: 'Orbitron', monospace;
  font-size: clamp(.58rem, 2.3vw, .82rem);
  letter-spacing: .3em; color: #88aaff44;
  text-transform: uppercase;
  pointer-events: none; user-select: none;
}
#solarSystem {
  position: relative;
  flex-shrink: 0;
  /* size set by JS */
}
.sun {
  position: absolute; border-radius: 50%;
  background: radial-gradient(circle at 38% 38%,
    #fffacc, #ffcc00, #ff8800, #ff3300);
  box-shadow: 0 0 28px #ffcc0066, 0 0 60px #ff880033;
  animation: sunPulse 3.5s ease-in-out infinite;
  z-index: 5;
}
@keyframes sunPulse {
  0%, 100% { box-shadow: 0 0 28px #ffcc0066, 0 0 60px #ff880033; }
  50%       { box-shadow: 0 0 44px #ffcc0099, 0 0 90px #ff880055; }
}
.orbit-ring {
  position: absolute; border-radius: 50%;
  border: 1px solid #ffffff08;
  pointer-events: none;
}
.planet-wrap {
  position: absolute; top: 50%; left: 50%;
  transform-origin: 0 0;
  /* animation set by JS */
}
.planet {
  position: absolute;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
  /* size / color / position set by JS */
}
.planet-hitbox {
  position: absolute;
  inset: -16px;
  border-radius: 50%;
  touch-action: manipulation;
  cursor: pointer;
}
.planet-name {
  position: absolute;
  top: calc(100% + 4px); left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: clamp(6px, 1.6vw, 9px);
  color: #ffffff44;
  pointer-events: none; user-select: none;
}
.saturn-ring {
  position: absolute;
  width: 160%; height: 30%;
  border-radius: 50%;
  border: 2px solid #c8a96466;
  top: 35%; left: -30%;
  transform: rotateX(65deg);
  pointer-events: none;
}

/* bottom prompt on solar scene */
#solarPrompt {
  position: absolute; bottom: 14px; left: 50%;
  transform: translateX(-50%);
  background: #000000cc;
  border: 1px solid #88aaff22;
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border-radius: 14px;
  padding: 16px 22px;
  text-align: center;
  width: min(92vw, 380px);
  animation: cardIn .8s ease 1.2s both;
}
#solarPrompt p {
  font-size: clamp(.75rem, 3vw, .88rem);
  color: #aac4e0; margin-bottom: 14px; line-height: 1.5;
}

/* ═══════════════════════════════════════════════
   PLANET INFO BOTTOM SHEET
═══════════════════════════════════════════════ */
#infoSheet {
  position: fixed; inset: 0; z-index: 200;
  display: flex; align-items: flex-end; justify-content: center;
  background: #00000077;
  backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px);
  animation: sheetBgIn .25s ease;
  touch-action: manipulation;
}
#infoSheet.hidden { display: none; }
@keyframes sheetBgIn { from { opacity: 0; } to { opacity: 1; } }
#infoCard {
  background: linear-gradient(155deg, #0d1440 0%, #040810 100%);
  border: 1px solid #88aaff22;
  border-radius: 22px 22px 0 0;
  padding: 26px 20px max(36px, env(safe-area-inset-bottom));
  width: 100%; max-width: 560px;
  max-height: 75vh; overflow-y: auto;
  animation: sheetIn .38s cubic-bezier(.16,1,.3,1) both;
  -webkit-overflow-scrolling: touch;
}
@keyframes sheetIn {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}
.sheet-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 18px;
}
#sheetPlanetName {
  font-family: 'Orbitron', monospace;
  font-size: clamp(1.2rem, 5.5vw, 1.8rem); font-weight: 700;
}
.sheet-close {
  width: 40px; height: 40px; border-radius: 50%;
  background: #ffffff0f; border: 1px solid #ffffff1a;
  color: #fff; font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0;
  touch-action: manipulation;
  -webkit-appearance: none;
}
.sheet-close:active { background: #ffffff22; }
.sheet-stats {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px; margin-bottom: 14px;
}
.sheet-stat {
  background: #ffffff06; border-radius: 10px; padding: 12px 14px;
}
.sheet-stat-label {
  font-size: clamp(.56rem, 2.2vw, .67rem);
  color: #88aaff77; text-transform: uppercase; letter-spacing: .08em;
  margin-bottom: 5px;
}
.sheet-stat-value {
  font-size: clamp(.78rem, 3.2vw, .92rem); font-weight: 600; color: #dce8ff;
}
.sheet-fact {
  background: #88aaff08; border-left: 3px solid #88aaff33;
  border-radius: 0 8px 8px 0; padding: 12px 14px;
  font-size: clamp(.76rem, 3vw, .87rem); color: #aac4e0; line-height: 1.65;
}

/* ═══════════════════════════════════════════════
   SCENE 4 — OBSERVABLE UNIVERSE
═══════════════════════════════════════════════ */
#scene-universe {
  background: #000;
  justify-content: center;
}
.universe-inner {
  display: flex; flex-direction: column;
  align-items: center; gap: 26px;
  padding: 20px;
}
#univSphere {
  width: clamp(240px, min(75vw, 72vh), 370px);
  height: clamp(240px, min(75vw, 72vh), 370px);
  border-radius: 50%; flex-shrink: 0;
  background: radial-gradient(circle at 38% 38%,
    #ffffff06 0%, #3333cc0f 20%, #220044 42%, #110022 65%, #040010 85%, #000 100%);
  box-shadow: 0 0 80px #4444ff1a, 0 0 160px #33003388,
              inset 0 0 80px #00000066;
  position: relative; overflow: hidden;
  animation: univPulse 9s ease-in-out infinite;
}
@keyframes univPulse {
  0%, 100% { box-shadow: 0 0 80px #4444ff1a, 0 0 160px #33003388; }
  50%       { box-shadow: 0 0 120px #6666ff33, 0 0 240px #440066aa; }
}
.g-cluster {
  position: absolute; border-radius: 50%;
  background: radial-gradient(circle, #ffffff55, transparent 70%);
  animation: gFloat var(--d) ease-in-out infinite alternate;
}
@keyframes gFloat {
  from { transform: translate(0,0) scale(.9); opacity: .3; }
  to   { transform: translate(var(--gx),var(--gy)) scale(1.15); opacity: .7; }
}
.u-earth-dot {
  position: absolute; bottom: 23%; right: 27%;
  width: 5px; height: 5px;
  background: #44aaff; border-radius: 50%;
  box-shadow: 0 0 8px #44aaff;
  animation: udot 2.2s ease-in-out infinite;
}
@keyframes udot { 0%,100%{transform:scale(1);opacity:1;} 50%{transform:scale(2.4);opacity:.5;} }
.u-here-label {
  position: absolute; bottom: calc(23% + 10px); right: calc(27% - 30px);
  font-size: clamp(6px, 1.8vw, 9px); color: #44aaff;
  white-space: nowrap; letter-spacing: .07em;
}
.univ-text {
  text-align: center; max-width: min(88vw, 460px);
  animation: cardIn .9s ease .5s both;
}
.univ-text h2 {
  font-family: 'Orbitron', monospace;
  font-size: clamp(.88rem, 3.8vw, 1.2rem);
  margin-bottom: 10px; letter-spacing: .06em;
}
.univ-text p {
  color: #8899bb; font-size: clamp(.74rem, 3vw, .88rem); line-height: 1.8;
}

/* ═══════════════════════════════════════════════
   TRANSITION OVERLAY
═══════════════════════════════════════════════ */
#transOverlay {
  position: fixed; inset: 0;
  background: #000; z-index: 500;
  opacity: 0; pointer-events: none;
  transition: opacity .5s ease;
}
#transOverlay.on { opacity: 1; pointer-events: all; }
</style>
</head>
<body>

<!-- Stars -->
<div id="stars"></div>

<!-- Transition overlay -->
<div id="transOverlay"></div>

<!-- ═══ SCENE 1: LAUNCH ═══ -->
<div class="scene" id="scene-launch">
  <div class="launch-header">
    <h1>KNOWN SPACE</h1>
    <p class="sub">A journey through the observable universe</p>
    <p class="hint">↓ &nbsp;Drag the rocket DOWN to launch&nbsp; ↓</p>
  </div>

  <div class="launch-stage">
    <div id="chargeLabel" class="visible" style="opacity:0">CHARGE</div>
    <div id="chargeBar"><div id="chargeFill"></div></div>
    <div class="ground"></div>
    <div class="launchpad"></div>
    <div id="smoke"></div>
    <div id="rocket">
      <div class="r-nose"></div>
      <div class="r-body">
        <div class="r-window"></div>
      </div>
      <div class="r-flame" id="rFlame"></div>
    </div>
  </div>
</div>

<!-- ═══ SCENE 2: SPACE ═══ -->
<div class="scene hidden" id="scene-space">
  <div class="earth-orb"></div>
  <div class="floating-rocket">🚀</div>
  <div class="glass-card">
    <h2>You've entered space.</h2>
    <p>Earth drifts silently behind you. The cosmos stretches endlessly in every direction. Ready to explore our Solar System?</p>
    <div class="btn-row">
      <button class="btn btn-primary" id="btnSolar">Explore Solar System →</button>
    </div>
  </div>
</div>

<!-- ═══ SCENE 3: SOLAR SYSTEM ═══ -->
<div class="scene hidden" id="scene-solar">
  <div class="solar-label">Our Solar System — Tap a Planet</div>
  <div id="solarSystem"></div>
  <div id="solarPrompt">
    <p>You've explored the Solar System. Ready to see the full Observable Universe?</p>
    <div class="btn-row">
      <button class="btn btn-primary" id="btnUniverse">Zoom to Universe →</button>
      <button class="btn btn-ghost" id="btnStay">Keep Exploring</button>
    </div>
  </div>
</div>

<!-- ═══ SCENE 4: UNIVERSE ═══ -->
<div class="scene hidden" id="scene-universe">
  <div class="universe-inner">
    <div id="univSphere"></div>
    <div class="univ-text">
      <h2>The Observable Universe</h2>
      <p>
        93 billion light-years across<br>
        2 trillion galaxies &nbsp;&middot;&nbsp; 13.8 billion years old<br><br>
        Every star you have ever seen with the naked eye<br>
        is inside the Milky Way — one of those 2 trillion galaxies.
      </p>
    </div>
  </div>
</div>

<!-- ═══ PLANET INFO SHEET ═══ -->
<div id="infoSheet" class="hidden">
  <div id="infoCard">
    <div class="sheet-header">
      <div id="sheetPlanetName">Planet</div>
      <button class="sheet-close" id="sheetClose">✕</button>
    </div>
    <div class="sheet-stats">
      <div class="sheet-stat">
        <div class="sheet-stat-label">Distance from Sun</div>
        <div class="sheet-stat-value" id="sd-dist"></div>
      </div>
      <div class="sheet-stat">
        <div class="sheet-stat-label">Size vs Earth</div>
        <div class="sheet-stat-value" id="sd-size"></div>
      </div>
      <div class="sheet-stat">
        <div class="sheet-stat-label">Temperature</div>
        <div class="sheet-stat-value" id="sd-temp"></div>
      </div>
      <div class="sheet-stat">
        <div class="sheet-stat-label">Known Moons</div>
        <div class="sheet-stat-value" id="sd-moons"></div>
      </div>
    </div>
    <div class="sheet-fact" id="sd-fact"></div>
  </div>
</div>

<script>
'use strict';

/* ══════════════════════════════════════════════════
   STARS
══════════════════════════════════════════════════ */
(function spawnStars() {
  const container = document.getElementById('stars');
  const frag = document.createDocumentFragment();
  for (let i = 0; i < 200; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    const sz = Math.random() * 2.2 + 0.4;
    s.style.cssText = [
      'width:'  + sz + 'px',
      'height:' + sz + 'px',
      'top:'    + (Math.random() * 100) + '%',
      'left:'   + (Math.random() * 100) + '%',
      '--d:'    + (Math.random() * 4 + 2).toFixed(1) + 's',
      '--del:'  + (Math.random() * 6).toFixed(1) + 's',
      'opacity:' + (Math.random() * 0.5 + 0.1).toFixed(2),
    ].join(';');
    frag.appendChild(s);
  }
  container.appendChild(frag);
})();

/* ══════════════════════════════════════════════════
   SCENE MANAGER
══════════════════════════════════════════════════ */
const transOverlay = document.getElementById('transOverlay');

function goToScene(id, delay) {
  delay = delay || 500;
  transOverlay.classList.add('on');
  setTimeout(function() {
    document.querySelectorAll('.scene').forEach(function(s) {
      s.classList.add('hidden');
    });
    const target = document.getElementById(id);
    target.classList.remove('hidden');
    if (id === 'scene-solar') buildSolar();
    if (id === 'scene-universe') buildUniverse();
    transOverlay.classList.remove('on');
  }, delay);
}

/* ══════════════════════════════════════════════════
   DRAG-TO-LAUNCH
   Uses Pointer Events — works on both touch and mouse
   with no platform-specific branching needed.
══════════════════════════════════════════════════ */
(function initLaunch() {
  const rocket     = document.getElementById('rocket');
  const rFlame     = document.getElementById('rFlame');
  const chargeBar  = document.getElementById('chargeBar');
  const chargeFill = document.getElementById('chargeFill');
  const chargeLabel= document.getElementById('chargeLabel');
  const smokeEl    = document.getElementById('smoke');

  const THRESHOLD  = 85;   // px pulled down = full charge
  const MAX_VISUAL = 58;   // max px rocket moves down on screen

  let active      = false;
  let launched    = false;
  let startY      = 0;
  let currentPull = 0;

  function setRY(px) {
    rocket.style.setProperty('--ry', px + 'px');
  }

  function resetDrag() {
    active      = false;
    currentPull = 0;
    chargeBar.classList.remove('visible');
    chargeLabel.classList.remove('visible');
    chargeFill.style.width  = '0%';
    chargeFill.classList.remove('ready');
    rFlame.style.borderTopWidth = '0px';
    // spring snap-back
    rocket.style.transition = 'transform .42s cubic-bezier(.34,1.5,.64,1)';
    setRY(0);
    setTimeout(function() { rocket.style.transition = ''; }, 450);
  }

  function doLaunch() {
    launched = true;
    active   = false;
    chargeBar.classList.remove('visible');
    chargeLabel.classList.remove('visible');
    // reset inline transition before adding class
    rocket.style.transition = '';
    setRY(0);
    // small delay so browser applies the reset
    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        rocket.classList.add('launching');
        smokeEl.classList.add('active');
        setTimeout(function() { goToScene('scene-space', 350); }, 2600);
      });
    });
  }

  rocket.addEventListener('pointerdown', function(e) {
    if (launched) return;
    active  = true;
    startY  = e.clientY;
    rocket.setPointerCapture(e.pointerId);
    rocket.style.transition = '';
    chargeBar.classList.add('visible');
    chargeLabel.classList.add('visible');
    e.preventDefault();
  });

  rocket.addEventListener('pointermove', function(e) {
    if (!active || launched) return;
    e.preventDefault();
    const dy = e.clientY - startY;
    currentPull = Math.max(0, dy);   // only downward drag counts

    // visual displacement — elastic feel
    const visual = Math.min(currentPull * 0.6, MAX_VISUAL);
    setRY(visual);

    // charge
    const pct = Math.min(currentPull / THRESHOLD * 100, 100);
    chargeFill.style.width = pct + '%';
    if (pct >= 100) chargeFill.classList.add('ready');
    else            chargeFill.classList.remove('ready');

    // flame height grows with charge
    const fh = Math.round(pct * 0.35);
    rFlame.style.borderTopWidth = fh + 'px';
    rFlame.style.borderTopStyle = 'solid';
    rFlame.style.borderTopColor = pct < 55 ? '#ff6611' : '#ffcc00';
  });

  rocket.addEventListener('pointerup', function(e) {
    if (!active || launched) return;
    rocket.releasePointerCapture(e.pointerId);
    if (currentPull >= THRESHOLD) {
      doLaunch();
    } else {
      resetDrag();
    }
  });

  rocket.addEventListener('pointercancel', function(e) {
    if (active) resetDrag();
  });
})();

/* ══════════════════════════════════════════════════
   SCENE 2 BUTTONS
══════════════════════════════════════════════════ */
document.getElementById('btnSolar').addEventListener('click', function() {
  goToScene('scene-solar', 500);
});

/* ══════════════════════════════════════════════════
   PLANET DATA
══════════════════════════════════════════════════ */
var PLANETS = [
  { name:'Mercury', color:'#b8b8b8', relSize:.38, orbit:.16, period:2.4,
    dist:'57.9M km', size:'0.38x Earth', temp:'-180 to 430C', moons:'0',
    fact:'Mercury has no atmosphere, so temperatures swing 600 degrees between day and night.' },
  { name:'Venus',   color:'#e8c96a', relSize:.95, orbit:.22, period:3.8,
    dist:'108.2M km', size:'0.95x Earth', temp:'465C avg', moons:'0',
    fact:'Venus is hotter than Mercury despite being farther from the Sun, due to its thick CO2 atmosphere trapping heat.' },
  { name:'Earth',   color:'#3a7bd5', relSize:1,   orbit:.29, period:5.0,
    dist:'149.6M km', size:'1x (home)', temp:'15C avg', moons:'1',
    fact:'Earth is the only known planet in the universe to harbour life — from deep-sea hydrothermal vents to its highest peaks.' },
  { name:'Mars',    color:'#c1440e', relSize:.53, orbit:.36, period:6.4,
    dist:'227.9M km', size:'0.53x Earth', temp:'-60C avg', moons:'2',
    fact:'Olympus Mons on Mars is the tallest volcano in the Solar System, nearly three times the height of Mount Everest.' },
  { name:'Jupiter', color:'#c88b3a', relSize:2.8, orbit:.47, period:8.5,
    dist:'778.5M km', size:'11.2x Earth', temp:'-110C clouds', moons:'95',
    fact:'Jupiter\'s Great Red Spot is a storm larger than Earth that has raged for over 350 years.' },
  { name:'Saturn',  color:'#e4d48e', relSize:2.4, orbit:.58, period:11,
    dist:'1.43B km', size:'9.45x Earth', temp:'-140C', moons:'146',
    fact:'Saturn\'s rings span 282,000 km yet are only a few hundred metres thick, made of billions of ice and rock particles.',
    ring: true },
  { name:'Uranus',  color:'#7de8e8', relSize:1.9, orbit:.70, period:14,
    dist:'2.87B km', size:'4x Earth', temp:'-195C', moons:'27',
    fact:'Uranus rotates on its side with a 98-degree axial tilt, so its poles experience 42 years of daylight then 42 years of darkness.' },
  { name:'Neptune', color:'#3f54ba', relSize:1.8, orbit:.83, period:18,
    dist:'4.5B km', size:'3.88x Earth', temp:'-200C', moons:'16',
    fact:'Neptune has the fastest winds in the Solar System, reaching 2,100 km/h, faster than the speed of sound on Earth.' },
];

/* ══════════════════════════════════════════════════
   SOLAR SYSTEM BUILDER
══════════════════════════════════════════════════ */
var _orbKF = [];   // track injected <style> nodes for cleanup

function buildSolar() {
  var container = document.getElementById('solarSystem');
  container.innerHTML = '';
  _orbKF.forEach(function(el) { if (el.parentNode) el.parentNode.removeChild(el); });
  _orbKF = [];

  var vw   = window.innerWidth;
  var vh   = window.innerHeight;
  var size = Math.min(vw * 0.92, vh * 0.60, 510);
  container.style.width  = size + 'px';
  container.style.height = size + 'px';

  var cx      = size / 2;
  var sunSize = Math.max(18, size * 0.075);

  // Sun
  var sun = document.createElement('div');
  sun.className = 'sun';
  sun.style.cssText = [
    'width:'       + sunSize + 'px',
    'height:'      + sunSize + 'px',
    'top:'         + (cx - sunSize / 2) + 'px',
    'left:'        + (cx - sunSize / 2) + 'px',
  ].join(';');
  container.appendChild(sun);

  PLANETS.forEach(function(p, i) {
    var orbitR = (size * p.orbit) / 2;
    var pSize  = Math.max(10, Math.round(sunSize * 0.42 * p.relSize));

    // orbit ring
    var ring = document.createElement('div');
    ring.className = 'orbit-ring';
    ring.style.cssText = [
      'width:'  + (orbitR * 2) + 'px',
      'height:' + (orbitR * 2) + 'px',
      'top:'    + (cx - orbitR) + 'px',
      'left:'   + (cx - orbitR) + 'px',
    ].join(';');
    container.appendChild(ring);

    // inject unique keyframe
    var startDeg = (i / PLANETS.length) * 360;
    var kfName   = 'orb_' + i + '_' + Date.now();
    var kfStyle  = document.createElement('style');
    kfStyle.textContent = '@keyframes ' + kfName + '{' +
      'from{transform:rotate(' + startDeg + 'deg) translateX(' + orbitR + 'px) rotate(-' + startDeg + 'deg);}' +
      'to{transform:rotate(' + (startDeg + 360) + 'deg) translateX(' + orbitR + 'px) rotate(-' + (startDeg + 360) + 'deg);}' +
    '}';
    document.head.appendChild(kfStyle);
    _orbKF.push(kfStyle);

    // planet wrapper (orbits)
    var wrap = document.createElement('div');
    wrap.className = 'planet-wrap';
    wrap.style.cssText = [
      'top:'       + cx + 'px',
      'left:'      + cx + 'px',
      'animation:' + kfName + ' ' + p.period.toFixed(1) + 's linear infinite',
    ].join(';');

    // planet disc
    var disc = document.createElement('div');
    disc.className = 'planet';
    disc.style.cssText = [
      'width:'       + pSize + 'px',
      'height:'      + pSize + 'px',
      'background:'  + 'radial-gradient(circle at 35% 35%,' + lighten(p.color) + ',' + p.color + ',' + darken(p.color) + ')',
      'box-shadow:'  + '0 0 ' + (pSize * 0.55) + 'px ' + p.color + '66',
      'margin-left:' + (-pSize / 2) + 'px',
      'margin-top:'  + (-pSize / 2) + 'px',
    ].join(';');

    if (p.ring) {
      var satRing = document.createElement('div');
      satRing.className = 'saturn-ring';
      disc.appendChild(satRing);
    }

    // name label
    var nameEl = document.createElement('div');
    nameEl.className = 'planet-name';
    nameEl.textContent = p.name;
    disc.appendChild(nameEl);

    // large invisible hit area
    var hit = document.createElement('div');
    hit.className = 'planet-hitbox';
    disc.appendChild(hit);

    wrap.appendChild(disc);
    container.appendChild(wrap);

    // tap handler — works for both click and touch
    (function(planet, wrapEl) {
      function openSheet(e) {
        e.stopPropagation();
        e.preventDefault();
        showPlanetSheet(planet, wrapEl);
      }
      hit.addEventListener('click',    openSheet, false);
      hit.addEventListener('touchend', openSheet, { passive: false });
    })(p, wrap);
  });
}

function lighten(hex) {
  return '#' + hex.slice(1).replace(/../g, function(m) {
    return Math.min(255, parseInt(m, 16) + 48).toString(16).padStart(2, '0');
  });
}
function darken(hex) {
  return '#' + hex.slice(1).replace(/../g, function(m) {
    return Math.max(0, parseInt(m, 16) - 38).toString(16).padStart(2, '0');
  });
}

window.addEventListener('resize', function() {
  if (!document.getElementById('scene-solar').classList.contains('hidden')) {
    buildSolar();
  }
});

/* ══════════════════════════════════════════════════
   PLANET INFO SHEET
══════════════════════════════════════════════════ */
var _activePlanetWrap = null;

function showPlanetSheet(p, wrapEl) {
  // pause orbit
  if (_activePlanetWrap) _activePlanetWrap.style.animationPlayState = 'running';
  _activePlanetWrap = wrapEl;
  wrapEl.style.animationPlayState = 'paused';

  document.getElementById('sheetPlanetName').textContent = p.name;
  document.getElementById('sheetPlanetName').style.color = p.color;
  document.getElementById('sd-dist').textContent  = p.dist;
  document.getElementById('sd-size').textContent  = p.size;
  document.getElementById('sd-temp').textContent  = p.temp;
  document.getElementById('sd-moons').textContent = p.moons;
  document.getElementById('sd-fact').textContent  = p.fact;

  var sheet = document.getElementById('infoSheet');
  sheet.classList.remove('hidden');
  // re-trigger animation
  var card = document.getElementById('infoCard');
  card.style.animation = 'none';
  requestAnimationFrame(function() {
    card.style.animation = '';
  });
}

function closeSheet() {
  document.getElementById('infoSheet').classList.add('hidden');
  if (_activePlanetWrap) {
    _activePlanetWrap.style.animationPlayState = 'running';
    _activePlanetWrap = null;
  }
}

document.getElementById('sheetClose').addEventListener('click', closeSheet);
document.getElementById('infoSheet').addEventListener('click', function(e) {
  if (e.target === document.getElementById('infoSheet')) closeSheet();
});

/* ══════════════════════════════════════════════════
   SCENE 3 BUTTONS
══════════════════════════════════════════════════ */
document.getElementById('btnUniverse').addEventListener('click', function() {
  goToScene('scene-universe', 700);
});
document.getElementById('btnStay').addEventListener('click', function() {
  document.getElementById('solarPrompt').style.display = 'none';
});

/* ══════════════════════════════════════════════════
   OBSERVABLE UNIVERSE BUILDER
══════════════════════════════════════════════════ */
function buildUniverse() {
  var sphere = document.getElementById('univSphere');
  if (sphere.dataset.built) return;
  sphere.dataset.built = '1';

  var frag = document.createDocumentFragment();
  for (var i = 0; i < 60; i++) {
    var cl = document.createElement('div');
    cl.className = 'g-cluster';
    var s = Math.random() * 28 + 4;
    cl.style.cssText = [
      'width:'  + s + 'px',
      'height:' + s + 'px',
      'top:'    + (Math.random() * 84 + 5) + '%',
      'left:'   + (Math.random() * 84 + 5) + '%',
      '--d:'    + (Math.random() * 6 + 4).toFixed(1) + 's',
      '--gx:'   + (Math.random() * 18 - 9).toFixed(0) + 'px',
      '--gy:'   + (Math.random() * 18 - 9).toFixed(0) + 'px',
      'animation-delay:' + (Math.random() * 6).toFixed(1) + 's',
    ].join(';');
    frag.appendChild(cl);
  }

  var dot = document.createElement('div'); dot.className = 'u-earth-dot';
  var lbl = document.createElement('div'); lbl.className = 'u-here-label';
  lbl.textContent = 'you are here';
  frag.appendChild(dot); frag.appendChild(lbl);
  sphere.appendChild(frag);
}

</script>
</body>
</html>"""

components.html(HTML, height=820, scrolling=False)
