import cv2
import numpy as np
import time

# --- CONFIGURATION ---
CAM_W, CAM_H = 320, 240
MAP_W, MAP_H = 1000, 600
OUTPUT_FILE = "multi_cam_recording.avi"  # Name of the output file
RECORDING_FPS = 20.0                     # Frame rate for the video file

def open_camera(index):
    """
    Attempts to open a camera with specific MJPG compression settings
    to save USB bandwidth.
    """
    print(f"DEBUG: Connecting to Camera {index}...")
    
    # 1. Use DirectShow (Windows) - often faster for USB cams
    # If on Linux/Mac, you might remove cv2.CAP_DSHOW or use cv2.CAP_V4L2
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    
    if cap.isOpened():
        # --- THE FIX: FORCE MJPG COMPRESSION ---
        # This compresses data so 3 cameras can fit in one USB 2.0/3.0 port bandwidth.
        # Without this, raw YUYV data often saturates the bus with just 1-2 cams.
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        
        # 2. Set Low Resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
        
        print(f"✅ Camera {index} connected successfully.")
        return cap
    else:
        print(f"❌ Camera {index} failed to open.")
        return None

def main():
    print("--- 3-Camera Fusion System (MJPG Mode) ---")
    
    # Initialize cameras with slight delays to prevent power spikes
    # We skip index 0 to avoid the built-in laptop webcam
    cap_left = open_camera(1)
    time.sleep(1) 
    
    cap_center = open_camera(2)
    time.sleep(1)
    
    cap_right = open_camera(3)
    time.sleep(1)

    # --- VIDEO WRITER SETUP ---
    # We use XVID codec for .avi files (widely supported)
    fourcc_out = cv2.VideoWriter_fourcc(*'XVID')
    # Note: Resolution must match the 'world_map' size exactly: (MAP_W, MAP_H)
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc_out, RECORDING_FPS, (MAP_W, MAP_H))
    print(f"Recording started: saving to {OUTPUT_FILE}")

    print("Starting Main Loop...")

    while True:
        # Create Black Canvas (The "World Map")
        world_map = np.zeros((MAP_H, MAP_W, 3), dtype=np.uint8)

        # --- PROCESS LEFT CAMERA (Index 1) ---
        if cap_left and cap_left.isOpened():
            ret, frame = cap_left.read()
            if ret:
                # Safety resize: Some cheap cameras ignore cap.set commands
                frame = cv2.resize(frame, (CAM_W, CAM_H))
                # Place in left slot
                world_map[100:100+CAM_H, 0:CAM_W] = frame
                cv2.putText(world_map, "CAM 1 (Left)", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(world_map, "SIGNAL LOST", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # --- PROCESS CENTER CAMERA (Index 2) ---
        if cap_center and cap_center.isOpened():
            ret, frame = cap_center.read()
            if ret:
                frame = cv2.resize(frame, (CAM_W, CAM_H))
                # Place in center slot
                world_map[100:100+CAM_H, 340:340+CAM_W] = frame
                cv2.putText(world_map, "CAM 2 (Center)", (350, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(world_map, "SIGNAL LOST", (390, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # --- PROCESS RIGHT CAMERA (Index 3) ---
        if cap_right and cap_right.isOpened():
            ret, frame = cap_right.read()
            if ret:
                frame = cv2.resize(frame, (CAM_W, CAM_H))
                # Place in right slot
                world_map[100:100+CAM_H, 680:680+CAM_W] = frame
                cv2.putText(world_map, "CAM 3 (Right)", (690, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(world_map, "SIGNAL LOST", (730, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Show the composite image
        cv2.imshow("Navya's Multi-Cam System", world_map)

        # Write the combined frame to the video file
        out.write(world_map)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    if cap_left: cap_left.release()
    if cap_center: cap_center.release()
    if cap_right: cap_right.release()
    
    out.release() # Important: Finalize the video file
    print("Video saved successfully.")
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()