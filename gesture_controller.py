import cv2
import mediapipe as mp

class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.cap = cv2.VideoCapture(0)

    def get_gesture(self):
        success, frame = self.cap.read()
        if not success: return None, None
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        command = "STAY"
        jump = False

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            index_tip = hand.landmark[8]
            
            # Logic: Screen thirds for Left/Right
            if index_tip.x < 0.33: command = "LEFT"
            elif index_tip.x > 0.66: command = "RIGHT"

            # Logic: Jump if index is high (low Y value)
            if index_tip.y < 0.3: jump = True

        return command, jump, frame

    def release(self):
        self.cap.release()