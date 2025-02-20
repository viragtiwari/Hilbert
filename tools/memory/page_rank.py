import json
import networkx as nx
from pathlib import Path
from operator import itemgetter
import re

class CodeDependencyGraphGenerator:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.file_colors = {
            'commandPalette.js': '#FF9999',
            'editor.js': '#99FF99',
            'fileExplorer.js': '#9999FF',
            'menuBar.js': '#FFFF99',
            'terminal.js': '#FF99FF',
            'server.js': '#99FFFF'
        }
        self.pagerank_scores = {}
        
    def parse_json_file(self, json_path):
        """Load and parse the JSON file containing code symbols."""
        with open(json_path, 'r') as f:
            return json.load(f)
            
    def extract_file_name(self, path):
        """Extract the base file name from a path."""
        return Path(path).name

    def extract_symbol_name(self, code_line):
        """Extract symbol name from a code line."""
        patterns = [
            (r'class\s+(\w+)', 'class'),
            (r'function\s+(\w+)', 'method'),
            (r'def\s+(\w+)', 'method'),
            (r'(\w+)\s*\([^)]*\)\s*{', 'method'),
            (r'(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', 'method'),
            (r'type\s+(\w+)', 'class'),
            (r'interface\s+(\w+)', 'class'),
            (r'struct\s+(\w+)', 'class'),
        ]
        
        for pattern, symbol_type in patterns:
            match = re.search(pattern, code_line)
            if match:
                name = match.group(1)
                if 'constructor' in code_line:
                    name = 'constructor'
                elif 'async' in code_line:
                    name = name.split()[-1]
                return name, symbol_type
        
        return code_line.split('(')[0].strip(), 'method'
        
    def add_nodes_from_data(self, data):
        """Add nodes to the graph from the parsed data."""
        for file_path, file_data in data.items():
            file_name = self.extract_file_name(file_path)
            color = self.file_colors.get(file_name, '#CCCCCC')
            
            for symbol in file_data['symbols']:
                symbol_name, symbol_type = self.extract_symbol_name(symbol)
                node_id = f"{file_name}:{symbol_name}"
                
                self.graph.add_node(node_id, 
                                  color=color, 
                                  type=symbol_type,
                                  file=file_name)
                
    def add_edges_from_code_analysis(self, data):
        """Add edges based on method calls and relationships."""
        for file_path, file_data in data.items():
            file_name = self.extract_file_name(file_path)
            
            for symbol in file_data['symbols']:
                source_name, _ = self.extract_symbol_name(symbol)
                source_node = f"{file_name}:{source_name}"
                
                for other_file, other_data in data.items():
                    other_file_name = self.extract_file_name(other_file)
                    
                    for other_symbol in other_data['symbols']:
                        other_name, _ = self.extract_symbol_name(other_symbol)
                        
                        if other_name in symbol and other_name != source_name:
                            target_node = f"{other_file_name}:{other_name}"
                            if source_node != target_node and source_node in self.graph and target_node in self.graph:
                                self.graph.add_edge(source_node, target_node)

    def calculate_pagerank(self):
        """Calculate PageRank scores for all nodes."""
        self.pagerank_scores = nx.pagerank(self.graph)
        
    def generate_concise_json(self, original_data, output_dir, top_percentage=30):
        """Generate a new JSON containing only the most important functions based on PageRank."""
        sorted_nodes = sorted(self.pagerank_scores.items(), key=itemgetter(1), reverse=True)
        
        num_nodes = len(sorted_nodes)
        top_nodes = sorted_nodes[:int(num_nodes * top_percentage / 100)]
        
        concise_data = {}
        
        for node, score in top_nodes:
            file_name, symbol_name = node.split(':')
            
            original_file_path = None
            for path in original_data.keys():
                if Path(path).name == file_name:
                    original_file_path = path
                    break
                    
            if original_file_path:
                if original_file_path not in concise_data:
                    concise_data[original_file_path] = {
                        "path": original_file_path,
                        "symbols": [],
                        "pagerank_score": score
                    }
                
                for symbol in original_data[original_file_path]["symbols"]:
                    symbol_found_name, _ = self.extract_symbol_name(symbol)
                    if symbol_found_name == symbol_name:
                        concise_data[original_file_path]["symbols"].append({
                            "code": symbol,
                            "pagerank_score": score
                        })
                        break
        
        # Save the concise JSON in the input directory
        output_path = Path(output_dir) / 'concise.json'
        with open(output_path, 'w') as f:
            json.dump(concise_data, f, separators=(',', ':'))
            
        return concise_data
    
    def generate_graph(self, json_path):
        """Generate the dependency graph and analyze it."""
        data = self.parse_json_file(json_path)
        input_dir = str(Path(json_path).parent)
        
        self.add_nodes_from_data(data)
        self.add_edges_from_code_analysis(data)
        
        self.calculate_pagerank()
        
        self.generate_concise_json(data, input_dir)
        
        print("\nGraph Statistics:")
        print(f"Number of nodes: {self.graph.number_of_nodes()}")
        print(f"Number of edges: {self.graph.number_of_edges()}")
        print(f"Number of connected components: {nx.number_connected_components(self.graph.to_undirected())}")
        
        print("\nTop 10 Most Important Functions (by PageRank):")
        top_functions = sorted(self.pagerank_scores.items(), key=itemgetter(1), reverse=True)[:10]
        for node, score in top_functions:
            print(f"{node}: {score:.3f}")
"""Usage Example:
generator = CodeDependencyGraphGenerator()
generator.generate_graph("D:/experiment_lagrange/OpenHands/.codemap/repo_map.json")
"""