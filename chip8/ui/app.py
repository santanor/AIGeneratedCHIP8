import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import imgui
from .windows.render_window import RenderWindow
from .windows.debug_window import DebugWindow
from chip8.emulator.chip8_emulator import Chip8Emulator
import threading
import sys
from pyobjus import autoclass

if sys.platform == 'darwin':
    from pyobjus import autoclass
    from pyobjus.dylib_manager import load_framework

class App:
    def __init__(self):
        self.window = None
        self.impl = None
        self.render_window = None
        self.debug_window = None
        self.emulator = None
        self.should_stop = False
        self.emulator_thread = None
        self.rom_path = None

    def run(self):
        self.init()
        self.emulator_thread = threading.Thread(target=self.emulator_loop)
        self.emulator_thread.start()
        try:
            self.main_loop()
        finally:
            self.shutdown()

    def init(self):
        if not glfw.init():
            print("Could not initialize OpenGL context")
            exit(1)

        self.window = self.impl_glfw_init()
        
        # Set up the menu callback
        glfw.set_drop_callback(self.window, self.drop_callback)

        imgui.create_context()
        self.impl = GlfwRenderer(self.window)
        self.emulator = Chip8Emulator()
        self.render_window = RenderWindow(self.emulator)
        self.debug_window = DebugWindow(self.emulator)
        self.load_rom("./roms/octopeg.ch8")  # Load default ROM
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
        window_width, window_height = self.get_window_size()
        
        # Main window
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(window_width, window_height)
        imgui.begin("CHIP-8 Emulator", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
        
        if imgui.button("Load ROM"):
            self.open_file_dialog()
        
        imgui.same_line()
        imgui.text(f"Current ROM: {self.rom_path or 'None'}")
        
        imgui.separator()
        
        # Calculate sizes
        render_width = int(window_width * 0.8)
        debug_width = window_width - render_width
        content_height = window_height - 60  # Subtract space for the top bar

        # Render window (80% width)
        imgui.set_next_window_position(0, 60)
        imgui.set_next_window_size(render_width, content_height)
        imgui.begin("Render", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        self.render_window.render()
        imgui.end()

        # Debug window (20% width)
        imgui.set_next_window_position(render_width, 60)
        imgui.set_next_window_size(debug_width, content_height)
        imgui.begin("Debug", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        self.debug_window.render()
        imgui.end()

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

    def impl_glfw_init(self):
        width, height = 1280, 720
        window_name = "CHIP-8 Emulator"

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
        if key == glfw.KEY_O and action == glfw.PRESS and mods & glfw.MOD_CONTROL:
            self.open_file_dialog()
        elif action == glfw.PRESS:
            self.emulator.keyboard.key_down(key)
        elif action == glfw.RELEASE:
            self.emulator.keyboard.key_up(key)

    def emulator_loop(self):
        while not self.should_stop:
            self.emulator.step()
            self.emulator.update_timers()

    def open_file_dialog(self):
        if sys.platform == 'darwin':
            load_framework('/System/Library/Frameworks/AppKit.framework')
            NSOpenPanel = autoclass('NSOpenPanel')
            NSURL = autoclass('NSURL')
            
            panel = NSOpenPanel.openPanel()
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setAllowedFileTypes_(["ch8"])
            
            if panel.runModal() == 1:  # NSModalResponseOK
                urls = panel.URLs()
                print(f"URLs Count: {urls.count()}")  # Debug print
                
                if urls.count() > 0:
                    url = urls.objectAtIndex_(0)
                    print(f"URL Object: {url}")  # Debug print
                    
                    # Step 1: Access the 'path' property
                    path_nsstr = url.path
                    print(f"Path (__NSCFString): {path_nsstr}")  # Debug print
                    
                    # Step 2: Get the UTF8 representation (bytes)
                    path_bytes = path_nsstr.UTF8String()

                    # Optional: Additional validation
                    if path_bytes.lower().endswith('.ch8'):
                        self.load_rom(path_bytes)
                    else:
                        print("Error: Selected file is not a .ch8 ROM file.")
                else:
                    print("Error: No file was selected.")
        else:
            # Fallback to tkinter for other platforms
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(filetypes=[("CHIP-8 ROM", "*.ch8")])
            if file_path:
                self.load_rom(file_path)

    def load_rom(self, rom_path):
        self.rom_path = rom_path
        self.emulator.reset()
        self.emulator.load_rom(rom_path)

    def drop_callback(self, window, paths):
        if paths:
            file_path = paths[0]
            if file_path.lower().endswith('.ch8'):
                self.load_rom(file_path)