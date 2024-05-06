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
