import hashlib
import html
import re
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from backend import Backend


st.set_page_config(
    page_title="Generate Code with AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

backend = Backend()


# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULTS = {
    "generated_code": "",
    "generated_language": "",
    "selected_language": "Python",   # chosen from the sidebar chips
    "theme_mode": "light" if st.query_params.get("theme") == "light" else "dark",
    "awaiting_input": False,   # Run clicked, waiting for the user to type input
    "run_done": False,         # a run has finished
    "run_success": None,
    "run_output": "",
    "run_inputs": [],          # [(label, value), ...] shown in the terminal
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Source+Code+Pro:wght@400;500&display=swap');

html,body,[class*="css"]{
    font-family:'Poppins',sans-serif;
}

#MainMenu,footer,[data-testid="stSidebarNav"]{
    visibility:hidden;
}

header{
    background:transparent!important;
}

/* ===== PAGE BACKGROUND (dark purple) ===== */

.stApp{
    background:
        radial-gradient(circle at 15% 10%, rgba(88,28,135,.55), transparent 45%),
        radial-gradient(circle at 90% 95%, rgba(37,19,200,.55), transparent 45%),
        radial-gradient(circle at 70% 40%, rgba(131,24,67,.35), transparent 50%),
        #07030F !important;
    color:#FFFFFF !important;
}

/* ===== MAIN CARD ===== */

.main .block-container{
    max-width:1400px;
    margin:1.5rem auto;
    padding:2.2rem 2.5rem;
    background:#0F0A1F;
    border:1px solid rgba(139,92,246,.35);
    border-radius:28px;
}

