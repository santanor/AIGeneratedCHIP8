import time

from .cpu import CPU
from .memory import Memory
from .timer import Timer
from .display import Display  # Import the Display class
from .instructions import Instructions  # Import the Instructions class
from .keyboard import Keyboard

class Chip8Emulator:
    def __init__(self, instructions_per_second=700):
        self.memory = Memory()
        self.timer = Timer()
        self.display = Display()  # Create a Display object
        self.instructions = Instructions(self)  # Create an Instructions object
        self.cpu = CPU(self, self.instructions)  # Pass emulator and instructions to CPU
        self.instruction_count = 0
        self.last_time = time.time()
        self.instructions_per_second = instructions_per_second
        self.nanoseconds_per_instruction = 1_000_000_000 // instructions_per_second
        self.last_instruction_time = time.time_ns()
        self.keyboard = Keyboard()

    def load_rom(self, rom_path):
        # Read the ROM file
        with open(rom_path, 'rb') as rom_file:
            rom_data = rom_file.read()
        
        # Check if the ROM fits in memory
        if len(rom_data) > 4096 - 0x200:
            raise ValueError("ROM is too large to fit in memory")
        
        # Load the ROM into memory
        self.memory.load_rom(rom_data)
        
        # Set the program counter to the start of the ROM
        self.cpu.pc = 0x200


    def step(self):
        # Execute one instruction
        self.cpu.step()

        # Calculate the time to sleep
        current_time = time.time_ns()
        time_elapsed = current_time - self.last_instruction_time
        time_to_sleep = self.nanoseconds_per_instruction - time_elapsed

        if time_to_sleep > 0:
            # Sleep for the remaining time
            time.sleep(time_to_sleep / 1_000_000_000)

        # Update the last instruction time
        self.last_instruction_time = time.time_ns()

    def update_timers(self):
        # Update delay and sound timers
        self.timer.update()

    def get_display(self):
        """Return the current state of the display."""
        return self.display.get_display()

    def set_key_pressed(self, key):
        # Set a key as pressed
        self.cpu.set_key_pressed(key)

    def set_key_released(self, key):
        # Set a key as released
        self.cpu.set_key_released(key)

    def is_sound_active(self):
        # Check if sound should be playing
        return self.timer.is_sound_active()

    def set_instructions_per_second(self, ips):
        """Set the number of instructions to execute per second."""
        self.instructions_per_second = ips