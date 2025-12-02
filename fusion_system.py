import cv2
import numpy as np
import time
import platform

# --- CONFIGURATION ---
CAM_W, CAM_H = 320, 240
MAP_W, MAP_H = 1000, 600

def open_camera(index):
    """
    Attempts to open a camera with specific MJPG compression settings
    to save USB bandwidth. Handles OS-specific backends.
    """
    print(f"DEBUG: Connecting to Camera {index}...")
    
    # 1. Choose Backend based on OS
    # Windows prefers CAP_DSHOW for speed. Linux/Mac prefers default (V4L2/AVFoundation).
    current_os = platform.system()
    if current_os == 'Windows':
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    else:
        # Linux/Mac (just use default backend)
        cap = cv2.VideoCapture(index)
    
    if cap.isOpened():
        # --- THE FIX: FORCE MJPG COMPRESSION ---
        # This compresses data so 3 cameras can fit in one USB 2.0/3.0 port bandwidth.
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
    # NOTE: If you only have 3 cameras total including the webcam, 
    # your indices might be 0, 1, 2 rather than 1, 2, 3.
    cap_left = open_camera(1)
    time.sleep(0.5) 
    
    cap_center = open_camera(2)
    time.sleep(0.5)
    
    cap_right = open_camera(3)
    time.sleep(0.5)

    print("Starting Main Loop... Press 'q' to quit.")

    while True:
        # Create Black Canvas (The "World Map")
        # Initialize fresh every frame to clear old drawings
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

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    if cap_left: cap_left.release()
    if cap_center: cap_center.release()
    if cap_right: cap_right.release()
    cv2.destroyAllWindows()

# --- FIXED ENTRY POINT ---
# Must use double underscores
if __name__ == "__main__":
    main()