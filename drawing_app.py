import cv2
import numpy as np
import mediapipe as mp
from collections import deque

def run_drawing_app(save_callback=None):
    # Colour-specific deque lists
    bpoints = [deque(maxlen=1024)]
    gpoints = [deque(maxlen=1024)]
    rpoints = [deque(maxlen=1024)]
    ypoints = [deque(maxlen=1024)]

    # Indexes to track current position in each color deque
    blue_index = green_index = red_index = yellow_index = 0

    # Colors: Blue, Green, Red, Yellow
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0

    # Canvas setup
    paintWindow = np.ones((471, 750, 3), dtype=np.uint8) * 255
    cv2.rectangle(paintWindow, (40, 1), (140, 65), (0, 0, 0), 2)
    cv2.rectangle(paintWindow, (160, 1), (255, 65), (255, 0, 0), 2)
    cv2.rectangle(paintWindow, (275, 1), (370, 65), (0, 255, 0), 2)
    cv2.rectangle(paintWindow, (390, 1), (485, 65), (0, 0, 255), 2)
    cv2.rectangle(paintWindow, (505, 1), (600, 65), (0, 255, 255), 2)
    cv2.rectangle(paintWindow, (620, 1), (710, 65), (0, 0, 0), 2)

    cv2.putText(paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(paintWindow, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(paintWindow, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(paintWindow, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(paintWindow, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(paintWindow, "SAVE & EXIT", (620, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

    # Initialize MediaPipe Hands
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    # Webcam input
    cap = cv2.VideoCapture(0)
    ret = True
    saved_image = None

    while ret:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (750, 480))
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # UI Buttons
        cv2.rectangle(frame, (40, 1), (140, 65), (0, 0, 0), 2)
        cv2.rectangle(frame, (160, 1), (255, 65), (255, 0, 0), 2)
        cv2.rectangle(frame, (275, 1), (370, 65), (0, 255, 0), 2)
        cv2.rectangle(frame, (390, 1), (485, 65), (0, 0, 255), 2)
        cv2.rectangle(frame, (505, 1), (600, 65), (0, 255, 255), 2)
        cv2.rectangle(frame, (620, 1), (710, 65), (0, 0, 0), 2)

        cv2.putText(frame, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "SAVE & EXIT", (620, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        result = hands.process(framergb)
        if result.multi_hand_landmarks:
            landmarks = []
            for handlm in result.multi_hand_landmarks:
                for lm in handlm.landmark:
                    lmx = int(lm.x * 750)
                    lmy = int(lm.y * 480)
                    landmarks.append([lmx, lmy])
                mpDraw.draw_landmarks(frame, handlm, mpHands.HAND_CONNECTIONS)

            fore_finger = tuple(landmarks[8])
            thumb = tuple(landmarks[4])
            center = fore_finger
            cv2.circle(frame, center, 5, (0, 255, 0), -1)

            if abs(thumb[1] - center[1]) < 30:
                bpoints.append(deque(maxlen=512))
                blue_index += 1
                gpoints.append(deque(maxlen=512))
                green_index += 1
                rpoints.append(deque(maxlen=512))
                red_index += 1
                ypoints.append(deque(maxlen=512))
                yellow_index += 1

            elif center[1] <= 65:
                if 40 <= center[0] <= 140:  # CLEAR
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]
                    blue_index = green_index = red_index = yellow_index = 0
                    paintWindow[67:, :, :] = 255

                elif 160 <= center[0] <= 255:
                    colorIndex = 0  # BLUE
                elif 275 <= center[0] <= 370:
                    colorIndex = 1  # GREEN
                elif 390 <= center[0] <= 485:
                    colorIndex = 2  # RED
                elif 505 <= center[0] <= 600:
                    colorIndex = 3  # YELLOW
                elif 620 <= center[0] <= 710:
                    saved_image = paintWindow.copy()
                    break  # SAVE & EXIT

            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(center)
        else:
            bpoints.append(deque(maxlen=512))
            blue_index += 1
            gpoints.append(deque(maxlen=512))
            green_index += 1
            rpoints.append(deque(maxlen=512))
            red_index += 1
            ypoints.append(deque(maxlen=512))
            yellow_index += 1

        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        cv2.imshow("Output", frame)
        cv2.imshow("Paint", paintWindow)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return saved_image