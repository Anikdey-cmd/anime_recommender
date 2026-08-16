import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import faiss


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AnimeVerse",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

animes = pd.read_csv("anime.csv")

# Load FAISS index instead of similarity.npy
index = faiss.read_index("anime.index")

animes["title"] = animes["title"].astype(str)


# ============================================================
# CHECK DATA AND INDEX
# ============================================================

if index.ntotal != len(animes):
    st.error(
        f"Anime data and FAISS index do not match. "
        f"anime.csv has {len(animes)} rows, "
        f"but anime.index has {index.ntotal} vectors."
    )
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "selected_anime" not in st.session_state:
    st.session_state.selected_anime = None

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "last_selected_anime" not in st.session_state:
    st.session_state.last_selected_anime = None


# ============================================================
# ANILIST API
# ============================================================

@st.cache_data(show_spinner=False, ttl=3600)
def get_image_url(title):

    query = """
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            coverImage {
                large
                extraLarge
            }
        }
    }
    """

    try:

        response = requests.post(
            "https://graphql.anilist.co",
            json={
                "query": query,
                "variables": {
                    "search": title
                }
            },
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            media = data.get(
                "data",
                {}
            ).get(
                "Media"
            )

            if media:

                cover = media.get(
                    "coverImage",
                    {}
                )

                return (
                    cover.get("extraLarge")
                    or cover.get("large")
                )

        elif response.status_code == 429:

            time.sleep(2)

    except requests.RequestException:

        pass

    return None


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def recommend(anime, top_n=10):

    # Find the anime's row/index in anime.csv
    matching_rows = animes.index[
        animes["title"] == anime
    ]

    if len(matching_rows) == 0:
        return []

    anime_index = matching_rows[0]

    # --------------------------------------------------------
    # Get the vector of the selected anime
    # --------------------------------------------------------
    #
    # Our FAISS index was created using IndexFlatL2,
    # so we can reconstruct the original vector.
    #

    query_vector = index.reconstruct(anime_index)

    query_vector = np.asarray(
        query_vector,
        dtype=np.float32
    ).reshape(1, -1)

    # --------------------------------------------------------
    # Search for similar anime
    # --------------------------------------------------------

    distances, indices = index.search(
        query_vector,
        top_n + 1
    )

    recommendations = []

    for i in indices[0]:

        # Skip the selected anime itself
        if i == anime_index:
            continue

        # Safety check
        if i < 0 or i >= len(animes):
            continue

        anime_data = animes.iloc[i]

        recommendations.append({
            "title": anime_data["title"]
        })

        if len(recommendations) == top_n:
            break

    return recommendations


# ============================================================
# GET SELECTED ANIME POSTER
# ============================================================

background_url = None

if st.session_state.selected_anime:

    background_url = get_image_url(
        st.session_state.selected_anime
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ================================
       MAIN BACKGROUND
       ================================ */

    .stApp {{
        background:
            linear-gradient(
                rgba(10, 12, 18, 0.92),
                rgba(10, 12, 18, 0.96)
            ),
            url("{background_url if background_url else ''}");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}


    /* ================================
       NAVBAR
       ================================ */

    .navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;

        padding: 20px 40px;

        margin-bottom: 40px;

        background: rgba(20, 20, 30, 0.70);

        border-radius: 15px;

        backdrop-filter: blur(12px);
    }}

    .logo {{
        font-size: 28px;
        font-weight: 800;
        color: white;
    }}

    .logo span {{
        color: #ff4b91;
    }}

    .nav-text {{
        color: #b8b8b8;
        font-size: 15px;
    }}


    /* ================================
       HERO
       ================================ */

    .hero {{
        text-align: center;

        margin-top: 40px;
        margin-bottom: 35px;
    }}

    .hero h1 {{
        font-size: 55px;
        font-weight: 800;

        color: white;

        margin-bottom: 10px;
    }}

    .hero p {{
        font-size: 18px;
        color: #b8b8b8;
    }}


    /* ================================
       SELECTED ANIME
       ================================ */

    .selected-box {{
        background: rgba(25, 25, 35, 0.80);

        border: 1px solid rgba(255, 255, 255, 0.10);

        border-radius: 15px;

        padding: 20px;

        margin-top: 25px;
        margin-bottom: 25px;

        text-align: center;

        backdrop-filter: blur(10px);
    }}

    .selected-label {{
        font-size: 12px;

        color: #ff4b91;

        font-weight: 700;

        letter-spacing: 2px;

        margin-bottom: 8px;
    }}

    .selected-title {{
        font-size: 24px;

        color: white;

        font-weight: 700;
    }}


    /* ================================
       RECOMMEND BUTTON
       ================================ */

    .recommend-button {{
        margin-top: 10px;
        margin-bottom: 20px;
    }}


    /* ================================
       RECOMMENDATION SECTION
       ================================ */

    .section-title {{
        font-size: 30px;

        color: white;

        font-weight: 700;

        margin-top: 40px;

        margin-bottom: 25px;
    }}

    .section-title span {{
        color: #ff4b91;
    }}


    /* ================================
       ANIME CARD
       ================================ */

    .anime-card {{
        background: rgba(25, 25, 35, 0.85);

        border-radius: 14px;

        overflow: hidden;

        margin-bottom: 25px;

        border: 1px solid rgba(255, 255, 255, 0.08);

        transition: transform 0.3s ease;
    }}

    .anime-card:hover {{
        transform: translateY(-7px);
    }}

    .anime-card img {{
        width: 100%;

        height: 300px;

        object-fit: cover;

        display: block;
    }}

    .anime-info {{
        padding: 14px;
    }}

    .anime-title {{
        color: white;

        font-size: 15px;

        font-weight: 600;

        line-height: 1.4;
    }}

    .no-poster {{
        height: 300px;

        display: flex;

        align-items: center;

        justify-content: center;

        color: #888;

        background: rgba(30, 30, 40, 0.9);
    }}


    /* ================================
       EMPTY STATE
       ================================ */

    .empty-state {{
        text-align: center;

        margin-top: 80px;

        padding: 60px;

        background: rgba(25, 25, 35, 0.70);

        border-radius: 20px;

        backdrop-filter: blur(10px);
    }}

    .empty-icon {{
        font-size: 60px;

        margin-bottom: 20px;
    }}

    .empty-text {{
        color: #aaa;

        font-size: 18px;
    }}


    /* ================================
       FOOTER
       ================================ */

    .footer {{
        text-align: center;

        margin-top: 80px;

        padding: 30px;

        color: #777;

        font-size: 14px;
    }}


    /* ================================
       STREAMLIT SELECTBOX
       ================================ */

    div[data-baseweb="select"] > div {{
        background-color: rgba(25, 25, 35, 0.90);

        border-radius: 12px;

        border: 1px solid rgba(255, 255, 255, 0.12);
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NAVBAR
# ============================================================

st.html(
    """
    <div class="navbar">

        <div class="logo">
            🎬 Anime<span>Verse</span>
        </div>

        <div class="nav-text">
            Discover • Explore • Recommend
        </div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="hero">

        <h1>Find Your Next Anime</h1>

        <p>
            Search for an anime and discover something you'll love.
        </p>

    </div>
    """
)


# ============================================================
# SEARCHABLE DROPDOWN
# ============================================================

anime_list = animes["title"].tolist()

selected_anime = st.selectbox(
    "Search Anime",
    anime_list,
    index=None,
    placeholder="🔎  Start typing an anime name...",
    key="anime_search"
)


# ============================================================
# WHEN ANIME IS SELECTED
# ============================================================

if selected_anime:

    st.session_state.selected_anime = selected_anime

    if (
        st.session_state.last_selected_anime
        != selected_anime
    ):

        st.session_state.recommendations = None

        st.session_state.last_selected_anime = (
            selected_anime
        )


# ============================================================
# SELECTED ANIME DISPLAY
# ============================================================

if st.session_state.selected_anime:

    selected = st.session_state.selected_anime

    st.html(
        f"""
        <div class="selected-box">

            <div class="selected-label">
                SELECTED ANIME
            </div>

            <div class="selected-title">
                🎬 {selected}
            </div>

        </div>
        """
    )


    # ========================================================
    # RECOMMEND BUTTON
    # ========================================================

    col1, col2, col3 = st.columns(
        [1, 1, 1]
    )

    with col2:

        st.markdown(
            '<div class="recommend-button">',
            unsafe_allow_html=True
        )

        recommend_clicked = st.button(
            "✨  Recommend Anime",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # GENERATE RECOMMENDATIONS
    # ========================================================

    if recommend_clicked:

        st.session_state.recommendations = recommend(
            selected,
            top_n=10
        )


# ============================================================
# SHOW RECOMMENDATIONS
# ============================================================

if st.session_state.recommendations:

    st.html(
        """
        <div class="section-title">
            Recommended <span>Anime</span>
        </div>
        """
    )

    recommendations = (
        st.session_state.recommendations
    )

    per_row = 5

    for row_start in range(
        0,
        len(recommendations),
        per_row
    ):

        row_items = recommendations[
            row_start:
            row_start + per_row
        ]

        cols = st.columns(per_row)

        for i, anime in enumerate(row_items):

            with cols[i]:

                image_url = get_image_url(
                    anime["title"]
                )

                if image_url:

                    st.html(
                        f"""
                        <div class="anime-card">

                            <img
                                src="{image_url}"
                                loading="lazy"
                            />

                            <div class="anime-info">

                                <div class="anime-title">
                                    {anime["title"]}
                                </div>

                            </div>

                        </div>
                        """
                    )

                else:

                    st.html(
                        f"""
                        <div class="anime-card">

                            <div class="no-poster">
                                Poster unavailable
                            </div>

                            <div class="anime-info">

                                <div class="anime-title">
                                    {anime["title"]}
                                </div>

                            </div>

                        </div>
                        """
                    )


# ============================================================
# EMPTY STATE
# ============================================================

elif not st.session_state.selected_anime:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                🍿
            </div>

            <div class="empty-text">
                Search for an anime to get
                personalized recommendations
            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">

        AnimeVerse • Your Personal Anime
        Recommendation System

    </div>
    """
)