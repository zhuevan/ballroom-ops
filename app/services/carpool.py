import sqlite3
from collections import defaultdict

DB_NAME = "ballroom.db"


# -------------------------
# STEP 1: Fetch raw rows
# -------------------------
def fetch_signups_for_date(event_date):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT m.name, s.is_driver, s.seats, l.time
    FROM signups s
    JOIN members m ON s.member_id = m.id
    JOIN lessons l ON s.lesson_id = l.id
    WHERE l.event_date = ?
    """, (event_date,))

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------
# STEP 2: Parse lesson time
# -------------------------
# def extract_time(lesson_str):
#     # "7pm - Intermediate" → "7pm"
#     return lesson_str.split(" - ")[0].strip()

def extract_time(time_str):
    return time_str.strip()


# -------------------------
# STEP 3: Combine into person-night
# -------------------------
def group_people(rows):
    people = {}

    for name, is_driver, seats, lesson_str in rows:
        time = extract_time(lesson_str)

        if name not in people:
            people[name] = {
                "name": name,
                "is_driver": is_driver,
                "seats": seats,
                "times": []
            }

        people[name]["times"].append(time)

    return list(people.values())


# -------------------------
# STEP 4: Get departure time
# -------------------------
def get_departure_time(times):
    # assumes times like ["6pm", "7pm", "9pm"]
    def time_to_number(t):
        num = int(t.replace("pm", "").replace("am", ""))
        if "pm" in t and num != 12:
            num += 12
        return num

    return sorted(times, key=time_to_number)[0]


# -------------------------
# STEP 5: Group by departure
# -------------------------
def group_by_departure(people):
    groups = defaultdict(list)

    for person in people:
        departure = get_departure_time(person["times"])
        groups[departure].append(person)

    return groups


# -------------------------
# STEP 6: Split drivers/riders
# -------------------------
def split_drivers_riders(group):
    drivers = []
    riders = []

    for p in group:
        if p["is_driver"] == "driver":
            drivers.append({
                "name": p["name"],
                "seats": p["seats"]
            })
        elif p["is_driver"] == "rider":
            riders.append({
                "name": p["name"]
            })
        # "self" → ignored

    return drivers, riders


# -------------------------
# STEP 7: Assign carpools
# -------------------------
def assign_carpools(drivers, riders):
    # biggest cars first
    drivers = sorted(drivers, key=lambda d: d["seats"], reverse=True)

    cars = []

    for driver in drivers:
        if not riders:
            break

        car = {
            "driver": driver["name"],
            "passengers": []
        }

        capacity = driver["seats"]

        while capacity > 0 and riders:
            rider = riders.pop(0)
            car["passengers"].append(rider["name"])
            capacity -= 1

        cars.append(car)

    if riders:
        print("WARNING: Not enough seats")
        print("Unassigned:", [r["name"] for r in riders])

    return cars


# -------------------------
# STEP 8: MAIN FUNCTION
# -------------------------
def generate_carpools_for_date(event_date):
    rows = fetch_signups_for_date(event_date)

    people = group_people(rows)

    departure_groups = group_by_departure(people)

    result = {}

    def time_to_number(t):
        num = int(t.replace("pm", "").replace("am", ""))
        if "pm" in t and num != 12:
            num += 12
        return num

    for departure_time in sorted(departure_groups.keys(), key=time_to_number):
        group = departure_groups[departure_time]
        drivers, riders = split_drivers_riders(group)
        cars = assign_carpools(drivers, riders)
        result[departure_time] = cars

    return result


# -------------------------
# TEST RUN
# -------------------------
if __name__ == "__main__":
    # CHANGE THIS to match your data
    test_date = "2025-02-17"

    carpools = generate_carpools_for_date(test_date)

    for time, cars in carpools.items():
        print(f"\n=== Departure: {time} ===")

        for i, car in enumerate(cars):
            print(f"Car {i+1}")
            print(" Driver:", car["driver"])
            print(" Riders:", car["passengers"])