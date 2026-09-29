"""Streamlit frontend for the AI recommendation system."""

from __future__ import annotations

import html
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
if not API_URL.startswith(("http://", "https://")):
    API_URL = f"https://{API_URL}"


st.set_page_config(
    page_title="CineMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Visual design
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(124, 92, 255, 0.16), transparent 28%),
            radial-gradient(circle at 90% 15%, rgba(0, 210, 255, 0.10), transparent 24%),
            #07080d;
        color: #f4f5f7;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(7, 8, 13, 0.72);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0e16 0%, #08090e 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    [data-testid="stSidebar"] * {
        font-family: 'DM Sans', sans-serif;
    }

    .brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: #ffffff;
        margin-bottom: 2.2rem;
    }

    .brand span {
        color: #8b7cff;
    }

    .hero {
        padding: 3.4rem 0 2rem 0;
        max-width: 900px;
    }

    .eyebrow {
        display: inline-block;
        padding: 0.38rem 0.75rem;
        border: 1px solid rgba(139,124,255,0.30);
        border-radius: 999px;
        background: rgba(139,124,255,0.08);
        color: #aaa0ff;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2.6rem, 5vw, 4.7rem);
        line-height: 0.98;
        letter-spacing: -0.055em;
        margin: 1.1rem 0 1rem 0;
        color: #ffffff;
    }

    .hero h1 .accent {
        background: linear-gradient(100deg, #a79aff, #64d9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        max-width: 690px;
        color: #a9acb8;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 0;
    }

    .search-label {
        color: #d9dbe3;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 0.45rem;
    }

    div[data-testid="stTextArea"] textarea {
        background: rgba(16, 18, 28, 0.92) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.18);
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(139,124,255,0.75) !important;
        box-shadow: 0 0 0 1px rgba(139,124,255,0.35), 0 12px 40px rgba(0,0,0,0.22);
    }

    .prompt-chip {
        display: inline-block;
        padding: 0.5rem 0.78rem;
        margin: 0.2rem 0.25rem 0.2rem 0;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 999px;
        color: #b9bdca;
        background: rgba(255,255,255,0.035);
        font-size: 0.78rem;
    }

    .section-heading {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.45rem;
        font-weight: 700;
        color: #ffffff;
        margin: 2.5rem 0 1rem 0;
    }

    .movie-card {
        min-height: 315px;
        padding: 1.35rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(22,24,35,0.96), rgba(12,13,20,0.96));
        box-shadow: 0 18px 50px rgba(0,0,0,0.24);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .movie-number {
        color: #8e92a3;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        text-transform: uppercase;
    }

    .movie-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #ffffff;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0.35rem 0 0.65rem 0;
    }

    .genre {
        display: inline-block;
        padding: 0.28rem 0.55rem;
        margin: 0 0.3rem 0.35rem 0;
        border-radius: 999px;
        background: rgba(139,124,255,0.10);
        border: 1px solid rgba(139,124,255,0.18);
        color: #bcb3ff;
        font-size: 0.72rem;
    }

    .movie-overview {
        color: #aeb2bf;
        font-size: 0.88rem;
        line-height: 1.65;
        margin: 0.7rem 0 1rem 0;
    }

    .score-row {
        display: flex;
        gap: 0.45rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .score {
        padding: 0.45rem 0.58rem;
        border-radius: 10px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.06);
        color: #c6c9d4;
        font-size: 0.72rem;
    }

    .score strong {
        color: #ffffff;
        font-size: 0.78rem;
    }

    .ai-panel {
        padding: 1.35rem 1.5rem;
        border: 1px solid rgba(100,217,255,0.15);
        border-radius: 18px;
        background:
            linear-gradient(135deg, rgba(100,217,255,0.06), rgba(139,124,255,0.08)),
            rgba(15,17,26,0.92);
        color: #cdd0db;
        line-height: 1.7;
        box-shadow: 0 18px 50px rgba(0,0,0,0.18);
    }

    .ai-label {
        color: #72dfff;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.62rem;
        border-radius: 999px;
        background: rgba(64, 210, 150, 0.08);
        border: 1px solid rgba(64, 210, 150, 0.18);
        color: #70dcae;
        font-size: 0.72rem;
    }

    .sidebar-note {
        color: #8e92a3;
        font-size: 0.76rem;
        line-height: 1.55;
        margin-top: 1.2rem;
    }

    .footer {
        color: #646876;
        text-align: center;
        font-size: 0.75rem;
        padding: 3rem 0 1rem 0;
    }

    .stButton > button[kind="primary"] {
        border: 0;
        border-radius: 13px;
        min-height: 3rem;
        background: linear-gradient(100deg, #7c68ff, #4cbfe9);
        color: white;
        font-family: 'DM Sans', sans-serif;
        font-weight: 700;
        box-shadow: 0 12px 30px rgba(96, 105, 255, 0.22);
    }

    .stButton > button[kind="primary"]:hover {
        border: 0;
        filter: brightness(1.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">CINEMIND <span>AI</span></div>', unsafe_allow_html=True)
    st.markdown("### Search settings")

    api_url = st.text_input(
        "API endpoint",
        value=API_URL,
        help="FastAPI backend used by the recommendation interface.",
    )

    top_k = st.slider(
        "Recommendations",
        min_value=1,
        max_value=10,
        value=5,
    )

    st.markdown(
        '<div class="status-pill">● API-powered recommendations</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-note">
        Describe the mood, genre, story, characters, or themes you want.
        CineMind converts natural language into ranked movie recommendations.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <span class="eyebrow">AI MOVIE DISCOVERY</span>
        <h1>Find a movie that feels<br><span class="accent">made for you.</span></h1>
        <p>
            Tell CineMind what you are in the mood for. The recommendation
            engine combines content matching, ranking signals, and grounded
            AI explanations to surface relevant titles.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="search-label">Describe what you want to watch</div>', unsafe_allow_html=True)

query = st.text_area(
    "movie_query",
    placeholder="Try: A dark sci-fi thriller about artificial intelligence with a mysterious atmosphere...",
    height=120,
    label_visibility="collapsed",
)

st.markdown(
    """
    <div>
        <span class="prompt-chip">Dark sci-fi</span>
        <span class="prompt-chip">Mind-bending thriller</span>
        <span class="prompt-chip">Feel-good adventure</span>
        <span class="prompt-chip">Emotional drama</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

if st.button("✦  Discover Movies", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Tell me what kind of movie you want first.")
    else:
        with st.spinner("Searching the movie universe..."):
            try:
                response = requests.post(
                    f"{api_url.rstrip('/')}/recommend",
                    json={"query": query.strip(), "top_k": top_k},
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as exc:
                st.error("The recommendation API could not be reached.")
                st.caption(str(exc))
            else:
                recommendations = data.get("recommendations", [])

                st.markdown(
                    f'<div class="section-heading">Your matches <span style="color:#777b89;font-size:0.9rem;">· {len(recommendations)} found</span></div>',
                    unsafe_allow_html=True,
                )

                if not recommendations:
                    st.info("No recommendations were returned for this query.")
                else:
                    columns = st.columns(2)

                    for index, movie in enumerate(recommendations, start=1):
                        title = html.escape(str(movie.get("title", "Untitled")))
                        overview = html.escape(str(movie.get("overview", "")))
                        genres = str(movie.get("genres", "") or "")

                        genre_html = "".join(
                            f'<span class="genre">{html.escape(g.strip())}</span>'
                            for g in genres.split("|")
                            if g.strip()
                        )

                        card = f"""
                        <div class="movie-card">
                            <div class="movie-number">MATCH {index:02d}</div>
                            <div class="movie-title">{title}</div>
                            <div>{genre_html}</div>
                            <div class="movie-overview">{overview}</div>
                            <div class="score-row">
                                <div class="score">Overall <strong>{float(movie.get("score", 0)):.3f}</strong></div>
                                <div class="score">Content <strong>{float(movie.get("content_score", 0)):.3f}</strong></div>
                                <div class="score">Semantic <strong>{float(movie.get("semantic_score", 0)):.3f}</strong></div>
                                <div class="score">Popularity <strong>{float(movie.get("popularity_score", 0)):.3f}</strong></div>
                            </div>
                        </div>
                        """

                        with columns[(index - 1) % 2]:
                            st.markdown(card, unsafe_allow_html=True)

                explanation = html.escape(str(data.get("explanation", "")))
                st.markdown(
                    """
                    <div class="section-heading">Why these movies?</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div class="ai-panel">
                        <div class="ai-label">✦ Grounded AI explanation</div>
                        {explanation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.markdown(
    """
    <div class="footer">
        CineMind AI · Hybrid recommendation + RAG architecture · Built with FastAPI & Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
