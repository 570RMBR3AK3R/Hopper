import ipaddress
from collections import defaultdict, deque
import argparse
import json
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import os

class Hopper:
    def __init__(self, subnet_mask="255.255.255.0"):
        self.subnet_mask = subnet_mask
        self.ip_to_network = {}
        self.network_map = defaultdict(list)
        self.graph = defaultdict(set)

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

        print("\n[*] Classified Networks:")
        for idx, (network, ips) in enumerate(sorted(self.network_map.items()), start=0):
            label = f"Network {chr(ord('A') + idx)}"
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

        connected_networks = defaultdict(set)
        for ip1, neighbors in self.graph.items():
            net1 = self.ip_to_network.get(ip1)
            if not net1:
                continue
            for ip2 in neighbors:
                net2 = self.ip_to_network.get(ip2)
                if net2 and net2 != net1:
                    connected_networks[net1].add(net2)

        print("\n[*] Connected Networks:")
        for net1, nets in connected_networks.items():
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
        print(f"\n[*] Exporting graph to {out_file} (JSON)...")
        data = {
            "nodes": list(self.graph.keys()),
            "edges": [(a, b) for a in self.graph for b in self.graph[a]]
        }
        with open(out_file, "w") as f:
            json.dump(data, f, indent=4)
        print("✅ JSON export complete.")

    def visualize_graph(self):
        print("\n[*] Drawing network graph...")
        G = nx.Graph()
        for node in self.graph:
            G.add_node(node)
            for neighbor in self.graph[node]:
                G.add_edge(node, neighbor)

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray', node_size=2000, font_size=10)
        plt.title("Hopper Network Graph")
        plt.tight_layout()
        plt.savefig("hopper_graph.png")
        plt.show()
        print("✅ Graph image saved as 'hopper_graph.png'")

    def generate_html_report(self):
        print("\n🧾 Generating HTML report...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = f"""
        <html>
        <head><title>Hopper Network Report</title></head>
        <body>
        <h1>📄 Hopper Network Report</h1>
        <p><b>Generated:</b> {timestamp}</p>
        <h2>🕸️ Network Graph</h2>
        <img src="hopper_graph.png" width="800">
        <h2>🔗 Connectivity Edges</h2>
        <ul>
        """
        for node in self.graph:
            for neighbor in self.graph[node]:
                html += f"<li>{node} ↔ {neighbor}</li>"

        html += """
        </ul>
        </body></html>
        """
        with open("hopper_report.html", "w") as f:
            f.write(html)
        print("✅ HTML report saved as 'hopper_report.html'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Hopper - Network Relationship Visualizer")
    parser.add_argument("ips_file", help="File containing IP addresses")
    parser.add_argument("edges_file", help="File containing IP-to-IP connectivity")
    parser.add_argument("--path", nargs=2, metavar=("SRC", "DST"), help="Find path from SRC to DST")
    parser.add_argument("--subnet", default="255.255.255.0", help="Subnet mask (default: 255.255.255.0)")
    parser.add_argument("--export", action="store_true", help="Export graph to JSON")
    parser.add_argument("--visualize", action="store_true", help="Visualize the graph")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")

    args = parser.parse_args()

    hopper = Hopper(subnet_mask=args.subnet)
    hopper.load_ips(args.ips_file)
    hopper.load_edges(args.edges_file)

    if args.path:
        hopper.find_path(args.path[0], args.path[1])

    if args.export:
        hopper.export_json("hopper_graph.json")

    if args.visualize:
        hopper.visualize_graph()

    if args.report:
        hopper.generate_html_report()
