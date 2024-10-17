import psycopg2
import psycopg2.extras  # Added import for psycopg2.extras
import requests
from geopy.distance import geodesic
from datetime import datetime

# Function to get IP country using GeoIPify
def get_country_from_ip(ip_address):
    api_key = 'at_qT8XaKJOjPsFWlHE3Ca2uIn3xLDMH'  # Replace with your actual API key
    url = f'https://geo.ipify.org/api/v1?apiKey={api_key}&ipAddress={ip_address}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('location', {}).get('country')
    return None

# Function to calculate 3D speed
def calculate_speed(prev_obs, curr_obs):
    # Geodesic distance (in km) using lat/long
    distance_2d = geodesic((prev_obs['lat'], prev_obs['long']), (curr_obs['lat'], curr_obs['long'])).kilometers
    
    # Altitude difference (in km)
    altitude_diff = abs(curr_obs['alt'] - prev_obs['alt']) / 1000  # Convert meters to km
    
    # Total 3D distance
    distance_3d = (distance_2d**2 + altitude_diff**2)**0.5
    
    # Time difference (in hours)
    time_diff = (curr_obs['timestamp'] - prev_obs['timestamp']).total_seconds() / 3600
    
    # Speed (in km/h)
    return distance_3d / time_diff if time_diff > 0 else 0

# Function to store validation results
def store_validation_results(cursor, results):
    query = """
        INSERT INTO validation_results (device_id, time_diff_minutes, country_mismatch, speed_flag, altitude_drop)
        VALUES %s
    """
    psycopg2.extras.execute_values(cursor, query, results)  # Ensure psycopg2.extras is used

# Connect to the PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="skyradar_db", user="skyradar_user", password="your_password", host="localhost"
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

# Validation tool
def validate_drone_data():
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()

    # Fetch observations from the database
    cursor.execute("SELECT id, lat, long, alt, timestamp, ip_address, drone_model FROM devices ORDER BY timestamp")
    observations = cursor.fetchall()

    # Simulated max speeds for each drone model (in km/h)
    max_speeds = {
        'drone_model_1': 80,  # Example drone model with max speed 80 km/h
        'drone_model_2': 60   # Another drone model with max speed 60 km/h
    }

    prev_obs = None
    validation_results = []

    for obs in observations:
        obs_data = {
            'id': obs[0],
            'lat': obs[1],
            'long': obs[2],
            'alt': obs[3],
            'timestamp': obs[4],
            'ip_address': obs[5],
            'drone_model': obs[6]
        }

        # 1. Timestamp validation (drone vs server)
        server_time = datetime.now()  # Simulated server time
        time_diff = (server_time - obs_data['timestamp']).total_seconds() / 60  # Time difference in minutes
        country_mismatch, speed_flag, altitude_drop = False, False, False

        if time_diff > 1:
            print(f"Observation {obs_data['id']} is suspicious (timestamp difference: {time_diff} minutes)")

        # 2. Speed validation (3D speed exceeding the drone model's max speed)
        if prev_obs:
            speed = calculate_speed(prev_obs, obs_data)  # Calculate 3D speed
            max_speed = max_speeds.get(obs_data['drone_model'], 50)  # Default max speed is 50 km/h if not specified
            if speed > max_speed:
                print(f"Observation {obs_data['id']} is suspicious (speed: {speed:.2f} km/h, max allowed: {max_speed} km/h)")
                speed_flag = True
            elif obs_data['alt'] < prev_obs['alt']:  # Check for rapid altitude drops
                print(f"Observation {obs_data['id']} may be falling (altitude drop detected)")
                altitude_drop = True

        # 3. Country mismatch validation (IP vs Lat/Long)
        ip_country = get_country_from_ip(obs_data['ip_address'])
        lat_long_country = 'some_country'  # Placeholder - Use a geolocation API to infer country from lat/long
        if ip_country and ip_country != lat_long_country:
            print(f"Observation {obs_data['id']} is suspicious (IP country: {ip_country} vs Lat/Long country: {lat_long_country})")
            country_mismatch = True

        # Store the validation result for bulk insert later
        validation_results.append((obs_data['id'], time_diff, country_mismatch, speed_flag, altitude_drop))
        prev_obs = obs_data

    # Bulk insert the validation results
    store_validation_results(cursor, validation_results)

    conn.commit()
    cursor.close()
    conn.close()

# Run the validation
validate_drone_data()
        