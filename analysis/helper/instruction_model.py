no_dest = [
    'sd', 'sw', 'sh', 'sb',
    'fsd', 'fsd'
    'c.sd', 'c.sw', 
    'c.fsw', 'c.fsd'
]

class Instruction:
    address = ''
    opcode = ''
    mnemonic = ''
    regs = []

    def __init__(self, address, opcode, mnemonic):
        if len(opcode) % 2 != 0:
            print(address, '', opcode, ' ', mnemonic)
            assert False
        self.address = address
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.regs = []

    def __str__(self):
        result = str(self.address) + '\t' + str(self.opcode) + (12 - len(str(self.opcode))) * ' ' + str(self.mnemonic) + ' ' 
        param_size = len(self.regs)
        for i in range(param_size):
            result += self.regs[i]
            if i != param_size - 1:
                result += ', '
        return result
    
    def get_size(self):
        assert len(self.opcode) % 2 == 0
        return int(len(self.opcode)/2)
    
    def get_params(self):
        if self.mnemonic in no_dest:
            return self.regs
        return self.regs[1:]

    def get_dest(self):
        if self.mnemonic in no_dest or len(self.regs) < 1:
            return 'no_dest'
        return self.regs[0]
