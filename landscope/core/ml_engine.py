from .models import Plot
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def run_ml_pipeline(obj):

    plots = Plot.objects.exclude(id=obj.id)

    data = []
    for plot in plots:
        if None in [plot.metro_distance, plot.crime_rate, plot.pollution, plot.infrastructure]:
            continue

        data.append({
            "price": plot.price,
            "metro_distance": plot.metro_distance,
            "crime_rate": plot.crime_rate,
            "pollution": plot.pollution,
            "infrastructure": plot.infrastructure,
            "area_sqft": plot.area_sqft,
            "growth_index": plot.infrastructure * 0.5 + (10 - plot.metro_distance) * 0.5
        })

    # 🚨 Handle small dataset case
    if len(data) < 3:
        return {
            "predicted_price": obj.price,
            "investment_score": 50
        }

    df = pd.DataFrame(data)

    X = df[['metro_distance','crime_rate','pollution','infrastructure','area_sqft','growth_index']]
    y = df['price']

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    # 🔥 Predict for CURRENT PLOT
    growth_index = obj.infrastructure * 0.5 + (10 - obj.metro_distance) * 0.5

    input_data = [[
        obj.metro_distance,
        obj.crime_rate,
        obj.pollution,
        obj.infrastructure,
        obj.area_sqft,
        growth_index
    ]]

    predicted_price = model.predict(input_data)[0]

    # 🔥 Investment Score (same logic)
    valuation_strength = predicted_price / df['price'].max()
    infra_score = obj.infrastructure / 10
    growth_score = growth_index / (df['price'].max())

    metro_access = 1 - (obj.metro_distance / df['metro_distance'].max())
    crime_safety = 1 - (obj.crime_rate / df['crime_rate'].max())

    investment_score = (
        0.40 * valuation_strength +
        0.20 * infra_score +
        0.15 * growth_score +
        0.15 * metro_access +
        0.10 * crime_safety
    ) * 100

    return {
        "predicted_price": predicted_price,
        "investment_score": investment_score
    }