import argparse
from pathlib import Path
import string

from helper import instruction_model, parse_utils, evaluator, modes, plotter

debug = False
plot_all = False

def parse_line(source_line):
    if source_line[0:1] == ' ' or source_line[0:1] == '1':
        source_line = source_line.strip()
        sl = source_line.replace('\t', ' ')
        while sl != source_line:
            source_line = sl
            sl = sl.replace('  ', ' ')
        elems = source_line.replace('  ', ' ').split(' ')
        elen = len(elems)
        if elen > 1:
            if debug:
                print(elems)

            address = elems[0]
            addr_len = len(address)
            assert len(address) > 0
            if address[addr_len-1] == ':':
                address = address[:(addr_len-1)]

                i = 1
                opcode = ''
                while len(elems[i]) == 2 and all(c in string.hexdigits for c in elems[i]) and i < 5:
                    opcode += elems[i]
                    i += 1
                
                mnemonic = elems[i]
                i += 1

                instruction = instruction_model.Instruction(address, opcode, mnemonic)

                if elen > i:
                    first_param = elems[i]
                    fp_len = len(first_param)
                    if fp_len == 0:
                        print(str(instruction))
                        print(first_param)
                    assert fp_len > 0
                    i += 1
                    if first_param[fp_len-1] == ',':
                        first_param = first_param[:(fp_len-1)]
                    instruction.regs.append(first_param)

                if elen > i:
                    second_param = elems[i]
                    i += 1
                    if second_param[-1] == ',':
                        second_param = second_param[:(len(second_param)-1)]
                    instruction.regs.append(second_param)

                if elen > i:
                    third_param = elems[i]
                    instruction.regs.append(third_param)
                
                if debug:
                    print(str(instruction))

                return instruction
            else:
                if debug:
                    print('ERROR: false assumed inst: ', source_line)
    else:
        if debug:
            print('INFO: not an inst: ', source_line)
    return None


def main(args):
    path = str(Path(args.path).absolute())
    tp = 'Static'
    total = []
    for file in args.files:
        if debug:
            print('Base Path: ', path)
            print('File to analyze: ', file)


        instructions = []
        fqpn = '{}/{}'.format(str(path), str(file))
        instructions = parse_utils.parse_file(fqpn, parse_line, debug)
        if len(instructions) > 0:
            total += instructions
            total_byte_count = evaluator.get_byte_count(instructions)
            inst_count = len(instructions)
            print(file, 'contains:', inst_count, 'insts, with', total_byte_count, 'bytes')
            
            if plot_all:
                for mode in modes.Mode:
                    stats = evaluator.most_inst(instructions, mode, modes.SearchKey.MNEMONIC, 10)
                    plotter.plot_bars(stats, str(file), path, tp, mode)
                stats = evaluator.most_inst(instructions, modes.Mode.ALL, modes.SearchKey.OPCODE, 10)
                plotter.plot_bars(stats, str(file), path, tp, modes.Mode.ALL, modes.SearchKey.OPCODE)

                stats = evaluator.most_inst(instructions, modes.Mode.ALL, modes.SearchKey.REGISTER, 10)
                plotter.plot_bars(stats, str(file), path, tp, modes.Mode.ALL, modes.SearchKey.REGISTER)
            
                chains = evaluator.longest_chains(instructions, 10)
                plotter.plot_bars(chains, str(file), path, tp, modes.Mode.ALL, modes.SearchKey.CHAIN)


            stats = evaluator.most_inst(instructions, modes.Mode.FULL, modes.SearchKey.MNEMONIC, 10000000)
            # x contains count of 32 Bit (4 Byte) instructions
            # x*2 is the count of Bytes saved by a reduction to 16 bit inst
            improvement = evaluator.get_improvement(stats, lambda x: x*2)
            print('  Improvement by replacing 32 with 16 Bit inst: ' + str(improvement) + ' Byte ==', round((1 - ((total_byte_count - improvement)/total_byte_count))*100), '%')

            if debug:
                pairs = evaluator.most_pairs(instructions, 10, equal=True)
                for pair in pairs:
                    print(pair)
                print()

                pairs = evaluator.most_pairs(instructions, 10, equal=False)
                for pair in pairs:
                    print(pair)
                print()

            pairs = evaluator.most_pairs(instructions, 10, equal=False, connected=True)
            if plot_all:
                plotter.plot_bars(pairs, str(file), path, tp, modes.Mode.ALL, modes.SearchKey.PAIR)



            pairs = evaluator.most_pairs(instructions, 10, equal=False, connected=True)
            # x contains count of 16 or 32 Bit instructions pairs
            # x*6 is the count of Bytes saved by a reduction to 16 bit inst
            improvement = evaluator.get_improvement(pairs, lambda x: x*6)
            # print('Max. improvement by replacing all 16 or 32 Bit instructions pairs with 16 Bit inst: ' + str(improvement) + ' Byte')
        else:
            print('ERROR: No instructions in', fqpn)
    if len(total) > 0:
        total_inst_count = len(total)
        total_byte_count = evaluator.get_byte_count(total)
        print('Total:', total_inst_count, ' insts, with', total_byte_count, 'bytes')
        for mode in modes.Mode:
            stats = evaluator.most_inst(total, mode, modes.SearchKey.MNEMONIC, 10)
            plotter.plot_bars(stats, '_Total', path, tp, mode)

        stats = evaluator.most_inst(total, modes.Mode.ALL, modes.SearchKey.OPCODE, 10)
        plotter.plot_bars(stats, '_Total', path, tp, modes.Mode.ALL, modes.SearchKey.OPCODE)

        stats = evaluator.most_inst(total, modes.Mode.ALL, modes.SearchKey.REGISTER, 10)
        plotter.plot_bars(stats, '_Total', path, tp, modes.Mode.ALL, modes.SearchKey.REGISTER)
        
        chains = evaluator.longest_chains(total, 10)
        plotter.plot_bars(chains, '_Total', path, tp, modes.Mode.ALL, modes.SearchKey.CHAIN)


        stats = evaluator.most_inst(total, modes.Mode.FULL, modes.SearchKey.MNEMONIC, 100000)
        # x contains count of 32 Bit (4 Byte) instructions
        # x*2 is the count of Bytes saved by a reduction to 16 bit inst
        improvement = evaluator.get_improvement(stats, lambda x: x*2)
        print('  Total Improvement by replacing 32 with 16 Bit inst: ' + str(improvement) + ' Byte ==', round((1 - ((total_byte_count - improvement)/total_byte_count))*100), '%')

        if debug:
            pairs = evaluator.most_pairs(total, 10, equal=True)
            for pair in pairs:
                print(pair)
            print()

            pairs = evaluator.most_pairs(total, 10, equal=False)
            for pair in pairs:
                print(pair)
            print()

        pairs = evaluator.most_pairs(total, 10, equal=False, connected=True)
        plotter.plot_bars(pairs, '_Total', path, tp, modes.Mode.ALL, modes.SearchKey.PAIR)

        pairs = evaluator.most_pairs(instructions, 1, equal=False, connected=True)
        # x contains count of 16 or 32 Bit instructions pairs
        # x*6 is the count of Bytes saved by a reduction to 16 bit inst
        improvement = evaluator.get_improvement(pairs, lambda x: x*6)
    else:
        print('ERROR: In total no instructions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count the instructions in an assembly file.')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to analyze')
    parser.add_argument('--path', type=str, help='base path for the files')

    main(parser.parse_args())

