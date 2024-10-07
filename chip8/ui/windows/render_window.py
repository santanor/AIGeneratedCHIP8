import imgui
import numpy as np
from OpenGL.GL import *

class RenderWindow:
    def __init__(self, emulator):
        self.emulator = emulator
        self.texture_id = None
        self.init_texture()

    def init_texture(self):
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    def update_texture(self, display_data):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        display_array = np.array(display_data, dtype=np.uint8) * 255
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 64, 32, 0, GL_RED, GL_UNSIGNED_BYTE, display_array)

    def render(self):
        display_data = self.emulator.get_display()
        self.update_texture(display_data)

        window_width = imgui.get_window_width()
        window_height = imgui.get_window_height()
        aspect_ratio = 64 / 32

        if window_width / window_height > aspect_ratio:
            image_height = window_height - 20
            image_width = image_height * aspect_ratio
        else:
            image_width = window_width - 20
            image_height = image_width / aspect_ratio

        imgui.image(self.texture_id, image_width, image_height)