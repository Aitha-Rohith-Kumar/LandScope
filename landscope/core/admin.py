from django.contrib import admin
from .models import Plot
from .ml_engine import run_ml_pipeline
import random

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):

    list_display = (
        'title','latitude','longitude','location',
        'metro_distance','crime_rate','pollution','infrastructure',
        'price','predicted_price','investment_score','is_approved'
    )

    list_editable = ('is_approved',)

    def save_model(self, request, obj, form, change):

        # 🔥 RUN ONLY ON FIRST APPROVAL
        if obj.is_approved and (not change or obj.investment_score is None):

            # ✅ FILL ONLY IF EMPTY OR INVALID

            if not obj.metro_distance:
                obj.metro_distance = random.uniform(1, 10)

            if not obj.crime_rate:
                obj.crime_rate = random.uniform(1, 10)

            if not obj.pollution:
                obj.pollution = random.uniform(1, 10)

            if not obj.infrastructure:
                obj.infrastructure = random.uniform(1, 10)

            # ✅ RUN ML
            result = run_ml_pipeline(obj)

            obj.predicted_price = result.get("predicted_price", obj.price)
            obj.investment_score = result.get("investment_score", 0)

        super().save_model(request, obj, form, change)