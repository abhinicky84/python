import cv2
import numpy as np
import requests
import json
import time

# Azure AI Vision API Details
AZURE_VISION_ENDPOINT = "https://e-us-test-vision-ai-service.cognitiveservices.azure.com/"
AZURE_VISION_KEY = "9vCIBu8Iwk33iRdvUHUyBCsP7Nt4y2f3QLmuZJDfoKcQRj4S8PZ3JQQJ99BAACYeBjFXJ3w3AAAFACOGG7Z3"

def analyze_frame_with_azure(image):
    """Send the frame to Azure AI Vision API for color analysis."""
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY,
        'Content-Type': 'application/octet-stream'
    }

    response = requests.post(
        f"{AZURE_VISION_ENDPOINT}/vision/v3.1/analyze?visualFeatures=Color",
        headers=headers,
        data=image
    )

    if response.status_code == 200:
        result = response.json()
        dominant_color = result['color']['dominantColors'][0]
        print(f"Detected Cloak Color: {dominant_color}")
        return dominant_color.lower()
    else:
        print("Azure Vision API Error:", response.text)
        return None

def capture_background():
    """Captures the background image when the cloak is not present."""
    cap = cv2.VideoCapture(0)
    time.sleep(2)  # Allow the camera to adjust
    print("Capturing background. Stay out of the frame...")
    
    for _ in range(30):
        ret, background = cap.read()
        if not ret:
            print("Failed to capture background.")
            cap.release()
            return None

    cap.release()
    print("Background captured successfully.")
    return background

def capture_cloak_color():
    """Captures a frame and sends it to Azure AI Vision to detect the cloak color."""
    cap = cv2.VideoCapture(0)
    time.sleep(2)
    
    print("Place the cloak in front of the camera and press 's' to detect the color.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.putText(frame, "Press 's' to detect cloak color", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Detect Cloak Color", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            _, img_encoded = cv2.imencode('.jpg', frame)
            detected_color = analyze_frame_with_azure(img_encoded.tobytes())
            break

    cap.release()
    cv2.destroyAllWindows()
    
    if detected_color:
        return detected_color
    return None

def create_color_mask(hsv, color):
    """Creates a mask for the detected cloak color."""
    color_ranges = {
        "red": ([0, 120, 70], [10, 255, 255]),
        "blue": ([90, 120, 70], [130, 255, 255]),
        "green": ([36, 100, 100], [86, 255, 255]),
        "yellow": ([20, 100, 100], [40, 255, 255]),
        "orange": ([5, 100, 100], [15, 255, 255]),
        "purple": ([130, 50, 50], [160, 255, 255]),
        "pink": ([140, 50, 50], [170, 255, 255]),
        "brown": ([10, 40, 50], [20, 255, 255]),
        "gray": ([0, 0, 50], [180, 50, 130]),
        "white": ([0, 0, 200], [180, 50, 255]),
        "black": ([0, 0, 0], [180, 255, 50]),
        "light_blue": ([90, 50, 50], [130, 255, 255]),
        "dark_blue": ([110, 50, 50], [130, 255, 255]),
        "light_green": ([35, 50, 50], [75, 255, 255]),
        "dark_green": ([40, 50, 50], [80, 255, 255]),
        "light_pink": ([145, 50, 50], [165, 255, 255]),
        "dark_pink": ([155, 50, 50], [175, 255, 255]),
        "light_purple": ([135, 50, 50], [155, 255, 255]),
        "dark_purple": ([140, 50, 50], [160, 255, 255]),
        "light_yellow": ([20, 50, 50], [40, 255, 255]),
        "dark_yellow": ([30, 50, 50], [50, 255, 255]),
        "light_brown": ([15, 50, 50], [25, 255, 255]),
        "dark_brown": ([10, 50, 50], [20, 255, 255]),
        "light_red": ([0, 50, 50], [10, 255, 255]),
        "dark_red": ([0, 50, 50], [10, 255, 150]),
        "beige": ([20, 40, 60], [30, 255, 255]),
        "mint": ([45, 50, 50], [85, 255, 255]),
        "emerald": ([60, 50, 50], [100, 255, 255]),
        "turquoise": ([80, 50, 50], [100, 255, 255]),
        "magenta": ([140, 50, 50], [160, 255, 255]),
        "lime": ([45, 50, 50], [75, 255, 255]),
        "cyan": ([80, 50, 50], [100, 255, 255]),
        "indigo": ([130, 50, 50], [160, 255, 255]),
        "violet": ([135, 50, 50], [160, 255, 255]),
        "charcoal": ([0, 0, 20], [180, 30, 60]),
        "peach": ([10, 40, 100], [20, 255, 255]),
        "plum": ([160, 50, 50], [180, 255, 255]),
        "gold": ([30, 100, 100], [50, 255, 255]),
        "ivory": ([0, 0, 200], [180, 30, 255]),
        "olive": ([30, 50, 50], [70, 255, 255]),
        "teal": ([90, 50, 50], [120, 255, 255]),
        "sand": ([20, 50, 50], [40, 255, 255]),
        "tan": ([20, 50, 50], [40, 255, 255]),
        "lavender": ([130, 50, 50], [160, 255, 255]),
        "sky_blue": ([90, 50, 50], [130, 255, 255]),
        "mint_green": ([45, 50, 50], [85, 255, 255]),
        "jade": ([60, 50, 50], [100, 255, 255]),
        "salmon": ([10, 50, 100], [20, 255, 255]),
        "periwinkle": ([135, 50, 50], [150, 255, 255]),
        "fuchsia": ([150, 50, 50], [180, 255, 255])
}


    if color in color_ranges:
        lower, upper = np.array(color_ranges[color][0]), np.array(color_ranges[color][1])
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.medianBlur(mask, 5)
        return mask
    else:
        print("Detected color is not in predefined ranges.")
        return None

def start_invisibility_effect(background, cloak_color):
    """Applies the invisibility effect using the detected cloak color."""
    cap = cv2.VideoCapture(0)
    print("Press 'q' to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = create_color_mask(hsv, cloak_color)

        if mask is not None:
            result = frame.copy()
            result[np.where(mask != 0)] = background[np.where(mask != 0)]
            cv2.imshow("Invisibility Cloak", result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    background = capture_background()
    if background is not None:
        cloak_color = capture_cloak_color()
        if cloak_color:
            start_invisibility_effect(background, cloak_color)
