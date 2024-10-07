import glfw

class Keyboard:
    def __init__(self):
        self.key_map = {
            glfw.KEY_1: 0x1, glfw.KEY_2: 0x2, glfw.KEY_3: 0x3, glfw.KEY_4: 0xC,
            glfw.KEY_Q: 0x4, glfw.KEY_W: 0x5, glfw.KEY_E: 0x6, glfw.KEY_R: 0xD,
            glfw.KEY_A: 0x7, glfw.KEY_S: 0x8, glfw.KEY_D: 0x9, glfw.KEY_F: 0xE,
            glfw.KEY_Z: 0xA, glfw.KEY_X: 0x0, glfw.KEY_C: 0xB, glfw.KEY_V: 0xF
        }
        self.keys = [False] * 16

    def key_down(self, key):
        if key in self.key_map:
            self.keys[self.key_map[key]] = True

    def key_up(self, key):
        if key in self.key_map:
            self.keys[self.key_map[key]] = False

    def is_key_pressed(self, key):
        return self.keys[key]

    def wait_for_key_press(self):
        while True:
            for i in range(16):
                if self.keys[i]:
                    return i
