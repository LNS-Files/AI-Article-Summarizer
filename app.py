import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="AI Article Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Layout ── */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.6rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* ── Stat cards ── */
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1rem 0.5rem;
        text-align: center;
    }
    .stat-value { font-size: 1.7rem; font-weight: 700; color: #818cf8; }
    .stat-label { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; }

    /* ── Summary output box ── */
    .summary-box {
        background: rgba(102,126,234,0.06);
        border: 1px solid rgba(102,126,234,0.25);
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        line-height: 1.8;
        font-size: 0.97rem;
        color: #d1d5db;
        white-space: pre-wrap;
    }

    /* ── Badges ── */
    .badges { display: flex; gap: 0.4rem; justify-content: flex-end; align-items: center; padding-top: 0.3rem; }
    .badge {
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .badge-purple { background: rgba(129,140,248,0.15); color: #818cf8; border: 1px solid rgba(129,140,248,0.35); }
    .badge-green  { background: rgba(52,211,153,0.15);  color: #34d399; border: 1px solid rgba(52,211,153,0.35); }
    .badge-amber  { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.35); }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.2rem 0 !important; }

    /* ── Primary button ── */
    div[data-testid="stButton"] > button[kind="primary"],
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #a78bfa) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
        padding: 0.65rem 1.5rem !important;
        transition: box-shadow 0.2s, transform 0.15s !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 22px rgba(102,126,234,0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: rgba(52,211,153,0.1) !important;
        color: #34d399 !important;
        border: 1px solid rgba(52,211,153,0.35) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(52,211,153,0.2) !important;
        box-shadow: 0 4px 14px rgba(52,211,153,0.25) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(15,15,26,0.97) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── Text area / input ── */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
        font-size: 0.93rem !important;
        line-height: 1.65 !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: rgba(102,126,234,0.5) !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.12) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #6b7280 !important;
        font-weight: 600 !important;
        border-radius: 0 !important;
        padding: 0.5rem 1.2rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #818cf8 !important;
        border-bottom: 2px solid #818cf8 !important;
    }

    /* ── Alerts ── */
    .stSuccess { background: rgba(52,211,153,0.08) !important; border: 1px solid rgba(52,211,153,0.25) !important; border-radius: 10px !important; }
    .stWarning { background: rgba(251,191,36,0.08) !important; border: 1px solid rgba(251,191,36,0.25) !important; border-radius: 10px !important; }
    .stError   { background: rgba(248,113,113,0.08) !important; border: 1px solid rgba(248,113,113,0.25) !important; border-radius: 10px !important; }

    /* ── History expanders ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        color: #9ca3af !important;
    }

    /* ── Info metric ── */
    .info-line {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 0.55rem 1rem;
        font-size: 0.87rem;
        color: #9ca3af;
    }
    .info-line strong { color: #818cf8; }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
for key, default in [
    ("history", []),
    ("current_summary", None),
    ("fetched_article", ""),
    ("fetch_error", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Anthropic client ─────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return Anthropic(api_key=api_key)

client = get_client()

# ── Helpers ──────────────────────────────────────────────────────────────────
def count_words(text: str) -> int:
    return len(text.split()) if text.strip() else 0

def reading_time(words: int) -> str:
    mins = max(1, round(words / 238))
    return f"{mins} min"

def fetch_from_url(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=12)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "figure", "form"]):
        tag.decompose()

    container = soup.find("article") or soup.find("main") or soup.find("body")
    raw = container.get_text(separator="\n", strip=True) if container else soup.get_text()

    lines = [l.strip() for l in raw.splitlines() if len(l.strip()) > 40]
    return "\n".join(lines)

LENGTH_GUIDE = {
    "Brief":         "Write a concise summary of 3–5 sentences only.",
    "Detailed":      "Write a thorough 2–3 paragraph summary covering all main points.",
    "Comprehensive": "Write a comprehensive summary covering all key arguments, evidence, data points, and conclusions in full detail.",
}

STYLE_GUIDE = {
    "Paragraph":        "Use clear, flowing prose paragraphs.",
    "Bullet Points":    "Format as concise bullet points (•). Each bullet must be a complete, standalone insight.",
    "Key Insights":     "Extract the 5 most important insights. Number each one and follow with a one-sentence explanation.",
    "Executive Summary":"Structure with three labeled sections — **Overview**, **Key Findings**, and **Implications** — in professional tone.",
}

def build_prompt(article: str, style: str, length: str) -> str:
    return f"""You are an expert analyst. Summarize the article below with precision and clarity.

Rules:
- {LENGTH_GUIDE[length]}
- {STYLE_GUIDE[style]}
- Preserve core meaning, important facts, and key arguments.
- Do not add opinions or information not present in the article.
- Use professional, clear language.

Article:
\"\"\"
{article}
\"\"\"

Summary:"""

def summarize(article: str, style: str, length: str) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": build_prompt(article, style, length)}],
    )
    return msg.content[0].text.strip()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">📰 AI Article Summarizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by Claude AI · summarize any article in seconds</p>', unsafe_allow_html=True)

# ── API key guard ─────────────────────────────────────────────────────────────
if client is None:
    st.error(
        "**ANTHROPIC_API_KEY not found.**  \n"
        "Create a `.env` file in this directory with:  \n"
        "```\nANTHROPIC_API_KEY=sk-ant-...\n```"
    )
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Options")
    st.markdown("---")

    summary_style = st.selectbox(
        "Summary Style",
        ["Paragraph", "Bullet Points", "Key Insights", "Executive Summary"],
        help="Controls the structure of the generated summary.",
    )

    summary_length = st.radio(
        "Summary Length",
        ["Brief", "Detailed", "Comprehensive"],
        index=1,
    )

    st.markdown("---")
    st.markdown("### 🕑 History")

    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - i
            with st.expander(f"#{idx} · {item['time']}  —  {item['style']}"):
                st.caption(f"{item['length']} · {item['words']} words in")
                preview = item["summary"][:220]
                if len(item["summary"]) > 220:
                    preview += "…"
                st.text(preview)
    else:
        st.caption("Summaries will appear here after you run one.")

# ── Input tabs ────────────────────────────────────────────────────────────────
tab_paste, tab_url = st.tabs(["✏️  Paste Text", "🔗  From URL"])

article_text = ""

with tab_paste:
    pasted = st.text_area(
        "Article text",
        height=280,
        placeholder="Paste the full article text here…",
        label_visibility="collapsed",
    )
    article_text = pasted

with tab_url:
    url_col, btn_col = st.columns([5, 1])
    with url_col:
        url_input = st.text_input(
            "URL",
            placeholder="https://example.com/some-article",
            label_visibility="collapsed",
        )
    with btn_col:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_clicked = st.button("Fetch", use_container_width=True)

    if fetch_clicked and url_input:
        with st.spinner("Fetching article from URL…"):
            try:
                fetched = fetch_from_url(url_input)
                if len(fetched.strip()) < 100:
                    st.session_state.fetch_error = "Couldn't extract readable text from that page. Try pasting the text directly."
                    st.session_state.fetched_article = ""
                else:
                    st.session_state.fetched_article = fetched
                    st.session_state.fetch_error = ""
            except Exception as e:
                st.session_state.fetch_error = f"Fetch failed: {e}"
                st.session_state.fetched_article = ""

    if st.session_state.fetch_error:
        st.error(st.session_state.fetch_error)

    if st.session_state.fetched_article:
        wc = count_words(st.session_state.fetched_article)
        st.success(f"Article fetched — **{wc:,} words** extracted.")
        with st.expander("Preview fetched content"):
            preview_len = min(len(st.session_state.fetched_article), 1200)
            st.text(st.session_state.fetched_article[:preview_len] + ("…" if len(st.session_state.fetched_article) > 1200 else ""))
        article_text = st.session_state.fetched_article

# ── Article stats ─────────────────────────────────────────────────────────────
if article_text and article_text.strip():
    wc = count_words(article_text)
    cc = len(article_text)
    rt = reading_time(wc)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{wc:,}</div><div class="stat-label">Words</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{cc:,}</div><div class="stat-label">Characters</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{rt}</div><div class="stat-label">Read time</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Action row ────────────────────────────────────────────────────────────────
btn_col, clear_col = st.columns([4, 1])
with btn_col:
    summarize_clicked = st.button("✨  Summarize Article", use_container_width=True)
with clear_col:
    if st.button("Clear", use_container_width=True):
        st.session_state.current_summary = None
        st.session_state.fetched_article = ""
        st.session_state.fetch_error = ""
        st.rerun()

if summarize_clicked:
    if not article_text or len(article_text.strip()) < 80:
        st.warning("Please provide an article with at least 80 characters of text.")
    else:
        with st.spinner("Claude is reading and summarizing…"):
            try:
                result = summarize(article_text, summary_style, summary_length)
                st.session_state.current_summary = result
                st.session_state.history.append({
                    "time":    datetime.now().strftime("%H:%M"),
                    "style":   summary_style,
                    "length":  summary_length,
                    "summary": result,
                    "words":   count_words(article_text),
                })
            except Exception as e:
                st.error(f"Summarization failed: {e}")

# ── Summary output ────────────────────────────────────────────────────────────
if st.session_state.current_summary:
    st.markdown("---")

    orig_words = count_words(article_text) if article_text.strip() else 0
    summ_words = count_words(st.session_state.current_summary)
    compression = round((1 - summ_words / orig_words) * 100) if orig_words > 0 else 0

    head_col, badge_col = st.columns([3, 2])
    with head_col:
        st.markdown("### Summary")
    with badge_col:
        st.markdown(
            f'<div class="badges">'
            f'<span class="badge badge-purple">{summary_style}</span>'
            f'<span class="badge badge-amber">{summary_length}</span>'
            f'<span class="badge badge-green">↓ {compression}% shorter</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    import html
    escaped = html.escape(st.session_state.current_summary)
    st.markdown(f'<div class="summary-box">{escaped}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    dl_col, info_col = st.columns([2, 3])
    with dl_col:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "⬇  Download Summary (.txt)",
            data=st.session_state.current_summary,
            file_name=f"summary_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with info_col:
        st.markdown(
            f'<div class="info-line">'
            f'Summary: <strong>{summ_words} words</strong>'
            f'&nbsp;&nbsp;·&nbsp;&nbsp;'
            f'Original: <strong style="color:#9ca3af">{orig_words:,} words</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )
