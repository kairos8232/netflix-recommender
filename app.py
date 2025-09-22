import pandas as pd
import streamlit as st

DEFAULTS = {"favorites": [], "genre_weight": 2, "min_overlap": 1, "top_n": 5}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("show_results", False)
st.session_state.setdefault("recs_df", None)
st.session_state.setdefault("snapshot", None)

def reset_inputs_to_defaults():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v

def snapshot_inputs():
    st.session_state.snapshot = {k: st.session_state.get(k) for k in DEFAULTS.keys()}

def restore_from_snapshot():
    snap = st.session_state.get("snapshot")
    if snap:
        for k, v in snap.items():
            st.session_state[k] = v

df = pd.read_csv("netflix_combined.csv")
df["genres"] = df["genres"].fillna("").apply(
    lambda x: [g.strip() for g in str(x).split(",") if g.strip()]
)
df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(
    df["vote_average"].median()
)

def recommend(favorites, top_n=5, genre_weight=2, min_overlap=1):
    favs = df[df["title"].isin(favorites)]
    fav_genres = set(g for row in favs["genres"] for g in row)
    fav_rating = favs["vote_average"].mean()
    results = []
    for _, row in df.iterrows():
        if row["title"] in favorites:
            continue
        overlap = len(fav_genres.intersection(row["genres"]))
        if overlap < min_overlap:
            continue
        rating_sim = 1 - abs(row["vote_average"] - fav_rating) / 10
        score = genre_weight * overlap + rating_sim
        results.append((row["title"], row["release_year"],
                        ", ".join(row["genres"]), row["vote_average"], score))
    recs = sorted(results, key=lambda x: x[4], reverse=True)[:top_n]
    return pd.DataFrame(recs, columns=["Title", "Year", "Genres", "Rating", "Score"])

st.title("🎬 Netflix Recommendation")

st.markdown("<div class='filter-panel-initial'>", unsafe_allow_html=True)
st.multiselect(
    "Select favorite titles", df["title"].unique(), key="favorites",
    help="Choose a few titles you like. Recommendations will align with these."
)
st.slider(
    "Genre overlap weight", 1, 5, key="genre_weight",
    help="Higher = shared genres matter more in the score."
)
st.slider(
    "Minimum genre overlap", 0, 3, 1, 1, key="min_overlap",
    help="Filters out titles that don't share enough genres with your favorites."
)
st.slider(
    "Number of recommendations", 3, 20, 5, 1, key="top_n",
    help="Number of top-ranked recommendations to display."
)

recommend_clicked = st.button("Recommend")
if recommend_clicked:
    if st.session_state.favorites:
        snapshot_inputs()
        st.session_state.recs_df = recommend(
            st.session_state.favorites,
            st.session_state.top_n,
            st.session_state.genre_weight,
            st.session_state.min_overlap
        )
        st.session_state.show_results = True
        st.rerun()
    else:
        st.warning("Please select at least one title.")
