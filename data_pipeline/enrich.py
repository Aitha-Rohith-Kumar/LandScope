import pandas as pd
import numpy as np

df = pd.read_csv("cleaned/clean_land_data.csv")

# Generate location clusters (no price dependency)
unique_locations = df["location"].unique()

location_coords = {}

for loc in unique_locations:
    lat = np.random.uniform(17.30, 17.55)
    lon = np.random.uniform(78.25, 78.55)
    location_coords[loc] = (lat, lon)

df["latitude"] = df["location"].apply(lambda x: location_coords[x][0])
df["longitude"] = df["location"].apply(lambda x: location_coords[x][1])

# Civic features generated independently
df["infrastructure"] = np.random.uniform(5, 10, len(df))
df["metro_distance"] = np.random.uniform(1, 12, len(df))
df["crime_rate"] = np.random.uniform(1, 8, len(df))
df["pollution"] = np.random.uniform(3, 8, len(df))

# Growth index based only on civic factors
df["growth_index"] = (
    df["infrastructure"] * 0.6 +
    (10 - (df["metro_distance"] / 12 * 10)) * 0.4
)

df.to_csv("processed/final_land_dataset_clean.csv", index=False)

print("Scientifically clean dataset generated.")