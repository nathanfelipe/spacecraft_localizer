# Heliospheric Current Sheet Analysis with Parker Spiral

## Overview

This project models the Heliospheric Current Sheet (HCS) using the Parker Spiral and integrates in situ spacecraft data from the Parker Solar Probe (PSP) and the Magnetospheric Multiscale (MMS) mission. The goal is to visualize and analyze the magnetic field structure in the inner heliosphere and compare theoretical predictions with observational data.

## Objectives

- Model the Heliospheric Current Sheet (HCS) using the Parker Spiral
- Visualize the 3D structure of the magnetic field and its variations
- Integrate spacecraft data from PSP and MMS to study real-time space weather conditions
- Fetch ephemeris and observational data using JPL's API and CDAWeb services
- Containerize the project with Docker for reproducibility and ease of deployment

## Project Structure

```
├── Dockerfile                        # Docker setup for running the project
├── requirements.txt                   # List of dependencies
├── project_outline.md                 # High-level description of the project
├── main.py                            # Main execution script
├── psp_plus_mms.py                    # Handles PSP & MMS data processing
├── psp_plus_mms_plus_parker_spiral.py # Combines spacecraft data with Parker Spiral model
├── jpl_approach_psp.py                # Queries PSP ephemeris data from JPL
├── mms.py                             # Processes MMS mission data
├── plot_with_parker_spiral.png        # Example visualization output
```

## Installation

### Using Docker (Recommended)

To ensure a consistent environment, you can run this project inside a Docker container:

docker build -t heliosphere_model .
docker run --rm -it heliosphere_model

### Manual Installation

If running locally, install dependencies using:

pip install -r requirements.txt

## Usage

### Running the Analysis

To execute the full analysis:

python main.py

This script will:
1. Fetch spacecraft data (PSP & MMS) from JPL and CDAWeb
2. Compute the Parker Spiral model for the heliospheric magnetic field
3. Generate a 3D visualization of the HCS with spacecraft positions
4. Save the plot as `plot_with_parker_spiral.png`

### Fetching PSP Ephemeris Data

To query the PSP position from JPL:

python jpl_approach_psp.py

### Processing MMS Data

To retrieve and process MMS mission data:

python mms.py

## Output

- The main output is a 3D visualization of the Parker Spiral and spacecraft positions
- The script saves figures as .png files
- Logs and computed data may be stored for further analysis

## Dependencies

This project requires the following Python libraries:

- `numpy`: Numerical computing
- `matplotlib`: Visualization
- `astroquery`: Querying astronomical databases
- `cdasws`: Accessing NASA CDAWeb data
- `xarray`: Handling scientific datasets
- `cdflib`: Reading CDF files

## Future Improvements

- Integrate real-time solar wind data for dynamic modeling
- Add more spacecraft trajectories (e.g., Solar Orbiter, Wind, ACE)
- Improve data interpolation methods for better accuracy