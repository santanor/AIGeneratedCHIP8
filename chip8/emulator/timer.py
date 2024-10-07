import time

class Timer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.delay_timer = 0
        self.sound_timer = 0
        self.last_update = time.time()

    def update(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update

        # CHIP-8 timers decrement at 60Hz
        decrement = int(elapsed_time * 60)

        if decrement > 0:
            self.delay_timer = max(0, self.delay_timer - decrement)
            self.sound_timer = max(0, self.sound_timer - decrement)
            self.last_update = current_time

    def set_delay_timer(self, value):
        self.delay_timer = value

    def set_sound_timer(self, value):
        self.sound_timer = value

    def get_delay_timer(self):
        return self.delay_timer

    def get_sound_timer(self):
        return self.sound_timer

    def is_sound_active(self):
        return self.sound_timer > 0
