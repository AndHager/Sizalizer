
def parse_file(fqfn, parse_line, debug):
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
