# moped

Using google forms I have been recording:
	date
	odometer
	amount of fuel
	cost of fuel/l
	total spend


This is stored in a google sheets document. I want to pull the data from that document and add some data - for example for any way, we can pull info.

And by making calculations based on the data we are recording, we can work out:
- fuel effiency in l/100km.
- fuel cost per km
- do these numbers change over time? (i expect not) (or is this something we would like to see visualised?)
- cost of fuel per month (tricky one because we don't fill up once a month)
- we should be able to approximate km for any day - by diff between fill up date and next fill up date.


Really amazing that I can get data out of this! It look many months to get here (Now is February, moped went into winter storage in November) but I am really impressed. I am not making any calculations - I am calling an API that does or has done the calculation - which is very intersting concept allowing us to define where processing is performed.
```
    {
        "month": "2025-08",
        "total_distance_km": 322.0,
        "total_fuel_liters": 7.52,
        "l_per_100km": 2.34,
        "total_cost": 13.69
    },
```

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



Use an api to ask things like what is mpg, or also to see when should there be a service or oil change.


I want to go into more detail of how the fuel stuff is calculated - i think there are some mistakes there.

i want to be able to say how much 1km costs.

To make fueling easy - if i know i can do a certian km, and then dump in 6 or 10 euro of fuel - that's cool. but standing there dripping fuel in to try to get it to be okay is a bit lame. i really wihs they woudl just have a bigger fuel tank on these!!

it woudl be nice to have a reminder to put fuel in - or maybe no tbecause there is a fuel guage.

it would be nice to have a remidner to do an oil change.

we need to check ranges of data - we should know if km goes down, we should know if there are any big changes in economy etc.

