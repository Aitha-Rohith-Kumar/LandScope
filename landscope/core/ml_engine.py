from .models import Plot
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

def run_ml_pipeline():
    
    plots = Plot.objects.all()
    
    # Convert Django queryset to DataFrame
    data = []
    for plot in plots:
        data.append({
            "id": plot.id,
            "price": plot.price,
            "metro_distance": plot.metro_distance,
            "crime_rate": plot.crime_rate,
            "pollution": plot.pollution,
            "infrastructure": plot.infrastructure,
            "area_sqft": plot.area_sqft,
            "growth_index": plot.infrastructure * 0.5 + (10 - plot.metro_distance) * 0.5
        })
    
    df = pd.DataFrame(data)
    
    # Features and Target
    X = df[['metro_distance','crime_rate','pollution','infrastructure','area_sqft','growth_index']]
    y = df['price']
    
    # Train Random Forest
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    predictions = model.predict(X)
    
    df['predicted_price'] = predictions
    
    # Simple Investment Score Formula
    # Normalize values
    valuation_strength = df['predicted_price'] / df['predicted_price'].max()
    infra_score = df['infrastructure'] / 10
    growth_score = df['growth_index'] / df['growth_index'].max()

    # Convert metro distance to accessibility score (inverse)
    metro_access = 1 - (df['metro_distance'] / df['metro_distance'].max())

    # Convert crime to safety score (inverse)
    crime_safety = 1 - (df['crime_rate'] / df['crime_rate'].max())

    # Advanced weighted scoring
    df['investment_score'] = (
        0.40 * valuation_strength +
        0.20 * infra_score +
        0.15 * growth_score +
        0.15 * metro_access +
        0.10 * crime_safety
    ) * 100
    
    # Save results back to DB
    for _, row in df.iterrows():
        plot = Plot.objects.get(id=row['id'])
        plot.predicted_price = row['predicted_price']
        plot.investment_score = row['investment_score']
        plot.save()
    
    return r2_score(y, predictions)
