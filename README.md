# Hopper - Network Path Discovery & Visualization Tool

**Hopper** is a lightweight Python tool designed for security researchers and pentesters to map host-to-host communication paths within complex networks. Given a list of IP addresses and connectivity mappings, Hopper groups hosts by subnet, builds an internal graph of connections, and allows users to:

* Identify network segment relationships
* Find the shortest path between any two IPs  
* Export the graph as JSON
* Visualize the network as a PNG
* Generate clean HTML reports


## 🚀 Features

- **Network Segmentation Analysis**: Automatically groups IPs by subnet and identifies inter-network connections
- **Path Discovery**: Find shortest paths between any two hosts using BFS algorithm
- **Multiple Output Formats**: 
  - JSON export for programmatic analysis
  - PNG network visualization
  - HTML reports with embedded graphs
- **Flexible Subnet Configuration**: Customizable subnet masks for different network architectures
- **Clean Visual Output**: Color-coded network diagrams with clear labeling

## 📋 Requirements

```bash
pip install networkx matplotlib ipaddress
```

## 🛠️ Installation

1. Clone or download the script
2. Install dependencies:
   ```bash
   pip install networkx matplotlib
   ```
3. Prepare your input files (see Input Format section)

## 📁 Input Format

### IP Address File (`ips.txt`)
One IP address per line:
```
192.168.1.10
192.168.1.20
10.0.0.5
10.0.0.15
172.16.1.100
```

### Connectivity File (`edges.txt`)
IP-to-IP connections separated by hyphens:
```
192.168.1.10-192.168.1.20
192.168.1.20-10.0.0.5
10.0.0.5-10.0.0.15
10.0.0.15-172.16.1.100
```

## 🎯 Usage

### Basic Network Analysis
```bash
python hopper.py ips.txt edges.txt
```

### Find Path Between Hosts
```bash
python hopper.py ips.txt edges.txt --path 192.168.1.10 172.16.1.100
```

### Export to JSON
```bash
python hopper.py ips.txt edges.txt --export
```

### Generate Network Visualization
```bash
python hopper.py ips.txt edges.txt --visualize
```

### Create HTML Report
```bash
python hopper.py ips.txt edges.txt --report
```

### Custom Subnet Mask
```bash
python hopper.py ips.txt edges.txt --subnet 255.255.0.0
```

### Combined Analysis
```bash
python hopper.py ips.txt edges.txt --path 192.168.1.10 10.0.0.5 --export --visualize --report
```

## 🔧 Command Line Options

| Option | Description |
|--------|-------------|
| `ips_file` | File containing IP addresses (required) |
| `edges_file` | File containing IP-to-IP connectivity (required) |
| `--path SRC DST` | Find shortest path between source and destination IPs |
| `--subnet MASK` | Custom subnet mask (default: 255.255.255.0) |
| `--export` | Export graph data to JSON format |
| `--visualize` | Generate PNG network visualization |
| `--report` | Create HTML report with embedded graph |

## 📊 Output Examples

### Console Output
```
[*] Loading IPs and grouping into networks...

[*] Classified Networks:

🌐 Network A: 192.168.1.0/24
   ↪ 192.168.1.10
   ↪ 192.168.1.20

🌐 Network B: 10.0.0.0/24
   ↪ 10.0.0.5
   ↪ 10.0.0.15

[*] Building connectivity graph...

[*] Connected Networks:
🔸 192.168.1.0/24 connected to:
   ↪ 10.0.0.0/24

[*] Looking for path from 192.168.1.10 to 172.16.1.100...

[*] Path Found:
192.168.1.10 → 192.168.1.20 → 10.0.0.5 → 10.0.0.15 → 172.16.1.100
```

### JSON Export Structure
```json
{
    "nodes": [
        "192.168.1.10",
        "192.168.1.20",
        "10.0.0.5",
        "10.0.0.15",
        "172.16.1.100"
    ],
    "edges": [
        ["192.168.1.10", "192.168.1.20"],
        ["192.168.1.20", "10.0.0.5"],
        ["10.0.0.5", "10.0.0.15"],
        ["10.0.0.15", "172.16.1.100"]
    ]
}
```

## 🔍 Use Cases

### Penetration Testing
- **Lateral Movement Planning**: Identify paths for network traversal
- **Network Mapping**: Understand target infrastructure layout
- **Pivot Point Analysis**: Find critical nodes for maintaining access

### Security Research
- **Network Topology Discovery**: Map complex enterprise networks
- **Attack Path Analysis**: Understand potential compromise routes
- **Infrastructure Assessment**: Identify network segmentation gaps

### Network Administration
- **Connectivity Troubleshooting**: Visualize communication paths
- **Network Documentation**: Generate topology reports
- **Segmentation Verification**: Validate network isolation

## 📁 Output Files

When using various options, Hopper generates:

- `hopper_graph.json` - JSON export of network data
- `hopper_graph.png` - Network visualization image
- `hopper_report.html` - Complete HTML report

## ⚠️ Limitations

- IPv4 addresses only
- Assumes bidirectional connectivity
- Basic subnet classification (no VLSM support)
- Visualization quality depends on network complexity

## 🤝 Contributing

Feel free to submit issues.


## 🛡️ Disclaimer

This tool is intended for authorized network analysis and penetration testing only. Users are responsible for ensuring they have proper authorization before analyzing any network infrastructure.

---

**Happy Network Mapping! 🕸️ (Made with 💖 and vibe coding) **