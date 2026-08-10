import streamlit as st
import pandas as pd
import numpy as np
import requests
import time


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
similarity = np.load("similarity.npy")

animes["title"] = animes["title"].astype(str)


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

    anime_index = animes[
        animes["title"] == anime
    ].index[0]

    distances = similarity[anime_index]

    anime_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:top_n + 1]

    recommendations = []

    for i in anime_list:

        anime_data = animes.iloc[i[0]]

        recommendations.append({
            "title": anime_data["title"]
        })

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

/* ============================================================
   MAIN APP BACKGROUND
   ============================================================ */

.stApp {{

    background-color: #08090f;

    background-image:
        linear-gradient(
            rgba(5, 6, 12, 0.82),
            rgba(5, 6, 12, 0.94)
        )
        {f', url("{background_url}")' if background_url else ''};

    background-size: cover;

    background-position: center top;

    background-attachment: fixed;

    background-repeat: no-repeat;
}}


/* ============================================================
   BACKGROUND EFFECT
   ============================================================ */

.stApp::before {{

    content: "";

    position: fixed;

    top: 0;
    left: 0;

    width: 100%;
    height: 100%;

    pointer-events: none;

    z-index: -1;

    background:
        radial-gradient(
            circle at 20% 20%,
            rgba(168, 85, 247, 0.18),
            transparent 35%
        ),

        radial-gradient(
            circle at 80% 30%,
            rgba(99, 102, 241, 0.12),
            transparent 35%
        );
}}


/* ============================================================
   HIDE STREAMLIT DEFAULT ELEMENTS
   ============================================================ */

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

header {{
    background: transparent !important;
}}


/* ============================================================
   NAVBAR
   ============================================================ */

.navbar {{

    display: flex;

    justify-content: space-between;

    align-items: center;

    padding: 20px 35px;

    margin-bottom: 25px;

    background:
        rgba(10, 10, 18, 0.62);

    border-bottom:
        1px solid
        rgba(255, 255, 255, 0.10);

    border-radius:
        0 0 20px 20px;

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);
}}


.logo {{

    font-size: 27px;

    font-weight: 800;

    color: white;
}}


.logo span {{

    color: #c084fc;
}}


.nav-text {{

    color: #c4c4ce;

    font-size: 14px;
}}


/* ============================================================
   HERO
   ============================================================ */

.hero {{

    text-align: center;

    padding:
        45px 20px 30px;
}}


.hero h1 {{

    font-size: 52px;

    font-weight: 900;

    margin-bottom: 10px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #e9d5ff,
            #c084fc
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;

    text-shadow:
        0 5px 30px
        rgba(0, 0, 0, 0.4);
}}


.hero p {{

    color: #d0d0d8;

    font-size: 18px;

    text-shadow:
        0 2px 10px
        rgba(0, 0, 0, 0.7);
}}


/* ============================================================
   SEARCH DROPDOWN
   ============================================================ */

div[data-testid="stSelectbox"] {{

    max-width: 700px;

    margin:
        0 auto;
}}


div[data-testid="stSelectbox"] > div {{

    background:
        rgba(12, 12, 20, 0.72);

    border:
        1px solid
        rgba(255, 255, 255, 0.18);

    border-radius:
        18px;

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);

    box-shadow:
        0 10px 35px
        rgba(0, 0, 0, 0.30);
}}


/* ============================================================
   SELECTED ANIME
   ============================================================ */

.selected-box {{

    max-width: 1000px;

    margin:
        30px auto;

    padding:
        22px 28px;

    background:
        rgba(10, 10, 18, 0.58);

    border:
        1px solid
        rgba(192, 132, 252, 0.35);

    border-radius:
        18px;

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);

    box-shadow:
        0 15px 45px
        rgba(0, 0, 0, 0.30);
}}


.selected-label {{

    color:
        #c4c4ce;

    font-size:
        12px;

    font-weight:
        700;

    letter-spacing:
        1.5px;
}}


.selected-title {{

    color:
        white;

    font-size:
        27px;

    font-weight:
        800;

    margin-top:
        5px;

    text-shadow:
        0 2px 12px
        rgba(0, 0, 0, 0.7);
}}


/* ============================================================
   BUTTONS
   ============================================================ */

div.stButton > button {{

    border-radius:
        12px;

    border:
        1px solid
        rgba(255, 255, 255, 0.14);

    background:
        rgba(10, 10, 18, 0.65);

    color:
        white;

    font-weight:
        600;

    transition:
        all 0.2s ease;

    backdrop-filter:
        blur(12px);
}}


div.stButton > button:hover {{

    background:
        rgba(168, 85, 247, 0.25);

    border-color:
        rgba(192, 132, 252, 0.70);

    color:
        white;

    transform:
        translateY(-1px);
}}


/* ============================================================
   RECOMMEND BUTTON
   ============================================================ */

.recommend-button div.stButton > button {{

    background:
        linear-gradient(
            135deg,
            #9333ea,
            #c026d3
        );

    border:
        none;

    font-size:
        16px;

    font-weight:
        700;

    box-shadow:
        0 8px 30px
        rgba(147, 51, 234, 0.40);
}}


/* ============================================================
   SECTION TITLE
   ============================================================ */

.section-title {{

    font-size:
        30px;

    font-weight:
        800;

    margin-top:
        45px;

    margin-bottom:
        25px;

    color:
        white;

    text-shadow:
        0 3px 15px
        rgba(0, 0, 0, 0.7);
}}


.section-title span {{

    color:
        #c084fc;
}}


/* ============================================================
   ANIME CARD
   ============================================================ */

.anime-card {{

    background:
        rgba(10, 10, 18, 0.70);

    border:
        1px solid
        rgba(255, 255, 255, 0.10);

    border-radius:
        16px;

    overflow:
        hidden;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        border-color 0.25s ease;

    margin-bottom:
        20px;

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);
}}


.anime-card:hover {{

    transform:
        translateY(-7px);

    border-color:
        rgba(192, 132, 252, 0.60);

    box-shadow:
        0 20px 45px
        rgba(0, 0, 0, 0.55);
}}


.anime-card img {{

    width:
        100%;

    height:
        300px;

    object-fit:
        cover;

    display:
        block;
}}


.anime-info {{

    padding:
        14px;

    min-height:
        65px;
}}


.anime-title {{

    color:
        #f4f4f5;

    font-size:
        14px;

    font-weight:
        700;

    line-height:
        1.35;
}}


/* ============================================================
   NO POSTER
   ============================================================ */

.no-poster {{

    height:
        300px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    text-align:
        center;

    color:
        #777780;

    background:
        #14151d;
}}


/* ============================================================
   EMPTY STATE
   ============================================================ */

.empty-state {{

    text-align:
        center;

    margin-top:
        70px;

    color:
        #aaaab5;
}}


.empty-icon {{

    font-size:
        55px;
}}


.empty-text {{

    font-size:
        17px;

    margin-top:
        10px;

    text-shadow:
        0 2px 10px
        rgba(0, 0, 0, 0.8);
}}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {{

    text-align:
        center;

    margin-top:
        80px;

    padding:
        30px;

    color:
        #888894;

    font-size:
        13px;
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