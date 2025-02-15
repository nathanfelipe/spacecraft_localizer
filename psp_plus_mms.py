from astroquery.jplhorizons import Horizons
from cdasws import CdasWs
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # registers the 3D projection
from jpl_approach_psp import fetch_psp_position_horizons
from mms import fetch_mms_position, plot_positions

# ----------------------------
# PSP functions (Heliocentric, in AU)
# ----------------------------
def fetch_psp_position_horizons(date=None):
    """
    Fetches the Parker Solar Probe (PSP) position from JPL Horizons.
    
    Returns:
        Tuple (x, y, z) in AU relative to the Sun.
    """
    # Use a timezone-aware current time in UTC if no date is provided
    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    
    # Create a 1-minute time window (to avoid "start must be earlier than stop" errors)
    start_time = date
    stop_time = (datetime.datetime.strptime(date, "%Y-%m-%d %H:%M") +
                 datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
    
    psp = Horizons(id='-96', 
                   location='@sun',
                   epochs={'start': start_time, 'stop': stop_time, 'step': '1m'})
    vectors = psp.vectors()
    x = float(vectors['x'][0])
    y = float(vectors['y'][0])
    z = float(vectors['z'][0])
    return x, y, z

# ----------------------------
# MMS functions (GSE in km relative to Earth)
# ----------------------------
def fetch_mms_position(spacecraft_id="mms1"):
    """
    Fetches the MMS spacecraft position from CDAWeb.
    
    Returns:
        A tuple (x, y, z) in kilometers in GSE coordinates (Earth at origin).
    """
    # For demonstration, we use a fixed time window (update as needed)
    start_time = "2024-02-01T00:00:00Z"
    end_time = "2024-02-01T01:00:00Z"
    
    print(f"Requesting MMS data from {start_time} to {end_time}")
    
    cdas = CdasWs()
    # Dataset name for MMS (this may need to be updated based on current CDAWeb datasets)
    dataset = f"{spacecraft_id.upper()}_MEC_SRVY_L2_EPHT89D"
    
    try:
        variables = ['mms1_mec_r_gse']
        print(f"Requesting dataset: {dataset}")
        res = cdas.get_data(dataset, variables, start_time, end_time)
        if res is None:
            print(f"No data returned for {spacecraft_id}")
            return None
            
        # Extract the data (assuming the result is an xarray Dataset)
        data = res[1]
        if 'mms1_mec_r_gse' not in data:
            print("Position data not found in response")
            return None
            
        # Get the first position vector (x, y, z)
        position = data['mms1_mec_r_gse'].values[0]
        x, y, z = position
        return float(x), float(y), float(z)
        
    except Exception as e:
        print(f"Error fetching MMS data: {str(e)}")
        return None

# ----------------------------
# Combined Plotting Function
# ----------------------------
def plot_spacecraft_positions(psp_pos, mms_pos):
    """
    Plots the positions of PSP and MMS on the same 3D plot in heliocentric coordinates (in AU).
    
    PSP's position is already in AU (relative to the Sun).
    MMS's position is given in km (Earth-centered GSE), so we:
      1. Convert from km to AU.
      2. Add Earth's heliocentric offset (assumed to be at (1, 0, 0) AU).
    """
    AU_km = 149597870.7  # 1 AU in kilometers
    
    # Convert MMS position from km to AU (still Earth-centered)
    mms_pos_au_rel = (mms_pos[0] / AU_km, mms_pos[1] / AU_km, mms_pos[2] / AU_km)
    
    # Assume Earth is at (1, 0, 0) AU in heliocentric coordinates.
    earth_heliocentric = (1.0, 0.0, 0.0)
    
    # Estimate MMS heliocentric position by adding Earth's offset.
    mms_heliocentric = (
        earth_heliocentric[0] + mms_pos_au_rel[0],
        earth_heliocentric[1] + mms_pos_au_rel[1],
        earth_heliocentric[2] + mms_pos_au_rel[2]
    )
    
    # Create the 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot PSP (in red)
    ax.scatter(psp_pos[0], psp_pos[1], psp_pos[2], color='red', s=100, label="PSP")
    ax.text(psp_pos[0], psp_pos[1], psp_pos[2], "PSP", color='red')
    
    # Plot MMS (in green)
    ax.scatter(mms_heliocentric[0], mms_heliocentric[1], mms_heliocentric[2],
               color='green', s=100, label="MMS")
    ax.text(mms_heliocentric[0], mms_heliocentric[1], mms_heliocentric[2],
            "MMS", color='green')
    
    # Plot the Sun at the origin
    ax.scatter(0, 0, 0, color='yellow', s=200, label="Sun")
    ax.text(0, 0, 0, "Sun", color='orange')
    
    # Plot Earth (assumed at (1, 0, 0) AU)
    ax.scatter(earth_heliocentric[0], earth_heliocentric[1], earth_heliocentric[2],
               color='blue', s=100, label="Earth")
    ax.text(earth_heliocentric[0], earth_heliocentric[1], earth_heliocentric[2],
            "Earth", color='blue')
    
    # Label axes and set title
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.legend()
    plt.title("PSP & MMS Positions (Heliocentric, in AU)")
    
    plt.show()

# ----------------------------
# Main Execution
# ----------------------------
def main():
    # Fetch PSP position (already in AU relative to the Sun)
    psp_position = fetch_psp_position_horizons()
    print("PSP Position (AU relative to Sun):", psp_position)
    
    # Fetch MMS position (in km relative to Earth, GSE)
    mms_position = fetch_mms_position("mms1")
    if mms_position is None:
        print("Could not retrieve MMS position.")
        return
    print("MMS Position (km relative to Earth, GSE):", mms_position)
    
    # Plot both spacecraft positions in heliocentric coordinates (AU)
    plot_spacecraft_positions(psp_position, mms_position)

def analyze_psp_mms(analysis_type):
    """
    Analyze both PSP and MMS data based on the specified analysis type.
    
    Args:
        analysis_type (str): Type of analysis to perform ('trajectory' or 'data_retrieval')
    """
    if analysis_type == "trajectory":
        try:
            # Get positions for both spacecraft
            psp_pos = fetch_psp_position_horizons()
            mms_pos = fetch_mms_position()
            
            if psp_pos and mms_pos:
                print(f"PSP Position (km): X={psp_pos[0]}, Y={psp_pos[1]}, Z={psp_pos[2]}")
                print(f"MMS Position (km): X={mms_pos[0]}, Y={mms_pos[1]}, Z={mms_pos[2]}")
                plot_both_positions(psp_pos, mms_pos)
            else:
                print("Failed to get positions for one or both spacecraft")
                
        except Exception as e:
            print(f"Error analyzing PSP and MMS trajectories: {str(e)}")
            
    elif analysis_type == "data_retrieval":
        print("PSP+MMS combined data retrieval not yet implemented")
    else:
        print(f"Unknown analysis type: {analysis_type}")

def plot_both_positions(psp_pos, mms_pos):
    """
    Creates a 3D plot showing both PSP and MMS positions, Earth, and the Sun in GSE.
    
    Args:
        psp_pos: Tuple (x, y, z) for PSP position (in km)
        mms_pos: Tuple (x, y, z) for MMS position (in km)
    """
    # Convert km to AU
    AU = 149597870.7  # 1 AU in kilometers
    psp_pos_au = (psp_pos[0]/AU, psp_pos[1]/AU, psp_pos[2]/AU)
    mms_pos_au = (mms_pos[0]/AU, mms_pos[1]/AU, mms_pos[2]/AU)
    
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot PSP position (in purple)
    ax.scatter(psp_pos_au[0], psp_pos_au[1], psp_pos_au[2], color='purple', s=100, label="PSP")
    ax.text(psp_pos_au[0], psp_pos_au[1], psp_pos_au[2], "PSP", color='purple')
    
    # Plot MMS position (in red)
    ax.scatter(mms_pos_au[0], mms_pos_au[1], mms_pos_au[2], color='red', s=100, label="MMS")
    ax.text(mms_pos_au[0], mms_pos_au[1], mms_pos_au[2], "MMS", color='red')
    
    # Plot Earth (origin in GSE)
    ax.scatter(0, 0, 0, color='blue', s=100, label="Earth")
    ax.text(0, 0, 0, "Earth", color='blue')
    
    # Plot the Sun in GSE: exactly 1 AU along the +X axis
    sun_pos = (1, 0, 0)  # 1 AU
    ax.scatter(sun_pos[0], sun_pos[1], sun_pos[2], color='yellow', s=200, label="Sun")
    ax.text(sun_pos[0], sun_pos[1], sun_pos[2], "Sun", color='orange')
    
    ax.set_box_aspect([1, 1, 1])
    
    max_range = sun_pos[0] * 1.1
    ax.set_xlim([-max_range/20, max_range])
    ax.set_ylim([-max_range/2, max_range/2])
    ax.set_zlim([-max_range/2, max_range/2])
    
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.legend()
    plt.title("PSP and MMS Positions in GSE (AU)")
    
    ax.grid(True)
    plt.show()

if __name__ == "__main__":
    main()