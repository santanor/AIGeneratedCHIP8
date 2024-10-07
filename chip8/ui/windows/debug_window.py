from ..window import Window
import imgui

class DebugWindow(Window):
    def __init__(self, emulator):
        super().__init__("Debug")
        self.emulator = emulator

    def draw_contents(self):
        if imgui.begin_table("debug_table", 2, imgui.TABLE_BORDERS | imgui.TABLE_SIZING_FIXED_FIT):
            imgui.table_setup_column("Label")
            imgui.table_setup_column("Value")
            imgui.table_headers_row()

            cpu = self.emulator.cpu

            debug_data = [
                ("PC", f"0x{cpu.pc:04X}"),
                ("I", f"0x{cpu.i:04X}"),
            ]

            for i in range(16):
                debug_data.append((f"V{i:X}", f"0x{cpu.v[i]:02X}"))

            for label, value in debug_data:
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text(label)
                imgui.table_next_column()
                imgui.text(value)

            imgui.end_table()