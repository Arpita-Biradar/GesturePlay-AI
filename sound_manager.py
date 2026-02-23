import array
import math
import pygame


def _build_tone(freq_hz, duration_ms, volume=0.35, sample_rate=44100):
    total = max(1, int(sample_rate * (duration_ms / 1000.0)))
    fade = max(1, int(total * 0.08))
    data = array.array("h")
    amp = int(32767 * max(0.0, min(1.0, volume)))
    for i in range(total):
        t = i / float(sample_rate)
        env = 1.0
        if i < fade:
            env = i / float(fade)
        elif i > total - fade:
            env = (total - i) / float(fade)
        sample = int(amp * env * math.sin(2.0 * math.pi * freq_hz * t))
        data.append(sample)
    return data


def _concat(*chunks):
    out = array.array("h")
    for chunk in chunks:
        out.extend(chunk)
    return out


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.available = False
        self.sounds = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.available = True
            self._build_sounds()
        except pygame.error:
            self.available = False

    def _sound_from(self, samples):
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _build_sounds(self):
        self.sounds["jump"] = self._sound_from(_build_tone(620, 90, 0.30))
        self.sounds["coin"] = self._sound_from(_build_tone(980, 70, 0.33))
        self.sounds["core"] = self._sound_from(_concat(_build_tone(720, 70, 0.32), _build_tone(1040, 90, 0.34)))
        self.sounds["attack"] = self._sound_from(_build_tone(420, 65, 0.32))
        self.sounds["hit"] = self._sound_from(_concat(_build_tone(190, 90, 0.36), _build_tone(150, 90, 0.30)))
        self.sounds["level_up"] = self._sound_from(
            _concat(_build_tone(520, 70, 0.28), _build_tone(700, 70, 0.30), _build_tone(920, 85, 0.34))
        )
        self.sounds["game_over"] = self._sound_from(
            _concat(_build_tone(440, 95, 0.32), _build_tone(300, 95, 0.32), _build_tone(190, 160, 0.34))
        )
        self.sounds["ui_click"] = self._sound_from(_concat(_build_tone(800, 45, 0.25), _build_tone(920, 40, 0.22)))

    def set_enabled(self, enabled):
        self.enabled = enabled

    def play(self, name):
        if not self.available or not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd is not None:
            snd.play()
