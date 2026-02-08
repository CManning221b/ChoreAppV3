# -*- coding: utf-8 -*-
"""
PropertyGraph.py
Created on 15/01/2026
@author: Callum
"""
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from pyvis.network import Network

class PropertyGraph:
    def __init__(self, graph = None):
        if graph is None:
            self.graph = nx.Graph()
        else:
            self.graph = graph

    def addNode(self, id: str, label: str, type: str, **kwargs):

        node_data = {
            'label': label,
            'type': type,
            **kwargs
        }
        self.graph.add_node(id, **node_data)

    def addEdge(self,  id: str, source: str, target: str, label: str, type: str, **kwargs):
        edge_data = {
            'id': id,
            'label': label,
            'type': type,
            **kwargs
        }
        self.graph.add_edge(source, target, **edge_data)

    def getAllNodes(self):
        return list(self.graph.nodes(data=True))

    def getAllEdges(self):
        return list(self.graph.edges(data=True))

    def getNodesByType(self, node_type: str):
        return [(node_id, data) for node_id, data in self.graph.nodes(data=True)
                if data.get('type') == node_type]

    def getEdgesByType(self, edge_type: str):
        return [(source, target, data) for source, target, data in self.graph.edges(data=True)
                if data.get('type') == edge_type]

    def getNodeTypes(self):
        return list(set(data.get('type') for _, data in self.graph.nodes(data=True)))

    def getEdgeTypes(self):
        return list(set(data.get('type') for _, _, data in self.graph.edges(data=True)))

    def _generateColorMap(self, types, colormap='Set3'):
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, len(types)))
        return {type_name: colors[i] for i, type_name in enumerate(types)}

    def gatherPlotData(self, node_color_map=None, edge_color_map=None):
        pos = nx.spring_layout(self.graph)

        if node_color_map is None:
            node_types = self.getNodeTypes()
            node_color_map = self._generateColorMap(node_types, 'Set3')

        if edge_color_map is None:
            edge_types = self.getEdgeTypes()
            edge_color_map = self._generateColorMap(edge_types, 'Set2')

        nodes_by_type = {}
        for node_type in self.getNodeTypes():
            nodes = self.getNodesByType(node_type)
            nodes_by_type[node_type] = [node_id for node_id, _ in nodes]

        edges_by_type = {}
        for edge_type in self.getEdgeTypes():
            edges = self.getEdgesByType(edge_type)
            edges_by_type[edge_type] = [(source, target) for source, target, _ in edges]

        return {
            'graph': self.graph,
            'pos': pos,
            'nodes_by_type': nodes_by_type,
            'edges_by_type': edges_by_type,
            'node_color_map': node_color_map,
            'edge_color_map': edge_color_map
        }

    def plotNetworkX(self, figsize=(12, 8), node_color_map=None, edge_color_map=None):
        plot_data = self.gatherPlotData(node_color_map, edge_color_map)

        plt.figure(figsize=figsize)

        for edge_type, edge_list in plot_data['edges_by_type'].items():
            nx.draw_networkx_edges(plot_data['graph'], plot_data['pos'], edgelist=edge_list,
                                   edge_color=plot_data['edge_color_map'][edge_type],
                                   width=1.5, alpha=0.6)

        for node_type, node_list in plot_data['nodes_by_type'].items():
            nx.draw_networkx_nodes(plot_data['graph'], plot_data['pos'], nodelist=node_list,
                                   node_color=plot_data['node_color_map'][node_type],
                                   node_size=500, label=node_type)

        nx.draw_networkx_labels(plot_data['graph'], plot_data['pos'], font_size=8)
        plt.legend(scatterpoints=1)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def plotPyvis(self, output_file='graph.html', node_color_map=None, edge_color_map=None, physics=True):
        """Plot the graph using pyvis and save as an interactive HTML file"""
        from pyvis.network import Network
        import matplotlib.colors as mcolors

        plot_data = self.gatherPlotData(node_color_map, edge_color_map)

        net = Network(directed=True)

        # Convert colors to hex strings for JSON serialization
        node_colors_hex = {node_type: mcolors.to_hex(color)
                           for node_type, color in plot_data['node_color_map'].items()}
        edge_colors_hex = {edge_type: mcolors.to_hex(color)
                           for edge_type, color in plot_data['edge_color_map'].items()}

        # Add nodes by type with colors and tooltips
        for node_id, node_data in plot_data['graph'].nodes(data=True):
            node_type = node_data.get('type', 'Unknown')
            label = node_data.get('label', node_id)
            color = node_colors_hex[node_type]

            # Build tooltip with all properties
            tooltip = f"{label} \nType: {node_type}\n"
            for key, value in node_data.items():
                if key not in ['label', 'type']:
                    tooltip += f"{key}: {value}\n"

            net.add_node(node_id, label=label, title=tooltip, color=color, size=25)

        # Add edges by type with colors and tooltips
        for source, target, edge_data in plot_data['graph'].edges(data=True):
            edge_type = edge_data.get('type', 'Unknown')
            label = edge_data.get('label', '')
            color = edge_colors_hex[edge_type]

            # Build tooltip with all properties
            tooltip = f"{label} \n Type: {edge_type}\n"
            for key, value in edge_data.items():
                if key not in ['label', 'type']:
                    tooltip += f"{key}: {value}\n"

            net.add_edge(source, target, label=label, color=color, title=tooltip)

        net.show(output_file, notebook = False)
        print(f"Graph saved to {output_file}")

pg = PropertyGraph()

# Add nodes and edges
pg.addNode('n1', label='Alice', type='Person')
pg.addNode('n2', label='Bob', type='Person')
pg.addNode('n3', label='NYC', type='Place')
pg.addEdge('e1', 'n1', 'n2', label='knows', type='friendship')
pg.addEdge('e2', 'n1', 'n3', label='lives_in', type='location')

# Simple plot with auto-generated colors
pg.plotNetworkX()

# Or gather data to use with other plotters
plot_data = pg.gatherPlotData()


pg.plotPyvis(output_file='my_graph_static.html', physics=False)
