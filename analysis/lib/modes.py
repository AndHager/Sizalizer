from enum import Enum

class Mode(Enum):
    ALL = 'all'          # All instructions
    COMPRESSED = '16Bit' # Only 16 Bit instructions
    FULL = '32Bit'       # Only 32 Bit instructions
    

class SearchKey(Enum):
    MNEMONIC = 'mnemonic'
    OPCODE = 'opcode'
    REGISTER = 'register'
    CHAIN = 'chain'
    CHAIN_DISTRIB = 'chain_distribution'
    PAIR = 'pair'
    TRIPLET = 'triplet'
    IMM = 'imm'
