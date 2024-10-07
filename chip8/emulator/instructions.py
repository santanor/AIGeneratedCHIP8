class Instructions:
    def __init__(self, emulator):
        self.emulator = emulator

    def execute(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        instruction_map = {
            0x0000: lambda: self._execute_0(opcode),  # Pass opcode to _execute_0
            0x1000: lambda: self.jump(nnn),
            0x2000: lambda: self.call_subroutine(nnn),
            0x3000: lambda: self.skip_if_equal(x, nn),
            0x4000: lambda: self.skip_if_not_equal(x, nn),
            0x5000: lambda: self.skip_if_registers_equal(x, y),
            0x6000: lambda: self.set_register(x, nn),
            0x7000: lambda: self.add_to_register(x, nn),
            0x8000: lambda: self.register_operations(x, y, n),
            0x9000: lambda: self.skip_if_registers_not_equal(x, y),
            0xA000: lambda: self.set_index_register(nnn),
            0xB000: lambda: self.jump_with_offset(nnn),
            0xC000: lambda: self.random(x, nn),
            0xD000: lambda: self.draw(x, y, n),
            0xE000: lambda: self.skip_if_key(x, nn),
            0xF000: lambda: self.execute_f_instructions(x, nn),
        }

        instruction = instruction_map.get(opcode & 0xF000)
        if instruction:
            instruction()
        else:
            print(f"Warning: Unknown opcode encountered: {opcode:04X}. Skipping.")
            self.emulator.cpu.pc += 2  # Move to the next instruction

    def _execute_0(self, opcode):
        if opcode == 0x00E0:
            self.clear_screen()
        elif opcode == 0x00EE:
            self.return_from_subroutine()
        elif opcode == 0x0000:
            # No operation (NOP)
            print(f"Warning: NOP instruction (0x0000) encountered at PC: {self.emulator.cpu.pc:04X}")
            pass
        else:
            print(f"Warning: Unknown 0x0000 opcode: {opcode:04X}. Skipping.")
            self.emulator.cpu.pc += 2  # Move to the next instruction

    def clear_screen(self):
        self.emulator.display.clear()

    def return_from_subroutine(self):
        self.emulator.cpu.pc = self.emulator.cpu.stack.pop()

    def jump(self, address):
        self.emulator.cpu.pc = address

    def call_subroutine(self, address):
        self.emulator.cpu.stack.append(self.emulator.cpu.pc)
        self.emulator.cpu.pc = address

    def skip_if_equal(self, x, value):
        if self.emulator.cpu.v[x] == value:
            self.emulator.cpu.pc += 2

    def skip_if_not_equal(self, x, value):
        if self.emulator.cpu.v[x] != value:
            self.emulator.cpu.pc += 2

    def skip_if_registers_equal(self, x, y):
        if self.emulator.cpu.v[x] == self.emulator.cpu.v[y]:
            self.emulator.cpu.pc += 2

    def set_register(self, x, value):
        self.emulator.cpu.v[x] = value

    def add_to_register(self, x, value):
        self.emulator.cpu.v[x] = (self.emulator.cpu.v[x] + value) & 0xFF

    def register_operations(self, x, y, operation):
        operations = {
            0x0: lambda: self.set_register(x, self.emulator.cpu.v[y]),
            0x1: lambda: self.set_register(x, self.emulator.cpu.v[x] | self.emulator.cpu.v[y]),
            0x2: lambda: self.set_register(x, self.emulator.cpu.v[x] & self.emulator.cpu.v[y]),
            0x3: lambda: self.set_register(x, self.emulator.cpu.v[x] ^ self.emulator.cpu.v[y]),
            0x4: lambda: self._add_with_carry(x, y),
            0x5: lambda: self._subtract_with_borrow(x, y),
            0x6: lambda: self._shift_right(x),
            0x7: lambda: self._subtract_from_with_borrow(x, y),
            0xE: lambda: self._shift_left(x),
        }
        op = operations.get(operation)
        if op:
            op()
        else:
            raise ValueError(f"Unknown register operation: {operation:X}")

    def _add_with_carry(self, x, y):
        result = self.emulator.cpu.v[x] + self.emulator.cpu.v[y]
        self.emulator.cpu.v[0xF] = 1 if result > 255 else 0
        self.emulator.cpu.v[x] = result & 0xFF

    def _subtract_with_borrow(self, x, y):
        self.emulator.cpu.v[0xF] = 1 if self.emulator.cpu.v[x] >= self.emulator.cpu.v[y] else 0
        self.emulator.cpu.v[x] = (self.emulator.cpu.v[x] - self.emulator.cpu.v[y]) & 0xFF

    def _shift_right(self, x):
        self.emulator.cpu.v[0xF] = self.emulator.cpu.v[x] & 0x1
        self.emulator.cpu.v[x] >>= 1

    def _subtract_from_with_borrow(self, x, y):
        self.emulator.cpu.v[0xF] = 1 if self.emulator.cpu.v[y] >= self.emulator.cpu.v[x] else 0
        self.emulator.cpu.v[x] = (self.emulator.cpu.v[y] - self.emulator.cpu.v[x]) & 0xFF

    def _shift_left(self, x):
        self.emulator.cpu.v[0xF] = (self.emulator.cpu.v[x] & 0x80) >> 7
        self.emulator.cpu.v[x] = (self.emulator.cpu.v[x] << 1) & 0xFF

    def skip_if_registers_not_equal(self, x, y):
        if self.emulator.cpu.v[x] != self.emulator.cpu.v[y]:
            self.emulator.cpu.pc += 2

    def set_index_register(self, value):
        self.emulator.cpu.i = value

    def jump_with_offset(self, address):
        self.emulator.cpu.pc = address + self.emulator.cpu.v[0]

    def random(self, x, mask):
        import random
        self.emulator.cpu.v[x] = random.randint(0, 255) & mask

    def draw(self, x, y, height):
        x_coord = self.emulator.cpu.v[x] % self.emulator.display.WIDTH
        y_coord = self.emulator.cpu.v[y] % self.emulator.display.HEIGHT
        
        self.emulator.cpu.v[0xF] = 0  # Reset collision flag
        
        for row in range(height):
            if y_coord + row >= self.emulator.display.HEIGHT:
                break
            
            sprite_byte = self.emulator.memory.read_byte(self.emulator.cpu.i + row)
            
            for col in range(8):
                if x_coord + col >= self.emulator.display.WIDTH:
                    break
                
                if sprite_byte & (0x80 >> col):
                    if self.emulator.display.set_pixel(x_coord + col, y_coord + row):
                        self.emulator.cpu.v[0xF] = 1  # Set collision flag

    def skip_if_key(self, x, operation):
        key = self.emulator.cpu.v[x]
        if operation == 0x9E:
            if self.emulator.keyboard.is_key_pressed(key):
                self.emulator.cpu.pc += 2
        elif operation == 0xA1:
            if not self.emulator.keyboard.is_key_pressed(key):
                self.emulator.cpu.pc += 2
        else:
            raise ValueError(f"Unknown key operation: {operation:X}")

    def execute_f_instructions(self, x, operation):
        operations = {
            0x07: lambda: self.set_register(x, self.emulator.timer.delay_timer),
            0x0A: lambda: self._wait_for_key_press(x),
            0x15: lambda: setattr(self.emulator.timer, 'delay_timer', self.emulator.cpu.v[x]),
            0x18: lambda: setattr(self.emulator.timer, 'sound_timer', self.emulator.cpu.v[x]),
            0x1E: lambda: self._add_to_index(x),
            0x29: lambda: self._set_index_to_sprite_location(x),
            0x33: lambda: self._store_bcd(x),
            0x55: lambda: self._store_registers(x),
            0x65: lambda: self._load_registers(x),
        }
        op = operations.get(operation)
        if op:
            op()
        else:
            raise ValueError(f"Unknown F operation: {operation:X}")

    def _wait_for_key_press(self, x):
        key = self.emulator.keyboard.wait_for_key_press()
        self.emulator.cpu.v[x] = key

    def _add_to_index(self, x):
        self.emulator.cpu.i += self.emulator.cpu.v[x]
        if self.emulator.cpu.i > 0xFFF:
            self.emulator.cpu.v[0xF] = 1
            self.emulator.cpu.i &= 0xFFF

    def _set_index_to_sprite_location(self, x):
        self.emulator.cpu.i = self.emulator.cpu.v[x] * 5

    def _store_bcd(self, x):
        value = self.emulator.cpu.v[x]
        self.emulator.memory.write_byte(self.emulator.cpu.i, value // 100)
        self.emulator.memory.write_byte(self.emulator.cpu.i + 1, (value % 100) // 10)
        self.emulator.memory.write_byte(self.emulator.cpu.i + 2, value % 10)

    def _store_registers(self, x):
        for i in range(x + 1):
            self.emulator.memory.write_byte(self.emulator.cpu.i + i, self.emulator.cpu.v[i])

    def _load_registers(self, x):
        for i in range(x + 1):
            self.emulator.cpu.v[i] = self.emulator.memory.read_byte(self.emulator.cpu.i + i)