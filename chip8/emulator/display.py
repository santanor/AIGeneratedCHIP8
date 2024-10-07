class Display:
    WIDTH = 64
    HEIGHT = 32

    def __init__(self):
        self.screen = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]

    def clear(self):
        """Clear the display, turning all pixels off."""
        self.screen = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]

    def set_pixel(self, x, y):
        self.screen[y][x] ^= 1
        return self.screen[y][x] == 0

    def get_display(self):
        """Return the current state of the display."""
        return self.screen
