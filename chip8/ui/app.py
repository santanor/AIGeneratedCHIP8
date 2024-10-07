import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import imgui
from .windows.render_window import RenderWindow
from .windows.debug_window import DebugWindow
from chip8.emulator.chip8_emulator import Chip8Emulator
import threading

class App:
    def __init__(self):
        self.window = None
        self.impl = None
        self.render_window = None
        self.debug_window = None
        self.emulator = None  # Add this line
        self.should_stop = False  # Add this line
        self.emulator_thread = None  # Add this line

    def run(self):
        self.init()
        # Start the emulator thread
        self.emulator_thread = threading.Thread(target=self.emulator_loop)
        self.emulator_thread.start()
        try:
            self.main_loop()
        finally:
            self.shutdown()

    def init(self):
        imgui.create_context()
        self.window = self.impl_glfw_init()
        self.impl = GlfwRenderer(self.window)
        self.emulator = Chip8Emulator()  # Initialize the emulator
        self.render_window = RenderWindow(self.emulator)
        self.debug_window = DebugWindow(self.emulator)
        self.emulator.load_rom("./roms/clock.ch8")  # Load a ROM file
        glfw.set_key_callback(self.window, self.key_callback)

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            self.process_frame()

    def process_frame(self):
        glfw.poll_events()
        self.impl.process_inputs()

        imgui.new_frame()

        self.draw_main_layout()

        self.render()

    def draw_main_layout(self):
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(*self.get_window_size())
        
        imgui.begin("CHIP-8 Emulator", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
        
        imgui.set_window_font_scale(1.5)
        imgui.text("CHIP-8")
        imgui.set_window_font_scale(1.0)
        
        imgui.separator()

        # Create a horizontal layout
        imgui.columns(2, "main_layout")
        
        # Render window on the left
        self.render_window.render()
        
        imgui.next_column()
        
        # Debug window on the right
        self.debug_window.render()
        
        imgui.columns(1)
        
        imgui.end()

    def render(self):
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        self.impl.render(imgui.get_draw_data())
        glfw.swap_buffers(self.window)

    def shutdown(self):
        self.impl.shutdown()
        glfw.terminate()

    @staticmethod
    def impl_glfw_init():
        width, height = 1280, 720
        window_name = "PyImGui CHIP-8 Emulator"

        if not glfw.init():
            print("Could not initialize OpenGL context")
            exit(1)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        window = glfw.create_window(int(width), int(height), window_name, None, None)
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            exit(1)

        return window

    def get_window_size(self):
        return glfw.get_window_size(self.window)

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.emulator.keyboard.key_down(key)
        elif action == glfw.RELEASE:
            self.emulator.keyboard.key_up(key)

    def emulator_loop(self):
        while not self.should_stop:
            self.emulator.step()
            self.emulator.update_timers()