import datapackage
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

INPUT_PACKAGE = "../plots/points/correlation_plots.zip"
FIGURE_PATH = "../plots/correlation_graphs.pdf"
package = datapackage.Package(INPUT_PACKAGE)

nodes = [str(i) + str(j) for i in range(1, 9) for j in range(1, 9)]
positions = {node: (int(node[0]) - 1, int(node[1]) - 1) for node in nodes}

resources = sorted(package.resources, key=lambda x: x.descriptor["date"])
resources = sorted(resources, key=lambda x: x.descriptor["replicate"])
with PdfPages(FIGURE_PATH) as pdf:
    for resource in tqdm(resources):
        G = nx.Graph()
        G.add_nodes_from(nodes)
        matrix = resource.read()
        channels = resource.headers
        for i in range(len(matrix)):
            for j in range(i, len(matrix[i])):
                G.add_edge(channels[i], channels[j], weight=matrix[i][j])
        edges = G.edges()
        weights = [abs(G[i][j]["weight"]) for i, j in edges]
        figure, axes = plt.subplots()
        nx.draw_networkx_nodes(G, pos=positions, node_size=100, ax=axes)
        for e, w in zip(edges, weights):
            nx.draw_networkx_edges(G, pos=positions, edgelist=[e], alpha=w, ax=axes)
        figure.suptitle(resource.descriptor["date"] + " D" +
                        str(resource.descriptor["age"]) + " " +
                        resource.descriptor["replicate"])
        figure.tight_layout()
        pdf.savefig()
        plt.close()
