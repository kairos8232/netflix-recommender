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

st.title("🎬 Netflix Recommendation")
