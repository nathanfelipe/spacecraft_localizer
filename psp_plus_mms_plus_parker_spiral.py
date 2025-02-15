import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import matplotlib.colors as colors
import datetime
from astroquery.jplhorizons import Horizons
from cdasws import CdasWs
from jpl_approach_psp import fetch_psp_position_horizons
from mms import fetch_mms_position

def get_input(prompt, default):
    """
    Ask the user for a float input; if none is provided, return the default.
    """
    user_input = input(f"{prompt} [default: {default}]: ")
    if user_input.strip() == "":
        return default
    try:
        return float(user_input)
    except ValueError:
        print(f"Invalid input. Using default value: {default}")
        return default

def compute_parker_spiral_surface(r_min=0.1, r_max=1.5, n_r=100, n_phi=100,
                                  tilt_deg=10.0, amp_deg=15.0,
                                  solar_rot_days=25.4, v_sw_km_s=400.0):
    """
    Computes a 3D surface approximating the warped heliospheric current sheet.
    """
    AU_km = 1.4959787e8  # km per AU
    
    # Convert angles to radians
    tilt = np.radians(tilt_deg)
    amp = np.radians(amp_deg)
    
    # Compute spiral winding parameter
    omega = 2 * np.pi / solar_rot_days  # rad/day
    v_sw_AU_day = (v_sw_km_s * 86400) / AU_km  # solar wind speed in AU/day
    alpha = omega / v_sw_AU_day  # winding rate (rad/AU)
    
    # Create grid in r and phi
    r_vals = np.linspace(r_min, r_max, n_r)
    phi_vals = np.linspace(0, 2 * np.pi, n_phi)
    R, Phi = np.meshgrid(r_vals, phi_vals)
    
    # Define polar angle theta with sinusoidal undulation
    theta = (np.pi / 2 - tilt) + amp * np.sin(2 * Phi)
    
    # Add spiral twist
    Phi_spiral = Phi + alpha * (R - r_min)
    
    # Convert to Cartesian coordinates
    x = R * np.sin(theta) * np.cos(Phi_spiral)
    y = R * np.sin(theta) * np.sin(Phi_spiral)
    z = R * np.cos(theta)
    
    # Calculate normalized magnetic field strength
    B0_norm = 1 / np.sqrt(1 + (omega / v_sw_AU_day)**2 * (np.cos(tilt))**2)
    B = B0_norm * (1 / R)**2 * np.sqrt(1 + (omega * R / v_sw_AU_day)**2 * (np.sin(theta))**2)
    
    return x, y, z, B

