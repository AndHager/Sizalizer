no_dest = [
    'sd', 'sw', 'sh', 'sb',
    'fsd', 'fsd'
    'c.sd', 'c.sw', 'c.swsp'
    'c.fsw', 'c.fsd'
]



class Instruction:
    address = ''
    opcode = ''
    mnemonic = ''
    regs = []

    def __init__(self, address, opcode, mnemonic):
        if len(opcode) % 2 != 0:
            print('Error: false Opcode detected in inst: ', address, '', opcode, ' ', mnemonic)
            assert False
        self.address = address
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.regs = []

    def __str__(self):
        shift = 32
        if len(self.opcode) < 16:
            shift = 12
        result = str(self.address) + '\t' + str(self.opcode) + (shift - len(str(self.opcode))) * ' ' + str(self.mnemonic) + ' ' 
        param_size = len(self.regs)
        for i in range(param_size):
            result += self.regs[i]
            if i != param_size - 1:
                result += ', '
        return result
    
    def __is_integer_num(self, n):
        if isinstance(n, int):
            return True
        if isinstance(n, float):
            return n.is_integer()
        return False
    
    def get_size(self):
        assert len(self.opcode) % 2 == 0
        if len(self.opcode) < 16:
            return int(len(self.opcode)/2)
        assert len(self.opcode) % 16 == 0
        return int(len(self.opcode)/8)
    
    def get_params(self):
        if self.mnemonic in no_dest:
            return self.regs
        return self.regs[1:]
    
    def get_dest(self):
        if self.mnemonic in no_dest or len(self.regs) < 1:
            return 'no_dest'
        return self.regs[0]

    def get_imm(self):
        reg = str(self.regs[-1]).strip()
        vals = reg.split('=')
        vlen = len(vals)
        if vlen != 2:
            if reg[:2] == '0x' or reg[:3] == '-0x':
                return int(reg, 16)
            if self.__is_integer_num(reg):
                return int(reg)
        if 'imm' == vals[0]:
            return int(vals[1])
        else:
            if len(self.regs) == 2:
                return 0
            print('ERROR not an imm', reg, ' for inst:', str(self))
            return None
    
    def get_base_mnemonic(self):
        return str(self.mnemonic) \
            .replace('c.', '') \
            .replace('sp', '')
