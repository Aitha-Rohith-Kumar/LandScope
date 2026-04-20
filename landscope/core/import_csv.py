import csv
from core.models import Plot

def import_csv_data(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Plot.objects.create(
                title=row['title'],
                location=row['location'],
                price=float(row['price']),
                area_sqft=float(row['area_sqft']),
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                metro_distance=float(row['metro_distance']),
                crime_rate=float(row['crime_rate']),
                pollution=float(row['pollution']),
                infrastructure=float(row['infrastructure'])
            )