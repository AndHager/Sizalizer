from enum import Enum
import math
from bitstring import Array
from typing import Tuple


class SavedBy(Enum):
    NotSaved = 'N'
    CALLER = 'R'
    CALLEE = 'E'


class Reg:
    names: list[str] = []
    saved_by: SavedBy = None

    def __init__(self, names: list[str], saved_by: SavedBy):
        self.names = names
        self.saved_by = saved_by


class Regs:
    all: list[Reg] = []
    reduced_regs: list[Reg] = []

    # encoded in 5 bits
    def __init__(self):
        self.all = [
            Reg(['x0', 'x0'], SavedBy.NotSaved), # hardwired zero
            Reg(['ra', 'x1'], SavedBy.CALLER), # return address
            Reg(['sp', 'x2'], SavedBy.CALLEE), # stack pointer
            Reg(['gp', 'x3'], SavedBy.NotSaved), # global pointer
            Reg(['tp', 'x4'], SavedBy.NotSaved), # thread pointer
            Reg(['t0', 'x5'], SavedBy.CALLER), # tmp  0
            Reg(['t1', 'x6'], SavedBy.CALLER), # tmp  1
            Reg(['t2', 'x7'], SavedBy.CALLER), # tmp  2
            Reg(['s0', 'fp', 'x8'], SavedBy.CALLEE), # frame pointer / saved  0
            Reg(['s1', 'x9'], SavedBy.CALLEE), # saved  1
            Reg(['a0', 'x10'], SavedBy.CALLER), # ret val 0 / arg 0
            Reg(['a1', 'x11'], SavedBy.CALLER), # ret val 1 / arg 1
            Reg(['a2', 'x12'], SavedBy.CALLER), # arg 2
            Reg(['a3', 'x13'], SavedBy.CALLER), # arg 3
            Reg(['a4', 'x14'], SavedBy.CALLER), # arg 4
            Reg(['a5', 'x15'], SavedBy.CALLER), # arg 5
            Reg(['a6', 'x16'], SavedBy.CALLER), # arg 6
            Reg(['a7', 'x17'], SavedBy.CALLER), # arg 7
            Reg(['s2', 'x18'], SavedBy.CALLEE), # saved  2
            Reg(['s3', 'x19'], SavedBy.CALLEE), # saved  3
            Reg(['s4', 'x20'], SavedBy.CALLEE), # saved  4
            Reg(['s5', 'x21'], SavedBy.CALLEE), # saved  5
            Reg(['s6', 'x22'], SavedBy.CALLEE), # saved  6
            Reg(['s7', 'x23'], SavedBy.CALLEE), # saved  7
            Reg(['s8', 'x24'], SavedBy.CALLEE), # saved  8
            Reg(['s9', 'x25'], SavedBy.CALLEE), # saved  9
            Reg(['s10', 'x26'], SavedBy.CALLEE), # saved  10
            Reg(['s11', 'x27'], SavedBy.CALLEE), # saved  11
            Reg(['t3', 'x28'], SavedBy.CALLER), # tmp 3
            Reg(['t4', 'x29'], SavedBy.CALLER), # tmp 4
            Reg(['t5', 'x30'], SavedBy.CALLER), # tmp 5
            Reg(['t6', 'x31'], SavedBy.CALLER) # tmp 6
        ]

        # encoded in 3 bits
        self.reduced_regs = self.all[8:16]
        assert len(self.all) == 32
        assert len(self.reduced_regs) == 8

    def get_all(self) -> list[Reg]:
        return self.all
    
    def get_width(self, compressed:bool=False) -> int:
        regs = self.all
        if compressed:
            regs = self.reduced_regs
        width = math.log(regs, 2)
        assert int(width) == width
        return int(width)
    
    def get_reduced(self) -> list[Reg]:
        return self.reduced_regs
    
    def get_index_reg(self, name, compressed_reg:bool=False) -> Tuple[int, Reg|None]:
        regs = self.all
        if compressed_reg:
            regs = self.reduced_regs
        for i in range(len(regs)):
            reg = regs[i]
            if name in reg.names:
                return (i, reg)
        return (-1, None)

    def get_reg(self, name:str, compressed_reg:bool=False) -> Reg|None:
        return self.get_index_reg(name, compressed_reg)[0]
    
    def get_coding(self, name, compressed_reg=False) -> Array:
        index, _ = self.get_index_reg(name)
        assert index >= 0
        format = f'uint{self.get_width}'
        return Array(format, index)


class BitWitdth(Enum):
    COMPRESSED = 16
    FULL = 32
    EXTENDED = 48


class Format:
    length_selecton_bits: map[BitWitdth, int] = {
        BitWitdth.COMPRESSED: 0,
        BitWitdth.BitWitdth: 2,
        BitWitdth.BitWitdth: 6
    }
    length_selecton_exclude: map[BitWitdth, int] = {
        BitWitdth.COMPRESSED: 1,
        BitWitdth.BitWitdth: 1,
        BitWitdth.BitWitdth: 0
    }
    regs: Regs = Regs()

    width: BitWitdth = BitWitdth.FULL
    op_len: int = 0

    
    def __init__(self, width: BitWitdth, op_len: int):
        assert width.value - self.length_selecton_bits[width] > op_len
        self.width = width
        self.op_len = op_len

    def get_available_bits(self) -> int:
        return self.width.value - self.op_len - self.length_selecton_bits[self.width]
    
    def get_available_insts(self) -> int:
        return 2**self.op_len - self.length_selecton_exclude[self.width]
    
    def get_max_regs_codeable(self, fun_bits: int=0, imm_bits: int=0, compressed_reg: bool=False) -> int:
        bits_for_sel = self.get_available_bits() - fun_bits - imm_bits
        reg_bits = self.regs.get_width(compressed_reg)
        return int(bits_for_sel/reg_bits)

    def get_remainig_bits(self, fun_bits: int=0, imm_bits: int=0, reg_count: int=0, compressed_reg: int=False) -> int:
        bits_for_sel = self.get_available_bits() - fun_bits - imm_bits
        reg_bits = self.regs.get_width(compressed_reg) * reg_count
        remaining_bits = bits_for_sel - reg_bits
        assert int(remaining_bits) == remaining_bits and remaining_bits >= 0
        return int(remaining_bits)



