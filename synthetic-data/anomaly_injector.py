""" 
This script fulfills the project requirements for Extreme Class Imbalance and 
the Injected Attack Taxonomy. It imports the clean, normal baseline dataset 
and programmatically injects specific malicious anomalies and edge cases. 

By keeping this injection logic modularized and separate from the normal baseline 
generator, we ensure that attack distributions can be easily audited, tuned, 
and tracked without having to rebuild the entire dataset from scratch. 
The resulting dataset will contain roughly 97% normal traffic and 3% anomalies,
perfectly mirroring real-world cybersecurity environments.
"""

import random
from datetime import timedelta
import pandas as pd
from schema import LabelType
 

def inject_brute_force(df_target, num_attacks=3):
    """ 
    Simulates rapid, repeated failed authentication attempts from a single 
    source IP within a very short time window (e.g., 2 minutes).
    """
    injected_rows = []
    unique_users = df_target[df_target['entity_type'] == 'user']['entity_id'].unique()

    for _ in range(num_attacks):
        victim_id = random.choice(unique_users)
        attacker_ip = f"185.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
         
        base_time = df_target['timestamp'].sample(1).values[0]
        base_dt = pd.to_datetime(base_time)
 
        for i in range(random.randint(15, 20)):
            attack_time = base_dt + timedelta(seconds=i * random.randint(3, 8))
            injected_rows.append({
                "entity_id": victim_id,
                "entity_type": "user",
                "timestamp": attack_time,
                "source_ip": attacker_ip,
                "geo_location": "Unknown Location / VPN Node",
                "resource_accessed": "/login",
                "auth_method": "password",
                "session_duration": round(random.uniform(0.1, 1.5), 2),
                "command_sequence": ["POST /login (FAILED)"],
                "device_fingerprint": "Python-requests/2.31.0",
                "label": LabelType.BRUTE_FORCE.value
            })

    return injected_rows


def inject_impossible_travel(df_target, num_attacks=3):
    """ 
    Simulates the same entity logging in from two geographically distant 
    locations within a time gap that makes physical travel impossible.
    """
    injected_rows = []
    users = df_target[df_target['entity_type'] == 'user']

    for _ in range(num_attacks): 
        sample_log = users.sample(1).iloc[0]
        original_time = pd.to_datetime(sample_log['timestamp'])
         
        impossible_time = original_time + timedelta(minutes=15)
        
        injected_rows.append({
            "entity_id": sample_log['entity_id'],
            "entity_type": sample_log['entity_type'],
            "timestamp": impossible_time,
            "source_ip": "103.21.244.0",
            "geo_location": "Tokyo, Japan",  # Discrepancy with original baseline location
            "resource_accessed": "/api/v1/dashboard",
            "auth_method": "token",
            "session_duration": round(random.uniform(10.0, 100.0), 2),
            "command_sequence": ["GET /dashboard"],
            "device_fingerprint": sample_log['device_fingerprint'],
            "label": LabelType.IMPOSSIBLE_TRAVEL.value
        })

    return injected_rows


def inject_device_spoofing(df_target, num_attacks=3):
    """ 
    Simulates an existing user ID logging in successfully, but utilizing a 
    device fingerprint (OS/MAC) that has never been seen in their baseline.
    """
    injected_rows = []
    users = df_target[df_target['entity_type'] == 'user']

    for _ in range(num_attacks):
        sample_log = users.sample(1).iloc[0]
        event_time = pd.to_datetime(sample_log['timestamp']) + timedelta(hours=1)

        injected_rows.append({
            "entity_id": sample_log['entity_id'],
            "entity_type": sample_log['entity_type'],
            "timestamp": event_time,
            "source_ip": sample_log['source_ip'],
            "geo_location": sample_log['geo_location'],
            "resource_accessed": sample_log['resource_accessed'],
            "auth_method": "password",
            "session_duration": 45.0,
            "command_sequence": ["GET /profile"],
            "device_fingerprint": "Android 11 | Spoofed Build v4.1",  # Unrecognized fingerprint
            "label": LabelType.DEVICE_SPOOFING.value
        })

    return injected_rows


def inject_lateral_movement(df_target, num_attacks=2):
    """
     
    Simulates a compromised account accessing high-privilege resources or 
    executing command sequences it has never touched before.
    """
    injected_rows = []
    users = df_target[df_target['entity_type'] == 'user']

    high_value_targets = [
        "/admin/database/export",
        "/internal/root_ca_keys",
        "/finance/wire_transfers"
    ]

    for _ in range(num_attacks):
        sample_log = users.sample(1).iloc[0]
        event_time = pd.to_datetime(sample_log['timestamp']) + timedelta(minutes=30)

        injected_rows.append({
            "entity_id": sample_log['entity_id'],
            "entity_type": sample_log['entity_type'],
            "timestamp": event_time,
            "source_ip": sample_log['source_ip'],
            "geo_location": sample_log['geo_location'],
            "resource_accessed": random.choice(high_value_targets),
            "auth_method": "token",
            "session_duration": 310.0,
            "command_sequence": ["ELEVATE_PRIVILEGES", "READ /etc/shadow"],
            "device_fingerprint": sample_log['device_fingerprint'],
            "label": LabelType.LATERAL_MOVEMENT.value
        })

    return injected_rows


