from astroquery.jplhorizons import Horizons
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Registers the 3D projection

def fetch_psp_position_horizons(date=None):
    """
    Fetches the Parker Solar Probe (PSP) position from JPL Horizons.
    
    Returns:
        Tuple (x, y, z) in AU relative to the Sun.
    """
    if date is None:
        # Update to use the new recommended way to get UTC time
        date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M")
    
    # Create a time window of 1 minute to avoid the "start must be earlier than stop" error
    psp = Horizons(id='-96', 
                   location='@sun',
                   epochs={
                       'start': date,
                       'stop': (datetime.datetime.strptime(date, "%Y-%m-%d %H:%M") + 
                               datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"),
                       'step': '1m'
                   })
    vectors = psp.vectors()
    x = float(vectors['x'][0])
    y = float(vectors['y'][0])
    z = float(vectors['z'][0])
    return x, y, z

def plot_positions(psp_pos):
    """
    Plots a 3D scatter plot of the PSP position along with the Sun and Earth.
    
    Args:
        psp_pos: Tuple (x, y, z) position of PSP in AU.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot PSP position
    ax.scatter(psp_pos[0], psp_pos[1], psp_pos[2], color='red', s=100, label="PSP")
    ax.text(psp_pos[0], psp_pos[1], psp_pos[2], "PSP", color='red')
    
    # Plot the Sun at the origin (0,0,0)
    ax.scatter(0, 0, 0, color='yellow', s=200, label="Sun")
    ax.text(0, 0, 0, "Sun", color='orange')
    
    # Plot Earth (approximate position in AU; adjust as needed)
    # For example, assuming Earth is at about (1, 0, 0) AU in heliocentric coordinates:
    earth_pos = (1.0, 0.0, 0.0)
    ax.scatter(earth_pos[0], earth_pos[1], earth_pos[2], color='blue', s=100, label="Earth")
    ax.text(earth_pos[0], earth_pos[1], earth_pos[2], "Earth", color='blue')
    
    # Label axes
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    
    ax.legend()
    plt.title("Spacecraft Positions")
    plt.show()

def analyze_psp(analysis_type):
    """
    Analyze PSP data based on the specified analysis type.
    
    Args:
        analysis_type (str): Type of analysis to perform ('trajectory' or 'data_retrieval')
    """
    if analysis_type == "trajectory":
        try:
            position = fetch_psp_position_horizons()
            print(f"PSP Position (km): X={position[0]}, Y={position[1]}, Z={position[2]}")
        except Exception as e:
            print(f"Error getting PSP trajectory: {str(e)}")
    elif analysis_type == "data_retrieval":
        print("PSP data retrieval not yet implemented")
    else:
        print(f"Unknown analysis type: {analysis_type}")

def main():
    # Fetch PSP position from Horizons
    psp_position = fetch_psp_position_horizons()
    print("PSP Position (AU relative to Sun):", psp_position)
    
    # Plot PSP, Sun, and Earth positions in a 3D plot
    plot_positions(psp_position)

if __name__ == "__main__":
    main()