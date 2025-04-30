import mss

with mss.mss() as sct:
    # Print all monitors information
    for i, monitor in enumerate(sct.monitors):
        print(f"\nMonitor #{i}: {monitor}")
    
    # Print the primary monitor
    print(f"\nPrimary monitor: {sct.monitors[0]}")
    
    # Try to capture full screen
    print("\nAttempting full screen capture...")
    full = sct.monitors[0]  # Monitor 0 is the "All in One" monitor
    print(f"Full screen bounds: {full}") 