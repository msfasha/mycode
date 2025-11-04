
from epanettools.epanettools import EPANetSimulation
import networkx as nx

# Load EPANET input file
es = EPANetSimulation("network.inp")

# Create a NetworkX graph
G = nx.Graph()

# Add nodes and edges from EPANET
for junc in es.network.nodes.values():
    G.add_node(junc.id)

for pipe in es.network.links.values():
    G.add_edge(pipe.startnode.id, pipe.endnode.id)

# Analyze topology
print("Number of connected components:", nx.number_connected_components(G))

# Find most central node (potential critical supply point)
centrality = nx.betweenness_centrality(G)
critical_node = max(centrality, key=centrality.get)
print("Most critical junction:", critical_node)
