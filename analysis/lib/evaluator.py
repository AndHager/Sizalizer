from lib import modes

def sort_dict(result, threshold):
    vals = [
        val 
        for val in result.items()
    ]
    return sorted(vals, key=lambda x:x[1], reverse=True)[:threshold]


def most_inst(instructions, mode=modes.Mode.ALL, search_key=modes.SearchKey.MNEMONIC, threshold=10): 
    result = {}
    for inst in instructions:
        is_comp = inst.get_size() == 2 and mode == modes.Mode.COMPRESSED
        is_full = inst.get_size() == 4 and mode == modes.Mode.FULL
        use_all = mode == modes.Mode.ALL
        if use_all or is_comp or is_full:
            keys = [inst.mnemonic]
            if search_key == modes.SearchKey.OPCODE:
                keys = [inst.opcode]
            if search_key == modes.SearchKey.REGISTER:
                keys = inst.regs
            for key in keys:
                if key in result:
                    result[key] += 1
                else:
                    result[key] = 1
    return sort_dict(result, threshold)


def longest_chains(instructions, threshold=2):
    result = {}
    last_key = instructions[0].mnemonic
    chain_len = 1
    for inst in instructions[1:]:
        key = inst.mnemonic
        if last_key == key:
            chain_len += 1
        else:
            if chain_len > 1:
                if last_key in result:
                    if result[last_key] < chain_len:
                        result[last_key] = chain_len
                else:
                    result[last_key] = chain_len
            chain_len = 1
        last_key = key
    return sort_dict(result, threshold)


def chain_distrib(instructions, threshold=2):
    result = {}
    last_mn = instructions[0].mnemonic
    chain_len = 1

    for inst in instructions[1:]:
        mn = inst.get_base_mnemonic()
        if last_mn == mn:
            chain_len += 1
        else:
            if chain_len > 1:
                key = last_mn + '_' + str(chain_len)
                if key in result:
                    result[key] += 1
                else:
                    result[key] = 1
            chain_len = 1
        last_mn = mn
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


def most_addr(instructions, threshold=10000): 
    result = {}
    for inst in instructions:
        key = inst.address
        if key in result:
            result[key] += 1
        else:
            result[key] = 1
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


def get_lswm_improvement(instructions, base_isnt, new_byte_count, base_regs, dest_regs):
    '''
    Retruns the improvement potential for the new_byte_count byte lwm instruction.

    The new_byte_count byte lwm instruction has the following form:
    lwm {base_regs}, dest_regs

    Parameters:
    - instructions a list of instructions.
    - base_inst the base instruction string. Eighter 'lw' ow 'sw'.
    - new_byte_count the byte count of the new instruction.
    - base_regs a list of registers for the adress calculation.
    - dest_regs a list of rgisters to be load ore stored

    Returns
    - `int`: the amount of bytes saved with the instruction 
    '''
    assert new_byte_count >= 2 and new_byte_count%2 == 0
    assert base_isnt == 'lw' or base_isnt == 'sw' 
    imp = 0
    last = instructions[0]
    chain_byte_saved = 0

    if dest_regs != 'all':
        dest_regs_it = dest_regs.copy()

    for inst in instructions[1:]:
        mn = inst.get_base_mnemonic()
        is_eq = last.get_base_mnemonic() == mn
        is_mem = mn == base_isnt

        is_base_reg = False
        is_last_base_reg = False
        if base_regs == 'all':
            is_base_reg = True
            is_last_base_reg = True
        else:
            is_base_reg = len(inst.regs) > 1 and inst.regs[1] in base_regs
            is_last_base_reg = len(last.regs) > 1 and last.regs[1] in base_regs

        is_dest_reg = False
        is_last_dest_reg = False
        if dest_regs == 'all':
            is_dest_reg = True
            is_last_dest_reg = True
        else:
            is_dest_reg = len(inst.regs) > 0 and inst.regs[0] in dest_regs_it
            is_last_dest_reg = len(last.regs) > 0 and last.regs[0] in dest_regs_it
        
        is_mem_pair = is_eq and is_mem and is_base_reg and is_last_base_reg and is_dest_reg and is_last_dest_reg and abs(abs(inst.get_imm()) - abs(last.get_imm())) == 4 and inst.regs[0] != last.regs[0]
        if is_mem_pair:
            # chain detected
            if chain_byte_saved == 0:
                # decrement the new isntruction byte count and include the first instruction
                chain_byte_saved += last.get_size() - new_byte_count
                if dest_regs != 'all':
                    # remove the dest reg of the first instruction from the dest reg list as it can not encode the same inst twice
                    dest_regs_it.remove(last.regs[0])
            # every further instruction has just a positive imact
            chain_byte_saved += inst.get_size()
            if dest_regs != 'all':
                # remove the dest reg of the n-th inst
                dest_regs_it.remove(inst.regs[0])
        else: 
            # chain finished
            if chain_byte_saved > 0:
                # only replace when there is a positive impact (especially for 32 and 48 bit inst)
                imp += chain_byte_saved
            chain_byte_saved = 0
            if dest_regs != 'all':
                # reset dest reg list
                dest_regs_it = dest_regs.copy()
        last = inst
    return imp


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


def get_byte_count(instructions):
    result = 0
    for inst in instructions:
        result += inst.get_size()
    return result
