# CP-047 FleetPulse: Fleet Fuel Efficiency and Maintenance Analytics System

## Team
[SRIKANTH K] ([1AT25CS182]), Python track

## How to run
Needs Python 3 (no extra libraries).

```
python fleetpulse.py
```

Type `y` at the first prompt to load sample data (3 vehicles, 8 fuel fills).

## Features that work
Core Features
1. Register vehicles with number, type and current odometer reading (also stores last service date and odometer)
2. Record fuel fills with litres, cost and odometer reading
3. Calculate mileage (km/l) per fill and average mileage per vehicle
4. Flag vehicles due for service by kilometres (every 10,000 km) or by date (every 180 days)
5. Show cost per km for each vehicle and the worst performer (highest Rs/km)

Extra options
- Record a service as done (resets the service counters)
- List all vehicles

Wrong input handled
- Letters, blanks or negative values where a number is expected
- Litres or cost of zero
- Odometer reading lower than the last reading
- Duplicate or unknown vehicle numbers
- Invalid dates (e.g. 31-02-2026), future service dates
- Invalid menu choices
- Reports with no vehicles or no fuel fills (no divide-by-zero crash)

## Sample run
```
--- Fuel Fill (wrong input) ---
  Vehicle number:   Last odometer reading for MH12XY9999: 15,000 km
  Litres filled: -5
  Error: value must be > 0.
  Litres filled: x
  Error: please enter a number, e.g. 45 or 45.5
  Litres filled: 20
  Total cost (Rs): 1500
  Odometer reading now (km): 14000
  Error: reading must be more than the last reading (15,000 km). Odometers only go up.
  Odometer reading now (km): 15400
  Fill saved. 400 km since last reading -> 20.00 km/l (Rs 75.00 per litre).

--- Mileage Report ---
  KA02CD5678 (Van)
    Fill   Odometer      Km   Litres    Km/l
    1        20,420     420     40.0   10.50
    2        20,830     410     38.0   10.79
    3        21,250     420     42.0   10.00
    Average mileage: 10.42 km/l over 1,250 km

--- Service Due Check ---
  Rule: service due every 10,000 km or every 180 days.
  DUE   KA01AB1234   253 days since service
  DUE   KA02CD5678   10,250 km since service
  OK    KA03EF9012   next in 8,570 km or 151 days
  2 vehicle(s) due for service.

--- Cost per Km ---
  Vehicle     Type          Km   Fuel cost   Rs/km
  KA01AB1234  Truck        930   22,530.00   24.23
  KA02CD5678  Van        1,250   11,400.00    9.12
  KA03EF9012  Car          930    6,090.00    6.55

  Worst performer: KA01AB1234 (Truck) at Rs 24.23 per km
```
