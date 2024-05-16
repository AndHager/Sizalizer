import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

from lib import modes

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": "Helvetica",
})

def plot_bars(stats, filename, tp, path, mode, search_key):
    # set width of bars
    # usetex for latex plots
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
            label.set_y(y_position - 0.12)  # Move down by a fraction; adjust as needed

    plt.tight_layout()
    # plt.legend().remove()

    fig_name = str(path) + '/' + str(name) + '_' + str(tp) + '_' + search_key.value + '_' + mode.value
    plt.savefig(str(fig_name) + '.pdf')
    tikzplotlib.save(fig_name + '.tex')
    plt.close()
