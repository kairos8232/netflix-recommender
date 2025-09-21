import os
import pandas as pd

# Get the folder where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build full paths
movies_path = os.path.join(script_dir, "netflix_movies_detailed_up_to_2025.csv")
shows_path  = os.path.join(script_dir, "netflix_tv_shows_detailed_up_to_2025.csv")

# Load CSVs
movies = pd.read_csv(movies_path)
shows  = pd.read_csv(shows_path)

print("✅ Loaded:", len(movies), "movies,", len(shows), "tv shows")

# Drop 'duration' if exists
movies = movies.drop(columns=["duration"], errors="ignore")
shows = shows.drop(columns=["duration"], errors="ignore")

# Ensure both have a 'type' column
if "type" not in movies.columns:
    movies["type"] = "Movie"
if "type" not in shows.columns:
    shows["type"] = "TV Show"

# Combine into one dataset
combined = pd.concat([movies, shows], ignore_index=True)

# Save outputs
combined.to_excel(os.path.join(script_dir, "netflix_combined.xlsx"), index=False)

print(f"✅ Combined dataset created with {len(combined)} rows and {len(combined.columns)} columns.")
