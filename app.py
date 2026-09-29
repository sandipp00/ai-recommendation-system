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

    div[data-testid="stHorizontalBlock"] button {
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.09);
        background: rgba(255,255,255,0.035);
        color: #b9bdca;
        font-size: 0.78rem;
        min-height: 2.25rem;
        transition: all 0.2s ease;
    }

    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: rgba(139,124,255,0.45);
        color: #ffffff;
        background: rgba(139,124,255,0.10);
    }

    .movie-card {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }

    .movie-poster {
        width: 82px;
        min-width: 82px;
        height: 122px;
        object-fit: cover;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.10);
        background: #11131b;
    }

    .movie-content {
        flex: 1;
        min-width: 0;
    }

    .movie-meta {
        display: flex;
        gap: 0.55rem;
        align-items: center;
        margin: 0.45rem 0 0.65rem 0;
        font-size: 0.76rem;
    }

    .movie-rating {
        color: #f6d36b;
        font-weight: 700;
    }

    .movie-votes, .movie-year {
        color: #858997;
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
        color: #858a9b;
        font-size: 0.78rem;
        line-height: 1.6;
        margin-top: 0.9rem;
    }

    [data-testid="stSidebar"] {
        min-width: 310px;
    }

    .sidebar-brand {
        padding: 0.25rem 0 1.4rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 1.35rem;
    }

    .sidebar-brand-row {
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }

    .sidebar-logo {
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: linear-gradient(135deg, #8b7cff, #4cbfe9);
        color: #ffffff;
        font-size: 1.05rem;
        box-shadow: 0 10px 26px rgba(91, 99, 255, 0.28);
    }

    .sidebar-brand-name {
        font-family: 'Space Grotesk', sans-serif;
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .sidebar-brand-name span {
        color: #8f82ff;
    }

    .sidebar-tagline {
        color: #777c8d;
        font-size: 0.68rem;
        margin: 0.65rem 0 0 0;
        line-height: 1.5;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.8rem;
        padding: 0.34rem 0.58rem;
        border: 1px solid rgba(100,217,255,0.18);
        border-radius: 999px;
        background: rgba(100,217,255,0.06);
        color: #79ddff;
        font-size: 0.63rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    .live-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #5fe0ff;
        box-shadow: 0 0 10px rgba(95,224,255,0.8);
    }

    .sidebar-section-label {
        color: #666b7b;
        font-size: 0.64rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0.2rem 0 0.7rem 0;
    }

    .discovery-card {
        padding: 1rem;
        margin: 0.45rem 0 1rem 0;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 17px;
        background:
            radial-gradient(circle at 100% 0%, rgba(139,124,255,0.12), transparent 45%),
            rgba(255,255,255,0.025);
    }

    .discovery-title {
        color: #f2f3f6;
        font-size: 0.86rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .discovery-subtitle {
        color: #777c8d;
        font-size: 0.68rem;
        line-height: 1.5;
        margin-bottom: 0.65rem;
    }

    .sidebar-vibe-title {
        color: #bfc3d0;
        font-size: 0.72rem;
        font-weight: 600;
        margin: 1.1rem 0 0.45rem 0;
    }

    .vibe-caption {
        color: #686d7c;
        font-size: 0.64rem;
        margin: -0.15rem 0 0.55rem 0;
    }

    .api-status-card {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.82rem 0.9rem;
        margin-top: 1.15rem;
        border: 1px solid rgba(64,210,150,0.15);
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(64,210,150,0.055), rgba(64,210,150,0.018));
    }

    .api-dot {
        width: 8px;
        height: 8px;
        flex: 0 0 8px;
        border-radius: 50%;
        background: #57d99b;
        box-shadow: 0 0 10px rgba(87,217,155,0.65);
    }

    .api-status-title {
        color: #d8f8e8;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .api-status-subtitle {
        color: #718879;
        font-size: 0.64rem;
        margin-top: 0.12rem;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 11px;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 2.25rem;
        border-radius: 11px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        color: #bfc3d0;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.35rem 0.5rem;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: rgba(139,124,255,0.45);
        background: rgba(139,124,255,0.10);
        color: #ffffff;
    }

    [data-testid="stSidebar"] .stExpander {
        margin-top: 0.9rem;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 13px;
        background: rgba(255,255,255,0.018);
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
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-row">
                <div class="sidebar-logo">✦</div>
                <div class="sidebar-brand-name">CINEMIND <span>AI</span></div>
            </div>
            <div class="sidebar-tagline">Personalized discovery for your next great watch.</div>
            <div class="live-badge"><span class="live-dot"></span> Live movie intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">Tune your discovery</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="discovery-card">
            <div class="discovery-title">Recommendation depth</div>
            <div class="discovery-subtitle">Choose how wide you want the search to explore.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result_options = [4, 5, 6, 8, 10]
    top_k = st.selectbox(
        "Number of recommendations",
        options=result_options,
        index=1,
        format_func=lambda value: f"{value} movies",
        label_visibility="collapsed",
        key="recommendation_count",
    )

    st.markdown('<div class="sidebar-vibe-title">Quick vibes</div>', unsafe_allow_html=True)
    st.markdown('<div class="vibe-caption">Start with a mood — you can edit it afterward.</div>', unsafe_allow_html=True)

    sidebar_prompts = {
        "🌌 Sci-Fi": "A dark science-fiction movie with artificial intelligence and a mysterious atmosphere.",
        "🧠 Mind-bending": "A mind-bending thriller with mystery, suspense, and an unexpected story.",
        "✨ Feel-good": "A feel-good adventure movie that is exciting, funny, and uplifting.",
        "🎭 Emotional": "An emotional drama with strong characters, meaningful relationships, and a powerful story.",
    }

    vibe_columns = st.columns(2)
    for column, (label, prompt) in zip(vibe_columns * 2, sidebar_prompts.items()):
        with column:
            if st.button(label, use_container_width=True, key=f"sidebar_{label}"):
                st.session_state["_pending_movie_query"] = prompt
                st.rerun()

    st.markdown(
        """
        <div class="api-status-card">
            <div class="api-dot"></div>
            <div>
                <div class="api-status-title">Engine ready</div>
                <div class="api-status-subtitle">FastAPI · TMDB live data</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("⚙ Connection settings"):
        api_url = st.text_input(
            "API endpoint",
            value=API_URL,
            help="FastAPI backend used by the recommendation interface.",
        )

    st.markdown(
        """
        <div class="sidebar-note">
            <strong style="color:#bfc3d0;">Tip</strong><br>
            Be specific about mood, genre, themes, pacing, or story style.
            CineMind uses those signals to find closer matches.
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

# Apply a prompt selected from a discovery chip before the text-area widget
# is instantiated. Streamlit does not allow changing a widget's keyed state
# after that widget has already been created in the current run.
if "_pending_movie_query" in st.session_state:
    st.session_state["movie_query"] = st.session_state.pop("_pending_movie_query")

query = st.text_area(
    "movie_query",
    placeholder="Try: A dark sci-fi thriller about artificial intelligence with a mysterious atmosphere...",
    height=120,
    label_visibility="collapsed",
    key="movie_query",
)

# Clickable discovery prompts
prompt_options = {
    "Dark sci-fi": "A dark science-fiction movie with artificial intelligence and a mysterious atmosphere.",
    "Mind-bending thriller": "A mind-bending thriller with mystery, suspense, and an unexpected story.",
    "Feel-good adventure": "A feel-good adventure movie that is exciting, funny, and uplifting.",
    "Emotional drama": "An emotional drama with strong characters, meaningful relationships, and a powerful story.",
}

prompt_columns = st.columns(len(prompt_options))

for column, (label, prompt) in zip(prompt_columns, prompt_options.items()):
    with column:
        if st.button(label, use_container_width=True, key=f"prompt_{label}"):
            st.session_state["_pending_movie_query"] = prompt
            st.rerun()

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
                        poster_url = str(movie.get("poster_url", "") or "")
                        vote_average = movie.get("vote_average")
                        vote_count = movie.get("vote_count")
                        release_year = movie.get("release_year")

                        genre_html = "".join(
                            f'<span class="genre">{html.escape(g.strip())}</span>'
                            for g in genres.split("|")
                            if g.strip()
                        )

                        rating_html = ""
                        if vote_average is not None:
                            rating_html = f'<span class="movie-rating">★ {float(vote_average):.1f}</span>'
                            if vote_count is not None:
                                rating_html += f'<span class="movie-votes">{int(vote_count):,} votes</span>'
                        year_html = f'<span class="movie-year">{int(release_year)}</span>' if release_year else ""
                        poster_html = (
                            f'<img class="movie-poster" src="{html.escape(poster_url)}" alt="{title} poster">'
                            if poster_url else ""
                        )

                        card = f"""
                        <div class="movie-card">
                            {poster_html}
                            <div class="movie-content">
                                <div class="movie-number">MATCH {index:02d}</div>
                                <div class="movie-title">{title}</div>
                                <div class="movie-meta">{rating_html}{year_html}</div>
                                <div>{genre_html}</div>
                                <div class="movie-overview">{overview}</div>
                                <div class="score-row">
                                    <div class="score">Match <strong>{float(movie.get("score", 0)):.3f}</strong></div>
                                <div class="score">Content <strong>{float(movie.get("content_score", 0)):.3f}</strong></div>
                                <div class="score">Semantic <strong>{float(movie.get("semantic_score", 0)):.3f}</strong></div>
                                    <div class="score">Rating <strong>{float(movie.get("popularity_score", 0)):.3f}</strong></div>
                                </div>
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
        CineMind AI · Hybrid recommendation + RAG architecture · Built with FastAPI & Streamlit<br>
        <span style="font-size:0.72rem;">This product uses the TMDB API but is not endorsed or certified by TMDB.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
