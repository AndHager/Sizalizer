import argparse
from neo4j import GraphDatabase
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

plt.rcParams["font.family"] = "cmb10"
debug = False


def clear_db(client):
    records, summary, keys = client.execute_query(
        'MATCH (n) DETACH DELETE n;'
    )


def sort_dict(result, threshold=0):
    vals = [
        val 
        for val in result.items()
    ]
    return sorted(vals, key=lambda x:x[1], reverse=True)[:threshold]


def plot_bars(stats, name):
    # set width of bars
    name = str(name)

    bar_width = 0.20

    plt.figure(figsize=(8, 3))
    plt.grid(visible = True, axis = 'y', color = 'gray', linestyle = '--', linewidth = 0.5, alpha = 0.7)
    plt.grid(visible = True, axis = 'y', which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.rc('axes', unicode_minus=False)

    _chains = [
        str(pair[0])
        for pair in stats
    ]
    chains = []
    for chain in _chains:
        label = ''
        first = True
        for line in chain.split('\n'):
            if first:
                label += line
            else: 
                label += '\n'
                nodes = line.split('-')
                label += ' '*(len(nodes[0])-1) 
                label += '\\-'
                label += '-'.join(nodes[1:])
            first = False
            
        chains += [label]
    assert len(chains) == len(_chains)

    counts = [
        pair[1]
        for pair in stats
    ]

    bars_y = counts
    bars_x = np.arange(len(bars_y))
    plt.bar(bars_x, bars_y, width=bar_width, edgecolor='white', label=chains, log=False)

    # plt.title(name)
    ylabel = 'Count Inst.'
    # plt.ylabel(ylabel)
    plt.xticks([r for r in range(len(chains))], chains)
    for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
        y_position = label.get_position()[1]  # Get current y position
        if index % 2 != 0:  # For odd indices
            label.set_y(y_position - 0.06)  # Move down by a fraction; adjust as needed

    plt.legend().remove()
    plt.tight_layout()

    fig_name = './out/_DFG_' + name
    plt.savefig(fig_name + '.pdf')
    tikzplotlib.save(fig_name + '.tex')
    plt.close()

def query_builder(length=1, width=1, special_cond='true', ignore=['Const', 'phi'], fixed_start=True):
    return query_builder2(
        [length for _ in range(width)],
        width,
        special_cond,
        ignore
    )

def query_builder2(length=[1], width=1, special_cond='true', ignore=['Const', 'phi'], fixed_start=True):
    assert len(length) == width
    assert width > 0
    query = ''
    for i in range(width):
        query += f'MATCH p{i}=(n'
        if fixed_start:
            query += '0'
        else:
            query += str(i)
        query += '0)'
        for j in range(1, length[i]):
            query += f'-[r{i}{j}:DFG]->(n{i}{j})'
        query += ' '
    query += 'WHERE ('

    if len(ignore) > 0:
        for name in ignore:
            start = 0
            if fixed_start: 
                start = 1
                query += f'n00.name != \'{name}\' AND '
            for i in range(0, width):
                for j in range(start, length[i]):
                    query += f'n{i}{j}.name != \'{name}\' AND '
    for i in range(1, width):
        for j in range(1, length[i]):
            if j - 1 in range(1, length[i-1]):
                query += f'n{i-1}{j} != n{i}{j} AND '
        query += f'p{i-1} != p{i} AND '
    if special_cond == '':
        special_cond = 'true'
    query += '(' + special_cond + ')) RETURN p0'
    
    for i in range(1, width):
        query += f', p{i}'

    return query + ';'


def plot_nodes(client, threshold=10):
    query = 'MATCH (n) WHERE n.name != \'Const\' AND n.name != \'phi\' RETURN n;'

    # Count the number of nodes in the database
    records, summary, keys = client.execute_query(
        query
    )

    # Get the result
    recs = [
        record['n']['name']
        for record in records
    ]
    recs_cout = {
        nodes: recs.count(nodes)
        for nodes in recs
    }

    sorted = sort_dict(recs_cout, threshold)
    plot_bars(sorted, str(1))


def get_rel_res(records, threshold):
    recs = [
        '-'.join([
            node['name']
            for node in list(dict.fromkeys([
                node
                for r in record['p0']
                for node in r.nodes
        ]))])
        for record in records
    ]
    recs_cout = {
        nodes: recs.count(nodes)
        for nodes in recs
    }
    return sort_dict(recs_cout, threshold)


def get_rel_res2(records, threshold, rels=['p0']):
    recs = [
        '\n'.join([
            '-'.join([
                node['name']
                for node in list(dict.fromkeys([
                    node
                    for r in record[rel]
                    for node in r.nodes
                ]))
            ])
            for rel in rels
        ])
        for record in records
    ]
    
    subgraph_count = {
        subgraph: recs.count(subgraph)
        for subgraph in recs
    }

    return sort_dict(subgraph_count, threshold)


def plot_duplicated_chains(client, length, ignore=['phi'], threshold=10):
    if type(length) == int and length > 0:
        query = query_builder(length, width=1, ignore=ignore)
        
        records, summary, keys = client.execute_query(
            query
        )

        # Get the result
        sorted = get_rel_res(records, threshold)
        plot_bars(sorted, length)


def plot_chains_with_fiexed_start_end(client, length, first, last, ignore=['phi'], threshold=10):
    if type(length) == int and length > 1:
        query = query_builder(length, width=1, special_cond=f'n00.name = \'{first}\' AND n0{length - 1}.name = \'{last}\'', ignore=ignore)
        records, summary, keys = client.execute_query(
            query
        )

        # Get the result
        sorted = get_rel_res(records, threshold)
        plot_bars(sorted, first + '_' + str(length - 1) + 'xX_' + last)


def plot_paralell_chains_fixed_start(client, length, width, ignore=['phi'], threshold=10):
    assert width >= 2
    query = query_builder(length, width=width, special_cond='', ignore=ignore, fixed_start=True)

    records, summary, keys = client.execute_query(
        query
    )

    # Get the result
    sorted = get_rel_res2(
        records, 
        threshold, 
        [f'p{i}' for i in range(width)]
    )
    plot_bars(sorted, 'Paralell_' + str(length) + '_X_' + str(width))


def print_num_nodes(client):
    # Count the number of nodes in the database
    records, summary, keys = client.execute_query(
        'MATCH (n) WHERE n.name != \'Const\' AND n.name != \'phi\' RETURN count(n) AS num_of_nodes;'
    )

    # Get the result
    for record in records:
        print('Number of nodes:', record['num_of_nodes'])


def main(args):
    uri = 'bolt://' + args.host + ':' + str(args.port)
    auth = ('', '')
    plot_dup_chains = args.pdc
    plot_dup_chains = True

    with GraphDatabase.driver(uri, auth=auth) as client:
        client.verify_connectivity()
        if args.clear_db:
            clear_db(client)
        else:
            if debug:
                print_num_nodes(client)
            plot_nodes(client, 16)

            ignore = ['Const', 'phi']

            for length in range(2, 5):
                plot_chains_with_fiexed_start_end(client, length, 'load', 'store', ignore, 10)
                plot_chains_with_fiexed_start_end(client, length, 'xor', 'store', ignore, 10)
                plot_chains_with_fiexed_start_end(client, length, 'add', 'store', ignore, 10)

            for length in range(2, 6):
                for width in range(2, 3):
                    plot_paralell_chains_fixed_start(client, length, width, ignore, threshold=6)

            if plot_dup_chains:
                for length in range(2, 9):
                    plot_duplicated_chains(client, length, ignore, 8)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze the File.')
    parser.add_argument('--host', nargs='?', type=str, default='localhost', help='host of the memgraph (or Neo4j) DB (reachable over bolt)')
    parser.add_argument('--port', nargs='?', type=int, default=7687, help='port of the Memgraph DB')
    parser.add_argument('--pdc', nargs='?', type=bool, default=False, help='Plot Duplicated Chains')
    parser.add_argument('--clear-db', nargs='?', type=bool, default=False, help='Clear the DB')
    main(parser.parse_args())
