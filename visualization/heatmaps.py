import sys
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import codecs, glob

def heatmap(xlabels=None, ylabels=None, weights=None, output_file=None, reverse=False):
    """
    Draw a heatmap showing the alignment between two sequences.
    :param xlabels: input words
    :param ylabels: output words
    :param weights: numpy array of shape (len(xlabels), len(ylabels))
    :param output_file: write the figure to this file, or show it into a window if None
    """
    if reverse and not ylabels:
        matplotlib.rcParams.update({'font.size': 18})

    def prettify(token):
        token_mapping = {
            '&quot;': '"',
            '&apos;': '\'',
            '&amp;': '&',
            '@@': '_'
        }
        for x, y in token_mapping.items():
            token = token.replace(x, y)
        return token

    xlabels = xlabels or []
    ylabels = ylabels or []
    xlabels = list(map(prettify, xlabels))
    ylabels = list(map(prettify, ylabels))

    if reverse:
        xlabels, ylabels = ylabels, xlabels
        weights = weights.T

    fig, ax = plt.subplots()

    plt.autoscale(enable=True, axis='x', tight=True)
    ax.pcolor(weights, cmap=plt.cm.Greys)
    ax.set_frame_on(False)
    # plt.colorbar(mappable=heatmap_)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(len(weights)) + 0.5, minor=False)
    ax.set_xticks(np.arange(len(weights[0])) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    ax.set_xticklabels(xlabels, minor=False)
    ax.set_yticklabels(ylabels, minor=False)
    ax.tick_params(axis='both', which='both', length=0)

    if not reverse:
        plt.xticks(rotation=90)

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.subplots_adjust(wspace=0, hspace=0)

    if not reverse or ylabels:
        plt.tight_layout()
        ax.set_aspect('equal')
        ax.grid(True)

    xsize = max(2.0 + len(xlabels) / 3, 8.0)
    ysize = max(2.0 + len(ylabels) / 3, 8.0)
    fig.set_size_inches(xsize, ysize, forward=True)

    if output_file is None:
        plt.show()
    else:
        plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def read_matrix(f_path):
    matrix = [line.strip("\n").split("\t") for line in codecs.open(f_path,"r","utf-8")]
    src_tokens = []
    trg_tokens = []
    weights = []
    for i in range(len(matrix)):
        if i == 0:
            src_tokens = matrix[i][1:]
        else:
            trg_tokens += [matrix[i][0]]
            weights.append([float(element) for element in matrix[i][1:]])
    return src_tokens, trg_tokens, weights



def main():
    root_dir = glob.glob(sys.argv[1] + "/*.txt")
    for f_path in root_dir:
        src, trg, weights = read_matrix(f_path)
        output = f_path.replace(".txt",".jpg")
        heatmap(src, trg, weights, output_file=output)
        


if __name__ == "__main__":
    main()