import os
import csv
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TOMTOM_API_KEY")

if not API_KEY:
    raise ValueError("TOMTOM_API_KEY not found")


# -----------------------------------
# Routes
# -----------------------------------

routes = [
    {
        "name": "Silk Board → Marathahalli",
        "start_lat": 12.9176,
        "start_lon": 77.6238,
        "end_lat": 12.9569,
        "end_lon": 77.7011
    },

    {
        "name": "Marathahalli → Silk Board",
        "start_lat": 12.9569,
        "start_lon": 77.7011,
        "end_lat": 12.9176,
        "end_lon": 77.6238
    },

    {
        "name": "KR Puram → Hebbal",
        "start_lat": 13.0075,
        "start_lon": 77.6959,
        "end_lat": 13.0358,
        "end_lon": 77.5970
    },

    {
        "name": "Hebbal → KR Puram",
        "start_lat": 13.0358,
        "start_lon": 77.5970,
        "end_lat": 13.0075,
        "end_lon": 77.6959
    }
]


# -----------------------------------
# Settings
# -----------------------------------

COLLECTIONS = 12
INTERVAL_SECONDS = 15 * 60

file_path = "data/traffic.csv"

os.makedirs("data", exist_ok=True)


# -----------------------------------
# Function to collect one round
# -----------------------------------

def collect_round(round_number):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print("\n================================")
    print(f"🚦 Collection Round {round_number}/{COLLECTIONS}")
    print("Timestamp:", timestamp)
    print("================================")

    file_exists = os.path.exists(file_path)

    with open(
        file_path,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Add header if CSV doesn't exist
        if not file_exists:

            writer.writerow([
                "timestamp",
                "route",
                "travel_time_minutes",
                "estimated_baseline_minutes",
                "traffic_delay_minutes",
                "distance_km"
            ])

        # -----------------------------------
        # Collect each route
        # -----------------------------------

        for route in routes:

            print("\n--------------------------------")
            print("Collecting:", route["name"])
            print("--------------------------------")

            url = (
                f"https://api.tomtom.com/routing/1/calculateRoute/"
                f"{route['start_lat']},{route['start_lon']}:"
                f"{route['end_lat']},{route['end_lon']}/json"
            )

            params = {
                "key": API_KEY,
                "traffic": "true"
            }

            try:

                response = requests.get(
                    url,
                    params=params,
                    timeout=30
                )

                print("HTTP Status:", response.status_code)

                if response.status_code != 200:

                    print("❌ API request failed")
                    print(response.text)

                    continue

                data = response.json()

                route_data = data["routes"][0]
                summary = route_data["summary"]

                # -----------------------------------
                # Calculate metrics
                # -----------------------------------

                travel_time = (
                    summary["travelTimeInSeconds"] / 60
                )

                traffic_delay = (
                    summary["trafficDelayInSeconds"] / 60
                )

                estimated_baseline = (
                    travel_time - traffic_delay
                )

                distance = (
                    summary["lengthInMeters"] / 1000
                )

                # -----------------------------------
                # Save row
                # -----------------------------------

                writer.writerow([
                    timestamp,
                    route["name"],
                    round(travel_time, 2),
                    round(estimated_baseline, 2),
                    round(traffic_delay, 2),
                    round(distance, 2)
                ])

                print("✅ Data collected")

                print(
                    "Travel time:",
                    round(travel_time, 2),
                    "minutes"
                )

                print(
                    "Traffic delay:",
                    round(traffic_delay, 2),
                    "minutes"
                )

                print(
                    "Distance:",
                    round(distance, 2),
                    "km"
                )

            except Exception as error:

                print("❌ Error:", error)


# -----------------------------------
# Main collection loop
# -----------------------------------

print("\n================================")
print("🚦 Bengaluru Traffic Collector")
print("================================")

print(f"Total rounds: {COLLECTIONS}")
print("Interval: 15 minutes")
print("Expected duration: 3 hours")
print("================================")


for round_number in range(1, COLLECTIONS + 1):

    collect_round(round_number)

    # Don't wait after the final round
    if round_number < COLLECTIONS:

        print("\n⏳ Waiting 15 minutes...")
        print(
            f"Next collection will be round "
            f"{round_number + 1}/{COLLECTIONS}"
        )

        time.sleep(INTERVAL_SECONDS)


print("\n================================")
print("✅ ALL COLLECTIONS COMPLETED")
print("================================")
print("Data saved to:", file_path)
