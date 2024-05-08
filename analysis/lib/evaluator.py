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


def most_pairs(instructions, threshold=5, equal=False, connected=False):
    result = {}
    old_inst = instructions[0]
    for inst in instructions[1:]:
        old_mn = old_inst.mnemonic
        new_mn = inst.mnemonic
        is_equal = old_mn == new_mn or equal
        is_connected = old_inst.get_dest() in inst.get_params() or connected
        if is_equal or is_connected:
            key = old_mn
            if not equal:
                key = old_mn + '-' + new_mn
            if key in result:
                result[key] += 1
            else:
                result[key] = 1
        old_inst = inst
    return sort_dict(result, threshold)


def most_triplets(instructions, threshold=5, equal=False, connected=False):
    # overlapping triples
    result = {}
    vold_inst = instructions[0]
    old_inst = instructions[1]
    for inst in instructions[2:]:
        vold_mn = vold_inst.mnemonic
        old_mn = old_inst.mnemonic
        new_mn = inst.mnemonic
        is_equal = vold_mn == old_mn and old_mn == new_mn and equal
        is_connected = vold_inst.get_dest() in old_inst.get_params() and old_inst.get_dest() in inst.get_params() and connected
        if is_equal or is_connected or (not equal and not connected):
            key = old_mn
            if not equal:
                key = vold_mn + '-' + old_mn + '-' + new_mn
            if key in result:
                result[key] += 1
            else:
                result[key] = 1
        vold_inst = old_inst
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
    Retruns the improvement potential for the `new_byte_count` byte lwm instruction.

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


def get_en_improvement(instructions, mns):
    '''
    Retruns the improvement potential for the 48 bit instruction.

    The e.li instruction has the following form:
    e.li rd, imm
    The imm is a full 32 bit immediate value.

    Can replace (saves 6 byte):
    13 d5 f8 01  	srli	a0, a7, 0x1f
    13 16 13 00  	slli	a2, t1, 0x1
    33 63 a6 00  	or	    t1, a2, a0

    Can replace (saves 2 byte):
    37 06 33 b9  	lui     a2, 0xb9330
    13 06 36 57  	addi	a2, a2, 0x573
    with e.li rd, imm

    or:
    93 04 00 08  	addi	s1, zero, 0x80
    93 08 c1 10  	addi	a7, sp, 0x10c
    with e.2addi rd1, rd2, rs1, rs2, imm1, imm2


    Parameters:
    - instructions a list of instructions.

    Returns
    - `int`: the amount of bytes saved with the instruction 
    '''
    new_byte_count = 6 # 48 bit == 6 Byte
    imp = 0
    n = len(mns)
    assert(n > 0)

    li = [
        instructions[i]
        for i in range(n-1)
    ]

    for inst in instructions[n-1:]:
        li.append(inst)
        assert len(li) == len(mns)
        is_eq = True
        for i in range(n):
            is_eq = is_eq and li[i].get_base_mnemonic() == mns[i]
        if is_eq:
            saved = sum([i.get_size() for i in li]) - new_byte_count
            if saved > 0:
                imp += saved
        li.remove(li[0])
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
