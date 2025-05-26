try:


    import subprocess
    import sys

    def install_requirements():
        try:
            import numpy  # Example check
        except ImportError:
            print("Installing required packages...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    install_requirements()

    import cv2
    import numpy as np
    import mss
    import winsound
    import time  # For cooldown handling

    # Load reference image (DO NOT resize)
    reference = cv2.imread("20Provacation.png", cv2.IMREAD_COLOR)

    monitor_number = 1  # Adjust for your target monitor
    match_count = 0  # Tracks consecutive matches
    max_match_limit = 3  # Number of times "Match found!" should trigger in a row
    match_active = False  # Tracks when a match was previously detected
    cooldown_time = 2  # Seconds before allowing a new match detection
    last_detection_time = 0  # Tracks the last detected time

    with mss.mss() as sct:
        monitor = sct.monitors[monitor_number]
        region_width = monitor["width"] // 4
        region_height = monitor["height"] // 6
        x_pos = (monitor["width"] - region_width) // 2
        lower_y = monitor["height"] - region_height
        higher_y = monitor["height"] - region_height * 2
        y_pos = (lower_y + higher_y) // 2

        monitor_region = {
            "left": monitor["left"] + x_pos,
            "top": monitor["top"] + y_pos,
            "width": region_width,
            "height": region_height
        }

        while True:
            # Capture screenshot of region
            screenshot = sct.grab(monitor_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Convert both images to grayscale for better matching
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            reference_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

            # Perform template matching (search for reference inside region)
            result = cv2.matchTemplate(img_gray, reference_gray, cv2.TM_CCOEFF_NORMED)
            threshold = 0.92  # High accuracy but allows minor variations

            locations = np.where(result >= threshold)
            if locations[0].size > 0:
                if not match_active or (time.time() - last_detection_time > cooldown_time):
                    match_active = True
                    match_count += 1
                    last_detection_time = time.time()  # Reset detection time

                    if match_count <= max_match_limit:
                        print("Match found!")
                        winsound.Beep(1000, 300)  # Play sound only a few times

            else:
                match_active = False
                match_count = 0  # Reset count when no match is found

            # Show captured region with detected matches
            cv2.imshow("Captured Region", img)

            # Exit condition (press 'q' to quit)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()


    input("Press any button to close")
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")