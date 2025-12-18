import cv2 
import numpy as np
import matplotlib.pyplot as plt



class LaneDetector:
    def __init__(self):
        # Define conversion variables (approximate for standard roads)
        # ym_per_pix: meters per pixel in y dimension
        # xm_per_pix: meters per pixel in x dimension
        self.ym_per_pix = 30/720 
        self.xm_per_pix = 3.7/700 
        
    def preprocess(self, img):
        """
        1. Convert to HSV
        2. Mask Yellow/White
        3. Canny Edge Detection
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define ranges for White and Yellow
        # Note: These need tuning based on lighting!
        lower_yellow = np.array([15, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        
        combined_mask = cv2.bitwise_or(mask_yellow, mask_white)
        
        # Edge Detection
        edges = cv2.Canny(combined_mask, 50, 150)
        
        return edges

    def perspective_transform(self, img):
        """
        Warps the image to a bird's eye view.
        """
        h, w = img.shape[:2]
        
        # Define source points (Trapezoid on the road)
        src = np.float32([
            [w * 0.45, h * 0.65],  # Top Left
            [w * 0.55, h * 0.65],  # Top Right
            [w * 0.1, h],          # Bottom Left
            [w * 0.9, h]           # Bottom Right
        ])
        
        # Define destination points (Rectangle)
        dst = np.float32([
            [w * 0.2, 0],
            [w * 0.8, 0],
            [w * 0.2, h],
            [w * 0.8, h]
        ])
        
        M = cv2.getPerspectiveTransform(src, dst)
        Minv = cv2.getPerspectiveTransform(dst, src)
        warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
        
        return warped, Minv

    def find_lane_pixels(self, binary_warped):
        """
        Uses Histogram and Sliding Windows to find lane pixels.
        """
        # Take a histogram of the bottom half of the image
        histogram = np.sum(binary_warped[binary_warped.shape[0]//2:, :], axis=0)
        
        # Find the peak of the left and right halves of the histogram
        midpoint = int(histogram.shape[0]//2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        # Setup sliding window hyperparameters
        nwindows = 9
        margin = 100
        minpix = 50
        
        window_height = int(binary_warped.shape[0]//nwindows)
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        leftx_current = leftx_base
        rightx_current = rightx_base
        
        left_lane_inds = []
        right_lane_inds = []

        for window in range(nwindows):
            win_y_low = binary_warped.shape[0] - (window+1)*window_height
            win_y_high = binary_warped.shape[0] - window*window_height
            
            # Identify window boundaries
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            
            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                            (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                            (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            
            # Recenter next window on their mean position
            if len(good_left_inds) > minpix:
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:
                rightx_current = int(np.mean(nonzerox[good_right_inds]))

        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds] 
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        
        return leftx, lefty, rightx, righty

    def fit_polynomial(self, binary_warped):
        leftx, lefty, rightx, righty = self.find_lane_pixels(binary_warped)

        # Fit a second order polynomial to each
        # y = Ax^2 + Bx + C
        if len(leftx) == 0 or len(rightx) == 0:
            return None, None, None # Error handling if no lines found
            
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        
        return left_fit, right_fit, (leftx, lefty, rightx, righty)

    def calculate_data(self, binary_warped, left_fit, right_fit):
        """
        Calculates center offset and heading angle.
        """
        h, w = binary_warped.shape
        
        # 1. Calculate Center Offset
        # We evaluate the polynomial at the bottom of the image (y = h)
        y_eval = h
        left_x_pos = left_fit[0]*y_eval**2 + left_fit[1]*y_eval + left_fit[2]
        right_x_pos = right_fit[0]*y_eval**2 + right_fit[1]*y_eval + right_fit[2]
        
        lane_center = (left_x_pos + right_x_pos) / 2
        image_center = w / 2
        
        # Offset in meters (negative is left, positive is right)
        offset = (lane_center - image_center) * self.xm_per_pix

        # 2. Calculate Heading Angle
        # Calculate the slope (derivative) at the bottom of the image
        # x = Ay^2 + By + C  => dx/dy = 2Ay + B
        # Heading is arctan(dx/dy)
        
        left_derivative = 2*left_fit[0]*y_eval + left_fit[1]
        right_derivative = 2*right_fit[0]*y_eval + right_fit[1]
        
        avg_derivative = (left_derivative + right_derivative) / 2
        
        # Angle in radians, converted to degrees
        heading_angle_rad = np.arctan(avg_derivative)
        heading_angle_deg = np.degrees(heading_angle_rad)
        
        return offset, heading_angle_deg

    def run_pipeline(self, frame):
        # 1. Edge Detection & Masking
        edges = self.preprocess(frame)
        
        # 2. Perspective Transform
        warped, Minv = self.perspective_transform(edges)
        
        # 3. Fit Lanes
        left_fit, right_fit, pixel_data = self.fit_polynomial(warped)
        
        if left_fit is not None and right_fit is not None:
            # 4. Calculate Data
            offset, heading = self.calculate_data(warped, left_fit, right_fit)
            return offset, heading, warped
        else:
            return 0, 0, warped

# --- Usage Example ---
# detector = LaneDetector()
# frame = cv2.imread('road.jpg')
# offset, heading, debug_view = detector.run_pipeline(frame)
# print(f"Offset: {offset:.2f}m, Heading: {heading:.2f} degrees")

# ... (Your LaneDetector class is above this line) ...

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Initialize the "Brain" (Create an instance of your class)
    detector = LaneDetector()

    # 2. Initialize the "Eyes" (Open the USB Camera)
    # Using index 1 and DSHOW based on our troubleshooting
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
    # Optional: Force resolution if the camera is stubborn
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Starting Lane Detection... Press 'q' to exit.")

    while True:
        # 3. Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # 4. Feed the frame to the pipeline
        # Returns: offset (meters), heading (degrees), and the bird's eye view image
        offset, heading, warped_view = detector.run_pipeline(frame)

        # 5. Visualize the Data
        # Let's write the numbers directly on the video so we can see them
        cv2.putText(frame, f"Offset: {offset:.2f} m", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Heading: {heading:.2f} deg", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 6. Show the Windows
        cv2.imshow('Driver View', frame)       # What the driver sees
        cv2.imshow('Computer View', warped_view) # What the computer sees (Bird's Eye)

        # 7. Quit logic
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
