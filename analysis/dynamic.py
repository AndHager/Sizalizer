import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

from lib import instruction_model, parse_utils, evaluator, modes, plotter

plt.rcParams["font.family"] = "cmb10"

debug = False
plot_all = False

def parse_line(source_line):
    """
    Parses a trace code line into an instruction object.

    This function is designed to parse a single trace code line provided as 
    a string in the trace format of ETISS.
    It expects the source line to contain an address, a mnemonic, and an opcode, and params 
    each separated by spaces. Each component is then extracted and used to construct
    an `Instruction` object from the `instruction_model` module.
    Additionally, the function parses up to three parameters that follow the opcode.
    Each parameter is assumed to be separated by spaces and optionally enclosed in 
    brackets, which are stripped if present.
    <address>: <mnemonic> # <opcode> [<param>=<value> | *]

    For Example:
    0x0000000010000c02: addi # 10000010100000011000011000010011 [rd=12 | rs1=3 | imm=2088]
    0x0000000010000c06: csub # 1000111000001001 [rs2=2 | rd=4]
    0x0000000010000c08: cjal # 0010010000000101 [imm=544].

    Parameters:
    - source_line (str): A string representing a single line of trace code.

    Returns:
    - `Instruction`: An Instruction object populated with the parsed data, or
      `None` if the source line does not start with '0x' or fails to parse.

    Note:
    - The function contains an undeclared variable `debug`. If `debug` is `True`, 
      it prints all source lines a message when the source line does not start with '0x' but does 
      not raise a `NameError`.
    - The global `instruction_model` with an `Instruction` class should be available
      in the context where this function is executed.
    """
    if source_line[0:2] == '0x':

        elems = source_line.split(' ')
        elen = len(elems)

        address = elems[0][2:-1]
        mnemonic = elems[1]
        opcode = elems[3]

        instruction = instruction_model.Instruction(address, opcode, mnemonic)

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
        
        if debug:
            print(str(instruction))
        return instruction
    if debug:
        print('No Inst:', source_line)
    return None

