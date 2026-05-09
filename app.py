import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
SUBJECTS   = ["FR", "AFM", "Audit", "DT", "IDT"]
COLORS     = ["#378ADD", "#1D9E75", "#EF9F27", "#D4537E", "#7F77DD"]
EXAM_DATE  = datetime(2026, 8, 31)

st.set_page_config(
    page_title="CA Final Pro Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────
@st.cache_resource
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    return client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1LmGqy7Wc55yItxpj96VrmUZmzOyVJQy5d2JNhGGkAlU/edit?gid=1533693941#gid=1533693941"
    )

@st.cache_data(ttl=15)
def load_subject(subject_name: str):
    sh = get_sheet()
    ws = sh.worksheet(subject_name)
    return pd.DataFrame(ws.get_all_records()), ws

def convert_to_hours(duration) -> float:
    if duration is None:
        return 0.0
    try:
        if pd.isna(duration):
            return 0.0
    except Exception:
        pass
    try:
        if isinstance(duration, (int, float)):
            return float(duration)
        if isinstance(duration, str):
            duration = duration.strip()
            if duration == "":
                return 0.0
            if ":" in duration:
                parts = duration.split(":")
                if len(parts) == 3:
                    return int(parts[0]) + int(parts[1]) / 60 + int(parts[2]) / 3600
            return float(duration)
        if hasattr(duration, "hour"):
            return duration.hour + duration.minute / 60
        if hasattr(duration, "total_seconds"):
            return duration.total_seconds() / 3600
    except Exception:
        return 0.0
    return 0.0

# ─────────────────────────────────────────
#  GLOBAL STYLES + ANIMATIONS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;500;600;700&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #080B12 !important;
    color: #E2E8F0 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Starfield canvas ── */
#stars-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.45;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1400px !important;
    position: relative;
    z-index: 1;
}

/* ── Keyframes ── */
@keyframes fadeUp   { from { opacity:0; transform:translateY(22px) } to { opacity:1; transform:translateY(0) } }
@keyframes fadeIn   { from { opacity:0 } to { opacity:1 } }
@keyframes pulse    { 0%,100%{opacity:1} 50%{opacity:.3} }
@keyframes flip     { 0%{transform:translateY(0);opacity:1} 45%{transform:translateY(-12px);opacity:0} 55%{transform:translateY(12px);opacity:0} 100%{transform:translateY(0);opacity:1} }
@keyframes barGrow  { from{width:0} to{width:var(--w)} }
@keyframes checkPop { 0%{transform:scale(0) rotate(-15deg)} 70%{transform:scale(1.3) rotate(3deg)} 100%{transform:scale(1)} }
@keyframes confetti { 0%{transform:translateY(-10px) rotate(0);opacity:1} 100%{transform:translateY(70px) rotate(720deg);opacity:0} }
@keyframes streakBeat { 0%,100%{transform:scale(1)} 50%{transform:scale(1.18)} }
@keyframes ringDraw { from{stroke-dashoffset:var(--c)} to{stroke-dashoffset:var(--o)} }
@keyframes heatPop  { from{transform:scale(0);opacity:0} to{transform:scale(1);opacity:1} }
@keyframes numUp    { from{opacity:0;transform:scale(.8)} to{opacity:1;transform:scale(1)} }
@keyframes neonGlow {
    0%,100% { box-shadow: 0 0 6px rgba(55,138,221,.15), 0 0 0 0 transparent; }
    50%     { box-shadow: 0 0 18px rgba(55,138,221,.35), 0 0 40px rgba(55,138,221,.1); }
}

/* ── Typography ── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: #F0F4FF !important; }
.mono { font-family: 'Space Mono', monospace !important; }

/* ── Section label ── */
.sec-lbl {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #4A5568;
    margin-bottom: .6rem;
    margin-top: 1.5rem;
    animation: fadeIn .6s ease both;
}

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.75rem;
    animation: fadeUp .5s ease both;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
    width: 40px; height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #1a3a5c, #0d2238);
    border: 1px solid #1e3d5c;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.brand-name { font-size: 18px; font-weight: 700; color: #F0F4FF; letter-spacing: -.01em; }
