import argparse
from pathlib import Path
import string

from lib import instruction_model, parse_utils, evaluator, modes, plotter

# Debug logs (very verbose)
debug = False
# Define if each asm file should be evaluated speratly or in total
plot_all = False

def parse_line(source_line):
    '''
    Parses a line of assembly code into an instruction object.

    This function is designed to parse a single line of assembly code provided as 
    a string in the intel format of llvm-objdump.
    It expects the source line to contain an address, a mnemonic, and an opcode, and params 
    each separated by spaces. Each component is then extracted and used to construct
    an `Instruction` object from the `instruction_model` module.
    Additionally, the function parses up to three parameters.
    <address> <opcode> <mnemonic> <params>, ...

    For Example:
    00000094 <.LBB0_11>:
          94: 08 40        	c.lw	a0, 0x0(s0)
          96: 13 65 05 08  	ori	    a0, a0, 0x80
          9a: 08 c0        	c.sw	a0, 0x0(s0)

    Parameters:
    - source_line (str): A string representing a single line of assembly code.

    Returns:
    - `Instruction`: An Instruction object populated with the parsed data, or
      `None` if the source line does not start with '0x' or fails to parse.

    Note:
    - The function contains an undeclared variable `debug`. If `debug` is `True`, 
      it prints all source lines a message when the source line does not start with '0x' but does 
      not raise a `NameError`.
    - The global `instruction_model` with an `Instruction` class should be available
      in the context where this function is executed.
    '''
    if source_line[0:1] == ' ' or source_line[0:1] in string.hexdigits:
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
                    if second_param[-1] == ')':
                        base_offset = second_param.split('(')
                        assert len(base_offset) == 2
                        base = base_offset[1]
                        second_param = base[:(len(base)-1)]
                        third_param = base_offset[0]
                        instruction.regs.append(second_param)
                        instruction.regs.append(third_param)
                    else:
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
    '''
    The main entry point for the script that processes and analyzes files.

    This function takes command-line arguments, extracts instructions from each provided file,
    performs the evaluation, generates plots, and prints static code size toghether with the improvement oportunity.

    Parameters:
    args (argparse.Namespace): command-line arguments.
                                It must have at least the following attributes:
                                - path: The base path where the asm files are located.
                                - files: An iterable with the names of the asm to be processed.

    '''
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
                    plotter.plot_bars(stats, str(file), tp, path, mode)
                stats = evaluator.most_inst(instructions, modes.Mode.ALL, modes.SearchKey.OPCODE, 10)
                plotter.plot_bars(stats, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.OPCODE)

                stats = evaluator.most_inst(instructions, modes.Mode.ALL, modes.SearchKey.REGISTER, 10)
                plotter.plot_bars(stats, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.REGISTER)
            
                chains = evaluator.longest_chains(instructions, 10)
                plotter.plot_bars(chains, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.CHAIN)


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
                plotter.plot_bars(pairs, str(file), tp, path, modes.Mode.ALL, modes.SearchKey.PAIR)



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
            plotter.plot_bars(stats, '_Total', tp, path, mode, modes.SearchKey.MNEMONIC)

        stats = evaluator.most_inst(total, modes.Mode.ALL, modes.SearchKey.OPCODE, 10)
        plotter.plot_bars(stats, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.OPCODE)

        stats = evaluator.most_inst(total, modes.Mode.ALL, modes.SearchKey.REGISTER, 10)
        plotter.plot_bars(stats, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.REGISTER)
        
        chains = evaluator.longest_chains(total, 10)
        plotter.plot_bars(chains, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.CHAIN)

        chains = evaluator.chain_distrib(total, 10)
        plotter.plot_bars(chains, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.CHAIN_DISTRIB)

        triplets = evaluator.most_triplets(total, 10, equal=False, connected=True)
        plotter.plot_bars(triplets, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.TRIPLET)

        triplets = evaluator.most_triplets(total, 10)
        plotter.plot_bars(triplets, '_Total_Free', tp, path, modes.Mode.ALL, modes.SearchKey.TRIPLET)

        lw16_imp = evaluator.get_lswm_improvement(total, base_isnt='lw', new_byte_count=2, base_regs=['sp', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4'], dest_regs=['ra', 'sp', 's0', 's1', 'a0', 'a1'])
        sw16_imp = evaluator.get_lswm_improvement(total, base_isnt='sw', new_byte_count=2, base_regs=['sp', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4'], dest_regs=['ra', 'sp', 's0', 's1', 'a0', 'a1'])
        
        lw32_imp = evaluator.get_lswm_improvement(total, base_isnt='lw', new_byte_count=4, base_regs='all', dest_regs={'ra', 'sp', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 's2', 's3', 's4', 's5', 's6', 's7'})
        sw32_imp = evaluator.get_lswm_improvement(total, base_isnt='sw', new_byte_count=4, base_regs='all', dest_regs={'ra', 'sp', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 's2', 's3', 's4', 's5', 's6', 's7'})
        
        lw48_imp = evaluator.get_lswm_improvement(total, base_isnt='lw', new_byte_count=6, base_regs='all', dest_regs='all')
        sw48_imp = evaluator.get_lswm_improvement(total, base_isnt='sw', new_byte_count=6, base_regs='all', dest_regs='all')

        eli_imp = evaluator.get_en_improvement(total, ['lui', 'addi'])
        e2addi_imp = evaluator.get_en_improvement(total, ['addi', 'addi'])
        e2add_imp = evaluator.get_en_improvement(total, ['add', 'add'])
        
        e3add_imp = evaluator.get_en_improvement(total, ['srli', 'slli', 'or'])

        imp = [
            ('e.li', eli_imp),
            ('e.2addi', e2addi_imp),
            ('e.2add', e2add_imp),
            ('e.slro', e3add_imp),
            ('c.lwm', lw16_imp),
            ('c.swm', sw16_imp),
            ('lwm', lw32_imp),
            ('swm', sw32_imp),
            ('e.lwm', lw48_imp),
            ('e.swm', sw48_imp),
        ]
    
        plotter.plot_bars(imp, '_Total_LSWM_IMP', tp, path, modes.Mode.ALL, modes.SearchKey.MNEMONIC)

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
        plotter.plot_bars(pairs, '_Total', tp, path, modes.Mode.ALL, modes.SearchKey.PAIR)

        pairs = evaluator.most_pairs(total, 10)
        plotter.plot_bars(pairs, '_Total_Free', tp, path, modes.Mode.ALL, modes.SearchKey.PAIR)

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

