import cv2
import mediapipe as mp
import time
import pyautogui
import math


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True, color=(255, 0, 255), z_axis=False):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                if z_axis == False:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                elif z_axis:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z, 3)
                    lmList.append([id, cx, cy, cz])

                if draw:
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)

        return lmList
    


# Function to calculate the distance between two points
def calculateDistance(lm1, lm2):
    return math.sqrt((lm1[1] - lm2[1]) ** 2 + (lm1[2] - lm2[2]) ** 2)


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector(maxHands=1)

    prev_volume = 0
    prev_scroll = 0
    prev_cursor = (0, 0)
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture frame.")
            break

        img = detector.findHands(img)
        lmList = detector.findPosition(img, z_axis=True, draw=False)

        if len(lmList) != 0:
            # Volume Control: Thumb and Index finger distance (close = lower volume, far = raise volume)
            thumb_tip = lmList[4]
            index_tip = lmList[8]
            distance = calculateDistance(thumb_tip, index_tip)
            if distance < 50:
                # Increase volume
                pyautogui.press('volumeup')
            elif distance > 100:
                # Decrease volume
                pyautogui.press('volumedown')

            # Scrolling: Middle finger and Ring finger Y-axis difference
            middle_finger = lmList[12]
            ring_finger = lmList[16]
            scroll_diff = middle_finger[2] - ring_finger[2]
            if scroll_diff > 20:
                pyautogui.scroll(10)  # Scroll down
            elif scroll_diff < -20:
                pyautogui.scroll(-10)  # Scroll up

            # Cursor Control: Index finger X and Y movement
            index_finger = lmList[8]
            cursor_x, cursor_y = index_finger[1], index_finger[2]
            if abs(cursor_x - prev_cursor[0]) > 10 or abs(cursor_y - prev_cursor[1]) > 10:
                pyautogui.moveTo(cursor_x * 2, cursor_y * 2)  # Adjust sensitivity

            prev_cursor = (cursor_x, cursor_y)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('q') or key == 27:
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
