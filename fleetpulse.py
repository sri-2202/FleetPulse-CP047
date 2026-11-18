"""
CP-047 FleetPulse: Fleet Fuel Efficiency and Maintenance Analytics System
Python track - menu-driven console application.

Data is kept in two lists:
  vehicles - one dictionary per vehicle
  fills    - one dictionary per fuel fill (linked to a vehicle by its number)
"""

import math
from datetime import date, datetime

# ---------------- Business rules (change here if needed) ----------------
SERVICE_KM = 10000        # service due every 10,000 km since last service
SERVICE_DAYS = 180        # ... or every 180 days since last service
VEHICLE_TYPES = ["Truck", "Van", "Car", "Bus"]
DATE_FORMAT = "%d-%m-%Y"  # dates are typed as DD-MM-YYYY, e.g. 18-11-2026

# ---------------- Data ----------------
vehicles = []   # {"number", "type", "start_odo", "current_odo", "last_service_odo", "last_service_date"}
fills = []      # {"number", "litres", "cost", "odo"}


# ======================= Input helpers (wrong-input handling) =======================

def read_text(prompt):
    """Keep asking until the user types something that is not empty."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("  Error: this cannot be empty. Try again.")


def read_number(prompt, minimum, allow_equal=True):
    """
    Read a number (decimals allowed). Rejects letters, blanks, NaN/infinity
    and anything below the minimum. If allow_equal is False the number must be
    strictly greater than the minimum (used for litres and cost, which must be > 0).
    """
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print("  Error: please enter a number, e.g. 45 or 45.5")
            continue
        if not math.isfinite(value):
            print("  Error: please enter a real number.")
            continue
        if value < minimum or (not allow_equal and value == minimum):
            sign = ">=" if allow_equal else ">"
            print(f"  Error: value must be {sign} {minimum:g}.")
            continue
        return value


def read_date(prompt, allow_blank_for_today=False):
    """Read a date in DD-MM-YYYY. Rejects bad formats and impossible dates like 31-02-2026."""
    while True:
        text = input(prompt).strip()
        if text == "" and allow_blank_for_today:
            return date.today()
        try:
            return datetime.strptime(text, DATE_FORMAT).date()
        except ValueError:
            print("  Error: enter a valid date as DD-MM-YYYY, e.g. 18-11-2026")


def read_vehicle_type():
    """Show the allowed types as a numbered list and read a valid choice."""
    for i, vtype in enumerate(VEHICLE_TYPES, start=1):
        print(f"   {i}. {vtype}")
    while True:
        choice = input("  Choose type (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(VEHICLE_TYPES):
            return VEHICLE_TYPES[int(choice) - 1]
        print(f"  Error: choose a number from 1 to {len(VEHICLE_TYPES)}.")


def clean_number(text):
    """Vehicle numbers are stored in capitals without spaces: 'ka 01 ab 1234' -> 'KA01AB1234'."""
    return text.replace(" ", "").replace("-", "").upper()


def find_vehicle(number):
    """Return the vehicle dictionary with this number, or None if it does not exist."""
    for v in vehicles:
        if v["number"] == number:
            return v
    return None


def ask_existing_vehicle():
    """Ask for a vehicle number and return the vehicle, or None if not found."""
    if not vehicles:
        print("  No vehicles registered yet. Register a vehicle first (option 1).")
        return None
    number = clean_number(read_text("  Vehicle number: "))
    vehicle = find_vehicle(number)
    if vehicle is None:
        print(f"  Error: vehicle {number} is not registered.")
    return vehicle


def fills_of(number):
    """All fuel fills for one vehicle, in the order they were recorded."""
    return [f for f in fills if f["number"] == number]


# ======================= Calculations (used by features 3 and 5) =======================

def mileage_per_fill(vehicle):
    """
    Returns a list of (fill, km_driven, km_per_litre) for each fill.
    km driven = this fill's odometer - previous odometer.
    For the first fill, the previous odometer is the odometer at registration.
    """
    result = []
    previous_odo = vehicle["start_odo"]
    for f in fills_of(vehicle["number"]):
        km = f["odo"] - previous_odo
        result.append((f, km, km / f["litres"]))
        previous_odo = f["odo"]
    return result


def totals(vehicle):
    """Total km driven, total litres and total fuel cost for a vehicle."""
    vehicle_fills = fills_of(vehicle["number"])
    total_km = vehicle["current_odo"] - vehicle["start_odo"]
    total_litres = sum(f["litres"] for f in vehicle_fills)
    total_cost = sum(f["cost"] for f in vehicle_fills)
    return total_km, total_litres, total_cost


# ======================= Core Feature 1: Register vehicle =======================

def register_vehicle():
    print("\n--- Register Vehicle ---")
    number = clean_number(read_text("  Vehicle number (e.g. KA01AB1234): "))
    if find_vehicle(number) is not None:
        print(f"  Error: vehicle {number} is already registered.")
        return

    vtype = read_vehicle_type()
    odo = read_number("  Current odometer reading (km): ", 0)

    # Needed for Feature 4 (service due check)
    while True:
        service_date = read_date("  Last service date (DD-MM-YYYY): ")
        if service_date > date.today():
            print("  Error: last service date cannot be in the future.")
        else:
            break
    while True:
        service_odo = read_number("  Odometer at last service (km): ", 0)
        if service_odo > odo:
            print("  Error: odometer at last service cannot be more than current odometer.")
        else:
            break

    vehicles.append({
        "number": number,
        "type": vtype,
        "start_odo": odo,
        "current_odo": odo,
        "last_service_odo": service_odo,
        "last_service_date": service_date,
    })
    print(f"  Vehicle {number} ({vtype}) registered at {odo:,.0f} km.")


# ======================= Core Feature 2: Record fuel fill =======================

def record_fuel_fill():
    print("\n--- Record Fuel Fill ---")
    vehicle = ask_existing_vehicle()
    if vehicle is None:
        return

    print(f"  Last odometer reading for {vehicle['number']}: {vehicle['current_odo']:,.0f} km")
    litres = read_number("  Litres filled: ", 0, allow_equal=False)
    cost = read_number("  Total cost (Rs): ", 0, allow_equal=False)
    while True:
        odo = read_number("  Odometer reading now (km): ", 0)
        if odo <= vehicle["current_odo"]:
            print(f"  Error: reading must be more than the last reading "
                  f"({vehicle['current_odo']:,.0f} km). Odometers only go up.")
        else:
            break

    km = odo - vehicle["current_odo"]
    fills.append({"number": vehicle["number"], "litres": litres, "cost": cost, "odo": odo})
    vehicle["current_odo"] = odo     # keep the vehicle's odometer up to date
    print(f"  Fill saved. {km:,.0f} km since last reading -> {km / litres:.2f} km/l "
          f"(Rs {cost / litres:.2f} per litre).")


# ======================= Core Feature 3: Mileage report =======================

def mileage_report():
    print("\n--- Mileage Report ---")
    if not vehicles:
        print("  No vehicles registered yet.")
        return

    for v in vehicles:
        print(f"\n  {v['number']} ({v['type']})")
        rows = mileage_per_fill(v)
        if not rows:
            print("    No fuel fills recorded yet - mileage not available.")
            continue
        print(f"    {'Fill':<5}{'Odometer':>10}{'Km':>8}{'Litres':>9}{'Km/l':>8}")
        for i, (f, km, kmpl) in enumerate(rows, start=1):
            print(f"    {i:<5}{f['odo']:>10,.0f}{km:>8,.0f}{f['litres']:>9.1f}{kmpl:>8.2f}")
        total_km, total_litres, _ = totals(v)
        # Average = total km / total litres (not the average of the per-fill numbers,
        # because a big fill should count more than a small one)
        print(f"    Average mileage: {total_km / total_litres:.2f} km/l "
              f"over {total_km:,.0f} km")


# ======================= Core Feature 4: Service due check =======================

def service_due_check():
    print("\n--- Service Due Check ---")
    if not vehicles:
        print("  No vehicles registered yet.")
        return
    print(f"  Rule: service due every {SERVICE_KM:,} km or every {SERVICE_DAYS} days.")
    today = read_date("  Today's date (DD-MM-YYYY, press Enter for today): ",
                      allow_blank_for_today=True)

    due_count = 0
    for v in vehicles:
        km_since = v["current_odo"] - v["last_service_odo"]
        days_since = (today - v["last_service_date"]).days
        if days_since < 0:
            print(f"  {v['number']}: today's date is before its last service date - skipped.")
            continue

        reasons = []
        if km_since >= SERVICE_KM:
            reasons.append(f"{km_since:,.0f} km since service")
        if days_since >= SERVICE_DAYS:
            reasons.append(f"{days_since} days since service")

        if reasons:
            due_count += 1
            print(f"  DUE   {v['number']:<12} " + " and ".join(reasons))
        else:
            km_left = SERVICE_KM - km_since
            days_left = SERVICE_DAYS - days_since
            print(f"  OK    {v['number']:<12} next in {km_left:,.0f} km or {days_left} days")
    print(f"  {due_count} vehicle(s) due for service.")


# ======================= Core Feature 5: Cost per km and worst performer =======================

def cost_report():
    print("\n--- Cost per Km ---")
    if not vehicles:
        print("  No vehicles registered yet.")
        return

    worst = None
    worst_cpk = -1
    print(f"  {'Vehicle':<12}{'Type':<7}{'Km':>9}{'Fuel cost':>12}{'Rs/km':>8}")
    for v in vehicles:
        total_km, _, total_cost = totals(v)
        if total_km == 0:
            print(f"  {v['number']:<12}{v['type']:<7}   no fuel fills recorded")
            continue
        cpk = total_cost / total_km
        print(f"  {v['number']:<12}{v['type']:<7}{total_km:>9,.0f}{total_cost:>12,.2f}{cpk:>8.2f}")
        if cpk > worst_cpk:
            worst, worst_cpk = v, cpk

    if worst is None:
        print("  No vehicle has fuel data yet, so there is no worst performer.")
    else:
        print(f"\n  Worst performer: {worst['number']} ({worst['type']}) "
              f"at Rs {worst_cpk:.2f} per km")


# ======================= Extra options =======================

def record_service():
    """Marks a vehicle as serviced so the Feature 4 check starts again from today."""
    print("\n--- Record Service Done ---")
    vehicle = ask_existing_vehicle()
    if vehicle is None:
        return
    while True:
        service_date = read_date("  Service date (DD-MM-YYYY, press Enter for today): ",
                                 allow_blank_for_today=True)
        if service_date < vehicle["last_service_date"]:
            print("  Error: date is before the previous service.")
        elif service_date > date.today():
            print("  Error: service date cannot be in the future.")
        else:
            break
    vehicle["last_service_date"] = service_date
    vehicle["last_service_odo"] = vehicle["current_odo"]
    print(f"  Service recorded for {vehicle['number']} at {vehicle['current_odo']:,.0f} km.")


def list_vehicles():
    print("\n--- All Vehicles ---")
    if not vehicles:
        print("  No vehicles registered yet.")
        return
    print(f"  {'Vehicle':<12}{'Type':<7}{'Odometer':>10}  {'Last service':<12}{'at km':>9}{'Fills':>7}")
    for v in vehicles:
        print(f"  {v['number']:<12}{v['type']:<7}{v['current_odo']:>10,.0f}  "
              f"{v['last_service_date'].strftime(DATE_FORMAT):<12}"
              f"{v['last_service_odo']:>9,.0f}{len(fills_of(v['number'])):>7}")


def load_sample_data():
    """Three vehicles with a few fills, so features 3-5 show real numbers in the demo."""
    samples = [
        ("KA01AB1234", "Truck", 45000, date(2026, 3, 10), 41000,
         [(80, 7600, 45320), (75, 7140, 45615), (82, 7790, 45930)]),
        ("KA02CD5678", "Van", 20000, date(2026, 9, 1), 11000,
         [(40, 3800, 20420), (38, 3610, 20830), (42, 3990, 21250)]),
        ("KA03EF9012", "Car", 12000, date(2026, 10, 20), 11500,
         [(30, 3150, 12480), (28, 2940, 12930)]),
    ]
    for number, vtype, odo, s_date, s_odo, vehicle_fills in samples:
        vehicles.append({"number": number, "type": vtype, "start_odo": odo,
                         "current_odo": odo, "last_service_odo": s_odo,
                         "last_service_date": s_date})
        for litres, cost, f_odo in vehicle_fills:
            fills.append({"number": number, "litres": litres, "cost": cost, "odo": f_odo})
            vehicles[-1]["current_odo"] = f_odo
    print("  Sample data loaded: 3 vehicles, 8 fuel fills.")


# ======================= Main menu =======================

MENU = """
========== FleetPulse ==========
 1. Register vehicle
 2. Record fuel fill
 3. Mileage report
 4. Service due check
 5. Cost per km and worst performer
 6. Record service done
 7. List all vehicles
 0. Exit
================================"""


def main():
    print("FleetPulse: Fleet Fuel Efficiency and Maintenance Analytics")
    if input("Load sample data? (y/n): ").strip().lower() == "y":
        load_sample_data()

    actions = {
        "1": register_vehicle,
        "2": record_fuel_fill,
        "3": mileage_report,
        "4": service_due_check,
        "5": cost_report,
        "6": record_service,
        "7": list_vehicles,
    }
    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        if choice in actions:
            actions[choice]()
        else:
            print("  Error: invalid choice. Enter a number from 0 to 7.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting FleetPulse.")
