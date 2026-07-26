"""
This script generates the Normal Baseline dataset. Rather than generating completely 
random noise, this script builds persistent, stateful profiles for 80 distinct entities 
(Human Users, Service Accounts, and Edge Devices). It assigns them consistent IP 
addresses, fixed working hours, and habitual resource access patterns. It then iterates 
through a 7-day time window, logging their routine behavior to create a realistic, 
benign baseline for the AI model to learn from.
"""

import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
from schema import AccessLog, EntityType, LabelType

# Initialize Faker for realistic mock data generation
fake = Faker()

# -------------------------------------------------------------------
# 1. PROFILE BUILDER: Create persistent entities with fixed habits
# -------------------------------------------------------------------
def create_entity_profiles(num_users=50, num_services=10, num_devices=20):
    profiles = []

    # Generate Human User Profiles
    for i in range(num_users):
        profiles.append({
            "entity_id": f"usr_{1000 + i}",
            "entity_type": EntityType.USER,
            "home_ip": fake.ipv4_public(),
            "location": f"{fake.city()}, {fake.country()}",
            "device_fingerprint": f"macOS 14.{random.randint(0, 3)} | Chrome 12{random.randint(0, 9)}.0",
            "working_hours": (8, 18),  # 8 AM to 6 PM
            "common_resources": ["/dashboard", "/profile", "/reports", "/api/v1/data"],
            "auth_method": "token"
        })

    # Generate Service Account Profiles (Automated, run 24/7)
    for i in range(num_services):
        profiles.append({
            "entity_id": f"svc_{2000 + i}",
            "entity_type": EntityType.SERVICE_ACCOUNT,
            "home_ip": "10.0.0." + str(random.randint(10, 250)),
            "location": "DataCenter-US-East",
            "device_fingerprint": "Linux x86_64 | Daemon 2.1",
            "working_hours": (0, 23),  # All day
            "common_resources": ["/internal/sync", "/internal/backup", "/healthcheck"],
            "auth_method": "certificate"
        })

    # Generate Edge Device Profiles (IoT / Hardware Gateways)
    for i in range(num_devices):
        profiles.append({
            "entity_id": f"dev_{3000 + i}",
            "entity_type": EntityType.EDGE_DEVICE,
            "home_ip": f"192.168.1.{100 + i}",
            "location": f"{fake.city()}, Factory-Floor",
            "device_fingerprint": f"RTOS v{random.randint(1, 4)}.0 | MAC:{fake.mac_address()}",
            "working_hours": (0, 23),
            "common_resources": ["/telemetry/upload", "/status"],
            "auth_method": "biometric" if random.random() > 0.8 else "token"
        })

    return profiles

# -------------------------------------------------------------------
# 2. LOG GENERATOR: Simulate access logs over a time window
# -------------------------------------------------------------------
def generate_normal_logs(profiles, start_time, duration_days=7):
    logs = []
    
    # Iterate day by day
    for day in range(duration_days):
        current_date = start_time + timedelta(days=day)

        for profile in profiles:
            # Determine how many sessions this entity initiates today
            if profile["entity_type"] == EntityType.USER:
                # Users log in 3 to 8 times during their workday
                num_events = random.randint(3, 8)
            else:
                # Services & Devices ping regularly (15 to 30 events per day)
                num_events = random.randint(15, 30)

            for _ in range(num_events):
                # Calculate time within active working hours
                start_hour, end_hour = profile["working_hours"]
                event_hour = random.randint(start_hour, end_hour)
                event_minute = random.randint(0, 59)
                event_second = random.randint(0, 59)
                
                event_timestamp = current_date.replace(
                    hour=event_hour, minute=event_minute, second=event_second
                )

                # Build a valid log strictly using the Pydantic schema
                log_item = AccessLog(
                    entity_id=profile["entity_id"],
                    entity_type=profile["entity_type"],
                    timestamp=event_timestamp,
                    source_ip=profile["home_ip"],
                    geo_location=profile["location"],
                    resource_accessed=random.choice(profile["common_resources"]),
                    auth_method=profile["auth_method"],
                    session_duration=round(random.uniform(1.0, 300.0), 2),
                    command_sequence=["GET /index", "POST /data"] if profile["entity_type"] == EntityType.USER else ["EXEC /sync"],
                    device_fingerprint=profile["device_fingerprint"],
                    label=LabelType.NORMAL
                )
                
                # Store as a dictionary for easy Pandas conversion
                logs.append(log_item.model_dump())

    return logs

# -------------------------------------------------------------------
# 3. EXECUTION & EXPORT
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Generating persistent entity profiles...")
    # Expanded entity pool for higher volume
    profiles = create_entity_profiles(num_users=150, num_services=30, num_devices=50)

    print("Simulating 14 days of normal access events...")
    start_date = datetime(2026, 7, 1)
    raw_logs = generate_normal_logs(profiles, start_date, duration_days=14)

    df = pd.DataFrame(raw_logs)
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    export_path = "exports/normal_baseline_logs.csv"
    df.to_csv(export_path, index=False)

    print(f"\nSuccess! Generated {len(df)} normal logs.")
    print(f"File saved to: {export_path}")