def fetch_psp_position_horizons(date=None):
    """
    Fetch PSP position from JPL Horizons in heliocentric coordinates (AU).
    
    Returns:
      (x, y, z) in AU relative to the Sun.
    """
    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    
    # Use a 1-minute time window to avoid errors
    start_time = date
    stop_time = (datetime.datetime.strptime(date, "%Y-%m-%d %H:%M") +
                 datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
    
    psp = Horizons(id='-96', location='@sun',
                   epochs={'start': start_time, 'stop': stop_time, 'step': '1m'})
    vectors = psp.vectors()
    x = float(vectors['x'][0])
    y = float(vectors['y'][0])
    z = float(vectors['z'][0])
    return (x, y, z)

def fetch_mms_position(spacecraft_id="mms1"):
    """
    Fetch MMS position from CDAWeb in GSE coordinates (km) relative to Earth.
    
    Returns:
      (x, y, z) in km.
    """
    # For demonstration, use a fixed time window (update as needed)
    start_time = "2024-02-01T00:00:00Z"
    end_time   = "2024-02-01T01:00:00Z"
    
    print(f"Requesting MMS data from {start_time} to {end_time}")
    
    cdas = CdasWs()
    dataset = f"{spacecraft_id.upper()}_MEC_SRVY_L2_EPHT89D"
    variables = ['mms1_mec_r_gse']
    
    try:
        res = cdas.get_data(dataset, variables, start_time, end_time)
        if res is None:
            print(f"No data returned for {spacecraft_id}")
            return None
        data = res[1]
        if 'mms1_mec_r_gse' not in data:
            print("Position data not found in response.")
            return None
        
        # Use the first position vector
        position = data['mms1_mec_r_gse'].values[0]
        x, y, z = position
        return (float(x), float(y), float(z))
    except Exception as e:
        print(f"Error fetching MMS data: {str(e)}")
        return None

def calculate_parker_spiral(r_range, theta_range, omega=2.7e-6, v_sw=400):
    """
    Calculate Parker Spiral coordinates with ripple-like wave pattern.
    
    Args:
        r_range: Array of radial distances (in AU)
        theta_range: Array of theta angles for the wave structure
        omega: Solar rotation rate (radians/s)
        v_sw: Solar wind speed (km/s)
    
    Returns:
        x, y, z coordinates of the spiral surface
    """
    r, theta = np.meshgrid(r_range, theta_range)
    
    # Calculate phi (azimuthal angle) for Parker Spiral
    phi = -omega * (r * 149597870.7) / v_sw  # Convert AU to km for calculation
    
    # Create ripple-like wave pattern
    wave_number = 4  # Number of wave peaks
    wave_amplitude = 0.05  # Height of waves
    decay_factor = np.exp(-2 * r)  # Waves decay with distance
    z_wave = wave_amplitude * np.sin(wave_number * phi) * decay_factor
    
    # Convert to cartesian coordinates
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = z_wave
    
    return x, y, z

def analyze_psp_mms_parker(analysis_type):
    """
    Analyze PSP and MMS data with Parker Spiral, based on the specified analysis type.
    """
    if analysis_type == "trajectory":
        try:
            # Get spacecraft positions
            psp_pos = fetch_psp_position_horizons()
            mms_pos = fetch_mms_position()
            
            if psp_pos and mms_pos:
                print(f"PSP Position (AU): X={psp_pos[0]}, Y={psp_pos[1]}, Z={psp_pos[2]}")
                
                # Convert MMS position from km to AU
                AU_km = 1.4959787e8
                mms_pos_au = tuple(coord/AU_km for coord in mms_pos)
                # Shift MMS position to heliocentric coordinates
                mms_helio = (1.0 + mms_pos_au[0], mms_pos_au[1], mms_pos_au[2])
                
                print(f"MMS Position (AU): X={mms_helio[0]}, Y={mms_helio[1]}, Z={mms_helio[2]}")
                
                plot_positions_with_parker(psp_pos, mms_helio)
            else:
                print("Failed to get positions for one or both spacecraft")
                
        except Exception as e:
            print(f"Error analyzing trajectories: {str(e)}")
            
    elif analysis_type == "data_retrieval":
        print("PSP+MMS+Parker Spiral data retrieval not yet implemented")
    else:
        print(f"Unknown analysis type: {analysis_type}")

def plot_positions_with_parker(psp_pos, mms_pos):
    """
    Creates a 3D plot showing PSP, MMS, Parker Spiral surface, Earth, and the Sun.
    """
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Compute Parker Spiral surface
    x_spiral, y_spiral, z_spiral, B = compute_parker_spiral_surface()
    
    # Create logarithmic color mapping for magnetic field strength
    norm = colors.LogNorm(vmin=np.min(B), vmax=np.max(B))
    cmap = plt.cm.viridis
    facecolors = cmap(norm(B))
    
    # Plot the spiral surface
    surf = ax.plot_surface(x_spiral, y_spiral, z_spiral, 
                          facecolors=facecolors,
                          rstride=1, cstride=1, 
                          linewidth=0, 
                          antialiased=False, 
                          alpha=0.8)
    
    # Add colorbar
    mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    mappable.set_array(B)
    cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label("Normalized Magnetic Field Strength (log scale)")
    
    # Plot Sun at origin
    ax.scatter(0, 0, 0, color='yellow', s=200, label="Sun")
    ax.text(0, 0, 0, "Sun", color='orange')
    
    # Plot Earth at (1,0,0) AU
    ax.scatter(1, 0, 0, color='blue', s=100, label="Earth")
    ax.text(1, 0, 0, "Earth", color='blue')
    
    # Plot PSP
    ax.scatter(psp_pos[0], psp_pos[1], psp_pos[2], 
               color='red', s=100, label="PSP")
    ax.text(psp_pos[0], psp_pos[1], psp_pos[2], "PSP", color='red')
    
    # Plot MMS
    ax.scatter(mms_pos[0], mms_pos[1], mms_pos[2], 
               color='green', s=100, label="MMS")
    ax.text(mms_pos[0], mms_pos[1], mms_pos[2], "MMS", color='green')
    
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.legend()
    ax.set_title("Heliospheric Current Sheet with Parker Spiral\n"
                 "and Positions of Sun, Earth, PSP & MMS")
    
    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])

    plt.show()
    
    plt.savefig('plot_with_parker_spiral.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("\nPlot saved as 'plot_with_parker_spiral.png'")

def main():
    # ----------------------------
    # 1. Get user parameters for the spiral
    # ----------------------------
    print("Enter parameters for the Parker Spiral / Heliospheric Current Sheet.")
    print("Press Enter to use default values.")
    tilt_deg = get_input("Tilt angle (deg)", 10.0)
    amp_deg = get_input("Undulation amplitude (deg)", 15.0)
    solar_rot_days = get_input("Solar rotation period (days)", 25.4)
    v_sw_km_s = get_input("Solar wind speed (km/s)", 400.0)
    r_max = get_input("Radial extent (AU)", 1.5)
    
    # ----------------------------
    # 2. Compute the Parker spiral surface and get grid parameters
    # ----------------------------
    x_spiral, y_spiral, z_spiral, B = compute_parker_spiral_surface(
        r_min=0.1, r_max=r_max, n_r=100, n_phi=100,
        tilt_deg=tilt_deg, amp_deg=amp_deg,
        solar_rot_days=solar_rot_days, v_sw_km_s=v_sw_km_s
    )
    
    # ----------------------------
    # 3. Fetch spacecraft positions
    # ----------------------------
    print("Fetching PSP position...")
    psp_pos = fetch_psp_position_horizons()
    print("PSP Position (AU relative to Sun):", psp_pos)
    
    print("Fetching MMS position...")
    mms_pos = fetch_mms_position("mms1")
    if mms_pos is None:
        print("Could not retrieve MMS position.")
        return
    print("MMS Position (km relative to Earth, GSE):", mms_pos)
    
    # Convert MMS position from km to AU and shift by Earth's heliocentric position.
    mms_pos_au_rel = (mms_pos[0] / 1.4959787e8, mms_pos[1] / 1.4959787e8, mms_pos[2] / 1.4959787e8)
    earth_heliocentric = (1.0, 0.0, 0.0)  # Approximate Earth position in heliocentric coordinates
    mms_heliocentric = (
        earth_heliocentric[0] + mms_pos_au_rel[0],
        earth_heliocentric[1] + mms_pos_au_rel[1],
        earth_heliocentric[2] + mms_pos_au_rel[2]
    )
    
    # ----------------------------
    # 4. Create the combined 3D plot with a log-scaled colorbar for B
    # ----------------------------
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Use a logarithmic normalization for the magnetic field.
    # Ensure the minimum value is > 0.
    norm = colors.LogNorm(vmin=np.min(B), vmax=np.max(B))
    cmap = plt.cm.viridis
    facecolors = cmap(norm(B))
    
    # Plot the spiral surface colored by the normalized magnetic field.
    surf = ax.plot_surface(x_spiral, y_spiral, z_spiral, facecolors=facecolors,
                           rstride=1, cstride=1, linewidth=0, antialiased=False, alpha=0.8)
    
    # Create a ScalarMappable for the colorbar with log normalization.
    mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    mappable.set_array(B)
    cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label("Normalized B (log scale, B at 1 AU = 1)")
    
    # Plot the Sun at the origin (0,0,0)
    ax.scatter(0, 0, 0, color='yellow', s=200, label="Sun")
    ax.text(0, 0, 0, "Sun", color='orange')
    
    # Plot Earth (assumed at (1,0,0) AU)
    ax.scatter(earth_heliocentric[0], earth_heliocentric[1], earth_heliocentric[2],
               color='blue', s=100, label="Earth")
    ax.text(earth_heliocentric[0], earth_heliocentric[1], earth_heliocentric[2],
            "Earth", color='blue')
    
    # Plot PSP position (already in AU relative to Sun)
    ax.scatter(psp_pos[0], psp_pos[1], psp_pos[2], color='red', s=100, label="PSP")
    ax.text(psp_pos[0], psp_pos[1], psp_pos[2], "PSP", color='red')
    
    # Plot MMS position (converted to heliocentric AU)
    ax.scatter(mms_heliocentric[0], mms_heliocentric[1], mms_heliocentric[2],
               color='green', s=100, label="MMS")
    ax.text(mms_heliocentric[0], mms_heliocentric[1], mms_heliocentric[2],
            "MMS", color='green')
    
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.legend()
    ax.set_title("Heliospheric Current Sheet with Parker Spiral\n"
                 "Colored by Norm. B (log scale, B at 1 AU = 1)\n"
                 "and Positions of Sun, Earth, PSP & MMS")
    ax.set_box_aspect((1, 1, 1))  # Equal scaling for all axes
    
    # Save the plot instead of showing it
    plt.savefig('plot_withparker_spiral.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("\nPlot saved as 'parker_spiral.png'")

if __name__ == "__main__":
    main()