def main(args):
    """
    The main entry point for the script that processes and analyzes files.

    This function takes command-line arguments, extracts instructions from each provided file,
    performs the evaluation, generates plots, and prints dynamic code size toghether with the improvement oportunity.

    Parameters:
    args (argparse.Namespace): command-line arguments.
                                It must have at least the following attributes:
                                - path: The base path where the traces are located.
                                - files: An iterable with the names of the traces to be processed.

    """
    path = Path(args.path).absolute()
    tp = 'Dynamic'
    total = []
    for file in args.files:
        if debug:
            print('Base Path: ', path)
            print('File to analyze: ', file)


        instructions = []
        fqpn = '{}/{}'.format(str(path), str(file))
        instructions = parse_utils.parse_file(fqpn, parse_line, debug)
        total += instructions
        if plot_all:
            for mode in modes.Mode:
                stats = evaluator.most_inst(instructions, mode, modes.SearchKey.MNEMONIC, 10)
                plotter.plot_bars(stats, str(file), tp, path, mode, modes.SearchKey.MNEMONIC)

            stats = evaluator.most_inst(instructions, modes.Mode.ALL, modes.SearchKey.OPCODE, 10)
            plotter.plot_bars(stats, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.OPCODE)

            stats = evaluator.most_inst(instructions, modes.Mode.ALL, modes.SearchKey.REGISTER, 10)
            plotter.plot_bars(stats, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.REGISTER)
            
            chains = evaluator.longest_chains(instructions, 10)
            plotter.plot_bars(chains, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.CHAIN)

            addi_dist = evaluator.inst_vals(instructions, 'addi', 10)
            plotter.plot_bars(addi_dist, str(file).replace('.txt', '_ADDI'), tp, path, modes.Mode.FULL, modes.SearchKey.IMM)

            lw_dist = evaluator.inst_vals(total, 'lw', 10)
            plotter.plot_bars(lw_dist, str(file).replace('.txt', '_LW'), tp, path, modes.Mode.FULL, modes.SearchKey.IMM)

        stats = evaluator.most_inst(instructions, modes.Mode.FULL, modes.SearchKey.MNEMONIC, 10000000)
        # x contains count of 32 Bit (4 Byte) instructions
        # x*2 is the count of Bytes saved by a reduction to 16 bit inst
        improvement = evaluator.get_improvement(stats, lambda x: x*2)
        inst_count = len(instructions)
        byte_count = evaluator.get_byte_count(instructions)
        print(file, 'contains', len(instructions), 'with', byte_count, 'bytes')
        print('  Improvement by replacing all 32 Bit inst with 16 Bit inst: ' + str(improvement) + ' Byte  ==', round((1 - ((byte_count - improvement)/byte_count))*100), '%')

        addrs = evaluator.most_addr(instructions, 10000000)
        
        bound = 99
        inst_count_80p = evaluator.get_inst_rate(addrs, inst_count, bound)
        print('  ', bound, '% time spend in ', inst_count_80p, ' instructions, equate to ', (inst_count_80p/inst_count)*100, '%')
        bound = 90
        while (inst_count_80p/inst_count)*100 > 50:
            inst_count_80p = evaluator.get_inst_rate(addrs, inst_count, bound)
            print('  ', bound, '% time spend in ', inst_count_80p, ' instructions, equate to ', (inst_count_80p/inst_count)*100, '%')
            bound -= 10

        if debug:
            pairs = evaluator.most_pairs(instructions, 10, equal=True)
            for pair in pairs:
                print(pair)
            print()

            pairs = evaluator.most_pairs(instructions, 10, equal=False)
            for pair in pairs:
                print(pair)
            print()

        if plot_all:
            pairs = evaluator.most_pairs(instructions, 10, equal=False, connected=True)
            plotter.plot_bars(pairs, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.PAIR)

    for mode in modes.Mode:
        stats = evaluator.most_inst(total, mode, modes.SearchKey.MNEMONIC, 10)
        plotter.plot_bars(stats, '_Total', tp, path, mode, modes.SearchKey.MNEMONIC)

    stats = evaluator.most_inst(total, modes.Mode.ALL, modes.SearchKey.OPCODE, 10)
    plotter.plot_bars(stats, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.OPCODE)

    stats = evaluator.most_inst(total, modes.Mode.ALL, modes.SearchKey.REGISTER, 10)
    plotter.plot_bars(stats, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.REGISTER)
    
    chains = evaluator.longest_chains(total, 10)
    plotter.plot_bars(chains, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.CHAIN)

    addi_dist = evaluator.inst_vals(total, 'addi', 10)
    plotter.plot_bars(addi_dist, '_Total_ADDI', tp, path, modes.Mode.FULL, modes.SearchKey.IMM)

    lw_dist = evaluator.inst_vals(total, 'lw', 10)
    plotter.plot_bars(lw_dist, '_Total_LW', tp, path, modes.Mode.FULL, modes.SearchKey.IMM)

    stats = evaluator.most_inst(total, modes.Mode.FULL, modes.SearchKey.MNEMONIC, 10000000000)
    # x contains count of 32 Bit (4 Byte) instructions
    # x*2 is the count of Bytes saved by a reduction to 16 bit inst
    improvement = evaluator.get_improvement(stats, lambda x: x*2)
    total_byte_count = evaluator.get_byte_count(total)
    total_inst_count = len(total)
    print('Total contains', len(total), 'with', total_byte_count, 'bytes')
    print('  Improvement by replacing all 32 Bit inst with 16 Bit inst: ' + str(improvement) + ' Byte  ==', round((1 - ((total_byte_count - improvement)/total_byte_count))*100), '%')

    addrs = evaluator.most_addr(total, 10000000)
    bound = 99
    inst_count_80p = evaluator.get_inst_rate(addrs, total_inst_count, bound)
    print('  Total ', bound, ' % time spend in ', inst_count_80p, ' instructions, equate to ', (inst_count_80p/total_inst_count)*100, '%')

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
    plotter.plot_bars(pairs, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.PAIR)

    pairs = evaluator.most_pairs(instructions, 10, equal=False, connected=True)
    # x contains count of 16 or 32 Bit instructions pairs
    # x*6 is the count of Bytes saved by a reduction to 16 bit inst
    improvement = evaluator.get_improvement(pairs, lambda x: x*6)
    # print('Max. improvement by replacing all 16 or 32 Bit instructions pairs with 16 Bit inst: ' + str(improvement) + ' Byte')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count the instructions in an trace file.')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to analyze')
    parser.add_argument('--path', type=str, help='base path for the files')

    main(parser.parse_args())

