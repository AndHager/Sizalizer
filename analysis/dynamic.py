import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
import tikzplotlib

plt.rcParams["font.family"] = "cmb10"

debug = False

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
            raise
        self.address = address
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.regs = []

    def __str__(self):
        result = str(self.address) + '\t' + str(self.opcode) + (34 - len(str(self.opcode))) * ' ' + str(self.mnemonic) + ' ' 
        param_size = len(self.regs)
        for i in range(param_size):
            result += self.regs[i]
            if i != param_size - 1:
                result += ', '
        return result
    
    def get_size(self):
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


class Mode(Enum):
    ALL = 'all'          # All instructions
    COMPRESSED = '16Bit' # Only 16 Bit instructions
    FULL = '32Bit'       # Only 32 Bit instructions


class SearchKey(Enum):
    MNEMONIC = 'mnemonic'
    OPCODE = 'opcode'
    REGISTER = 'register'
    CHAIN = 'chain'
    PAIR = 'pair'
    IMM = 'imm'


def parse_line(source_line):
    # use WordEnd to avoid parsing leading a-f of non-hex numbers as a hex
    if source_line[0:2] == '0x':

        elems = source_line.split(' ')
        elen = len(elems)

        address = elems[0][2:-1]
        mnemonic = elems[1]
        opcode = elems[3]

        instruction = Instruction(address, opcode, mnemonic)

        if elen > 4:
            first_param = elems[4][1:]
            instruction.regs.append(first_param)

        
        if elen > 6:
            second_param = elems[6]
            if elen == 7:
                second_param = second_param[:-1]
            instruction.regs.append(second_param)

        if elen > 8:
            third_param = elems[8][:-1]
            instruction.regs.append(third_param)
        
        # print(str(instruction))
        return instruction
    if debug:
        print('No Inst:', source_line)
    return None


def parse_file(fqfn):
    instructions = []
    with open(fqfn, 'r', errors='replace') as file:
            lines = file.read().split('\n')
            if debug:
                print('Line count: ', len(lines))
            
            instructions = [
                inst
                for source_line in lines
                for inst in [parse_line(source_line)]
                if inst != None
            ]
    if debug:     
        for inst in instructions[1:20]:
            print(str(inst))
    return instructions    


def most_addr(instructions, threshold=10000): 
    result = {}
    for inst in instructions:
        key = inst.address
        if key in result:
            result[key] += 1
        else:
            result[key] = 1
    return sort_dict(result, threshold)


def sort_dict(result, threshold):
    vals = [
        val 
        for val in result.items()
    ]
    return sorted(vals, key=lambda x:x[1], reverse=True)[:threshold]


def most_inst(instructions, mode=Mode.ALL, search_key=SearchKey.MNEMONIC, threshold=10): 
    result = {}
    for inst in instructions:
        is_comp = inst.get_size() == 2 and mode == Mode.COMPRESSED
        is_full = inst.get_size() == 4 and mode == Mode.FULL
        use_all = mode == Mode.ALL
        if use_all or is_comp or is_full:
            keys = [inst.mnemonic]
            if search_key == SearchKey.OPCODE:
                keys = [inst.opcode]
            if search_key == SearchKey.REGISTER:
                keys = inst.regs
            for key in keys:
                if key in result:
                    result[key] += 1
                else:
                    result[key] = 1
    return sort_dict(result, threshold)


def longest_chains(instructions, threshold=10):
    result = {}
    last_key = instructions[0].mnemonic
    chain_len = 1
    for inst in instructions[1:]:
        key = inst.mnemonic
        if last_key == key:
            chain_len += 1
        else:
            if chain_len >= threshold:
                if last_key in result:
                    if result[last_key] < chain_len:
                        result[last_key] = chain_len
                else:
                    result[last_key] = chain_len
            chain_len = 1
        last_key = key
    return sort_dict(result, threshold)
    

def most_pairs(instructions, threshold=5, equal=True, connected=False):
    result = {}
    old_inst = instructions[0]
    for inst in instructions[1:]:
        old_mn = old_inst.mnemonic
        new_mn = inst.mnemonic
        is_equal = old_mn == new_mn or not equal
        is_connected = old_inst.get_dest() in inst.get_params() or not connected
        if is_equal and is_connected:
            key = old_mn
            if not equal:
                key = old_mn + '-' + new_mn
            if key in result:
                result[key] += 1
            else:
                result[key] = 1
        old_inst = inst
    return sort_dict(result, threshold)


