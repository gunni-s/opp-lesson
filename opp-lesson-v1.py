# app.py
# Operator Mini-Quiz — multi-try buttons per card, single feedback, 3-col expression

import random
import streamlit as st

st.set_page_config(page_title="Operator Mini-Quiz", page_icon="📘", layout="centered")

# ------------------ Styles: gradient boxes + dark/light safe hint ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

:root{
  --op-font: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
  --brand-grad: linear-gradient(135deg, #6366f1 0%, #22c55e 100%);
}

.block-container{ padding-top:1rem; }

/* Hero */
.app-hero{
  background: var(--brand-grad);
  border-radius:16px; padding:18px 16px; color:#fff; margin-bottom:12px;
}
.app-hero h1{ margin:0; font-size:1.6rem; line-height:1.2; }
.app-hero p{ margin:6px 0 0 0; font-size:0.95rem; color:#f0fdf4; }
.app-hero code{
  font-family:var(--op-font);
  font-variant-ligatures:none;
  -webkit-font-feature-settings:"liga"0,"clig"0,"calt"0;
  font-feature-settings:"liga"0,"clig"0,"calt"0;
}

/* Expression (3 columns, 1 row) — now new gradient + white text */
.expr-row{
  display:grid; grid-template-columns:1fr 0.35fr 1fr; gap:10px;
  margin:8px 0 6px 0; align-items:stretch;
}
.box{
  border:1px solid rgba(255,255,255,.22);
  /* Nicer gradient: teal to blue to violet for a fresh, modern look */
  background: linear-gradient(135deg, #f9a8d4 0%, #fcd34d 50%, #a5b4fc 100%);
  border-radius:14px; padding:16px 12px; text-align:center;
  font-family:var(--op-font); font-size:1.08rem;
  color:#fff; text-shadow:0 1px 0 rgba(0,0,0,.28);
  font-variant-ligatures:none;
  -webkit-font-feature-settings:"liga"0,"clig"0,"calt"0;
  font-feature-settings:"liga"0,"clig"0,"calt"0;
  white-space:nowrap;
}
.box.mid{ /* keep same gradient for consistency */ }

@media (prefers-color-scheme: light){
  .box{ border-color: rgba(0,0,0,.08); text-shadow:none; }
}

/* Buttons */
.stButton>button{
  padding:.9rem 1rem; font-size:1.05rem; border-radius:12px;
  background: linear-gradient(135deg,#f3f4f6 0%,#e5e7eb 100%);
  border:1px solid #d1d5db; color:#111827; transition:all .2s ease;
  font-family:var(--op-font);
  font-variant-ligatures:none;
  -webkit-font-feature-settings:"liga"0,"clig"0,"calt"0;
  font-feature-settings:"liga"0,"clig"0,"calt"0;
}
.stButton>button:hover{ transform:translateY(-1px); box-shadow:0 8px 16px -6px rgba(0,0,0,.15); }

.progress{ text-align:right; color:#6b7280; font-size:.92rem; }

/* Feedback */
.feedback{
  border-radius:12px; padding:12px 14px; margin-top:8px;
  font-family:var(--op-font);
  font-variant-ligatures:none;
  -webkit-font-feature-settings:"liga"0,"clig"0,"calt"0;
  font-feature-settings:"liga"0,"clig"0,"calt"0;
}
.ok{   background:#ecfdf5; border:1px solid #10b98133; }
.nope{ background:#fef2f2; border:1px solid #ef444433; }

/* Hint chip — auto-contrast for dark/light */
.hint-chip{
  display:inline-block; padding:6px 10px; border-radius:999px; font-size:.9rem;
  border:1px solid;
}
@media (prefers-color-scheme: dark){
  .hint-chip{ background:rgba(255,255,255,.08); color:#e5e7eb; border-color:rgba(255,255,255,.18); }
}
@media (prefers-color-scheme: light){
  .hint-chip{ background:rgba(0,0,0,.05); color:#374151; border-color:rgba(0,0,0,.08); }
}
</style>
""", unsafe_allow_html=True)

# ------------------ Questions (customize messages) ------------------
QUESTIONS = [
    {
        "lhs": "putti",
        "rhs": "best doggo ever",
        "correct": "==",
        # Only ONE message will show depending on correctness:
        "correct_msg": "✅ putti is indeed 'equal to' best doggo ever.",
        "incorrect_msg": "❌ ummm try again, isn't putti the best doggo ever?",
    },
    {
        "lhs": "gunni",
        "rhs": "kinda funny",
        "correct": ">=",
        "correct_msg": "✅ gunni is definitely 'greater than or equal to' kinda funny",
        "incorrect_msg": "❌ cmonnn gunni is kinda funny innit",
    },
    {
        "lhs": "hvolsvöllur",
        "rhs": "Hella",
        "correct": "<=",
        "correct_msg": "✅ hvolsvöllur is 'less than or equal to' hella. tbh, hvolsvöllur is less than hella but for this teaching exercise, it had to be done this way",
        "incorrect_msg": "❌ neiii, hvolsvöllur is definitely less than hella",
    },
]

OPS = ["==", "<=", ">="]
DISPLAY = {"==": "==", "<=": "<\u200B=", ">=": ">\u200B="}  # prevents ligatures

# ------------------ State ------------------
if "idx" not in st.session_state: st.session_state.idx = 0
if "score" not in st.session_state: st.session_state.score = 0
if "attempted" not in st.session_state: st.session_state.attempted = False
if "selected" not in st.session_state: st.session_state.selected = None
if "finished" not in st.session_state: st.session_state.finished = False

def reset_quiz():
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.attempted = False
    st.session_state.selected = None
    st.session_state.finished = False

def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ------------------ Header ------------------
st.markdown(
    """
    <div class="app-hero">
      <h1>Operator Mini-Quiz</h1>
      <p>Pick the sign that makes the statement <b>True</b>: <code>==</code> · <code>&lt;=</code> · <code>&gt;=</code></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------ Finish screen ------------------
if st.session_state.finished:
    st.subheader("Done!")
    st.write(f"Score: **{st.session_state.score} / {len(QUESTIONS)}**")
    if st.button("Play again", type="primary", use_container_width=True):
        reset_quiz(); st.rerun()
    st.stop()

# ------------------ Current question ------------------
q = QUESTIONS[st.session_state.idx]

# Progress
st.markdown(f"<div class='progress'>{st.session_state.idx + 1} / {len(QUESTIONS)}</div>", unsafe_allow_html=True)
st.progress(int((st.session_state.idx / len(QUESTIONS)) * 100))

# Expression row (now gradient boxes w/ white text)
st.markdown(
    f"""
    <div class="expr-row">
      <div class="box">{html_escape(q['lhs'])}</div>
      <div class="box mid">?</div>
      <div class="box">{html_escape(q['rhs'])}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)


# Hint chip (readable in dark + light)
st.markdown("<div class='hint-chip'>Try any option. You can change your mind before moving on.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
# Operator buttons (multi-try; never disabled)
clicked = None
for op in OPS:
    if st.button(DISPLAY[op], key=f"btn_{st.session_state.idx}_{op}", use_container_width=True):
        clicked = op

if clicked is not None:
    st.session_state.selected = clicked
    st.session_state.attempted = True

# Single feedback + Next
if st.session_state.attempted and st.session_state.selected is not None:
    is_correct = (st.session_state.selected == q["correct"])
    st.markdown(
        f"<div class='feedback {'ok' if is_correct else 'nope'}'>{q['correct_msg'] if is_correct else q['incorrect_msg']}</div>",
        unsafe_allow_html=True,
    )

next_label = "Finish" if st.session_state.idx == len(QUESTIONS) - 1 else "Next →"
next_disabled = not st.session_state.attempted

def _advance():
    if st.session_state.selected == q["correct"]:
        st.session_state.score += 1
    if st.session_state.idx == len(QUESTIONS) - 1:
        st.session_state.finished = True
    else:
        st.session_state.idx += 1
        st.session_state.attempted = False
        st.session_state.selected = None
    st.rerun()

st.button(next_label, key=f"next_{st.session_state.idx}", type="primary",
          use_container_width=True, disabled=next_disabled, on_click=_advance)
