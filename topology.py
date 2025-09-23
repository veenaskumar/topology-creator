import json
import networkx as nx
import matplotlib.pyplot as plt

# ---------- Load JSON ----------
with open("topology.json") as f:
    data = json.load(f)

G = nx.Graph()

# ---------- Add Nodes ----------
for vm in data["VMs"]:
    name = vm["name"]
    if name.startswith("s"):
        G.add_node(name, type="switch")
    elif name.startswith("l"):
        G.add_node(name, type="leaf")
    elif name.startswith("h"):
        G.add_node(name, type="host")
    elif name.startswith("b"):
        G.add_node(name, type="bridge")

# Add IXIA node (special)
if "Ixia_connections" in data and data["Ixia_connections"]:
    G.add_node("ixia", type="ixia")

# ---------- Add Edges ----------
edges_with_ports = []  # store edge and port info
for conn in data.get("InterConnect", []):
    a, b = conn.split(":")
    a_node, a_port = a.split("_")[0], a.split("_")[1]
    b_node, b_port = b.split("_")[0], b.split("_")[1]
    G.add_edge(a_node, b_node)
    edges_with_ports.append((a_node, a_port, b_node, b_port))

# IXIA connections
for conn in data.get("Ixia_connections", []):
    a, b = conn.split(":")
    a_node, a_port = a.split("_")[0], a.split("_")[1]
    G.add_edge(a_node, "ixia")
    edges_with_ports.append((a_node, a_port, "ixia", b))

# Bridge connections
for conn in data.get("Bridge_connections", []):
    parts = conn.split(":")
    bridge = None
    for p in parts:
        if p.startswith("b"):
            bridge = p.split("_")[0]
            break
    if bridge:
        for p in parts:
            if p.startswith("s") or p.startswith("h") or p.startswith("l"):
                G.add_edge(p.split("_")[0], bridge)

# ---------- Draw Styles ----------
pos = nx.spring_layout(G, seed=42)
shapes = {"switch": "s", "leaf": "o", "host": "^", "bridge": "D", "ixia": "h"}
colors = {"switch": "skyblue", "leaf": "orange", "host": "lightgreen", "bridge": "violet", "ixia": "red"}

plt.figure(figsize=(12, 8), facecolor='white')
ax = plt.gca()
ax.set_facecolor('white')

# Draw nodes
for node_type, shape in shapes.items():
    nodelist = [n for n, attr in G.nodes(data=True) if attr["type"] == node_type]
    nx.draw_networkx_nodes(G, pos, nodelist=nodelist, node_shape=shape,
                           node_color=colors[node_type], node_size=1000, label=node_type)

# Draw edges
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos, font_size=8, font_color="black")

# ---------- Draw ports ----------
for a_node, a_port, b_node, b_port in edges_with_ports:
    x, y = pos[a_node]
    dx, dy = 0.05, 0.05  # offset for top-right placement
    ax.text(x + dx, y + dy, a_port, fontsize=6,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.1'))

# ---------- Save & Show ----------
plt.title("Network Topology with Ports", color='black')
plt.axis("off")
plt.legend(scatterpoints=1)
plt.tight_layout()
plt.savefig("topology_ports.png", dpi=300, facecolor='white')  # diagram saved in PNG
plt.show()
