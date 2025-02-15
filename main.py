from jpl_approach_psp import analyze_psp
from mms import analyze_mms
from psp_plus_mms import analyze_psp_mms
from psp_plus_mms_plus_parker_spiral import analyze_psp_mms_parker

def get_user_input():
    """Get spacecraft and analysis type from user interactively."""
    print("\nSpacecraft Trajectory Analyzer")
    print("============================")
    
    # Spacecraft selection
    print("\nAvailable spacecraft options:")
    print("1. PSP (Parker Solar Probe)")
    print("2. MMS (Magnetospheric Multiscale)")
    print("3. PSP + MMS")
    print("4. PSP + MMS + Parker Spiral")
    
    while True:
        try:
            spacecraft_choice = int(input("\nEnter your choice (1-4): "))
            if 1 <= spacecraft_choice <= 4:
                break
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    # Convert choice to spacecraft string
    spacecraft_map = {
        1: "psp",
        2: "mms",
        3: "psp+mms",
        4: "psp+mms+parker"
    }
    spacecraft = spacecraft_map[spacecraft_choice]
    
    # Analysis type selection
    print("\nAvailable analysis types:")
    print("1. Trajectory (show spacecraft positions)")
    print("2. Data Retrieval (not yet implemented)")
    
    while True:
        try:
            analysis_choice = int(input("\nEnter your choice (1-2): "))
            if 1 <= analysis_choice <= 2:
                break
            print("Please enter either 1 or 2")
        except ValueError:
            print("Please enter a valid number")
    
    # Convert choice to analysis type string
    analysis_map = {
        1: "trajectory",
        2: "data_retrieval"
    }
    analysis = analysis_map[analysis_choice]
    
    return spacecraft, analysis

def main():
    try:
        # Get user input
        spacecraft, analysis = get_user_input()
        
        print(f"\nAnalyzing {spacecraft} with {analysis} analysis...")
        
        # Call the appropriate function based on user input
        if spacecraft == "psp":
            analyze_psp(analysis)
        elif spacecraft == "mms":
            analyze_mms(analysis)
        elif spacecraft == "psp+mms":
            analyze_psp_mms(analysis)
        elif spacecraft == "psp+mms+parker":
            analyze_psp_mms_parker(analysis)
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()