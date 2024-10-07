from .instructions import Instructions  # Add this import at the top of the file
import threading

class CPU:
    def __init__(self, emulator, instructions):
        self.emulator = emulator
        self.instructions = instructions
        self.lock = threading.Lock()
        self.memory = emulator.memory
        self.timer = emulator.timer
        self.pc = 0x200  # Program counter
        self.v = [0] * 16  # V registers
        self.i = 0  # Index register
        self.stack = []
        self.sp = 0  # Stack pointer

    def fetch(self):
        # Fetch the instruction at the current PC
        instruction = (self.memory.read_byte(self.pc) << 8) | self.memory.read_byte(self.pc + 1)
        self.pc += 2
        return instruction

    def execute(self, instruction):
        # Execute the instruction
        self.instructions.execute(instruction)

    def step(self):
        instruction = self.fetch()
        self.execute(instruction)

    def read_register(self, index):
        with self.lock:
            return self.v[index]

