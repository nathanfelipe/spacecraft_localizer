from cdasws import CdasWs
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # registers the 3D projection
import numpy as np

def fetch_mms_position(spacecraft_id="mms1"):
    """
    Fetches the MMS spacecraft position from CDAWeb.
    
    Returns:
        A tuple (x, y, z) in kilometers in GSE coordinates.
    """
    start_time = "2024-02-01T00:00:00Z"
    end_time = "2024-02-01T01:00:00Z"
    
    print(f"Requesting MMS data from {start_time} to {end_time}")
    
    cdas = CdasWs()
    dataset = f"{spacecraft_id.upper()}_MEC_SRVY_L2_EPHT89D"
    
    try:
        variables = ['mms1_mec_r_gse']
        res = cdas.get_data(dataset, variables, start_time, end_time)
        
        # Debug print
        print("Data received from CDAS:")
        print(f"Response type: {type(res)}")
        print(f"Response content: {res}")
        
        if res is None or len(res) < 2:
            print(f"No data returned for {spacecraft_id}")
            return None
            
        data = res[1]
        print(f"Data type: {type(data)}")
        print(f"Data keys: {data.keys()}")
        
        if 'mms1_mec_r_gse' not in data:
            print("Position data not found in response")
            return None
            
        # Get raw position data
        raw_position = data['mms1_mec_r_gse']
        print(f"Position data type: {type(raw_position)}")
        print(f"Position data: {raw_position}")
        
        # Try to get the first position vector directly from the array
        try:
            # Convert to numpy array if it isn't already
            position_array = np.array(raw_position)
            first_position = position_array[0]
            
            # Ensure we have three components
            if len(first_position) != 3:
                print(f"Unexpected position format: {first_position}")
                return None
                
            return (float(first_position[0]), 
                    float(first_position[1]), 
                    float(first_position[2]))
                    
        except Exception as e:
            print(f"Error converting position data: {str(e)}")
            # Fallback: try direct access
            try:
                return (float(raw_position[0][0]), 
                        float(raw_position[0][1]), 
                        float(raw_position[0][2]))
            except Exception as e2:
                print(f"Fallback access failed: {str(e2)}")
                return None
                
    except Exception as e:
        print(f"Error fetching MMS data: {str(e)}")
        return None

def analyze_mms(analysis_type):
    """
    Analyze MMS data based on the specified analysis type.
    
    Args:
        analysis_type (str): Type of analysis to perform ('trajectory' or 'data_retrieval')
    """
    if analysis_type == "trajectory":
        try:
            position = fetch_mms_position()
            if position:
                print(f"MMS Position (km): X={position[0]}, Y={position[1]}, Z={position[2]}")
                plot_positions(position)
            else:
                print("Failed to get MMS position")
        except Exception as e:
            print(f"Error getting MMS trajectory: {str(e)}")
    elif analysis_type == "data_retrieval":
        print("MMS data retrieval not yet implemented")
    else:
        print(f"Unknown analysis type: {analysis_type}")

def plot_positions(mms_pos):
    """
    Creates a 3D plot showing the MMS position, Earth, and the Sun in GSE.
    
    Args:
        mms_pos: Tuple (x, y, z) for MMS position (in km).
    """
    # Convert km to AU
    AU = 149597870.7  # 1 AU in kilometers
    mms_pos_au = (mms_pos[0]/AU, mms_pos[1]/AU, mms_pos[2]/AU)
    
    fig = plt.figure(figsize=(12, 12))  # Make the figure square
    ax = fig.add_subplot(111, projection='3d')
    
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
    
    # Set equal aspect ratio for all axes
    ax.set_box_aspect([1, 1, 1])
    
    # Set the same limits for all axes based on the Sun's distance
    max_range = sun_pos[0] * 1.1  # Add 10% margin
    ax.set_xlim([-max_range/20, max_range])  # Asymmetric to show more +X (Sun direction)
    ax.set_ylim([-max_range/2, max_range/2])
    ax.set_zlim([-max_range/2, max_range/2])
    
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.legend()
    plt.title("MMS Position in GSE (AU)")
    
    # Add a grid for better spatial reference
    ax.grid(True)
    
    plt.show()

def main():
    mms_position = fetch_mms_position("mms1")
    if mms_position:
        print("MMS1 position (GSE, km):", mms_position)
        plot_positions(mms_position)

if __name__ == "__main__":
    main()