# SkyTrade Drone Data Validator

This project is a Python-based tool that validates drone location data against various criteria like time discrepancies, speed limits, altitude drops, and country mismatches (based on IP and Lat/Long coordinates). The results of the validation are stored in a PostgreSQL database.

## Features

- **Timestamp Validation**: Compares the drone's timestamp with the server's current time and flags any significant delays.
- **Country Mismatch Detection**: Uses IP geolocation to detect if the drone's IP-based country differs from its latitude/longitude-based location.
- **Speed Validation**: Calculates the 3D speed of the drone based on geolocation and altitude. If the speed exceeds a model's predefined maximum speed, it is flagged as suspicious.
- **Altitude Drop Detection**: Checks for any sudden drops in altitude and flags them.

## Project Structure

