import pandas as pd

df = pd.read_csv("raw/raw_land_data.csv")

# Rename important columns
df = df.rename(columns={
    "property_title": "title",
    "locality": "location",
    "rounded_price_rs": "price",
    "plot_area_sqft": "area_sqft"
})

# Keep only relevant columns
df = df[["title", "location", "price", "area_sqft", "price_per_sqft"]]

# Remove duplicates
df = df.drop_duplicates()

# Remove unrealistic area (less than 600 sqft)
df = df[df["area_sqft"] >= 600]

# Remove unrealistic price (below 5 lakh)
df = df[df["price"] >= 500000]

# Remove extreme luxury outliers (above 10 crore)
df = df[df["price"] <= 100000000]

# Reset index
df = df.reset_index(drop=True)

print("Cleaned Shape:", df.shape)

df.to_csv("cleaned/clean_land_data.csv", index=False)

print("Cleaned dataset saved.")