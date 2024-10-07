from ..window import Window
import imgui

class MainWindow(Window):
    def __init__(self):
        super().__init__("CHIP-8 Emulator")
        self.render_window = RenderWindow()
        self.debug_window = DebugWindow()

    def draw_contents(self):
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

from .render_window import RenderWindow
from .debug_window import DebugWindow