h1,h2,h3,h4,p,label,
[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p{
    color:#FFFFFF;
}

.grad-title{
    background:linear-gradient(90deg,#EC4899,#F43F5E);
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
    color:transparent;
}

/* ===== BUTTONS ===== */

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] button{
    width:100%;
    height:52px;
    border:none !important;
    border-radius:999px;
    background:linear-gradient(90deg,#DC3555,#EC4899) !important;
    color:#FFFFFF !important;
    font-size:16px;
    font-weight:600;
    box-shadow:none !important;
    transition:.25s;
}

.stButton > button[kind="primary"] p,
.stButton > button[data-testid="stBaseButton-primary"] p,
[data-testid="stFormSubmitButton"] button p{
    color:#FFFFFF !important;
    font-weight:600;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover{
    filter:brightness(1.12);
    transform:translateY(-1px);
}

.stDownloadButton > button,
.stButton > button[kind="secondary"]{
    width:100%;
    height:52px;
    border-radius:999px;
    background:transparent !important;
    border:1px solid rgba(139,92,246,.55) !important;
    color:#FFFFFF !important;
    font-size:16px;
    font-weight:600;
    box-shadow:none !important;
    transition:.25s;
}

.stDownloadButton > button p,
.stButton > button[kind="secondary"] p{
    color:#FFFFFF !important;
    font-weight:600;
}

.stDownloadButton > button:hover,
.stButton > button[kind="secondary"]:hover{
    border:1px solid #EC4899 !important;
    background:rgba(236,72,153,.08) !important;
}

.stButton > button:disabled,
.stDownloadButton > button:disabled{
    opacity:.4 !important;
    cursor:not-allowed;
    transform:none !important;
    filter:none !important;
}

/* ===== PROMPT BOX + DROPDOWN: white bg, black text, black cursor ===== */

.stTextArea textarea,
.stTextInput input{
    background:#FFFFFF !important;
    color:#000000 !important;
    caret-color:#000000 !important;
    border:1px solid #D1D5DB !important;
    border-radius:18px !important;
}

div[data-baseweb="textarea"],
div[data-baseweb="input"],
div[data-baseweb="base-input"]{
    background:#FFFFFF !important;
    border-radius:18px !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder{
    color:#6B7280 !important;
    opacity:1 !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus{
    border:1px solid #EC4899 !important;
    box-shadow:0 0 0 1px #EC4899 !important;
}

div[data-baseweb="select"]{
    width:220px !important;
}

div[data-baseweb="select"] > div{
    min-height:45px !important;
    background:#FFFFFF !important;
    border:1px solid #D1D5DB !important;
    border-radius:999px !important;
    cursor:pointer !important;
}

div[data-baseweb="select"] *{
    color:#000000 !important;
}

div[data-baseweb="select"] svg{
    fill:#000000 !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="popover"] li *{
    color:#000000 !important;
}

/* ===== TWO SEPARATE BOXES: white inside, pink chip-colour border ===== */

/* outer wrapper is invisible now, only the two boxes show */
.st-key-workbox{
    background:transparent;
    border:none;
    padding:0 !important;
    margin-top:1.2rem;
}

/* gap between the two boxes */
.st-key-workbox [data-testid="stHorizontalBlock"]{
    gap:28px !important;
}

/* each box: white inside, border = same pink gradient as the sidebar chips */
.st-key-workbox [data-testid="stColumn"]:has(.cell-title),
.st-key-workbox [data-testid="column"]:has(.cell-title){
    border:2px solid transparent;
    border-radius:18px;
    padding:14px 18px;
    min-width:0;
    box-sizing:border-box;
    background:
        linear-gradient(var(--box-fill, #FFFFFF), var(--box-fill, #FFFFFF)) padding-box,
        linear-gradient(135deg, #DC3555, #EC4899) border-box;
}

/* the small prompt / input columns inside the output box stay tight */
.st-key-out_pane [data-testid="stHorizontalBlock"]{
    gap:1rem !important;
}

.cell-title{
    font-family:'Poppins',sans-serif;
    font-size:15px;
    font-weight:600;
    color:#111827;
    margin-bottom:8px;
}

.st-key-code_pane,
.st-key-out_pane{
    min-height:500px;
    max-height:500px;
    overflow:auto;
}

.st-key-code_pane::-webkit-scrollbar,
.st-key-out_pane::-webkit-scrollbar{
    width:10px;
    height:10px;
}

.st-key-code_pane::-webkit-scrollbar-thumb,
.st-key-out_pane::-webkit-scrollbar-thumb{
    background:#C4B5FD;
    border-radius:10px;
}

/* ----- generated code cell: built-in code block (has the copy icon) ----- */

.st-key-code_pane [data-testid="stCode"],
.st-key-code_pane [data-testid="stCodeBlock"]{
    background:#F8FAFC !important;
    border:1px solid #E5E7EB;
    border-radius:12px;
}

.st-key-code_pane pre,
.st-key-code_pane code{
    font-family:'Source Code Pro',monospace !important;
    font-size:14px !important;
}

/* copy icon: always visible and dark */
.st-key-code_pane [data-testid="stCode"] button,
.st-key-code_pane [data-testid="stCodeBlock"] button,
.st-key-code_pane [data-testid="stCodeCopyButton"]{
    opacity:1 !important;
    visibility:visible !important;
    color:#374151 !important;
}

.empty-note{
    color:#6B7280;
    font-family:'Source Code Pro',monospace;
    font-size:14px;
    padding:6px 2px;
}

/* ----- output cell: terminal text on white, input typed inside it ----- */

.st-key-out_pane [data-testid="stForm"]{
    border:none !important;
    padding:0 !important;
    background:transparent !important;
}

.term{
    margin:0;
    font-family:'Source Code Pro',monospace;
    font-size:14px;
    line-height:1.6;
    color:#111827;
    white-space:pre-wrap;
    word-break:break-word;
}

.term.err{
    color:#DC2626;
}

.term-prompt{
    font-family:'Source Code Pro',monospace;
    font-size:14px;
    color:#111827;
    line-height:2.3;
}

.status{
    font-family:'Source Code Pro',monospace;
    font-size:12px;
    margin-bottom:10px;
}

.status.ok{ color:#16A34A; }
.status.bad{ color:#DC2626; }

/* inputs inside the output cell: no box, just a line with a black cursor */

.st-key-out_pane .stTextInput input,
.st-key-out_pane .stTextArea textarea{
    background:transparent !important;
    color:#000000 !important;
    caret-color:#000000 !important;
    border:none !important;
    border-bottom:1px solid #9CA3AF !important;
    border-radius:0 !important;
    font-family:'Source Code Pro',monospace !important;
    font-size:14px !important;
    box-shadow:none !important;
}

.st-key-out_pane div[data-baseweb="input"],
.st-key-out_pane div[data-baseweb="base-input"],
.st-key-out_pane div[data-baseweb="textarea"]{
    background:transparent !important;
    border:none !important;
    border-radius:0 !important;
}

.st-key-out_pane .stTextInput input:focus,
.st-key-out_pane .stTextArea textarea:focus{
    border-bottom:1px solid #EC4899 !important;
    box-shadow:none !important;
}

.st-key-out_pane [data-testid="stFormSubmitButton"] button{
    height:38px;
    font-size:14px;
}

/* ===== SIDEBAR ===== */

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div{
    background:#0B0716 !important;
    backdrop-filter:none !important;
    border-right:1px solid rgba(139,92,246,.25);
}

section[data-testid="stSidebar"] *{
    color:#FFFFFF !important;
}

section[data-testid="stSidebar"] p{
    color:#CBD5E1 !important;
}

@property --angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}

/* Logo card: line travelling around the border */

section[data-testid="stSidebar"] .logo-card{
    --angle: 0deg;
    border:2px solid transparent;
    border-radius:22px;
    padding:28px;
    margin-bottom:25px;
    text-align:center;
    box-shadow:none;
    background:
        linear-gradient(var(--chip-fill, #0F0A1F), var(--chip-fill, #0F0A1F)) padding-box,
        conic-gradient(
            from var(--angle),
            rgba(139,92,246,.25) 0deg,
            rgba(139,92,246,.25) 250deg,
            #DC3555 310deg,
            #EC4899 360deg
        ) border-box;
    animation:logo-border-spin 7s linear infinite;
}

@keyframes logo-border-spin{
    from{ --angle:0deg; }
    to{ --angle:360deg; }
}

/* Language chips = clickable buttons.
   Not selected: animated line travelling around the border (alternate direction).
   Selected: filled pink gradient (same as the Generate / Run buttons). */

.st-key-lang_list button[kind="secondary"],
.st-key-lang_list button[data-testid="stBaseButton-secondary"],
.st-key-lang_list button[kind="secondary"]:hover,
.st-key-lang_list button[kind="secondary"]:focus,
.st-key-lang_list button[kind="secondary"]:active,
.st-key-lang_list button[data-testid="stBaseButton-secondary"]:hover,
.st-key-lang_list button[data-testid="stBaseButton-secondary"]:focus,
.st-key-lang_list button[data-testid="stBaseButton-secondary"]:active{
    width:100%;
    height:50px;
    border:2px solid transparent !important;
    border-radius:999px !important;
    color:#FFFFFF !important;
    font-size:16px;
    font-weight:600;
    box-shadow:none !important;
    outline:none !important;
    transform:none !important;
    background:
        linear-gradient(var(--chip-fill, #0F0A1F), var(--chip-fill, #0F0A1F)) padding-box,
        conic-gradient(
            from var(--angle),
            rgba(139,92,246,.25) 0deg,
            rgba(139,92,246,.25) 250deg,
            #DC3555 310deg,
            #EC4899 360deg
        ) border-box !important;
}

[class*="st-key-lang_cw_"] button{
    animation:chip-cw 7s linear infinite;
}

[class*="st-key-lang_ccw_"] button{
    animation:chip-ccw 7s linear infinite;
}

.st-key-lang_list button[kind="primary"],
.st-key-lang_list button[data-testid="stBaseButton-primary"]{
    height:50px;
    border-radius:999px !important;
    font-size:16px;
}

.st-key-lang_list button p{
    font-size:16px;
    font-weight:600;
}

@keyframes chip-cw{
    from{ --angle:0deg; }
    to{ --angle:360deg; }
}

@keyframes chip-ccw{
    from{ --angle:360deg; }
    to{ --angle:0deg; }
}

/* ===== SIDEBAR HIDE / SHOW BUTTON: white ===== */

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button{
    display:inline-flex !important;
    visibility:visible !important;
    opacity:1 !important;
}

[data-testid="stSidebarCollapseButton"] *,
[data-testid="stExpandSidebarButton"] *,
[data-testid="stSidebarCollapsedControl"] *,
[data-testid="collapsedControl"] *{
    color:#FFFFFF !important;
    fill:#FFFFFF !important;
    stroke:#FFFFFF !important;
    opacity:1 !important;
}

/* Hide only the Deploy button */
[data-testid="stAppDeployButton"],
.stAppDeployButton{
    display:none !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# THEME (dark / light) - toggle button is in the title row
# ==========================================================

def toggle_theme():

    new_mode = "light" if st.session_state.theme_mode == "dark" else "dark"

    st.session_state.theme_mode = new_mode

    # keep the choice after a browser refresh
    st.query_params["theme"] = new_mode


IS_DARK = st.session_state.theme_mode == "dark"


THEME_COMMON_CSS = """
/* ----- inside fill (changes with the mode) + pink border (same in both modes) ----- */

.stApp .st-key-workbox [data-testid="stColumn"]:has(.cell-title),
.stApp .st-key-workbox [data-testid="column"]:has(.cell-title){
    background:var(--fill), linear-gradient(135deg, #DC3555, #EC4899) border-box;
}

/* prompt box: same pink border as the Generated Code / Output boxes */
.stApp .st-key-prompt_text div[data-baseweb="textarea"]{
    border:2px solid transparent !important;
    border-radius:18px !important;
    background:var(--fill), linear-gradient(135deg, #DC3555, #EC4899) border-box !important;
}

.stApp .st-key-prompt_text div[data-baseweb="base-input"]{
    background:transparent !important;
}

.stApp .st-key-prompt_text textarea,
.stApp .st-key-prompt_text textarea:focus{
    background:transparent !important;
    border:none !important;
    box-shadow:none !important;
}

/* ----- theme toggle button (round, top right) ----- */

.st-key-theme_toggle{
    display:flex;
    justify-content:flex-end;
}

.st-key-theme_toggle .stButton{
    width:auto;
}

.st-key-theme_toggle button[kind="secondary"],
.st-key-theme_toggle button[data-testid="stBaseButton-secondary"],
.st-key-theme_toggle button[kind="secondary"]:hover,
.st-key-theme_toggle button[kind="secondary"]:focus,
.st-key-theme_toggle button[kind="secondary"]:active{
    width:54px !important;
    height:54px !important;
    min-height:54px !important;
    padding:0 !important;
    border-radius:14px !important;
    border:1px solid var(--toggle-border) !important;
    background-color:var(--toggle-bg) !important;
    background-image:var(--toggle-icon) !important;
    background-repeat:no-repeat !important;
    background-position:center !important;
    background-size:30px 30px !important;
    box-shadow:none !important;
    transform:none !important;
}

/* the icon is drawn as a background image, so hide the label text */
.st-key-theme_toggle button p{
    font-size:0 !important;
    line-height:0 !important;
    color:transparent !important;
}

/* ----- tooltips ("Copy" / "Copied!" on the code copy button) -----
   They open outside the page, so the page text colour leaked in and left
   white text on a white box. Dark box + white text is readable in both modes. */

[data-testid="stTooltipContent"],
div[data-baseweb="tooltip"],
div[role="tooltip"],
div[data-baseweb="popover"]:has([data-testid="stTooltipContent"]),
div[data-baseweb="popover"]:has([data-testid="stTooltipContent"]) > div,
div[data-baseweb="popover"]:has([data-testid="stTooltipContent"]) > div > div{
    background:#111827 !important;
    background-color:#111827 !important;
    border-radius:8px !important;
    box-shadow:none !important;
}

div[data-baseweb="popover"]:has([data-testid="stTooltipContent"]){
    border:1px solid #EC4899 !important;
}

[data-testid="stTooltipContent"],
[data-testid="stTooltipContent"] *,
div[data-baseweb="tooltip"],
div[data-baseweb="tooltip"] *,
div[role="tooltip"],
div[role="tooltip"] *,
div[data-baseweb="popover"]:has([data-testid="stTooltipContent"]) *{
    color:#FFFFFF !important;
    font-size:13px !important;
}

/* ----- responsive: tablets and phones ----- */

@media (max-width: 900px){
    .st-key-workbox [data-testid="stHorizontalBlock"]{
        gap:16px !important;
    }
}

@media (max-width: 640px){
    .stApp .main .block-container,
    .stApp [data-testid="stMainBlockContainer"]{
        margin:0 !important;
        padding:3.2rem 12px 1.2rem 12px !important;
        max-width:100% !important;
        border-radius:0 !important;
        border-left:none !important;
        border-right:none !important;
        box-sizing:border-box !important;
    }
    .stApp [data-testid="stAppViewContainer"],
    .stApp .main{
        overflow-x:hidden !important;
    }
    /* ===== PHONE: ONE box. Top = 3 buttons, below = code OR output ===== */

    /* top part of the box: the Generate | Run | Download row */
    .stApp [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]){
        border:2px solid transparent !important;
        border-bottom:none !important;
        border-radius:18px 18px 0 0 !important;
        padding:12px 12px 12px 12px !important;
        box-sizing:border-box !important;
        background:var(--fill), linear-gradient(135deg,#DC3555,#EC4899) border-box !important;
    }

    /* bottom part of the box: joins the row above (no gap, no top corners) */
    .stApp .st-key-workbox{
        margin-top:-1rem !important;
        padding:12px !important;
        box-sizing:border-box !important;
        border:2px solid transparent !important;
        border-top:1px solid rgba(236,72,153,.7) !important;
        border-radius:0 0 18px 18px !important;
        background:var(--fill), linear-gradient(135deg,#DC3555,#EC4899) border-box !important;
    }

    /* the two cells lose their own boxes (the one big box is drawn above) */
    .stApp .st-key-workbox [data-testid="stHorizontalBlock"]:has(.st-key-code_pane){
        display:block !important;
    }
    .stApp .st-key-workbox [data-testid="stColumn"]:has(.cell-title),
    .stApp .st-key-workbox [data-testid="column"]:has(.cell-title){
        width:100% !important;
        flex:none !important;
        border:none !important;
        border-radius:0 !important;
        padding:0 !important;
        background:transparent !important;
    }

    /* titles are not needed, the buttons say what is shown */
    .stApp .st-key-workbox .cell-title{
        display:none !important;
    }

    /* the hidden marker takes no space */
    .stApp .st-key-workbox [data-testid="stElementContainer"]:has(.view-marker){
        display:none !important;
    }

    /* show only one view: code first, output after Run */
    .stApp .st-key-workbox:has(.show-code) [data-testid="stColumn"]:has(.st-key-out_pane),
    .stApp .st-key-workbox:has(.show-out) [data-testid="stColumn"]:has(.st-key-code_pane){
        display:none !important;
    }

    .st-key-code_pane,
    .st-key-out_pane{
        min-height:300px !important;
        max-height:480px !important;
    }
    .st-key-theme_toggle button[kind="secondary"],
    .st-key-theme_toggle button[data-testid="stBaseButton-secondary"]{
        width:44px !important;
        height:44px !important;
        min-height:44px !important;
        background-size:24px 24px !important;
    }
    h1{
        font-size:1.2rem !important;
        line-height:1.25 !important;
    }

    /* row 1: title on the left, dark-mode button on the right */
    .stApp [data-testid="stHorizontalBlock"]:has(.st-key-theme_toggle){
        flex-wrap:nowrap !important;
        gap:8px !important;
        align-items:center !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has(.st-key-theme_toggle) > [data-testid="stColumn"]{
        min-width:0 !important;
        width:auto !important;
        flex:1 1 auto !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has(.st-key-theme_toggle) > [data-testid="stColumn"]:has(.st-key-theme_toggle){
        flex:0 0 auto !important;
    }

    /* row 3: Generate | Run | Download side by side */
    .stApp [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]){
        flex-wrap:nowrap !important;
        gap:6px !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]) > [data-testid="stColumn"]{
        min-width:0 !important;
        width:auto !important;
        flex:1 1 0 !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]) button{
        width:100% !important;
        height:46px !important;
        min-height:46px !important;
        padding:0 6px !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]) button p{
        font-size:11px !important;
        line-height:1.1 !important;
        white-space:normal !important;
        text-align:center !important;
    }
}
"""


DARK_CSS = """
.stApp{
    --chip-fill:#0F0A1F;
    /* inside colour of the prompt box + Generated Code + Output boxes:
       the same purple glow / dark base as the main page background */
    --fill:
        radial-gradient(circle at 15% 10%, rgba(88,28,135,.55), transparent 45%) padding-box,
        radial-gradient(circle at 90% 95%, rgba(37,19,200,.55), transparent 45%) padding-box,
        radial-gradient(circle at 70% 40%, rgba(131,24,67,.35), transparent 50%) padding-box,
        linear-gradient(#07030F, #07030F) padding-box;
    --toggle-bg:rgba(255,255,255,.08);
    --toggle-border:rgba(139,92,246,.65);
    --toggle-icon:__ICON__;
}

/* prompt box: visible white text (fill + pink border come from the common CSS) */
.stApp .st-key-prompt_text textarea{
    color:#FFFFFF !important;
    caret-color:#FFFFFF !important;
}

.stApp .st-key-prompt_text textarea::placeholder{
    color:#9CA3AF !important;
    opacity:1 !important;
}

/* Generated Code / Output boxes: light text on the purple fill */
.stApp .cell-title{ color:#FFFFFF; }
.stApp .empty-note{ color:#9CA3AF; }
.stApp .term,
.stApp .term-prompt{ color:#F3F4F6; }
.stApp .term.err{ color:#FCA5A5; }
.stApp .status.ok{ color:#4ADE80; }
.stApp .status.bad{ color:#F87171; }

.stApp .st-key-out_pane .stTextInput input,
.stApp .st-key-out_pane .stTextArea textarea{
    color:#FFFFFF !important;
    caret-color:#FFFFFF !important;
    border-bottom:1px solid #6B7280 !important;
}

.stApp [data-testid="stSpinner"],
.stApp [data-testid="stSpinner"] *{
    color:#FFFFFF !important;
}

/* code block: no box of its own, so the purple fill of the cell shows through
   (light text, copy icon stays) */
.stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]){
    background:transparent !important;
    border:none !important;
}

.stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]) pre,
.stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]) code{
    background:transparent !important;
}

/* Streamlit follows the computer's theme; when that is light the code text is
   dark, so flip it to light (colours keep their hue) */
@media (prefers-color-scheme: light){
    .stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]){
        filter:invert(1) hue-rotate(180deg);
    }
}
"""


LIGHT_CSS = """
.stApp{
    --chip-fill:#FFFFFF;
    --fill:linear-gradient(#FFFFFF, #FFFFFF) padding-box;
    --toggle-bg:#F1F1F1;
    --toggle-border:#D9D9D9;
    --toggle-icon:__ICON__;
    background:#FFFFFF !important;
    color:#111827 !important;
}

.stApp .main .block-container{
    background:#FFFFFF;
    border:1px solid rgba(139,92,246,.35);
}

/* white text -> black text (coloured text is untouched) */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMarkdownContainer"] p{
    color:#111827;
}

.stApp [data-testid="stSpinner"],
.stApp [data-testid="stSpinner"] *{
    color:#111827 !important;
}

/* Download button */
.stApp .stDownloadButton > button,
.stApp .stDownloadButton > button p{
    color:#111827 !important;
}

/* Sidebar: white, black text */
.stApp section[data-testid="stSidebar"],
.stApp section[data-testid="stSidebar"] > div{
    background:#FFFFFF !important;
    border-right:1px solid rgba(139,92,246,.3);
}

.stApp section[data-testid="stSidebar"] *{
    color:#111827 !important;
}

.stApp section[data-testid="stSidebar"] .logo-card p{
    color:#6366F1 !important;
}

/* unselected chips: dark text on the white chip.
   (an older "secondary button text = white" rule was stronger and hid it) */
.stApp .st-key-lang_list button[kind="secondary"],
.stApp .st-key-lang_list button[kind="secondary"] p,
.stApp .st-key-lang_list button[kind="secondary"] *,
.stApp .st-key-lang_list button[data-testid="stBaseButton-secondary"] p,
.stApp .st-key-lang_list button[data-testid="stBaseButton-secondary"] *{
    color:#111827 !important;
}

/* selected chip is pink, so its text stays white */
.stApp .st-key-lang_list button[kind="primary"],
.stApp .st-key-lang_list button[kind="primary"] *,
.stApp .st-key-lang_list button[data-testid="stBaseButton-primary"],
.stApp .st-key-lang_list button[data-testid="stBaseButton-primary"] *{
    color:#FFFFFF !important;
}

/* sidebar hide / show arrows: dark */
.stApp [data-testid="stSidebarCollapseButton"] *,
.stApp [data-testid="stExpandSidebarButton"],
.stApp [data-testid="stExpandSidebarButton"] *,
.stApp [data-testid="stSidebarCollapsedControl"] *,
.stApp [data-testid="collapsedControl"] *{
    color:#111827 !important;
    fill:#111827 !important;
    stroke:#111827 !important;
}

/* code block: white background */
.stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]){
    background:#FFFFFF !important;
    border:1px solid #E5E7EB !important;
}

.stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]) pre,
.stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]) code{
    background:transparent !important;
}

/* if the computer is in dark mode Streamlit makes the code block dark,
   so flip it back to white */
@media (prefers-color-scheme: dark){
    .stApp .st-key-code_pane :is([data-testid="stCode"], [data-testid="stCodeBlock"]){
        background:#000000 !important;
        filter:invert(1) hue-rotate(180deg);
    }
}
"""


# Toggle icons: outlined shapes in the same crimson-pink as the reference.
# Dark mode shows a sun (click -> light), light mode shows a crescent (click -> dark).

ICON_COLOR = "#FF1744"

SUN_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    f"stroke='{ICON_COLOR}' stroke-width='2.4' stroke-linecap='round' "
    "stroke-linejoin='round'>"
    "<circle cx='12' cy='12' r='4.6'/>"
    "<path d='M12 1.5v2.4M12 20.1v2.4M4.6 4.6l1.7 1.7M17.7 17.7l1.7 1.7"
    "M1.5 12h2.4M20.1 12h2.4M4.6 19.4l1.7-1.7M17.7 6.3l1.7-1.7'/>"
    "</svg>"
)

MOON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    f"stroke='{ICON_COLOR}' stroke-width='2.4' stroke-linecap='round' "
    "stroke-linejoin='round'>"
    "<path transform='rotate(45 12 12)' "
    "d='M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z'/>"
    "</svg>"
)


def svg_as_css_url(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="") + '")'


THEME_CSS = (
    DARK_CSS.replace("__ICON__", svg_as_css_url(SUN_SVG))
    if IS_DARK
    else LIGHT_CSS.replace("__ICON__", svg_as_css_url(MOON_SVG))
)

st.markdown(
    "<style>" + THEME_COMMON_CSS + THEME_CSS + "</style>",
    unsafe_allow_html=True
)


# ==========================================================
# INPUT DETECTION (one box per input call in the code)
# ==========================================================

READ_PATTERNS = {
    "Python": r'\binput\s*\(',
    "Java": r'\.\s*(?:nextInt|nextLine|nextDouble|nextLong|nextFloat|nextBoolean|next)\s*\(|\.readLine\s*\(',
    "C": r'\bscanf\s*\(|\bfgets\s*\(|\bgets\s*\(',
    "C++": r'\bcin\s*>>|\bgetline\s*\(\s*cin',
    "JavaScript": r'\.question\s*\(',
}

PRINT_PATTERNS = {
    "Java": r'System\.out\.print(?:ln)?\s*\(\s*"([^"]*)"\s*\)',
    "C": r'printf\s*\(\s*"([^"]*)"',
    "C++": r'cout\s*<<\s*"([^"]*)"',
}


def is_in_loop(code, pos, lang):
    """True if the input call at position pos sits inside a loop."""

    if lang == "Python":

        rest_of_line = code[pos:].split("\n")[0]
        if re.search(r'\bfor\b', rest_of_line):
            return True

        lines = code[:pos].split("\n")
        current = lines[-1]
        indent_now = len(current) - len(current.lstrip())

        for line in reversed(lines[:-1]):
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if indent < indent_now:
                if re.match(r'\s*(for|while)\b', line):
                    return True
                indent_now = indent

        return False

    prefix = code[:pos]
    stack = []
    last = -1
    paren = 0

    for i, ch in enumerate(prefix):
        if ch == '(':
            paren += 1
        elif ch == ')':
            paren -= 1
        elif ch == '{':
            header = prefix[last + 1:i]
            stack.append(bool(re.match(r'\s*(for|while|do)\b', header)))
            last = i
        elif ch == '}':
            if stack:
                stack.pop()
            last = i
        elif ch == ';' and paren == 0:
            last = i

    return any(stack)


def detect_inputs(lang, code):
    """Return a list of (prompt_label, in_loop) - one entry per input call."""

    boxes = []

    read_pattern = READ_PATTERNS.get(lang)

    read_matches = (
        list(re.finditer(read_pattern, code)) if read_pattern else []
    )

    if lang in ("Python", "JavaScript"):

        for m in read_matches:
            pm = re.match(r'\s*f?["\']([^"\']*)["\']', code[m.end():])
            boxes.append((
                pm.group(1) if pm else "",
                is_in_loop(code, m.start(), lang)
            ))

    elif lang in PRINT_PATTERNS:

        prints = list(re.finditer(PRINT_PATTERNS[lang], code))

        previous_end = 0

        for m in read_matches:

            text = ""

            for p in prints:
                if previous_end <= p.start() and p.end() <= m.start():
                    text = p.group(1)

            previous_end = m.end()

            boxes.append((text, is_in_loop(code, m.start(), lang)))

    # Node.js programs that read all of stdin at once
    if not boxes and lang == "JavaScript" and "readFileSync" in code:
        boxes.append(("", True))

    return boxes


def display_label(label, index):
    """Prompt text shown in the terminal (placeholders removed)."""

    text = re.sub(r'\{[^}]*\}|%[dsfc]|%l[df]', '', label).strip()

    return text if text else f"Input {index + 1}:"


def prompt_regex(label):
    """Regex that matches the prompt text inside the program output."""

    parts = re.split(r'\{[^}]*\}|%[dsfc]|%l[df]', label)

    return ".*?".join(re.escape(p) for p in parts)


# ==========================================================
# RUN HELPER
# ==========================================================

def execute(language, code, stdin_text, boxes):
    """Run the code through the backend and store the cleaned result."""

    progress = st.progress(0)

    with st.spinner("⚙️ Running Code..."):

        progress.progress(30)

        result = backend.run_code(language, code, stdin_text)

        progress.progress(100)

        progress.empty()

    output = result.get("output", "") or ""

    # Prompts are printed without a newline, so they stick to the output.
    # They are shown in the terminal as typed lines instead.
    for label, _ in boxes:
        if label.strip():
            output = re.sub(prompt_regex(label), "", output)

    st.session_state.run_output = output.strip()
    st.session_state.run_success = bool(result.get("success", False))
    st.session_state.run_done = True


# ==========================================================
# TITLE
# ==========================================================

title_col, toggle_col = st.columns([12, 1], vertical_alignment="center")

with title_col:

    st.markdown(
        "<h1><span class='grad-title'>Generate</span> code with AI</h1>",
        unsafe_allow_html=True
    )

with toggle_col:

    with st.container(key="theme_toggle"):

        st.button(
            "☀️" if IS_DARK else "🌙",
            key="theme_btn",
            on_click=toggle_theme
        )


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("""
        <div class="logo-card">

        <div style="font-size:58px;margin-bottom:10px;">🤖</div>

        <h2 style="color:white;margin:0;font-size:28px;font-weight:700;">
        Code Generator
        </h2>

        <p style="color:#A5B4FC;margin-top:8px;font-size:15px;">
        AI Powered
        </p>

        </div>
    """, unsafe_allow_html=True)

    st.markdown("## Supported Languages")

    languages = [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "HTML and CSS",
    ]

    def choose_language(name):
        st.session_state.selected_language = name

    lang_list = st.container(key="lang_list")

    with lang_list:

        for i, lang in enumerate(languages):

            direction = "cw" if i % 2 == 0 else "ccw"

            st.button(
                lang,
                key=f"lang_{direction}_{i}",
                type=(
                    "primary"
                    if st.session_state.selected_language == lang
                    else "secondary"
                ),
                on_click=choose_language,
                args=(lang,),
                use_container_width=True
            )


# ==========================================================
# TOP: PROMPT BOX (grows with the prompt)
# ==========================================================

# language comes from the sidebar chips
language = st.session_state.selected_language

prompt_text = st.session_state.get("prompt_text", "")

visual_lines = sum(
    max(1, len(line) // 110 + 1) for line in prompt_text.split("\n")
)

prompt_height = max(100, min(420, 26 * visual_lines + 46))

prompt = st.text_area(
    "Your prompt",
    key="prompt_text",
    height=prompt_height,
    placeholder="Give  me  prompt .....",
    label_visibility="collapsed"
)


# ==========================================================
# BUTTON ROW: Generate | Run | Download
# ==========================================================

has_code = bool(st.session_state.generated_code)

b1, b2, b3 = st.columns(3)

with b1:
    generate_clicked = st.button("Generate Code", type="primary")

with b2:
    run_clicked = st.button(
        "▶ Run Code",
        type="primary",
        disabled=not has_code
    )

with b3:

    ext = {
        "Python": "py",
        "Java": "java",
        "C": "c",
        "C++": "cpp",
        "JavaScript": "js",
        "HTML": "html",
        "CSS": "css"
    }.get(st.session_state.generated_language, "txt")

    st.download_button(
        "⬇ Download Code",
        st.session_state.generated_code or " ",
        file_name=f"generated_code.{ext}",
        mime="text/plain",
        disabled=not has_code
    )


# ==========================================================
# GENERATE
# ==========================================================

if generate_clicked:

    if not prompt.strip():

        st.warning("Please enter a prompt first.")

    else:

        progress = st.progress(0)

        with st.spinner("🤖 Generating Code..."):

            progress.progress(20)

            # "HTML and CSS" chip = one HTML file with the CSS inside <style>
            gen_language = language
            gen_prompt = prompt

            if language == "HTML and CSS":
                gen_language = "HTML"
                gen_prompt = (
                    prompt
                    + "\n\nWrite one complete HTML file. "
                    "Put all the CSS inside a <style> tag in the <head>."
                )

            result = backend.generate(gen_language, gen_prompt)

            progress.progress(100)

            progress.empty()

        if result.get("success"):

            st.session_state.generated_code = result["code"]
            st.session_state.generated_language = gen_language
            st.session_state.awaiting_input = False
            st.session_state.run_done = False
            st.session_state.run_success = None
            st.session_state.run_output = ""
            st.session_state.run_inputs = []

            st.rerun()

        else:

            st.error(result.get("error", "Unknown error"))


# ==========================================================
# RUN
# ==========================================================

if run_clicked and st.session_state.generated_code:

    run_lang = st.session_state.generated_language
    run_code = st.session_state.generated_code

    st.session_state.awaiting_input = False
    st.session_state.run_done = False
    st.session_state.run_inputs = []

    if run_lang in ("HTML", "CSS"):

        st.session_state.run_output = ""
        st.session_state.run_success = True
        st.session_state.run_done = True

    else:

        run_boxes = detect_inputs(run_lang, run_code)

        if run_boxes:
            # Terminal asks for the input first, then the program runs
            st.session_state.awaiting_input = True
        else:
            execute(run_lang, run_code, "", [])


# ==========================================================
# ONE BOX WITH TWO CELLS: generated code | output terminal
# ==========================================================

code = st.session_state.generated_code
code_lang = st.session_state.generated_language
code_key = hashlib.md5(code.encode("utf-8")).hexdigest()[:10]

HIGHLIGHT_NAME = {
    "Python": "python",
    "Java": "java",
    "C": "c",
    "C++": "cpp",
    "JavaScript": "javascript",
    "HTML": "html",
    "CSS": "css",
}

workbox = st.container(key="workbox")

with workbox:

    # phone layout shows ONE view at a time: the code, or (after Run) the output.
    # This hidden marker only tells the CSS which one to show.
    _showing_output = bool(
        st.session_state.awaiting_input or st.session_state.run_done
    )

    st.html(
        '<div class="view-marker '
        + ("show-out" if _showing_output else "show-code")
        + '"></div>'
    )

    left, right = st.columns(2, gap="small")

    # ---------- LEFT CELL: generated code (scroll both ways + copy icon) ----------

    with left:

        st.html('<div class="cell-title">Generated Code</div>')

        code_pane = st.container(key="code_pane")

        with code_pane:

            if code:

                lang_name = HIGHLIGHT_NAME.get(code_lang, "text")

                try:
                    st.code(code, language=lang_name, line_numbers=True)
                except TypeError:
                    # older Streamlit versions have no line_numbers option
                    st.code(code, language=lang_name)

            else:

                st.html(
                    '<div class="empty-note">'
                    'Generated code will appear here.'
                    '</div>'
                )

    # ---------- RIGHT CELL: output, input is typed inside it ----------

    with right:

        st.html('<div class="cell-title">Output</div>')

        out_pane = st.container(key="out_pane")

        with out_pane:

            # 1) Waiting for input: prompts appear inside the output cell
            if st.session_state.awaiting_input and code:

                boxes = detect_inputs(code_lang, code)

                with st.form(f"run_form_{code_key}", clear_on_submit=False):

                    values = []
                    labels = []

                    for i, (label, in_loop) in enumerate(boxes):

                        shown = display_label(label, i)
                        labels.append(shown)

                        if in_loop:

                            st.html(
                                f'<div class="term-prompt">{html.escape(shown)}'
                                f' <span style="color:#6B7280">'
                                f'(har value nayi line me)</span></div>'
                            )

                            values.append(
                                st.text_area(
                                    shown,
                                    key=f"in_{code_key}_{i}",
                                    height=110,
                                    label_visibility="collapsed"
                                ).strip("\n")
                            )

                        else:

                            c1, c2 = st.columns([1, 1])

                            with c1:
                                st.html(
                                    f'<div class="term-prompt">'
                                    f'{html.escape(shown)}</div>'
                                )

                            with c2:
                                values.append(
                                    st.text_input(
                                        shown,
                                        key=f"in_{code_key}_{i}",
                                        label_visibility="collapsed"
                                    )
                                )

                    submitted = st.form_submit_button("Run ↵")

                if submitted:

                    st.session_state.run_inputs = list(zip(labels, values))
                    st.session_state.awaiting_input = False

                    execute(code_lang, code, "\n".join(values), boxes)

                    st.rerun()

            # 2) Finished: typed input + program output
            elif st.session_state.run_done:

                if code_lang in ("HTML", "CSS"):

                    if code_lang == "HTML":
                        page = code
                    else:
                        page = (
                            f"<html><head><style>{code}</style></head><body>"
                            "<h1>Sample Heading</h1>"
                            "<p>This is a sample paragraph to preview your CSS.</p>"
                            "<button>Sample Button</button>"
                            '<div class="box" style="width:100px;height:100px;'
                            'background:#ccc;margin-top:10px;">Box</div>'
                            "</body></html>"
                        )

                    components.html(page, height=470, scrolling=True)

                else:

                    ok = st.session_state.run_success

                    st.html(
                        '<div class="status ok">✓ Code executed successfully</div>'
                        if ok else
                        '<div class="status bad">✗ Code execution failed</div>'
                    )

                    transcript = []

                    for label, value in st.session_state.run_inputs:

                        value_lines = value.split("\n") if value else [""]

                        if len(value_lines) == 1:
                            transcript.append(f"{label} {value_lines[0]}")
                        else:
                            transcript.append(label)
                            transcript.extend(value_lines)

                    if st.session_state.run_output:
                        transcript.append(st.session_state.run_output)

                    text = "\n".join(transcript) if transcript else "(No output)"

                    css_class = "term" if ok else "term err"

                    st.html(
                        f'<pre class="{css_class}">{html.escape(text)}</pre>'
                    )

            # 3) Nothing run yet
            else:

                st.html(
                    '<div class="empty-note">'
                    'output will appear here.'
                    '</div>'
                )