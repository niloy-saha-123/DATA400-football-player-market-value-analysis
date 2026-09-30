"""Small HTML/CSS helpers for the Streamlit data story (app.py)."""
from html import escape

import streamlit as st

ACCENT = "#1F4E79"

CSS = f"""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {{display: none;}}
header[data-testid="stHeader"] {{background: transparent; height: 0;}}
[data-testid="stToolbar"] {{display: none;}}
.block-container {{max-width: 1120px; padding-top: 1.5rem; padding-bottom: 5rem;}}
html, body, [class*="css"] {{font-size: 17px;}}
p, li {{line-height: 1.6;}}

.topnav {{position: sticky; top: 0; z-index: 99; background: rgba(255,255,255,0.95); backdrop-filter: blur(4px);
  border-bottom: 1px solid #e6e9ef; padding: 0.55rem 0; margin-bottom: 1rem; font-size: 0.85rem;}}
.topnav a {{color: #5b6472; text-decoration: none; margin-right: 1.4rem; letter-spacing: 0.02em;}}
.topnav a:hover {{color: {ACCENT};}}

.hero {{padding: 3.5rem 0 1.5rem 0;}}
.hero h1 {{font-size: 3.1rem; line-height: 1.12; font-weight: 800; color: #14213d; margin: 0 0 1.6rem 0;}}
.eyebrow {{text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.78rem; font-weight: 700; color: {ACCENT}; margin-bottom: 0.4rem;}}
.rq {{font-size: 1.35rem; line-height: 1.5; color: #1f2a3a; border-left: 4px solid {ACCENT}; padding-left: 1.1rem; margin: 0.4rem 0 1.4rem 0;}}
.lead {{font-size: 1.08rem; color: #3d4654; max-width: 820px;}}
.disclaimer {{background: #f3f6fa; border-radius: 10px; padding: 0.9rem 1.2rem; margin: 1.2rem 0 2rem 0; color: #1f2a3a; font-weight: 600;}}

.stats {{display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin: 0.5rem 0 1rem 0;}}
.stat {{background: #fff; border: 1px solid #e6e9ef; border-radius: 14px; padding: 1.3rem 1.2rem;}}
.stat .num {{font-size: 2.2rem; font-weight: 800; color: #14213d; line-height: 1.1;}}
.stat .lbl {{color: #5b6472; font-size: 0.92rem; margin-top: 0.35rem;}}
.meta {{color: #5b6472; font-size: 0.95rem;}}

.section {{padding-top: 3.5rem; margin-top: 2.5rem; border-top: 1px solid #eceff4;}}
.section h2 {{font-size: 2.05rem; font-weight: 800; color: #14213d; margin: 0 0 0.6rem 0; line-height: 1.2;}}
.question {{font-size: 1.15rem; color: #5b6472; font-style: italic; margin-bottom: 1.2rem;}}

.card {{background: #fff; border: 1px solid #e6e9ef; border-radius: 14px; padding: 1.2rem 1.3rem; height: 100%;}}
.card h4 {{margin: 0 0 0.5rem 0; font-size: 1.05rem; color: #14213d;}}
.card p {{margin: 0.3rem 0; font-size: 0.97rem; color: #3d4654;}}
.card p.big {{font-size: 1.7rem; font-weight: 800; color: #14213d; margin: 0.6rem 0 0 0;}}
.cards {{display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin: 1rem 0;}}
.kicker {{font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; color: {ACCENT};}}

.callout {{border-radius: 12px; padding: 1rem 1.25rem; margin: 1rem 0;}}
.callout .tag {{font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 800; margin-bottom: 0.3rem;}}
.callout p {{margin: 0.2rem 0;}}
.c-shows {{background: #eef4fb; border-left: 4px solid {ACCENT};}}
.c-shows .tag {{color: {ACCENT};}}
.c-caution {{background: #fff7ea; border-left: 4px solid #d98b00;}}
.c-caution .tag {{color: #a86a00;}}
.c-key {{background: #14213d; color: #fff;}}
.c-key .tag {{color: #9fc3ea;}}
.c-key p {{color: #fff;}}

.pipeline {{display: flex; flex-wrap: wrap; align-items: stretch; gap: 0.4rem; margin: 1.2rem 0;}}
.step {{flex: 1 1 120px; background: #f3f6fa; border-radius: 10px; padding: 0.8rem 0.7rem; text-align: center;}}
.step b {{display: block; color: #14213d; font-size: 0.95rem;}}
.step span {{font-size: 0.8rem; color: #5b6472;}}
.arrow {{align-self: center; color: {ACCENT}; font-weight: 800;}}
.step.final {{background: {ACCENT};}}
.step.final b, .step.final span {{color: #fff;}}

.rowdemo {{display: grid; grid-template-columns: 1.2fr 0.8fr 0.5fr 0.8fr 1.3fr 0.8fr 0.7fr 0.8fr 0.8fr 0.9fr 1.1fr; border: 1px solid #e6e9ef; border-radius: 10px; overflow: hidden; font-size: 0.85rem;}}
.rowdemo > div {{padding: 0.5rem 0.6rem; border-right: 1px solid #eceff4; min-width: 0; overflow-wrap: break-word;}}
.rowdemo > div:last-child {{border-right: none;}}
.rowdemo .h {{color: #5b6472; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;}}

.finding {{background: #fff; border: 1px solid #e6e9ef; border-top: 4px solid {ACCENT}; border-radius: 12px; padding: 1.1rem 1.2rem;}}
.finding .n {{font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; color: {ACCENT};}}
.finding h4 {{margin: 0.2rem 0 0.4rem 0; font-size: 1.1rem; color: #14213d;}}
.finding .s {{font-size: 1.5rem; font-weight: 800; color: #14213d; margin-top: 0.5rem;}}
.finding .sl {{font-size: 0.8rem; color: #5b6472;}}
.no {{background: #fff5f3; border: 1px solid #f3d3cc; border-radius: 12px; padding: 1rem 1.2rem;}}
.no b {{color: #9b2c1f;}}
@media (max-width: 800px) {{ .rowdemo {{grid-template-columns: repeat(3, 1fr);}} .hero h1 {{font-size: 2.2rem;}} }}
.footer {{margin-top: 4rem; color: #8a93a1; font-size: 0.85rem; text-align: center;}}
</style>
"""


def css():
    st.markdown(CSS, unsafe_allow_html=True)


def html(s):
    st.markdown(s, unsafe_allow_html=True)


def section(anchor, title, question=None):
    q = f'<div class="question">{question}</div>' if question else ""
    html(f'<div class="section" id="{anchor}"><h2>{title}</h2>{q}</div>')


def callout(kind, tag, body):
    """kind: shows | caution | key. body may contain simple HTML."""
    html(f'<div class="callout c-{kind}"><div class="tag">{escape(tag)}</div>{body}</div>')


def cards(items, cls="card", min_px=240):
    """items: list of (kicker, title, body_html)."""
    inner = "".join(
        f'<div class="{cls}">' + (f'<div class="kicker">{k}</div>' if k else "") + f"<h4>{t}</h4>{b}</div>"
        for k, t, b in items)
    html(f'<div class="cards" style="grid-template-columns: repeat(auto-fit, minmax({min_px}px, 1fr))">{inner}</div>')
