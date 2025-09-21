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

# Preprocess genres and ratings
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
