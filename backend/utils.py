import math
from datetime import datetime

def create_features(car, bike, bus, truck, traffic):

    now = datetime.now()

    hour = now.hour
    minute = now.minute
    day = now.day
    month = now.month
    year = now.year
    dayofweek = now.weekday()
    weekofyear = now.isocalendar().week

    is_weekend = 1 if dayofweek >= 5 else 0

    is_peak_hour = 1 if (7 <= hour <= 10 or 17 <= hour <= 20) else 0

    total = car + bike + bus + truck

    heavy_vehicle = bus + truck

    two_wheel_ratio = bike / total if total else 0

    four_wheel_ratio = (car + bus + truck) / total if total else 0

    hour_sin = math.sin(2 * math.pi * hour / 24)
    hour_cos = math.cos(2 * math.pi * hour / 24)

    month_sin = math.sin(2 * math.pi * month / 12)
    month_cos = math.cos(2 * math.pi * month / 12)

    return {
        "hour": hour,
        "minute": minute,
        "day": day,
        "month": month,
        "year": year,
        "dayofweek": dayofweek,
        "weekofyear": weekofyear,
        "is_weekend": is_weekend,
        "is_peak_hour": is_peak_hour,
        "HeavyVehicle": heavy_vehicle,
        "TwoWheelRatio": two_wheel_ratio,
        "FourWheelRatio": four_wheel_ratio,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "month_sin": month_sin,
        "month_cos": month_cos
    }