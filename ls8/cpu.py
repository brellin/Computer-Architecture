"""CPU functionality."""

import sys
HLT = 0x01   # Halt CPU and exit emulator
LDI = 0x82   # Set value of register to integer
PRN = 0x47   # Print numeric value stored in register
MUL = 0xA2   # Multiply values in two registers together and store the result in the first register
POP = 0x46   # Pop the value at the top of the stack into the given register
PUSH = 0x45  # Push value in given register on stack


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 0x100
        self.reg = [0] * 0x08
        self.pc = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0x00
        self.sp = 0xF4
        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            POP: self.pop,
            PUSH: self.push,
            'ALU': {
                MUL: self.alu
            }
        }

    def load(self, path):
        """Load a program into memory."""

        address = 0

        f = open(path)
        program = f.read().splitlines()
        f.close()

        for index, line in enumerate(program):
            comment = line.find('#')
            if comment != -1:
                line = line[:comment]
            if line != '':
                line = int(line.strip(), 2)
            program[index] = line

        while '' in program:
            program.remove('')

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def hlt(self, *args):
        exit()

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            reg1 = self.reg[reg_a]
            reg2 = self.reg[reg_b]
            mul = reg1 * reg2
            self.reg[reg_a] = mul
        else:
            raise Exception("Unsupported ALU operation")

    def pop(self, operand_a, operand_b):
        # Copy val from sp to given register
        val = self.ram_read(self.sp)
        self.reg[operand_a] = val
        # Increment sp
        self.sp += 1

    def push(self, operand_a, operand_b):
        # Decrement sp
        self.sp -= 1
        # Copy value in given register to sp
        self.ram_write(self.sp, self.reg[operand_a])

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while True:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir in self.branchtable:
                self.branchtable[ir](operand_a, operand_b)
                self.pc += (ir >> 6) + 1

            elif ir in self.branchtable['ALU']:
                self.branchtable['ALU'][ir](ir, operand_a, operand_b)
                self.pc += (ir >> 6) + 1

        self.trace()

    def ram_read(self, address):
        self.mar = address
        self.mdr = self.ram[address]
        return self.mdr

    def ram_write(self, address, value):
        self.mar = address
        self.mdr = value
        self.ram[self.mar] = self.mdr
