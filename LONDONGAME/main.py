import cv2
import time
import pygame

class MotionDetector:
    def __init__(self, threshold=50):
        self.threshold = threshold
        self.previous_frame = None
        self.start_time = None
        
    def detect_motion(self, frame):
        # Convert frame to grayscaleq
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Blur the grayscale image to reduce noise
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # If this is the first frame, initialize previous frame and return False
        if self.previous_frame is None:
            self.previous_frame = gray
            self.start_time = time.time()
            return False
        
        # Compute absolute difference between current frame and previous frame
        frame_diff = cv2.absdiff(self.previous_frame, gray)
        # Apply a threshold to the difference image to extract foreground regions
        thresholded = cv2.threshold(frame_diff, self.threshold, 255, cv2.THRESH_BINARY)[1]
        # Dilate the thresholded image to fill in holes
        thresholded = cv2.dilate(thresholded, None, iterations=2)
        
        # Find contours in the thresholded image
        contours, hierarchy = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if any contours were found
        if len(contours) > 0:
            # Motion detected, update previous frame and return True
            self.previous_frame = gray
            self.start_time = time.time()
            return True
        
        # No motion detected, update previous frame and return False
        self.previous_frame = gray
        return False

# Initialize Pygame mixer for playing background music
pygame.mixer.init()
pygame.mixer.music.load("SQUID.mp3")  # Replace "background_music.mp3" with your audio file
pygame.mixer.music.play(-1)  # Loop the music indefinitely

# Initialize the MotionDetector object
md = MotionDetector()

# Open the laptop webcam
cap = cv2.VideoCapture(0)

start_time = cv2.getTickCount()
countdown_time = 25  # Countdown time in seconds
elapsed_time = 0
game_over = False
motiond = 0
end = 0

circle_color = (0, 255, 0)  # Green color
circle_radius = 50
circle_thickness = 5
circle_center = (100, 150)
last_color_change_time = time.time()

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    
    # If the frame was not captured, exit the loop
    if not ret:
        break
    
    # Resize the frame for faster processing
    frame = cv2.resize(frame, (1280, 720))
    
    
    # Detect motion in the frame
    motion_detected = md.detect_motion(frame)

    # Check if the color of the circle should be changed
    current_time = time.time()
    if current_time - last_color_change_time > 3:
        last_color_change_time = current_time
        if circle_color == (0, 255, 0):
            circle_color = (0, 0, 255)  # Red color
        else:
            circle_color = (0, 255, 0)  # Green color
    
    # Draw the circle
    cv2.circle(frame, circle_center, circle_radius, circle_color, circle_thickness)
    
    # Display the countdown timer on the top left corner of the frame
    if not game_over:
        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        remaining_time = countdown_time - int(elapsed_time)
        if remaining_time <= 0 or motiond == 1:
            game_over = True
        else:
            cv2.putText(frame, "Time: {}".format(remaining_time), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            if cv2.waitKey(1) & 0xFF == ord('w'):
                cv2.putText(frame, "You Win!", (520, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                win_start_time = time.time()
                while time.time() - win_start_time < 2:
                    cv2.imshow('Frame', frame)
                    cv2.waitKey(1)
                end = 1
                break

    
    # Display the text "detected" or "not detected" depending on whether motion is detected
    if motion_detected:
        if circle_color == (0, 0, 255):
           motiond = 1
        cv2.putText(frame, "Motion Detected", (1000, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Not Detected", (1000, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display the frame
    cv2.imshow('Frame', frame)
    
    if game_over == True and end == 0:
        cv2.putText(frame, "Game Over", (480, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        game_over_start_time = time.time()
        while time.time() - game_over_start_time < 2:
            cv2.imshow('Frame', frame)
            cv2.waitKey(1)
        end = 1
        break

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
