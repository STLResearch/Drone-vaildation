# SkyTrade Drone Data Validator

This project is a Python-based tool that validates drone location data against various criteria like time discrepancies, speed limits, altitude drops, and country mismatches (based on IP and Lat/Long coordinates). The results of the validation are stored in a PostgreSQL database.

## Features

- **Timestamp Validation**: Compares the drone's timestamp with the server's current time and flags any significant delays.
- **Country Mismatch Detection**: Uses IP geolocation to detect if the drone's IP-based country differs from its latitude/longitude-based location.
- **Speed Validation**: Calculates the 3D speed of the drone based on geolocation and altitude. If the speed exceeds a model's predefined maximum speed, it is flagged as suspicious.
- **Altitude Drop Detection**: Checks for any sudden drops in altitude and flags them.

## Database Schema

### 1. `devices` Table

The `devices` table stores the raw drone observation data.

```sql
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    lat DOUBLE PRECISION,                -- Latitude of the drone
    long DOUBLE PRECISION,               -- Longitude of the drone
    alt DOUBLE PRECISION,                -- Altitude of the drone in meters
    timestamp TIMESTAMP,                 -- Timestamp when the observation was made
    ip_address VARCHAR(255),             -- IP address of the drone or operator
    drone_model VARCHAR(255)             -- Model of the drone
);
```
### 2. `Validation` table

```sql
CREATE TABLE validation_results (
    id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(id), -- Foreign key linking to the `devices` table
    time_diff_minutes DOUBLE PRECISION,   -- Time difference between drone timestamp and server timestamp (in minutes)
    country_mismatch BOOLEAN,             -- Whether there was a country mismatch between IP and lat/long
    speed_flag BOOLEAN,                   -- Whether the drone's speed exceeded the model's maximum speed
    altitude_drop BOOLEAN                 -- Whether a significant altitude drop was detected
);
```