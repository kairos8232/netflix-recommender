# 🎬 Netflix Recommender (Streamlit App)

A lightweight Streamlit web app that recommends Netflix titles based on your favorites.

You simply pick a few favorite shows or movies, click **"Recommend"**, and the app displays a ranked list of suggested titles.  
This project uses a simple scoring approach — no machine learning required!

---

## 📂 Dataset Source

Data comes from Kaggle:
> [Netflix Movies and TV shows till 2025](https://www.kaggle.com/datasets/bhargavchirumamilla/netflix-movies-and-tv-shows-till-2025/)

Downloaded files:
- `netflix_movies_detailed_up_to_2025.csv`
- `netflix_tv_shows_detailed_up_to_2025.csv`

These are merged using [`combine_command.py`](combine_command.py) into:
- `netflix_combined.xlsx`

---

## 🚀 How to Run Locally

1. **Install dependencies:**
   ```bash
   pip install streamlit pandas openpyxl
   ```
2. Start the app:
   ```sh
   streamlit run app.py
   ```
