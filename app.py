"""Streamlit frontend for the AI recommendation system."""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
if not API_URL.startswith(("http://", "https://")):
    API_URL = f"https://{API_URL}"


st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 AI-Powered Movie Recommendation System")
st.caption("Hybrid retrieval + RAG + LLM-powered explanations")

with st.sidebar:
    st.header("Recommendation Settings")
    api_url = st.text_input("API URL", value=API_URL)
    top_k = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)

query = st.text_area(
    "What kind of movie are you looking for?",
    placeholder="Example: I want a dark science-fiction movie about artificial intelligence.",
    height=120,
)

if st.button("Get Recommendations", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a movie preference.")
    else:
        with st.spinner("Finding movies and generating explanations..."):
            try:
                response = requests.post(
                    f"{api_url.rstrip('/')}/recommend",
                    json={"query": query.strip(), "top_k": top_k},
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as exc:
                st.error(
                    "Could not reach the recommendation API. "
                    "Start the FastAPI server and try again."
                )
                st.caption(str(exc))
            else:
                st.subheader("Recommendations")

                for index, movie in enumerate(data["recommendations"], start=1):
                    with st.container(border=True):
                        st.markdown(f"### {index}. {movie['title']}")
                        st.write(movie["overview"])

                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Hybrid Score", f"{movie['score']:.3f}")
                        col2.metric("Semantic", f"{movie['semantic_score']:.3f}")
                        col3.metric("Content", f"{movie['content_score']:.3f}")
                        col4.metric("Popularity", f"{movie['popularity_score']:.3f}")

                        if movie["genres"]:
                            st.caption(f"Genres: {movie['genres']}")

                st.subheader("🤖 AI Explanation")
                st.write(data["explanation"])
