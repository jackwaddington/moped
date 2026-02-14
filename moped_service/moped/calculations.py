from collections import defaultdict
from decimal import Decimal


def fuel_efficiency(qs):
    """Calculate l/100km for a queryset of FuelEntry objects.
    Returns None if not enough data."""
    entries = qs.order_by("odometer_km")
    if entries.count() < 2:
        return None

    first = entries.first()
    last = entries.last()
    distance = last.odometer_km - first.odometer_km
    if distance <= 0:
        return None

    total_liters = sum(e.fuel_liters for e in entries.exclude(pk=first.pk))
    return round((total_liters / distance) * 100, 2)


def cost_per_km(qs):
    """Calculate cost per km driven.
    Returns None if not enough data."""
    entries = qs.order_by("odometer_km")
    if entries.count() < 2:
        return None

    first = entries.first()
    last = entries.last()
    distance = last.odometer_km - first.odometer_km
    if distance <= 0:
        return None

    total_cost = sum(
        float(e.total_spend) for e in entries.exclude(pk=first.pk) if e.total_spend
    )
    return round(total_cost / distance, 3)


def fillup_pairs(qs):
    """Analyze each segment between consecutive fillups.
    Returns a list of dicts with per-segment stats."""
    entries = list(qs.order_by("odometer_km"))
    if len(entries) < 2:
        return []

    pairs = []
    for i in range(1, len(entries)):
        prev = entries[i - 1]
        curr = entries[i]

        distance = curr.odometer_km - prev.odometer_km
        days = (curr.timestamp - prev.timestamp).days
        l_per_100km = round((curr.fuel_liters / distance) * 100, 2) if distance > 0 else 0
        cost_km = round(float(curr.total_spend) / distance, 3) if distance > 0 and curr.total_spend else None

        pairs.append({
            "date": curr.timestamp.date().isoformat(),
            "distance_km": round(distance, 1),
            "fuel_liters": curr.fuel_liters,
            "l_per_100km": l_per_100km,
            "cost": float(curr.total_spend) if curr.total_spend else None,
            "cost_per_km": cost_km,
            "days": days,
        })

    return pairs


def monthly_summary(qs):
    """Group fillup data by month.
    Uses fillup_pairs so first entry's fuel is excluded."""
    pairs = fillup_pairs(qs)
    if not pairs:
        return []

    months = defaultdict(lambda: {"distance": 0, "fuel": 0, "cost": Decimal("0")})

    for pair in pairs:
        month_key = pair["date"][:7]  # "2025-01"
        months[month_key]["distance"] += pair["distance_km"]
        months[month_key]["fuel"] += pair["fuel_liters"]
        if pair["cost"]:
            months[month_key]["cost"] += Decimal(str(pair["cost"]))

    return [
        {
            "month": month,
            "total_distance_km": round(data["distance"], 1),
            "total_fuel_liters": round(data["fuel"], 2),
            "l_per_100km": round((data["fuel"] / data["distance"]) * 100, 2) if data["distance"] > 0 else 0,
            "total_cost": float(round(data["cost"], 2)),
        }
        for month, data in sorted(months.items())
    ]
