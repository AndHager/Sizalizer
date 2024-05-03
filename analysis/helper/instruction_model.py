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

    def get_imm(self):
        reg = self.regs[-1]
        vals = reg.split('=')
        vlen = len(vals)
        if vlen != 2:
            print('ERROR false vals len:', reg)
            print(str(self))
        assert(vlen == 2)
        if 'imm' == vals[0]:
            return int(vals[1])
        else:
            print('ERROR not an imm for inst:', str(self))

    def get_dest(self):
        if self.mnemonic in no_dest or len(self.regs) < 1:
            return 'no_dest'
        return self.regs[0]
