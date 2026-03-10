import os
import json
import gpxpy

def get_gpx_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

            # 1. Get internal name, fallback to filename if missing
            name = "Untitled Track"
            if gpx.tracks and gpx.tracks[0].name:
                name = gpx.tracks[0].name
            elif gpx.name:
                name = gpx.name
            else:
                name = os.path.basename(file_path).replace('.gpx', '')

            # 2. Calculate Distance (km)
            dist_m = gpx.length_2d()
            distance = round((dist_m + 500) / 1000, 0)

            # 3. Calculate Elevation Gain (m)
            uphill, downhill = gpx.get_uphill_downhill()
            elevation = round(uphill)

            return name, distance, elevation
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, 0, 0

def build_index(root_dir):
    tracks_data = []

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.gpx'):
                full_path = os.path.join(root, file)

                # Extract metadata from folder structure
                # gpx / {type} / {location} / file.gpx
                parts = os.path.normpath(root).split(os.sep)

                # Adjusted indices based on your folder structure
                pavement_type = parts[1].capitalize() if len(parts) > 1 else "Unknown"
                location = parts[2] if len(parts) > 2 else "General"

                print(f"Parsing: {file}...")

                name, dist, elev = get_gpx_data(full_path)

                if name:
                    tracks_data.append({
                        "name": name,
                        "file": full_path.replace('\\', '/'),
                        "distance": dist,
                        "elevation": elev,
                        "type": pavement_type,
                        "location": location
                    })

    # Sort by distance ascending as a nice default
    tracks_data.sort(key=lambda x: x['distance'], reverse=False)

    with open('gpx/data.json', 'w', encoding='utf-8') as f:
        json.dump(tracks_data, f, indent=4, ensure_ascii=False)

    print(f"\nDone! data.json created with {len(tracks_data)} routes.")

if __name__ == "__main__":
    # Run this from the folder containing the 'gpx' directory
    build_index('gpx')