from mss import mss
import numpy as np
import time
import cv2

with mss() as sct:
    # Define screen capture settings
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    
    for _ in range(120):
        last_time = time.time()
        
        # Capture screen frame
        img = np.array(sct.grab(monitor))
        
        cv2.imshow("OpenCV/Numpy normal", img)
        
        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale', cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

        print(f"fps: {1 / (time.time() - last_time)}")

        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break