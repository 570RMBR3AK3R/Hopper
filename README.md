# Hopper

**Network Path Discovery & Visualization Tool**

Hopper is a lightweight Python tool designed for security researchers and penetration testers to map host-to-host communication paths within complex networks. It provides comprehensive network analysis capabilities including path discovery, visualization, and detailed reporting.

## Overview

Given a list of IP addresses and connectivity mappings, Hopper automatically groups hosts by subnet, builds an internal graph of connections, and enables users to:

- **Identify network segment relationships** and inter-network connectivity
- **Find shortest paths** between any two IP addresses using optimized algorithms
- **Export network data** in JSON format for programmatic analysis
- **Generate visualizations** in multiple styles (network, detailed, hierarchical)
- **Create professional HTML reports** with embedded network graphs
- **Organize outputs** in structured project directories

## Key Features

### 🔍 Network Analysis
- **Automated Subnet Grouping**: Intelligently classifies IP addresses by network segments
- **Path Discovery**: Implements BFS algorithm for shortest path calculation
- **Inter-network Mapping**: Identifies connections between different network segments

### 📊 Visualization & Reporting
- **Multiple Output Formats**: JSON, PNG visualizations, and HTML reports
- **Flexible Visualization Styles**: Network-level, detailed, and hierarchical views
- **Professional Reports**: Clean HTML output with embedded network diagrams
- **Color-coded Diagrams**: Clear visual distinction between networks and connections

### ⚙️ Configuration
- **Custom Subnet Masks**: Configurable network classification
- **Project Organization**: User-defined output directories
- **Flexible Input Formats**: Simple text-based configuration files

## Installation

### Prerequisites
```bash
pip install networkx matplotlib ipaddress
```

### Setup
1. Clone or download the Hopper script
2. Install the required dependencies
3. Prepare your input files according to the format specification

## Input Format

### IP Address File (`ips.txt`)
```
192.168.1.10
192.168.1.20
10.0.0.5
10.0.0.15
172.16.1.100
```

### Connectivity File (`edges.txt`)
```
192.168.1.10-192.168.1.20
192.168.1.20-10.0.0.5
10.0.0.5-10.0.0.15
10.0.0.15-172.16.1.100
```

## Usage Examples

### Basic Network Analysis
```bash
python hopper.py ips.txt edges.txt --project my_network_project
```

### Path Discovery
```bash
python hopper.py ips.txt edges.txt --project my_network_project --path 192.168.1.10 172.16.1.100
```

### Comprehensive Analysis
```bash
python hopper.py ips.txt edges.txt --project my_network_project --path 192.168.1.10 10.0.0.5 --export --visualize --report
```

### Custom Configuration
```bash
python hopper.py ips.txt edges.txt --project my_network_project --subnet 255.255.0.0 --vis-style hierarchical
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `ips_file` | File containing IP addresses *(required)* |
| `edges_file` | File containing IP-to-IP connectivity *(required)* |
| `--path SRC DST` | Find shortest path between source and destination IPs |
| `--subnet MASK` | Custom subnet mask *(default: 255.255.255.0)* |
| `--project FOLDER` | Project folder name for output files *(default: hopper_output)* |
| `--export` | Export graph data to JSON format |
| `--visualize` | Generate PNG network visualization |
| `--vis-style STYLE` | Visualization style: `network`, `detailed`, or `hierarchical` *(default: detailed)* |
| `--report` | Create HTML report with embedded graphs |

## Sample Output

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
    "metadata": {
        "subnet_mask": "255.255.255.0",
        "total_networks": 3,
        "total_ips": 5,
        "total_connections": 4,
        "generated_at": "2025-06-28T14:26:00.123456"
    },
    "networks": {
        "192.168.1.0/24": {
            "label": "Network A",
            "ips": ["192.168.1.10", "192.168.1.20"],
            "ip_count": 2,
            "connected_to": ["10.0.0.0/24"]
        }
    },
    "nodes": ["192.168.1.10", "192.168.1.20", "10.0.0.5"],
    "edges": [
        {
            "source": "192.168.1.10",
            "target": "192.168.1.20",
            "source_network": "192.168.1.0/24",
            "target_network": "192.168.1.0/24",
            "is_inter_network": false
        }
    ]
}
```

## Use Cases

### Penetration Testing
- **Lateral Movement Planning**: Map potential attack paths through network infrastructure
- **Network Reconnaissance**: Understand target network topology and segmentation
- **Pivot Point Analysis**: Identify critical nodes for maintaining network access

### Security Research
- **Network Topology Discovery**: Map complex enterprise network architectures
- **Attack Path Analysis**: Analyze potential compromise routes and vulnerabilities
- **Infrastructure Assessment**: Evaluate network segmentation effectiveness

### Network Administration
- **Connectivity Troubleshooting**: Visualize communication paths for diagnostics
- **Network Documentation**: Generate comprehensive topology documentation
- **Segmentation Verification**: Validate network isolation and security boundaries

## Output Files

All output files are organized within the specified project folder:

| File | Description |
|------|-------------|
| `hopper_graph.json` | Complete network data in JSON format |
| `hopper_graph.png` | Primary network visualization |
| `network_view.png` | Network-level topology view |
| `detailed_view.png` | Detailed IP-level visualization |
| `hierarchical_view.png` | Hierarchical network structure |
| `hopper_report.html` | Professional HTML report with all visualizations |

## Limitations

- **IPv4 Support Only**: Currently limited to IPv4 address analysis
- **Bidirectional Connectivity**: Assumes symmetric network connections
- **Basic Subnet Classification**: No Variable Length Subnet Masking (VLSM) support
- **Visualization Complexity**: Performance may vary with very large networks


## Contributing

I welcome contributions to improve Hopper! Please feel free to:
- Submit bug reports and feature requests through GitHub issues
- Propose improvements via pull requests
- Share use cases and feedback

## License & Disclaimer

**⚠️ Important**: This tool is intended for **authorized network analysis and penetration testing only**. Users are responsible for ensuring they have proper authorization before analyzing any network infrastructure.

## Support

For questions, issues, or feature requests, please use the project's issue tracker.

---

*Built with ❤️ and vibe coding for the security research community*