def inst_vals(instructions, menomic, treshold=5):
    result = {}
    for inst in instructions:
        if inst.mnemonic == menomic:
            key = inst.get_imm()
            if key != None:
                if key in result:
                    result[key] += 1
                else:
                    result[key] = 1
            else:
                print('Error: inst does not contain imm:', str(inst))
    return sort_dict(result, treshold)


def get_improvement(stats, imp_map):
    imp = 0
    for stat in stats:
        imp += imp_map(stat[1])
    return imp


def get_inst_rate(addrs, inst_count, bound):
    sum = 0
    count_inst = 0
    while (sum/inst_count)*100 < bound:
        sum += addrs[count_inst][1]
        count_inst += 1
    return count_inst


def plot_bars(stats, filename, mode=Mode.ALL, search_key=SearchKey.MNEMONIC):
    # set width of bars
    name = filename.split('.')[0]

    bar_width = 0.20

    plt.figure(figsize=(8, 3))
    plt.grid(visible = True, axis = 'y', color = 'gray', linestyle = '--', linewidth = 0.5, alpha = 0.7)
    plt.grid(visible = True, axis = 'y', which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.rc('axes', unicode_minus=False)

    mnemonics = [
        pair[0]
        for pair in stats
    ]
    counts = [
        pair[1]
        for pair in stats
    ]

    bars_y = counts
    bars_x = np.arange(len(bars_y))
    plt.bar(bars_x, bars_y, width=bar_width, edgecolor='white', label=mnemonics, log=False)

    # plt.title(name)
    ylabel = search_key.value + ' Count ' +  mode.value + ' Inst.'
    # plt.ylabel(ylabel)
    plt.xticks([r for r in range(len(mnemonics))], mnemonics)
    for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
        y_position = label.get_position()[1]  # Get current y position
        if index % 2 != 0:  # For odd indices
            label.set_y(y_position - 0.06)  # Move down by a fraction; adjust as needed

    plt.tight_layout()
    plt.legend().remove()

    fig_name = './out/' + name + '_Dynamic_' + search_key.value + '_' + mode.value
    plt.savefig(fig_name + '.pdf')
    tikzplotlib.save(fig_name + '.tex')
    plt.close()


def get_byte_count(instructions):
    result = 0
    for inst in instructions:
        result += inst.get_size()
    return result


def main(args):
    path = Path(args.path).absolute()
    total = []
    for file in args.files:
        if debug:
            print('Base Path: ', path)
            print('File to analyze: ', file)


        instructions = []
        fqpn = '{}/{}'.format(str(path), str(file))
        instructions = parse_file(fqpn)
        total += instructions
        for mode in Mode:
            stats = most_inst(instructions, mode, SearchKey.MNEMONIC, 10)
            plot_bars(stats, str(file), mode)

        stats = most_inst(instructions, Mode.ALL, SearchKey.OPCODE, 10)
        plot_bars(stats, str(file), Mode.ALL, SearchKey.OPCODE)

        stats = most_inst(instructions, Mode.ALL, SearchKey.REGISTER, 10)
        plot_bars(stats, str(file), Mode.ALL, SearchKey.REGISTER)
        
        chains = longest_chains(instructions, 10)
        plot_bars(chains, str(file), Mode.ALL, SearchKey.CHAIN)

        addi_dist = inst_vals(instructions, 'addi', 10)
        plot_bars(addi_dist, str(file).replace('.txt', '_ADDI'), Mode.FULL, SearchKey.IMM)

        lw_dist = inst_vals(total, 'lw', 10)
        plot_bars(lw_dist, str(file).replace('.txt', '_LW'), Mode.FULL, SearchKey.IMM)

        stats = most_inst(instructions, Mode.FULL, SearchKey.MNEMONIC, 10000000)
        # x contains count of 32 Bit (4 Byte) instructions
        # x*2 is the count of Bytes saved by a reduction to 16 bit inst
        improvement = get_improvement(stats, lambda x: x*2)
        inst_count = len(instructions)
        byte_count = get_byte_count(instructions)
        print(file, 'contains', len(instructions), 'with', byte_count, 'bytes')
        print('  Improvement by replacing all 32 Bit inst with 16 Bit inst: ' + str(improvement) + ' Byte  ==', round((1 - ((byte_count - improvement)/byte_count))*100), '%')

        addrs = most_addr(instructions, 10000000)
        
        bound = 99
        inst_count_80p = get_inst_rate(addrs, inst_count, bound)
        print('  ', bound, '% time spend in ', inst_count_80p, ' instructions, equate to ', (inst_count_80p/inst_count)*100, '%')
        bound = 90
        while (inst_count_80p/inst_count)*100 > 50:
            inst_count_80p = get_inst_rate(addrs, inst_count, bound)
            print('  ', bound, '% time spend in ', inst_count_80p, ' instructions, equate to ', (inst_count_80p/inst_count)*100, '%')
            bound -= 10

        if debug:
            pairs = most_pairs(instructions, 10, equal=True)
            for pair in pairs:
                print(pair)
            print()

            pairs = most_pairs(instructions, 10, equal=False)
            for pair in pairs:
                print(pair)
            print()

        pairs = most_pairs(instructions, 10, equal=False, connected=True)
        plot_bars(pairs, str(file), Mode.ALL, SearchKey.PAIR)

    for mode in Mode:
        stats = most_inst(total, mode, SearchKey.MNEMONIC, 10)
        plot_bars(stats, '_Total', mode)

    stats = most_inst(total, Mode.ALL, SearchKey.OPCODE, 10)
    plot_bars(stats, '_Total', Mode.ALL, SearchKey.OPCODE)

    stats = most_inst(total, Mode.ALL, SearchKey.REGISTER, 10)
    plot_bars(stats, '_Total', Mode.ALL, SearchKey.REGISTER)
    
    chains = longest_chains(total, 10)
    plot_bars(chains, '_Total', Mode.ALL, SearchKey.CHAIN)

    addi_dist = inst_vals(total, 'addi', 10)
    plot_bars(addi_dist, '_Total_ADDI', Mode.FULL, SearchKey.IMM)

    lw_dist = inst_vals(total, 'lw', 10)
    plot_bars(lw_dist, '_Total_LW', Mode.FULL, SearchKey.IMM)

    stats = most_inst(total, Mode.FULL, SearchKey.MNEMONIC, 10000000000)
    # x contains count of 32 Bit (4 Byte) instructions
    # x*2 is the count of Bytes saved by a reduction to 16 bit inst
    improvement = get_improvement(stats, lambda x: x*2)
    total_byte_count = get_byte_count(total)
    total_inst_count = len(total)
    print('Total contains', len(total), 'with', total_byte_count, 'bytes')
    print('  Improvement by replacing all 32 Bit inst with 16 Bit inst: ' + str(improvement) + ' Byte  ==', round((1 - ((total_byte_count - improvement)/total_byte_count))*100), '%')

    addrs = most_addr(total, 10000000)
    bound = 99
    inst_count_80p = get_inst_rate(addrs, total_inst_count, bound)
    print('  Total ', bound, ' % time spend in ', inst_count_80p, ' instructions, equate to ', (inst_count_80p/total_inst_count)*100, '%')

    if debug:
        pairs = most_pairs(total, 10, equal=True)
        for pair in pairs:
            print(pair)
        print()

        pairs = most_pairs(total, 10, equal=False)
        for pair in pairs:
            print(pair)
        print()

    pairs = most_pairs(total, 10, equal=False, connected=True)
    plot_bars(pairs, '_Total', Mode.ALL, SearchKey.PAIR)

    pairs = most_pairs(instructions, 10, equal=False, connected=True)
    # x contains count of 16 or 32 Bit instructions pairs
    # x*6 is the count of Bytes saved by a reduction to 16 bit inst
    improvement = get_improvement(pairs, lambda x: x*6)
    # print('Max. improvement by replacing all 16 or 32 Bit instructions pairs with 16 Bit inst: ' + str(improvement) + ' Byte')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count the instructions in an trace file.')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to analyze')
    parser.add_argument('--path', type=str, help='base path for the files')

    main(parser.parse_args())

