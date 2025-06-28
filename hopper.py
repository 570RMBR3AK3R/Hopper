import ipaddress
from collections import defaultdict, deque
import argparse
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import os
import numpy as np
import base64
from io import BytesIO

class Hopper:
    def __init__(self, subnet_mask="255.255.255.0", project_folder="hopper_output"):
        self.subnet_mask = subnet_mask
        self.project_folder = project_folder
        self.ip_to_network = {}
        self.network_map = defaultdict(list)
        self.graph = defaultdict(set)
        self.network_labels = {}
        self.connected_networks = defaultdict(set)
        # Create project folder if it doesn't exist
        os.makedirs(self.project_folder, exist_ok=True)

    def load_ips(self, ip_file):
        print("\n[*] Loading IPs and grouping into networks...")
        with open(ip_file, "r") as f:
            for line in f:
                ip = line.strip()
                if not ip:
                    continue
                try:
                    net = ipaddress.IPv4Network(f"{ip}/{self.subnet_mask}", strict=False)
                    net_str = str(net)
                    self.network_map[net_str].append(ip)
                    self.ip_to_network[ip] = net_str
                except ValueError:
                    print(f"[*] Invalid IP skipped: {ip}")

        # Generate network labels
        for idx, network in enumerate(sorted(self.network_map.keys())):
            self.network_labels[network] = f"Network {chr(ord('A') + idx)}"

        print("\n[*] Classified Networks:")
        for idx, (network, ips) in enumerate(sorted(self.network_map.items()), start=0):
            label = self.network_labels[network]
            print(f"\n🌐 {label}: {network}")
            for ip in ips:
                print(f"   ↪ {ip}")

    def load_edges(self, edge_file):
        print("\n[*] Building connectivity graph...")
        with open(edge_file, "r") as f:
            for line in f:
                if "-" not in line:
                    continue
                part = line.strip().split("-")
                if len(part) != 2:
                    continue
                ip1 = part[0].strip()
                ip2 = part[1].strip()
                self.graph[ip1].add(ip2)
                self.graph[ip2].add(ip1)

        # Build network connections
        for ip1, neighbors in self.graph.items():
            net1 = self.ip_to_network.get(ip1)
            if not net1:
                continue
            for ip2 in neighbors:
                net2 = self.ip_to_network.get(ip2)
                if net2 and net2 != net1:
                    self.connected_networks[net1].add(net2)
                    self.connected_networks[net2].add(net1)

        print("\n[*] Connected Networks:")
        for net1, nets in self.connected_networks.items():
            print(f"🔸 {net1} connected to:")
            for net2 in nets:
                print(f"   ↪ {net2}")

    def find_path(self, src, dst):
        print(f"\n[*] Looking for path from {src} to {dst}...")
        visited = set()
        queue = deque([[src]])

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node == dst:
                print("\n[*] Path Found:")
                print(" → ".join(path))
                return path

            if node not in visited:
                visited.add(node)
                for neighbor in self.graph[node]:
                    if neighbor not in visited:
                        queue.append(path + [neighbor])

        print("[*] No path found.")
        return None

    def export_json(self, out_file):
        print(f"\n[*] Exporting graph to {os.path.join(self.project_folder, out_file)} (JSON)...")
        
        data = {
            "metadata": {
                "subnet_mask": self.subnet_mask,
                "total_networks": len(self.network_map),
                "total_ips": sum(len(ips) for ips in self.network_map.values()),
                "total_connections": sum(len(neighbors) for neighbors in self.graph.values()) // 2,
                "generated_at": datetime.now().isoformat()
            },
            "networks": {},
            "nodes": list(self.graph.keys()),
            "edges": []
        }
        
        for network, ips in self.network_map.items():
            data["networks"][network] = {
                "label": self.network_labels.get(network, network),
                "ips": ips,
                "ip_count": len(ips),
                "connected_to": list(self.connected_networks.get(network, []))
            }
        
        processed_edges = set()
        for node in self.graph:
            for neighbor in self.graph[node]:
                edge = tuple(sorted([node, neighbor]))
                if edge not in processed_edges:
                    processed_edges.add(edge)
                    data["edges"].append({
                        "source": edge[0],
                        "target": edge[1],
                        "source_network": self.ip_to_network.get(edge[0], "Unknown"),
                        "target_network": self.ip_to_network.get(edge[1], "Unknown"),
                        "is_inter_network": self.ip_to_network.get(edge[0]) != self.ip_to_network.get(edge[1])
                    })
        
        with open(os.path.join(self.project_folder, out_file), "w") as f:
            json.dump(data, f, indent=4)
        print("✅ JSON export complete.")

    def visualize_graph(self, output_file="hopper_graph.png", style="network"):
        print(f"\n[*] Drawing network graph (style: {style})...")
        output_path = os.path.join(self.project_folder, output_file)
        
        if style == "network":
            self._visualize_network_level(output_path)
        elif style == "detailed":
            self._visualize_detailed_graph(output_path)
        elif style == "hierarchical":
            self._visualize_hierarchical(output_path)
        else:
            self._visualize_detailed_graph(output_path)

    def _visualize_network_level(self, output_file):
        plt.figure(figsize=(14, 10))
        plt.style.use('default')
        
        G = nx.Graph()
        for network in self.network_map.keys():
            G.add_node(network)
        
        for net1, connected_nets in self.connected_networks.items():
            for net2 in connected_nets:
                if not G.has_edge(net1, net2):
                    G.add_edge(net1, net2)
        
        if len(G.nodes()) > 1:
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        else:
            pos = {list(G.nodes())[0]: (0, 0)} if G.nodes() else {}
        
        colors = plt.cm.Set3(np.linspace(0, 1, max(len(self.network_map), 1)))
        node_colors = [colors[i] for i in range(len(G.nodes()))]
        
        nx.draw_networkx_nodes(G, pos, 
                             node_color=node_colors,
                             node_size=4000,
                             alpha=0.8,
                             edgecolors='black',
                             linewidths=2)
        
        nx.draw_networkx_edges(G, pos,
                             edge_color='#666666',
                             width=3,
                             alpha=0.7)
        
        labels = {}
        for network in G.nodes():
            label = self.network_labels.get(network, network)
            ip_count = len(self.network_map[network])
            labels[network] = f"{label}\n({ip_count} hosts)\n{network}"
        
        nx.draw_networkx_labels(G, pos, labels, 
                               font_size=9,
                               font_weight='bold',
                               font_color='black')
        
        plt.title("Network Topology - Subnet Level View", 
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        print(f"✅ Network-level graph saved as '{output_file}'")

    def _visualize_detailed_graph(self, output_file):
        plt.figure(figsize=(16, 12))
        plt.style.use('default')
        
        G = nx.Graph()
        for node in self.graph:
            G.add_node(node)
            for neighbor in self.graph[node]:
                G.add_edge(node, neighbor)
        
        if not G.nodes():
            print("❌ No nodes to visualize")
            return
        
        pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
        
        colors = plt.cm.Set3(np.linspace(0, 1, max(len(self.network_map), 1)))
        network_color_map = {}
        for i, network in enumerate(sorted(self.network_map.keys())):
            network_color_map[network] = colors[i]
        
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            network = self.ip_to_network.get(node)
            if network:
                node_colors.append(network_color_map[network])
                node_sizes.append(500 + len(self.graph[node]) * 100)
            else:
                node_colors.append('gray')
                node_sizes.append(500)
        
        nx.draw_networkx_nodes(G, pos,
                             node_color=node_colors,
                             node_size=node_sizes,
                             alpha=0.8,
                             edgecolors='black',
                             linewidths=1)
        
        inter_network_edges = []
        intra_network_edges = []
        
        for edge in G.edges():
            net1 = self.ip_to_network.get(edge[0])
            net2 = self.ip_to_network.get(edge[1])
            if net1 != net2:
                inter_network_edges.append(edge)
            else:
                intra_network_edges.append(edge)
        
        nx.draw_networkx_edges(G, pos, edgelist=intra_network_edges,
                             width=2, alpha=0.6, edge_color='#4CAF50')
        
        nx.draw_networkx_edges(G, pos, edgelist=inter_network_edges,
                             width=3, alpha=0.8, edge_color='#FF5722')
        
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        
        legend_elements = []
        for network, color in network_color_map.items():
            label = self.network_labels.get(network, network)
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                           markerfacecolor=color, markersize=12,
                                           label=f"{label}: {network}"))
        
        legend_elements.append(plt.Line2D([0], [0], color='#4CAF50', linewidth=3,
                                       label='Intra-network'))
        legend_elements.append(plt.Line2D([0], [0], color='#FF5722', linewidth=3,
                                       label='Inter-network'))
        
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        plt.title("Detailed Network Topology - IP Level View", 
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        print(f"✅ Detailed graph saved as '{output_file}'")

    def _visualize_hierarchical(self, output_file):
        fig, ax = plt.subplots(figsize=(16, 12))
        plt.style.use('default')
        
        G = nx.Graph()
        for node in self.graph:
            G.add_node(node)
            for neighbor in self.graph[node]:
                G.add_edge(node, neighbor)
        
        if not G.nodes():
            print("❌ No nodes to visualize")
            return
        
        network_positions = {}
        colors = plt.cm.Set3(np.linspace(0, 1, max(len(self.network_map), 1)))
        
        y_offset = 0
        for i, (network, ips) in enumerate(sorted(self.network_map.items())):
            if len(ips) == 1:
                positions = [(0, y_offset)]
            else:
                x_positions = np.linspace(-2, 2, len(ips))
                positions = [(x, y_offset) for x in x_positions]
            
            for j, ip in enumerate(ips):
                network_positions[ip] = positions[j]
            
            if len(ips) > 1:
                rect = patches.Rectangle((-2.5, y_offset - 0.3), 5, 0.6,
                                       linewidth=2, edgecolor=colors[i],
                                       facecolor=colors[i], alpha=0.2)
                ax.add_patch(rect)
            
            label = self.network_labels.get(network, network)
            ax.text(-3, y_offset, f"{label}\n{network}", 
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=colors[i], alpha=0.7))
            
            y_offset -= 2
        
        for node in G.nodes():
            x, y = network_positions[node]
            network = self.ip_to_network.get(node)
            network_idx = list(sorted(self.network_map.keys())).index(network)
            
            circle = patches.Circle((x, y), 0.15, 
                                  facecolor=colors[network_idx], 
                                  edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            ax.text(x, y, node, ha='center', va='center', 
                   fontsize=7, fontweight='bold')
        
        for edge in G.edges():
            x1, y1 = network_positions[edge[0]]
            x2, y2 = network_positions[edge[1]]
            
            net1 = self.ip_to_network.get(edge[0])
            net2 = self.ip_to_network.get(edge[1])
            
            if net1 != net2:
                ax.plot([x1, x2], [y1, y2], 'r-', linewidth=2, alpha=0.8)
            else:
                ax.plot([x1, x2], [y1, y2], 'g-', linewidth=1, alpha=0.6)
        
        ax.set_xlim(-4, 3)
        ax.set_ylim(y_offset - 1, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title("Hierarchical Network View", fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        print(f"✅ Hierarchical graph saved as '{output_file}'")

    def generate_html_report(self, include_images=True):
        print("\n🧾 Generating HTML report...")
        
        graph_files = []
        if include_images:
            self.visualize_graph("network_view.png", "network")
            self.visualize_graph("detailed_view.png", "detailed") 
            self.visualize_graph("hierarchical_view.png", "hierarchical")
            graph_files = ["network_view.png", "detailed_view.png", "hierarchical_view.png"]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hopper Network Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .network-box {{
            background: #ecf0f1;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .ip-list {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border: 1px solid #ddd;
        }}
        .connection {{
            background: #e8f6f3;
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            border-left: 3px solid #27ae60;
        }}
        .graph-container {{
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }}
        .graph-container img {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Hopper Network Analysis Report</h1>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Subnet Mask:</strong> {self.subnet_mask}</p>
        <p><strong>Project Folder:</strong> {self.project_folder}</p>
        
        <h2>📈 Network Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <span class="stat-number">{len(self.network_map)}</span>
                Networks Discovered
            </div>
            <div class="stat-box">
                <span class="stat-number">{sum(len(ips) for ips in self.network_map.values())}</span>
                Total Hosts
            </div>
            <div class="stat-box">
                <span class="stat-number">{sum(len(neighbors) for neighbors in self.graph.values()) // 2}</span>
                Connections
            </div>
            <div class="stat-box">
                <span class="stat-number">{len(self.connected_networks)}</span>
                Inter-Network Links
            </div>
        </div>
"""
        
        html += """
        <h2>🌐 Network Breakdown</h2>
"""
        
        for network, ips in sorted(self.network_map.items()):
            label = self.network_labels.get(network, network)
            html += f"""
        <div class="network-box">
            <h3>{label}: {network}</h3>
            <p><strong>Hosts:</strong> {len(ips)}</p>
            <div class="ip-list">
"""
            for ip in ips:
                connections = len(self.graph.get(ip, []))
                html += f"                <span title='{connections} connections'>{ip}</span> "
            
            html += """
            </div>
"""
            
            connected_nets = self.connected_networks.get(network, set())
            if connected_nets:
                html += "            <p><strong>Connected to:</strong></p>\n"
                for conn_net in connected_nets:
                    conn_label = self.network_labels.get(conn_net, conn_net)
                    html += f"            <div class='connection'>↔ {conn_label} ({conn_net})</div>\n"
            
            html += "        </div>\n"
        
        html += """
        <h2>🔗 Connectivity Matrix</h2>
        <table>
            <thead>
                <tr>
                    <th>Source IP</th>
                    <th>Target IP</th>
                    <th>Source Network</th>
                    <th>Target Network</th>
                    <th>Connection Type</th>
                </tr>
            </thead>
            <tbody>
"""
        
        processed_pairs = set()
        for ip1, neighbors in self.graph.items():
            for ip2 in neighbors:
                pair = tuple(sorted([ip1, ip2]))
                if pair not in processed_pairs:
                    processed_pairs.add(pair)
                    net1 = self.ip_to_network.get(ip1, "Unknown")
                    net2 = self.ip_to_network.get(ip2, "Unknown")
                    net1_label = self.network_labels.get(net1, net1)
                    net2_label = self.network_labels.get(net2, net2)
                    conn_type = "Inter-Network" if net1 != net2 else "Intra-Network"
                    style = "color: #e74c3c; font-weight: bold;" if net1 != net2 else "color: #27ae60;"
                    
                    html += f"""
                <tr>
                    <td>{ip1}</td>
                    <td>{ip2}</td>
                    <td>{net1_label}</td>
                    <td>{net2_label}</td>
                    <td style="{style}">{conn_type}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
"""
        
        if include_images and graph_files:
            html += """
        <h2>📊 Network Visualizations</h2>
"""
            
            titles = ["Network-Level View", "Detailed IP View", "Hierarchical View"]
            descriptions = [
                "Shows networks as nodes with inter-network connections",
                "Shows individual IPs with color-coded networks and connection types",
                "Shows hierarchical layout grouped by network subnets"
            ]
            
            for i, (graph_file, title, desc) in enumerate(zip(graph_files, titles, descriptions)):
                full_path = os.path.join(self.project_folder, graph_file)
                if os.path.exists(full_path):
                    html += f"""
        <div class="graph-container">
            <h3>{title}</h3>
            <p>{desc}</p>
            <img src="{graph_file}" alt="{title}">
        </div>
"""
        
        html += f"""
        <div class="footer">
            <p>Report generated by Hopper Network Analysis Tool</p>
            <p>For more information, visit the project documentation</p>
        </div>
    </div>
</body>
</html>
"""
        
        report_path = os.path.join(self.project_folder, "hopper_report.html")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML report saved as '{report_path}'")
        for graph_file in graph_files:
            print(f"   - Graph saved: {os.path.join(self.project_folder, graph_file)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Hopper - Network Relationship Visualizer")
    parser.add_argument("ips_file", help="File containing IP addresses")
    parser.add_argument("edges_file", help="File containing IP-to-IP connectivity")
    parser.add_argument("--path", nargs=2, metavar=("SRC", "DST"), help="Find path from SRC to DST")
    parser.add_argument("--subnet", default="255.255.255.0", help="Subnet mask (default: 255.255.255.0)")
    parser.add_argument("--project", default="hopper_output", help="Project folder name for output files (default: hopper_output)")
    parser.add_argument("--export", action="store_true", help="Export graph to JSON")
    parser.add_argument("--visualize", action="store_true", help="Visualize the graph")
    parser.add_argument("--vis-style", choices=["network", "detailed", "hierarchical"], 
                       default="detailed", help="Visualization style")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")

    args = parser.parse_args()

    hopper = Hopper(subnet_mask=args.subnet, project_folder=args.project)
    hopper.load_ips(args.ips_file)
    hopper.load_edges(args.edges_file)

    if args.path:
        hopper.find_path(args.path[0], args.path[1])

    if args.export:
        hopper.export_json("hopper_graph.json")

    if args.visualize:
        hopper.visualize_graph("hopper_graph.png", args.vis_style)

    if args.report:
        hopper.generate_html_report()