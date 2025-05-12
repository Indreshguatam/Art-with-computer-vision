import cv2
import numpy as np
import mediapipe as mp
from collections import deque

class DrawingApp:
    def __init__(self):
        # Initialize drawing parameters
        self.bpoints = [deque(maxlen=1024)]
        self.gpoints = [deque(maxlen=1024)]
        self.rpoints = [deque(maxlen=1024)]
        self.ypoints = [deque(maxlen=1024)]
        
        self.blue_index = 0
        self.green_index = 0
        self.red_index = 0
        self.yellow_index = 0
        
        # Colors: Blue, Green, Red, Yellow
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
        self.colorIndex = 0
        
        # Button areas: [x1, x2, y1, y2]
        self.buttons = {
            "clear": [40, 140, 1, 65],
            "blue": [160, 255, 1, 65],
            "green": [275, 370, 1, 65],
            "red": [390, 485, 1, 65],
            "yellow": [505, 600, 1, 65],
            "exit": [620, 710, 1, 65]
        }
        
        # Initialize MediaPipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils

    def run(self):
        # Initialize canvas
        paintWindow = np.ones((471, 750, 3), dtype=np.uint8) * 255
        self._setup_ui(paintWindow)
        
        cap = cv2.VideoCapture(0)
        saved_image = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (750, 480))
            framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            result = self.hands.process(framergb)
            
            if result.multi_hand_landmarks:
                landmarks = []
                for handlm in result.multi_hand_landmarks:
                    for lm in handlm.landmark:
                        lmx = int(lm.x * 750)
                        lmy = int(lm.y * 480)
                        landmarks.append([lmx, lmy])
                    self.mpDraw.draw_landmarks(frame, handlm, self.mpHands.HAND_CONNECTIONS)

                if landmarks:
                    fore_finger = (landmarks[8][0], landmarks[8][1])
                    thumb = (landmarks[4][0], landmarks[4][1])
                    
                    # Check for pinch (stop drawing)
                    if abs(thumb[1] - fore_finger[1]) < 30:
                        self._new_stroke()
                    # Check for button press
                    elif fore_finger[1] <= 65:
                        button = self._check_button_press(fore_finger)
                        if button == "exit":
                            saved_image = paintWindow.copy()
                            break
                        elif button == "clear":
                            self._clear_canvas(paintWindow)
                        elif button in ["blue", "green", "red", "yellow"]:
                            self.colorIndex = ["blue", "green", "red", "yellow"].index(button)
                    # Normal drawing
                    else:
                        self._add_point(fore_finger)

            # Draw all points
            self._draw_points(frame, paintWindow)
            
            # Show windows
            cv2.imshow("Output", frame)
            cv2.imshow("Paint", paintWindow)
            
            # Keyboard controls
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:  # ESC or Q to quit
                break
            elif key == ord('s'):  # S to save
                saved_image = paintWindow.copy()
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return saved_image

    def _setup_ui(self, window):
        # Setup UI buttons
        cv2.rectangle(window, (40, 1), (140, 65), (0, 0, 0), 2)
        cv2.rectangle(window, (160, 1), (255, 65), (255, 0, 0), 2)
        cv2.rectangle(window, (275, 1), (370, 65), (0, 255, 0), 2)
        cv2.rectangle(window, (390, 1), (485, 65), (0, 0, 255), 2)
        cv2.rectangle(window, (505, 1), (600, 65), (0, 255, 255), 2)
        cv2.rectangle(window, (620, 1), (710, 65), (0, 0, 0), 2)

        cv2.putText(window, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(window, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(window, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(window, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(window, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(window, "SAVE & EXIT", (620, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    def _check_button_press(self, pos):
        x, y = pos
        for button, (x1, x2, y1, y2) in self.buttons.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return button
        return None

    def _add_point(self, pos):
        if self.colorIndex == 0:
            self.bpoints[self.blue_index].append(pos)
        elif self.colorIndex == 1:
            self.gpoints[self.green_index].append(pos)
        elif self.colorIndex == 2:
            self.rpoints[self.red_index].append(pos)
        elif self.colorIndex == 3:
            self.ypoints[self.yellow_index].append(pos)

    def _draw_points(self, frame, canvas):
        points = [self.bpoints, self.gpoints, self.rpoints, self.ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k-1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k-1], points[i][j][k], self.colors[i], 2)
                    cv2.line(canvas, points[i][j][k-1], points[i][j][k], self.colors[i], 2)

    def _new_stroke(self):
        self.bpoints.append(deque(maxlen=512))
        self.blue_index += 1
        self.gpoints.append(deque(maxlen=512))
        self.green_index += 1
        self.rpoints.append(deque(maxlen=512))
        self.red_index += 1
        self.ypoints.append(deque(maxlen=512))
        self.yellow_index += 1

    def _clear_canvas(self, window):
        self.bpoints = [deque(maxlen=512)]
        self.gpoints = [deque(maxlen=512)]
        self.rpoints = [deque(maxlen=512)]
        self.ypoints = [deque(maxlen=512)]
        self.blue_index = 0
        self.green_index = 0
        self.red_index = 0
        self.yellow_index = 0
        window[67:, :, :] = 255