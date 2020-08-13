import datapackage
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

INPUT_PACKAGE = "../plots/points/correlation_plots.zip"
FIGURE_PATH = "../plots/correlation_graphs.pdf"
package = datapackage.Package(INPUT_PACKAGE)

nodes = [str(i) + str(j) for i in range(1, 9) for j in range(1, 9)]
positions = {node: (int(node[0]) - 1, int(node[1]) - 1) for node in nodes}

with PdfPages(FIGURE_PATH) as pdf:
    for resource in package.resources:
        G = nx.Graph()
        G.add_nodes_from(nodes)
        matrix = resource.read()
        channels = resource.headers
        for i in range(len(matrix)):
            for j in range(i, len(matrix[i])):
                G.add_edge(channels[i], channels[j], weight=matrix[i][j])
        edges = G.edges()
        weights = [int(G[i][j]["weight"] > 0.7) for i, j in edges]
        nx.draw(G, pos=positions, edges=edges, width=weights)
        plt.tight_layout()
        pdf.savefig()
