import pandas as pd

df = pd.read_csv("raw/raw_land_data.csv")

print("🔎 Dataset Shape:", df.shape)
print("\n📌 Columns:", df.columns.tolist())

print("\n❗ Missing Values:")
print(df.isnull().sum())

print("\n🔁 Duplicate Rows:", df.duplicated().sum())

print("\n💰 Price Statistics:")
print(df["rounded_price_rs"].describe())

print("\n📐 Area Statistics:")
print(df["plot_area_sqft"].describe())