.brand-sub  { font-size: 11px; color: #4A5568; margin-top: 1px; }
.live-pill {
    display: flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 20px;
    border: 1px solid #1A2535;
    background: #0D1422;
    font-size: 11px; color: #4A5568;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #1D9E75;
    animation: pulse 2s infinite;
}

/* ── Countdown ── */
.cd-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 1.25rem;
}
.cd-card {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 14px;
    padding: 1rem .5rem;
    text-align: center;
    animation: fadeUp .5s ease both;
    transition: transform .2s, border-color .2s;
}
.cd-card:hover { transform: translateY(-3px); border-color: #263548; }
.cd-n {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #F0F4FF;
    line-height: 1;
}
.cd-n.flip { animation: flip .32s ease; }
.cd-l { font-size: 9px; letter-spacing: .1em; color: #4A5568; margin-top: 4px; text-transform: uppercase; }

/* ── Streak bar ── */
.streak-bar {
    display: flex; align-items: center; gap: 14px;
    padding: .85rem 1.25rem;
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 14px;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s .06s ease both;
}
.streak-fire { font-size: 24px; animation: streakBeat 2.2s ease infinite; }
.streak-num  { font-size: 20px; font-weight: 700; color: #EF9F27; font-family: 'Space Mono', monospace; }
.streak-lbl  { font-size: 11px; color: #4A5568; margin-top: 2px; }
.streak-dots { display: flex; gap: 5px; margin-left: auto; }
.sdot {
    width: 10px; height: 10px; border-radius: 3px;
    background: #1A2535;
    transition: background .4s, transform .3s;
}
.sdot.active { background: #EF9F27; transform: scale(1.15); }

/* ── Overall card ── */
.ov-card {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s .1s ease both;
}
.ov-top  { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
.ov-lbl  { font-size: 12px; color: #4A5568; }
.ov-pct  { font-family: 'Space Mono', monospace; font-size: 28px; font-weight: 700; color: #F0F4FF; }
.ov-track { height: 10px; background: #141E2E; border-radius: 6px; overflow: hidden; margin-bottom: 6px; }
.ov-fill  {
    height: 100%; border-radius: 6px;
    background: linear-gradient(90deg, #1a5fa5, #378ADD, #60ADEF);
    width: 0; transition: width 1.8s cubic-bezier(.4,0,.2,1);
}
.ov-meta { display: flex; justify-content: space-between; font-size: 11px; color: #4A5568; }

/* ── Metric cards ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 1.25rem;
}
.mc {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 14px;
    padding: .9rem 1.1rem;
    animation: fadeUp .5s ease both;
    transition: transform .2s, border-color .2s;
    cursor: default;
}
.mc:hover { transform: translateY(-3px); border-color: #263548; animation: neonGlow .8s ease; }
.mc-ic { font-size: 16px; color: #4A5568; margin-bottom: 5px; }
.mc-v  { font-family: 'Space Mono', monospace; font-size: 22px; font-weight: 700; color: #F0F4FF; animation: numUp .5s ease; }
.mc-l  { font-size: 11px; color: #4A5568; margin-top: 2px; }
.mc-b  { height: 3px; background: #141E2E; border-radius: 2px; overflow: hidden; margin-top: 10px; }
.mc-bf { height: 100%; border-radius: 2px; width: 0; transition: width 1.4s cubic-bezier(.4,0,.2,1); }

/* ── Subject cards ── */
.subj-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 1.25rem;
}
.sc {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 14px;
    padding: .9rem 1rem;
    cursor: pointer;
    animation: fadeUp .5s ease both;
    transition: transform .2s, border-color .2s, box-shadow .2s;
}
.sc:hover    { transform: translateY(-3px); }
.sc.active   { border-width: 1.5px; }
.sc-head     { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
.sc-name     { font-size: 14px; font-weight: 700; color: #F0F4FF; }
.sc-pct      { font-family: 'Space Mono', monospace; font-size: 11px; color: #4A5568; }
.sc-track    { height: 5px; background: #141E2E; border-radius: 3px; overflow: hidden; margin-bottom: 5px; }
.sc-fill     { height: 100%; border-radius: 3px; width: 0; transition: width 1.5s cubic-bezier(.4,0,.2,1); }
.sc-foot     { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.sc-hrs      { font-size: 10px; color: #4A5568; }
.sc-eta      { font-size: 10px; font-weight: 600; }

/* ── Tasks panel ── */
.tasks-wrap {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
    min-height: 80px;
    animation: fadeUp .5s ease both;
}
.tasks-title { font-size: 13px; font-weight: 600; color: #F0F4FF; margin-bottom: .75rem; display: flex; align-items: center; gap: 7px; }
.task-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 8px; border-radius: 9px;
    cursor: pointer;
    transition: background .15s;
    animation: fadeUp .3s ease both;
}
.task-row:hover { background: #111927; }
.tcb {
    width: 18px; height: 18px; border-radius: 6px;
    border: 1.5px solid #263548;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    transition: background .2s, border-color .2s;
}
.tcb.done { background: #1D9E75; border-color: #1D9E75; }
.tcb.done span { animation: checkPop .3s ease; opacity: 1 !important; }
.tcb span { font-size: 11px; color: #fff; opacity: 0; transition: opacity .15s; }
.t-txt  { font-size: 12px; color: #B0BEC5; flex: 1; transition: color .2s; }
.t-txt.done  { color: #37434F; text-decoration: line-through; }
.t-tag  { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: #111927; color: #4A5568; flex-shrink: 0; font-family: 'Space Mono', monospace; }
.confetti-piece {
    position: absolute;
    width: 7px; height: 7px; border-radius: 2px;
    pointer-events: none;
    animation: confetti .9s ease forwards;
}

/* ── Rings ── */
.rings-section {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: .9rem 1.4rem;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s ease both;
}
.rings-row { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 8px; margin-top: .6rem; }
.rw { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.rl { font-size: 10px; color: #4A5568; letter-spacing: .04em; }

/* ── Pomodoro ── */
.pomo-card {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s ease both;
}
.pomo-inner  { display: flex; align-items: center; gap: 20px; }
.pomo-ring-w { position: relative; flex-shrink: 0; }
.pomo-time   {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Space Mono', monospace;
    font-size: 15px; font-weight: 700; color: #F0F4FF;
    text-align: center; line-height: 1;
}
.pomo-info     { flex: 1; }
.pomo-session  { font-size: 14px; font-weight: 600; color: #F0F4FF; margin-bottom: 3px; }
.pomo-hint     { font-size: 11px; color: #4A5568; margin-bottom: 12px; }
.pomo-btns     { display: flex; gap: 8px; }
.pomo-btns button {
    font-size: 12px; padding: 6px 16px;
    border-radius: 9px;
    border: 1px solid #1A2535;
    background: #111927;
    color: #B0BEC5;
    cursor: pointer;
    font-family: 'Syne', sans-serif;
    transition: background .15s, transform .1s, border-color .2s;
}
.pomo-btns button:hover { background: #1A2535; border-color: #263548; }
.pomo-btns button:active { transform: scale(.96); }
.pomo-sessions { display: flex; gap: 5px; margin-top: 10px; }
.ps-dot { width: 9px; height: 9px; border-radius: 50%; background: #1A2535; transition: background .4s; }
.ps-dot.done { background: #378ADD; }

/* ── Heat map ── */
.heat-section {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: .9rem 1.4rem;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s ease both;
}
.heat-grid {
    display: grid;
    grid-template-columns: repeat(14, 1fr);
    gap: 4px;
    margin-top: .6rem;
}
.heat-cell {
    aspect-ratio: 1; border-radius: 4px;
    transition: transform .2s;
    animation: heatPop .3s ease both;
    cursor: default;
}
.heat-cell:hover { transform: scale(1.35); }
.heat-legend { display: flex; align-items: center; gap: 5px; margin-top: 8px; font-size: 10px; color: #4A5568; }
.hl-box { width: 10px; height: 10px; border-radius: 3px; }

/* ── Weak subject ── */
.weak-section {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: .9rem 1.4rem;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s ease both;
}
.weak-row {
    display: flex; align-items: center; gap: 10px;
    padding: .55rem .5rem;
    border-radius: 9px;
    font-size: 12px; color: #B0BEC5;
    transition: background .15s;
}
.weak-row:hover { background: #111927; }
.weak-name { min-width: 42px; font-weight: 700; color: #F0F4FF; }
.weak-bar-wrap { flex: 1; height: 4px; background: #141E2E; border-radius: 2px; overflow: hidden; }
.weak-bar-fill  { height: 100%; border-radius: 2px; transition: width 1.3s cubic-bezier(.4,0,.2,1); }
.weak-pct { min-width: 36px; text-align: right; font-family: 'Space Mono', monospace; font-size: 11px; color: #4A5568; }

/* ── Pressure banner ── */
.pressure-row {
    display: flex; align-items: center; gap: 10px;
    padding: .85rem 1.25rem;
    border-radius: 14px;
    border: 1px solid #1A2535;
    background: #0D1422;
    margin-bottom: 1.25rem;
    font-size: 13px; color: #B0BEC5;
    animation: fadeUp .5s ease both;
    transition: border-color .4s;
}

/* ── Motivation ── */
.motiv {
    padding: .85rem 1.25rem;
    border-radius: 14px;
    border: 1px solid #1A2535;
    background: #0D1422;
    font-size: 13px; color: #4A5568;
    display: flex; align-items: center; gap: 10px;
    animation: fadeIn .8s 1s ease both;
    opacity: 0;
}

/* ── ETA table ── */
.eta-section {
    background: #0D1422;
    border: 1px solid #1A2535;
    border-radius: 16px;
    padding: .9rem 1.4rem;
    margin-bottom: 1.25rem;
    animation: fadeUp .5s ease both;
}
.eta-row {
    display: flex; align-items: center; gap: 10px;
    padding: .5rem 0;
    border-bottom: 1px solid #111927;
    font-size: 12px;
}
.eta-row:last-child { border-bottom: none; }
.eta-subj { min-width: 50px; font-weight: 700; color: #F0F4FF; }
.eta-date  { flex: 1; color: #4A5568; font-family: 'Space Mono', monospace; font-size: 11px; }
.eta-badge {
    font-size: 10px; padding: 2px 9px; border-radius: 10px;
    font-weight: 600; letter-spacing: .03em;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080B12; }
::-webkit-scrollbar-thumb { background: #1A2535; border-radius: 3px; }
</style>

<!-- Stars canvas -->
<canvas id="stars-canvas"></canvas>

<script>
// ── Starfield ──
(function(){
    const canvas = document.getElementById('stars-canvas');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
    resize(); window.addEventListener('resize', resize);
    const stars = Array.from({length:80}, ()=>({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        r: Math.random()*1.3+.2,
        speed: Math.random()*.25+.05,
        o: Math.random()
    }));
    function draw(){
        ctx.clearRect(0,0,canvas.width,canvas.height);
        stars.forEach(s=>{
            s.o += .008*(Math.random()>.5?1:-1);
            s.o = Math.max(.05, Math.min(.9, s.o));
            s.y -= s.speed;
            if(s.y<0){ s.y=canvas.height; s.x=Math.random()*canvas.width; }
            ctx.beginPath();
            ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
            ctx.fillStyle=`rgba(55,138,221,${s.o.toFixed(2)})`;
            ctx.fill();
        });
        requestAnimationFrame(draw);
    }
    draw();
})();

// ── Countdown flip ──
function startCountdown(targetISO){
    const target = new Date(targetISO);
    const ids = ['cd-d','cd-h','cd-m','cd-s'];
    function pad(n){ return String(n).padStart(2,'0'); }
    function tick(){
        const diff = Math.max(target - new Date(), 0);
        const vals = [
            Math.floor(diff/86400000),
            Math.floor(diff%86400000/3600000),
            Math.floor(diff%3600000/60000),
            Math.floor(diff%60000/1000)
        ];
        vals.forEach((v,i)=>{
            const el = document.getElementById(ids[i]);
            if(!el) return;
            const str = pad(v);
            if(el.textContent !== str){
                el.classList.remove('flip');
                void el.offsetWidth;
                el.classList.add('flip');
                el.textContent = str;
            }
        });
    }
    tick(); setInterval(tick, 1000);
}

// ── Animated number counter ──
function animateNum(id, target, decimals, suffix, duration){
    const el = document.getElementById(id);
    if(!el) return;
    const start = performance.now();
    function step(now){
        const p = Math.min((now-start)/duration, 1);
        const ease = 1 - Math.pow(1-p, 3);
        el.textContent = (target*ease).toFixed(decimals) + (suffix||'');
        if(p<1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// ── Bar animate ──
function animateBar(id, pct, delay){
    setTimeout(()=>{
        const el = document.getElementById(id);
        if(el) el.style.width = pct.toFixed(1)+'%';
    }, delay||0);
}

// ── Ring animate ──
function animateRing(id, pct, circ, delay){
    setTimeout(()=>{
        const el = document.getElementById(id);
        if(el) el.style.strokeDashoffset = (circ - pct/100*circ).toFixed(2);
    }, delay||0);
}

// ── Confetti burst ──
function confettiBurst(containerId){
    const wrap = document.getElementById(containerId);
    if(!wrap) return;
    const colors = ['#378ADD','#1D9E75','#EF9F27','#D4537E','#7F77DD'];
    for(let i=0;i<10;i++){
        const c = document.createElement('div');
        c.className = 'confetti-piece';
        c.style.cssText = `left:${15+Math.random()*70}%;top:${5+Math.random()*40}%;background:${colors[i%5]};animation-delay:${Math.random()*.4}s`;
        wrap.appendChild(c);
        setTimeout(()=>c.remove(), 1200);
    }
}
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────
subject_data = {}
worksheets   = {}

with st.spinner("Syncing with Google Sheets..."):
    for subj in SUBJECTS:
        try:
            df, ws = load_subject(subj)
            total = sum(convert_to_hours(r["Hours"]) for _, r in df.iterrows())
            done  = sum(
                convert_to_hours(r["Hours"])
                for _, r in df.iterrows()
                if str(r.get("Completed", "")).strip().lower() == "true"
            )
            subject_data[subj] = {"df": df, "ws": ws, "done": done, "total": total}
            worksheets[subj]   = ws
        except Exception as e:
            st.error(f"Could not load {subj}: {e}")
            subject_data[subj] = {"df": pd.DataFrame(), "ws": None, "done": 0, "total": 0}

total_hours     = sum(v["total"] for v in subject_data.values())
completed_hours = sum(v["done"]  for v in subject_data.values())
remaining_hours = max(total_hours - completed_hours, 0)
days_left       = max((EXAM_DATE.date() - date.today()).days, 1)
rpd             = remaining_hours / days_left
overall_pct     = (completed_hours / total_hours * 100) if total_hours else 0

pressure = ("🟢 LOW" if rpd < 4 else "🟡 MEDIUM" if rpd < 8 else "🔴 HIGH")
pressure_color = ("#1D9E75" if rpd < 4 else "#EF9F27" if rpd < 8 else "#E24B4A")

# ─────────────────────────────────────────
#  TOP BAR
# ─────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="brand">
    <div class="brand-icon">🚀</div>
    <div>
      <div class="brand-name">CA Final Pro</div>
      <div class="brand-sub">Aug 31 · 2026 · Your personal command center</div>
    </div>
  </div>
  <div style="display:flex;gap:8px;align-items:center">
    <div class="live-pill"><div class="live-dot"></div>Live sync</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  LIVE COUNTDOWN
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Countdown to exam</div>', unsafe_allow_html=True)
st.markdown("""
<div class="cd-row">
  <div class="cd-card" style="animation-delay:.0s"><div class="cd-n mono" id="cd-d">--</div><div class="cd-l">DAYS</div></div>
  <div class="cd-card" style="animation-delay:.06s"><div class="cd-n mono" id="cd-h">--</div><div class="cd-l">HRS</div></div>
  <div class="cd-card" style="animation-delay:.12s"><div class="cd-n mono" id="cd-m">--</div><div class="cd-l">MIN</div></div>
  <div class="cd-card" style="animation-delay:.18s"><div class="cd-n mono" id="cd-s">--</div><div class="cd-l">SEC</div></div>
</div>
<script>startCountdown("2026-08-31T00:00:00");</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  STREAK BAR
# ─────────────────────────────────────────
streak_days = 7  # replace with real streak calc if you track dates
streak_dots = "".join(
    f'<div class="sdot{"  active" if i < streak_days else ""}"></div>'
    for i in range(14)
)
st.markdown(f"""
<div class="streak-bar">
  <div class="streak-fire">🔥</div>
  <div>
    <div class="streak-num">{streak_days} day streak</div>
    <div class="streak-lbl">Keep going — don't break the chain</div>
  </div>
  <div class="streak-dots">{streak_dots}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  OVERALL PROGRESS
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Overall progress</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="ov-card">
  <div class="ov-top">
    <span class="ov-lbl">📈 Study completion</span>
    <span class="ov-pct mono" id="ov-pct">0%</span>
  </div>
  <div class="ov-track"><div class="ov-fill" id="ov-fill"></div></div>
  <div class="ov-meta">
    <span>{completed_hours:.1f} / {total_hours:.1f} hrs completed</span>
    <span>{rpd:.1f} hrs/day needed</span>
  </div>
</div>
<script>
  animateNum('ov-pct', {overall_pct:.4f}, 1, '%', 1200);
  animateBar('ov-fill', {overall_pct:.4f}, 300);
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  METRIC CARDS
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Key stats</div>', unsafe_allow_html=True)
mc_data = [
    ("✅", completed_hours, 1, "", "Done hrs",      "#1D9E75", completed_hours/max(total_hours,1)*100),
    ("⏳", remaining_hours, 1, "", "Remaining",     "#E24B4A", remaining_hours/max(total_hours,1)*100),
    ("⚡", rpd,             1, "", "Hrs/day needed","#EF9F27", min(rpd/12*100,100)),
    ("📅", days_left,       0, "", "Days left",     "#378ADD", min(days_left/200*100,100)),
]
mc_html = '<div class="metrics-grid">'
for i, (ic, val, dec, suf, lbl, col, bar_pct) in enumerate(mc_data):
    mc_html += f"""
    <div class="mc" style="animation-delay:{.04+i*.06}s">
      <div class="mc-ic">{ic}</div>
      <div class="mc-v mono" id="mv{i}">0</div>
      <div class="mc-l">{lbl}</div>
      <div class="mc-b"><div class="mc-bf" id="mb{i}" style="background:{col}"></div></div>
    </div>"""
mc_html += "</div><script>"
for i, (ic, val, dec, suf, lbl, col, bar_pct) in enumerate(mc_data):
    mc_html += f"animateNum('mv{i}',{val:.4f},{dec},'{suf}',900);"
    mc_html += f"animateBar('mb{i}',{bar_pct:.2f},{300+i*80});"
mc_html += "</script>"
st.markdown(mc_html, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SUBJECT CARDS
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Subjects</div>', unsafe_allow_html=True)
subj_html = '<div class="subj-grid">'
CIRC_MINI = 2 * 3.14159 * 13
for i, subj in enumerate(SUBJECTS):
    d = subject_data[subj]
    p = (d["done"] / d["total"] * 100) if d["total"] else 0
    rem_subj = d["total"] - d["done"]
    eta_days = (rem_subj / rpd) if rpd > 0 else 999
    eta_date = date.today().__add__(__import__('datetime').timedelta(days=int(eta_days)))
    eta_str  = "Done! ✓" if d["done"] >= d["total"] else eta_date.strftime("%d %b")
    off_mini = CIRC_MINI - p / 100 * CIRC_MINI
    subj_html += f"""
    <div class="sc" id="sc_{subj}" style="animation-delay:{.04+i*.07}s" onclick="selectSubject('{subj}')">
      <div class="sc-head">
        <span class="sc-name">{subj}</span>
        <span class="sc-pct mono" id="scp_{subj}">{p:.0f}%</span>
      </div>
      <div class="sc-track"><div class="sc-fill" id="scf_{subj}" style="background:{COLORS[i]}"></div></div>
      <div class="sc-foot">
        <span class="sc-hrs">{d['done']:.1f}/{d['total']:.0f}h</span>
        <svg width="32" height="32" viewBox="0 0 32 32">
          <circle cx="16" cy="16" r="13" fill="none" stroke="#141E2E" stroke-width="3.5"/>
          <circle cx="16" cy="16" r="13" fill="none" stroke="{COLORS[i]}" stroke-width="3.5" stroke-linecap="round"
            stroke-dasharray="{CIRC_MINI:.2f}" stroke-dashoffset="{CIRC_MINI:.2f}"
            style="transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1) {.4+i*.1:.2f}s"
            id="smr_{subj}"/>
        </svg>
        <span class="sc-eta" style="color:{COLORS[i]}">{eta_str}</span>
      </div>
    </div>"""

subj_html += "</div><script>"
for i, subj in enumerate(SUBJECTS):
    d = subject_data[subj]
    p = (d["done"] / d["total"] * 100) if d["total"] else 0
    off_mini = CIRC_MINI - p / 100 * CIRC_MINI
    subj_html += f"animateBar('scf_{subj}',{p:.2f},{350+i*80});"
    subj_html += f"animateRing('smr_{subj}',{p:.2f},{CIRC_MINI:.2f},{450+i*100});"

subj_html += """
function selectSubject(s){
    document.querySelectorAll('.sc').forEach(c=>c.classList.remove('active'));
    const card = document.getElementById('sc_'+s);
    if(card){ card.classList.add('active'); }
    // Signal streamlit via URL hash (handled by st.query_params in newer streamlit)
    window.location.hash = 'subj_'+s;
}
</script>"""
st.markdown(subj_html, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TASK PANEL
# ─────────────────────────────────────────
selected = st.selectbox(
    "📘 Select subject to manage tasks",
    ["— select —"] + SUBJECTS,
    label_visibility="collapsed",
)

if selected != "— select —":
    d  = subject_data[selected]
    df = d["df"]
    ws = d["ws"]
    color_idx = SUBJECTS.index(selected)
    col = COLORS[color_idx]

    tasks_html = f"""
    <div class="tasks-wrap" id="tasks-wrap">
      <div class="tasks-title">
        <span style="width:10px;height:10px;border-radius:3px;background:{col};display:inline-block"></span>
        {selected} — Tasks
      </div>"""

    for idx, row in df.iterrows():
        hrs  = convert_to_hours(row["Hours"])
        done = str(row.get("Completed", "")).strip().lower() == "true"
        tasks_html += f"""
      <div class="task-row" id="trow_{idx}" onclick="toggleTask({idx})">
        <div class="tcb{'  done' if done else ''}" id="tcb_{idx}">
          <span>✓</span>
        </div>
        <div class="t-txt{'  done' if done else ''}" id="ttx_{idx}">
          Day {row['Day']} · Part {row['Part']} · {row['Topic']}
        </div>
        <span class="t-tag">{hrs:.1f}h</span>
      </div>"""

    tasks_html += """</div>
    <script>
    function toggleTask(idx){
        const cb  = document.getElementById('tcb_'+idx);
        const tx  = document.getElementById('ttx_'+idx);
        const now = !cb.classList.contains('done');
        cb.classList.toggle('done', now);
        tx.classList.toggle('done', now);
        if(now) confettiBurst('tasks-wrap');
    }
    </script>"""
    st.markdown(tasks_html, unsafe_allow_html=True)

    st.markdown("---")
    for idx, row in df.iterrows():
        hrs  = convert_to_hours(row["Hours"])
        done = str(row.get("Completed", "")).strip().lower() == "true"
        new_val = st.checkbox(
            f"Day {row['Day']} | Part {row['Part']} | {row['Topic']} ({hrs:.1f} hrs)",
            value=done,
            key=f"cb_{selected}_{idx}",
        )
        if new_val != done and ws is not None:
            ws.update_cell(idx + 2, 5, new_val)
            ws.update_cell(idx + 2, 6, str(date.today()) if new_val else "")
            st.cache_data.clear()
            st.toast(f"{'✅ Marked done' if new_val else '↩️ Unmarked'}: {row['Topic']}")
            st.rerun()

# ─────────────────────────────────────────
#  COMPLETION RINGS
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Completion rings</div>', unsafe_allow_html=True)
R_BIG  = 28
CIRC_B = 2 * 3.14159 * R_BIG
rings_html = '<div class="rings-section"><div class="rings-row">'
for i, subj in enumerate(SUBJECTS):
    d = subject_data[subj]
    p = (d["done"] / d["total"] * 100) if d["total"] else 0
    rings_html += f"""
    <div class="rw">
      <svg width="68" height="68" viewBox="0 0 68 68">
        <circle cx="34" cy="34" r="{R_BIG}" fill="none" stroke="#141E2E" stroke-width="5.5"/>
        <circle cx="34" cy="34" r="{R_BIG}" fill="none" stroke="{COLORS[i]}" stroke-width="5.5" stroke-linecap="round"
          stroke-dasharray="{CIRC_B:.2f}" stroke-dashoffset="{CIRC_B:.2f}"
          style="transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset 1.5s cubic-bezier(.4,0,.2,1) {.5+i*.12:.2f}s"
          id="rr_{subj}"/>
        <text x="34" y="38" text-anchor="middle" font-size="11" font-weight="700" fill="{COLORS[i]}">{p:.0f}%</text>
      </svg>
      <div class="rl">{subj}</div>
    </div>"""
rings_html += "</div></div><script>"
for i, subj in enumerate(SUBJECTS):
    d = subject_data[subj]
    p = (d["done"] / d["total"] * 100) if d["total"] else 0
    rings_html += f"animateRing('rr_{subj}',{p:.2f},{CIRC_B:.2f},{550+i*110});"
rings_html += "</script>"
st.markdown(rings_html, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  POMODORO TIMER
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Pomodoro focus timer</div>', unsafe_allow_html=True)
POMO_CIRC = 2 * 3.14159 * 33
st.markdown(f"""
<div class="pomo-card">
  <div class="pomo-inner">
    <div class="pomo-ring-w">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r="33" fill="none" stroke="#141E2E" stroke-width="5"/>
        <circle cx="45" cy="45" r="33" fill="none" stroke="#378ADD" stroke-width="5" stroke-linecap="round"
          stroke-dasharray="{POMO_CIRC:.2f}" stroke-dashoffset="0"
          style="transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset .5s linear"
          id="pomo-ring"/>
      </svg>
      <div class="pomo-time mono" id="pomo-time">25:00</div>
    </div>
    <div class="pomo-info">
      <div class="pomo-session" id="pomo-session">Focus session</div>
      <div class="pomo-hint"   id="pomo-hint">25 min deep work block</div>
      <div class="pomo-btns">
        <button id="pomo-start" onclick="pomoToggle()">▶ Start</button>
        <button onclick="pomoReset()">↺ Reset</button>
      </div>
      <div class="pomo-sessions" id="pomo-sessions"></div>
    </div>
  </div>
</div>
<script>
const POMO_CIRC = {POMO_CIRC:.2f};
const POMO_CFG  = {{work:25,brk:5}};
let pomoState   = {{running:false,secs:25*60,isWork:true,sessions:0,iv:null}};
function pomoDisplay(){{
    const m=Math.floor(pomoState.secs/60),s=pomoState.secs%60;
    document.getElementById('pomo-time').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
    const total=(pomoState.isWork?POMO_CFG.work:POMO_CFG.brk)*60;
    const prog=(total-pomoState.secs)/total;
    document.getElementById('pomo-ring').style.strokeDashoffset=(POMO_CIRC*(1-prog)).toFixed(2);
    document.getElementById('pomo-session').textContent=pomoState.isWork?'Focus session':'Break time ☕';
    document.getElementById('pomo-hint').textContent=pomoState.isWork?'25 min deep work block':'5 min rest — breathe';
    const dots=document.getElementById('pomo-sessions');dots.innerHTML='';
    for(let i=0;i<4;i++){{const d=document.createElement('div');d.className='ps-dot'+(i<pomoState.sessions?' done':'');dots.appendChild(d);}}
}}
function pomoToggle(){{
    if(pomoState.running){{clearInterval(pomoState.iv);pomoState.running=false;document.getElementById('pomo-start').textContent='▶ Start';}}
    else{{
        pomoState.running=true;document.getElementById('pomo-start').textContent='⏸ Pause';
        pomoState.iv=setInterval(()=>{{
            pomoState.secs--;
            if(pomoState.secs<=0){{
                if(pomoState.isWork)pomoState.sessions=Math.min(pomoState.sessions+1,4);
                pomoState.isWork=!pomoState.isWork;
                pomoState.secs=(pomoState.isWork?POMO_CFG.work:POMO_CFG.brk)*60;
            }}
            pomoDisplay();
        }},1000);
    }}
}}
function pomoReset(){{
    clearInterval(pomoState.iv);pomoState.running=false;pomoState.secs=25*60;pomoState.isWork=true;
    document.getElementById('pomo-start').textContent='▶ Start';
    pomoDisplay();
}}
pomoDisplay();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  ACTIVITY HEATMAP
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Activity heatmap — last 14 days</div>', unsafe_allow_html=True)
heat_vals   = [0,1,2,0,3,4,2,1,0,2,3,1,4,2]   # replace with real data
heat_colors = ["#141E2E","#1a3a5c","#1e5080","#378ADD","#60ADEF"]
heat_cells  = "".join(
    f'<div class="heat-cell" style="background:{heat_colors[min(v,4)]};animation-delay:{i*.03:.2f}s" title="{v*1.5:.1f}h studied"></div>'
    for i, v in enumerate(heat_vals)
)
st.markdown(f"""
<div class="heat-section">
  <div style="font-size:12px;color:#4A5568;margin-bottom:.25rem">Each cell = one day — darker = more hours</div>
  <div class="heat-grid">{heat_cells}</div>
  <div class="heat-legend" style="margin-top:8px">
    <span>Less</span>
    {"".join(f'<div class="hl-box" style="background:{c}"></div>' for c in heat_colors)}
    <span>More</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  WEAK SUBJECT ALERTS
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Weak subject alerts</div>', unsafe_allow_html=True)
sorted_subjects = sorted(
    SUBJECTS,
    key=lambda s: (subject_data[s]["done"] / subject_data[s]["total"]) if subject_data[s]["total"] else 0
)
weak_html = '<div class="weak-section">'
for subj in sorted_subjects:
    d   = subject_data[subj]
    p   = (d["done"] / d["total"] * 100) if d["total"] else 0
    ci  = SUBJECTS.index(subj)
    icon = "🔴" if p < 30 else "🟡" if p < 60 else "🟢"
    weak_html += f"""
  <div class="weak-row">
    <span>{icon}</span>
    <span class="weak-name">{subj}</span>
    <div class="weak-bar-wrap"><div class="weak-bar-fill" id="wb_{subj}" style="background:{COLORS[ci]};width:0%"></div></div>
    <span class="weak-pct">{p:.0f}%</span>
  </div>"""
weak_html += "</div><script>"
for i, subj in enumerate(sorted_subjects):
    d = subject_data[subj]
    p = (d["done"] / d["total"] * 100) if d["total"] else 0
    weak_html += f"animateBar('wb_{subj}',{p:.2f},{300+i*90});"
weak_html += "</script>"
st.markdown(weak_html, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SUBJECT ETA TABLE
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">Subject ETA — estimated finish dates</div>', unsafe_allow_html=True)
eta_html = '<div class="eta-section">'
for i, subj in enumerate(SUBJECTS):
    d        = subject_data[subj]
    rem_subj = d["total"] - d["done"]
    if d["done"] >= d["total"]:
        eta_str   = "Completed ✓"
        badge_col = "#1D9E75"
        badge_bg  = "#0d2a1e"
    elif rpd > 0:
        eta_days = rem_subj / rpd
        eta_dt   = date.today().__add__(__import__('datetime').timedelta(days=int(eta_days)))
        eta_str  = eta_dt.strftime("%d %b %Y")
        badge_col = COLORS[i]
        badge_bg  = "#0D1422"
    else:
        eta_str   = "No pace set"
        badge_col = "#4A5568"
        badge_bg  = "#0D1422"
    p = (d["done"] / d["total"] * 100) if d["total"] else 0
    eta_html += f"""
  <div class="eta-row">
    <span class="eta-subj" style="color:{COLORS[i]}">{subj}</span>
    <span class="eta-date">{eta_str}</span>
    <span class="eta-badge" style="color:{badge_col};background:{badge_bg};border:1px solid {badge_col}33">{p:.0f}% done</span>
  </div>"""
eta_html += "</div>"
st.markdown(eta_html, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PRESSURE BANNER
# ─────────────────────────────────────────
pressure_icon = "😌" if rpd < 4 else "⚠️" if rpd < 8 else "🔥"
pressure_msg  = (
    f"Low pressure — {rpd:.1f} hrs/day needed. You're well on track."
    if rpd < 4 else
    f"Medium pressure — {rpd:.1f} hrs/day needed. Stay consistent every day."
    if rpd < 8 else
    f"High pressure — {rpd:.1f} hrs/day needed. Push hard every single day."
)
st.markdown(f"""
<div class="pressure-row" style="border-color:{pressure_color}33">
  <span style="font-size:18px">{pressure_icon}</span>
  <span>{pressure_msg}</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  MOTIVATION
# ─────────────────────────────────────────
if overall_pct >= 75:
    motiv_icon, motiv_text = "🏆", "You're very close to CA Final victory! Keep it going."
elif overall_pct >= 50:
    motiv_icon, motiv_text = "💪", "Excellent work. You're ahead of many students."
elif overall_pct >= 25:
    motiv_icon, motiv_text = "🔥", "Good progress. Keep the momentum going."
else:
    motiv_icon, motiv_text = "🚀", "Start pushing harder. Consistency is key."

st.markdown(f"""
<div class="motiv">
  <span style="font-size:18px">{motiv_icon}</span>
  <span>{motiv_text}</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────
st.markdown("""
<div style="text-align:center;font-size:11px;color:#1A2535;margin-top:2rem;padding-top:1rem;border-top:1px solid #0f1820">
  ⚡ CA Final Pro Dashboard · Built with Streamlit + Google Sheets cloud sync
</div>
""", unsafe_allow_html=True)
