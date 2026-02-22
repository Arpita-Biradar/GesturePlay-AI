import cv2
import mediapipe as mp

class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )
        self.drawer = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.controls = {
            "direction": 0,
            "jump": False,
            "crouch": False,
            "attack": False,
            "label": "IDLE",
        }

    def _finger_open(self, hand, tip, pip):
        return hand.landmark[tip].y < hand.landmark[pip].y

    def _classify_controls(self, hand):
        index_tip = hand.landmark[8]
        wrist = hand.landmark[0]

        open_count = sum([
            self._finger_open(hand, 8, 6),
            self._finger_open(hand, 12, 10),
            self._finger_open(hand, 16, 14),
            self._finger_open(hand, 20, 18),
        ])

        direction = 0
        if index_tip.x < 0.38:
            direction = -1
        elif index_tip.x > 0.62:
            direction = 1

        jump = index_tip.y < 0.27 and open_count >= 2
        crouch = wrist.y > 0.72 and open_count >= 2
        attack = open_count <= 1

        label = "IDLE"
        if attack:
            label = "ATTACK"
        elif crouch:
            label = "CROUCH"
        elif jump:
            label = "JUMP"
        elif direction != 0:
            label = "MOVE"

        return {
            "direction": direction,
            "jump": jump,
            "crouch": crouch,
            "attack": attack,
            "label": label,
        }

    def get_gesture(self):
        controls = {
            "direction": 0,
            "jump": False,
            "crouch": False,
            "attack": False,
            "label": "IDLE",
        }

        if not self.cap.isOpened():
            return controls, None

        success, frame = self.cap.read()
        if not success:
            return controls, None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            controls = self._classify_controls(hand)
            self.drawer.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)

        self.controls = controls
        return controls, frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
        self.hands.close()
