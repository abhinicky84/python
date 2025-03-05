import cv2
import numpy as np
import time

def capture_background():
    cap = cv2.VideoCapture(0)
    time.sleep(2)  # Allow camera to adjust
    print("Capturing background... Stay out of frame.")
    
    for _ in range(30):  # Capture multiple frames for better accuracy
        ret, background = cap.read()
        if not ret:
            print("Failed to capture background")
            return None

    cap.release()
    return background

background = capture_background()
cv2.imwrite("background.jpg", background)
print("Background captured and saved as 'background.jpg'")

def cloak_effect():
    cap = cv2.VideoCapture(0)
    background = cv2.imread("background.jpg")

    if background is None:
        print("Background image not found!")
        return

    print("Wear the cloak and stay in front of the camera.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert to HSV
       
        # Define cloak color range (adjust as needed)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])

        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        mask = mask1 + mask2

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3), np.uint8))

        mask_inv = cv2.bitwise_not(mask)

        res1 = cv2.bitwise_and(background, background, mask=mask)
        res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)

        final_output = cv2.addWeighted(res1, 1, res2, 1, 0)
        cv2.imshow("Invisibility Cloak", final_output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

cloak_effect()
