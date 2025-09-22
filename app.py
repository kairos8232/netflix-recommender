import pandas as pd
import streamlit as st

# --- Styling (full) ---
CARD_CSS = """
<style>
.rec-card{padding:.75rem 1rem;margin-bottom:.6rem;border:1px solid #2a3542;border-radius:10px;
background:linear-gradient(135deg,#1f2933,#131b22);box-shadow:0 2px 4px rgba(0,0,0,.35);}
.rec-rank{font-size:.8rem;font-weight:600;color:#ff4b4b;letter-spacing:.5px;}
.rec-title{font-size:1rem;font-weight:600;margin:0;color:#fff;}
.rec-meta{font-size:.7rem;color:#c7d1dc;margin-top:.15rem;}
.score-badge{float:right;background:#ffb300;color:#1a1a1a;padding:2px 10px;border-radius:14px;
font-size:.7rem;font-weight:700;box-shadow:0 0 0 1px #e09f00 inset;}
.genres{margin-top:.35rem;}
.genre-badge{display:inline-block;background:#304055;color:#e5ecf3;padding:2px 6px;margin:2px 4px 0 0;
border-radius:6px;font-size:.6rem;font-weight:500;}
.after-results .stSlider, .after-results .stMultiSelect { margin-bottom:.55rem; }
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

EXTRA_CSS = """
<style>
.main-wrap { max-width: 1150px; margin: 0 auto; }
.results-panel, .filter-panel-initial { width: 100%; }
.filter-narrow { padding-right: 0.75rem; }
.filter-narrow .stSlider, .filter-narrow .stMultiSelect { margin-bottom: .55rem; }
.results-panel .rec-card { margin-right:4px; }
</style>
"""
st.markdown(EXTRA_CSS, unsafe_allow_html=True)

FONT_OVERRIDES = """
<style>
  .rec-title { font-size: 1.2rem; }
  .rec-meta { font-size: 0.9rem; }
  .genre-badge { font-size: 0.8rem; }
  .score-badge { font-size: 0.85rem; }
  .rec-rank { font-size: 0.95rem; }
</style>
"""
st.markdown(FONT_OVERRIDES, unsafe_allow_html=True)

LABEL_OVERRIDES = """
<style>
  [data-testid="stWidgetLabel"],
  [data-testid="stWidgetLabel"] * {
    font-size: 1.2rem !important;
    line-height: 1.3 !important;
  }
  [data-testid="stWidgetLabel"] p,
  [data-testid="stWidgetLabel"] label {
    font-weight: 400 !important;
    margin-bottom: .15rem !important;
  }
</style>
"""
st.markdown(LABEL_OVERRIDES, unsafe_allow_html=True)

# --- Session defaults & helpers ---
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

# --- Database loading ---
df = pd.read_csv("netflix_combined.csv")
df["genres"] = df["genres"].fillna("").apply(
    lambda x: [g.strip() for g in str(x).split(",") if g.strip()]
)
df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(
    df["vote_average"].median()
)

# --- Recommendation function ---
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

# --- Results rendering ---
def render_recommendations(df_recs: pd.DataFrame):
    if df_recs is None or df_recs.empty:
        st.info("No matches under current filters.")
        return
    max_score = df_recs["Score"].max()
    for idx, row in df_recs.reset_index(drop=True).iterrows():
        pct = (row.Score / max_score) if max_score else 0
        shade = int(255 - pct * 110)
        score_html = f"<span class='score-badge' style='background:linear-gradient(90deg,#ffb300 {pct*100:.0f}%,#5a5a5a {pct*100:.0f}%);'>{row.Score:.2f}</span>"
        genres_html = " ".join(f"<span class='genre-badge'>{g.strip()}</span>" for g in row.Genres.split(","))
        st.markdown(f"""
        <div class='rec-card' style='border-color: rgb({shade},{shade},{shade});'>
          <div class='rec-rank'>#{idx+1}</div>
          {score_html}
          <p class='rec-title'>{row.Title}</p>
          <div class='rec-meta'>Year: {row.Year} • Rating: {row.Rating:.1f}</div>
          <div class='genres'>{genres_html}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Page UI ---
st.title("🎬 Netflix Recommendation")

with st.container():
    st.markdown("<div class='main-wrap'>", unsafe_allow_html=True)

    if st.session_state.show_results:
        # Back & Reset buttons
        btn_left, btn_right = st.columns([1, 1])
        with btn_left:
            if st.button("← Back to filters", use_container_width=True):
                restore_from_snapshot()
                st.session_state.show_results = False
                st.rerun()
        with btn_right:
            if st.button("Reset filters", use_container_width=True):
                reset_inputs_to_defaults()
                st.session_state.recs_df = None
                st.session_state.show_results = False
                st.rerun()

        # Results
        st.write("### 🎯 Recommended for you")
        render_recommendations(st.session_state.recs_df)

        # Explanation
        with st.expander("ℹ️ How are recommendation scores calculated?"):
            st.latex(r"\text{Score} = \text{genre\_points} + \text{rating\_points}")
            st.latex(r"\text{genre\_points} = \text{genre\_weight} \times \text{shared\_genres}")
            st.latex(r"\text{rating\_points} = 1 - \frac{|R_{\text{candidate}} - R_{\text{fav\_avg}}|}{10}")
            st.markdown(
                "- shared_genres: number of genres in common with your favorites\n"
                "- R_candidate: the candidate title's rating (0–10)\n"
                "- R_fav_avg: the average rating of your selected favorites (0–10)"
            )

    else:
        # Input UI
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

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
