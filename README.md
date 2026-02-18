# Moped Analyser

Using google forms I have been recording:
- date
- odometer
- amount of fuel
- cost of fuel/l
- total spend


This is stored in a google sheets document. I pull this data from that document, make some calculations and make that accessable via API.

The calculations we can make from our data points are:
- fuel effiency in l/100km.
- fuel cost per km
- how much does 1km cost
- km between fill ups
- do these numbers change over time? (i expect not) (or is this something we would like to see visualised?)
- cost of fuel per month

We also have a simple reminder of when do to maintenance (it's every 1k and 3k). I bet this can be integrated to notification, MQTT for example.

I should add data validation - does KM only go up, are fuel costs consistant (they would be).

Really amazing that I can get data out of this! It look many months to get here (Now is February, moped went into winter storage in November) but I am really impressed.

I am not making any calculations - I am calling an API that has already made the calculation - which is very intersting concept allowing us to define where processing is performed.

## Monthly Summary
```
    {
        "month": "2025-08",
        "total_distance_km": 322.0,
        "total_fuel_liters": 7.52,
        "l_per_100km": 2.34,
        "total_cost": 13.69
    },
```

## Summary between top ups
```
   {
        "date": "2025-09-08",
        "distance_km": 150.0,
        "fuel_liters": 3.47,
        "l_per_100km": 2.31,
        "cost": 6.83,
        "cost_per_km": 0.046,
        "days": 4
    },
```
And here we see the funny thing about the moped - I struggle to get 10 euro of fuel into it.

I see optimisation in knowing the right time to drop 7 euro in without it overflowing :-D