def inject_credential_stuffing(df_target, num_attacks=2):
    """
     
    Simulates an automated script trying many different User IDs from a 
    single source IP, resulting in a massive failure rate across the board.
    """
    injected_rows = []
    unique_users = df_target[df_target['entity_type'] == 'user']['entity_id'].unique()

    for _ in range(num_attacks):
        attacker_ip = f"45.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        base_time = pd.to_datetime(df_target['timestamp'].sample(1).values[0])

        # Try 30 different users rapidly from this single attacker IP
        for i in range(30):
            target_user = random.choice(unique_users)
            attack_time = base_time + timedelta(seconds=i * 2)

            injected_rows.append({
                "entity_id": target_user,
                "entity_type": "user",
                "timestamp": attack_time,
                "source_ip": attacker_ip,
                "geo_location": "Unknown / Datacenter",
                "resource_accessed": "/login",
                "auth_method": "password",
                "session_duration": 0.5,
                "command_sequence": ["POST /login (FAILED)"],
                "device_fingerprint": "Curl/7.68.0",
                "label": LabelType.CREDENTIAL_STUFFING.value
            })

    return injected_rows


def inject_low_and_slow(df_target, num_cases=2):
    """
     
    Simulates stealthy data exfiltration. A compromised user accesses sensitive 
    files very slowly, late at night, spread over multiple days to avoid 
    tripping standard, volume-based security alarms.
    """
    injected_rows = []
    users = df_target[df_target['entity_type'] == 'user']

    for _ in range(num_cases):
        victim = users.sample(1).iloc[0] 
        start_time = pd.to_datetime(df_target['timestamp'].min())

        # Spread small downloads over 5 consecutive days strictly at 3 AM
        for day_offset in range(5):
            stealth_time = start_time + timedelta(days=day_offset)
            stealth_time = stealth_time.replace(hour=3, minute=random.randint(0, 59))

            injected_rows.append({
                "entity_id": victim['entity_id'],
                "entity_type": victim['entity_type'],
                "timestamp": stealth_time,
                "source_ip": victim['source_ip'],
                "geo_location": victim['geo_location'],
                "resource_accessed": "/finance/db_backup_chunk",
                "auth_method": "token",
                "session_duration": 400.0,
                "command_sequence": ["GET /finance/db_backup_chunk"],
                "device_fingerprint": victim['device_fingerprint'],
                "label": LabelType.LOW_AND_SLOW.value
            })

    return injected_rows


def inject_insider_drift(df_target, num_cases=5):
    """
     
    Simulates a legitimate user slowly expanding their scope (e.g., getting a 
    promotion and accessing new docs) or working late hours. 
    This is classified as an EDGE CASE, not an attack. It is strictly used to 
    evaluate whether the ML model generates false-positives on legitimate human growth.
    """
    injected_rows = []
    users = df_target[df_target['entity_type'] == 'user']

    for _ in range(num_cases):
        sample_log = users.sample(1).iloc[0]
        # Late-night access for a normal user working extra hours
        late_night_time = pd.to_datetime(sample_log['timestamp']).replace(hour=2, minute=15)

        injected_rows.append({
            "entity_id": sample_log['entity_id'],
            "entity_type": sample_log['entity_type'],
            "timestamp": late_night_time,
            "source_ip": sample_log['source_ip'],
            "geo_location": sample_log['geo_location'],
            "resource_accessed": "/api/v1/new_project_docs",   
            "auth_method": "token",
            "session_duration": 180.0,
            "command_sequence": ["GET /new_project_docs"],
            "device_fingerprint": sample_log['device_fingerprint'],
            "label": LabelType.INSIDER_DRIFT.value
        })

    return injected_rows

 
if __name__ == "__main__":
    print("Loading baseline logs...")
    baseline_path = "exports/normal_baseline_logs.csv"
    
    try:
        df_baseline = pd.read_csv(baseline_path)
    except FileNotFoundError:
        print(f"Error: {baseline_path} not found. Please run generator.py first.")
        exit(1)

    print("Injecting scaled attack patterns and edge cases (High Volume)...")
    
    anomalies = []
    # Massively increased injection volume to eliminate 0.00 scores
    anomalies.extend(inject_brute_force(df_baseline, num_attacks=200))
    anomalies.extend(inject_impossible_travel(df_baseline, num_attacks=200))
    anomalies.extend(inject_device_spoofing(df_baseline, num_attacks=150))
    anomalies.extend(inject_lateral_movement(df_baseline, num_attacks=150))
    anomalies.extend(inject_credential_stuffing(df_baseline, num_attacks=150))
    anomalies.extend(inject_low_and_slow(df_baseline, num_cases=150))
    anomalies.extend(inject_insider_drift(df_baseline, num_cases=100))
 
    df_anomalies = pd.DataFrame(anomalies)

    # Combine normal logs with injected anomalies
    df_final = pd.concat([df_baseline, df_anomalies], ignore_index=True)
 
    df_final['timestamp'] = pd.to_datetime(df_final['timestamp'])
    df_final = df_final.sort_values(by="timestamp").reset_index(drop=True)

    # Export final, combined dataset ready for ML training
    final_export_path = "exports/final_training_dataset.csv"
    df_final.to_csv(final_export_path, index=False)

    # Printing evaluation metrics for terminal verification
    print("\n--- DATASET GENERATION COMPLETE ---")
    print(f"Total Rows Generated: {len(df_final)}")
    print(f"Normal Rows (Baseline): {len(df_baseline)}")
    print(f"Injected Anomaly Rows: {len(df_anomalies)}")
    print(f"Anomaly Proportion: {(len(df_anomalies) / len(df_final)) * 100:.2f}%")
    print(f"\nSaved final training dataset to: {final_export_path}")

    print("\nLabel Breakdown:")
    print(df_final['label'].value_counts())