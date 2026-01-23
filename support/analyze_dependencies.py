#!/usr/bin/env python3
"""
Agda Module Dependency Analyzer

This script analyzes the semantic dependencies between Agda modules in the 1lab repository.
It identifies:
- Foundational definitions (modules at the base of the dependency tree)
- Hub concepts (modules referenced by many others)
- Long dependency chains vs shallow ones
- Outputs both a DOT graph and a Markdown report
"""

import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, Set, List, Tuple
import argparse


class AgdaModule:
    """Represents an Agda module with its dependencies."""
    
    def __init__(self, name: str, filepath: str):
        self.name = name
        self.filepath = filepath
        self.imports: Set[str] = set()
        self.public_imports: Set[str] = set()
        self.is_literate = filepath.endswith('.lagda.md')
        
    def __repr__(self):
        return f"AgdaModule({self.name})"


class DependencyAnalyzer:
    """Analyzes dependencies between Agda modules."""
    
    def __init__(self, src_dir: str):
        self.src_dir = Path(src_dir)
        self.modules: Dict[str, AgdaModule] = {}
        self.reverse_deps: Dict[str, Set[str]] = defaultdict(set)
        
    def scan_modules(self):
        """Scan all Agda files in the source directory."""
        print(f"Scanning Agda modules in {self.src_dir}...")
        
        # Find all .agda and .lagda.md files
        agda_files = []
        for pattern in ['**/*.agda', '**/*.lagda.md']:
            agda_files.extend(self.src_dir.glob(pattern))
        
        print(f"Found {len(agda_files)} Agda files")
        
        for filepath in agda_files:
            module_name = self._filepath_to_module_name(filepath)
            if module_name:
                module = AgdaModule(module_name, str(filepath))
                self._parse_imports(module, filepath)
                self.modules[module_name] = module
        
        # Build reverse dependency graph
        for module_name, module in self.modules.items():
            for imported in module.imports:
                self.reverse_deps[imported].add(module_name)
        
        print(f"Parsed {len(self.modules)} modules")
    
    def _filepath_to_module_name(self, filepath: Path) -> str:
        """Convert a filepath to an Agda module name."""
        try:
            rel_path = filepath.relative_to(self.src_dir)
            # Remove .agda or .lagda.md extension
            name = str(rel_path)
            if name.endswith('.lagda.md'):
                name = name[:-9]
            elif name.endswith('.agda'):
                name = name[:-5]
            # Replace path separators with dots
            return name.replace(os.sep, '.')
        except ValueError:
            return ""
    
    def _parse_imports(self, module: AgdaModule, filepath: Path):
        """Parse import statements from an Agda file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle literate Agda files - extract code blocks
            if module.is_literate:
                content = self._extract_code_blocks(content)
            
            # Match import statements
            # Pattern: "open import ModuleName" or "import ModuleName"
            import_pattern = r'^\s*(?:open\s+)?import\s+([\w.]+)(?:\s+.*)?$'
            public_pattern = r'\bpublic\b'
            
            for line in content.split('\n'):
                # Skip comments
                if line.strip().startswith('--'):
                    continue
                
                match = re.match(import_pattern, line)
                if match:
                    imported_module = match.group(1)
                    module.imports.add(imported_module)
                    
                    # Check if it's a public import
                    if re.search(public_pattern, line):
                        module.public_imports.add(imported_module)
        
        except Exception as e:
            print(f"Error parsing {filepath}: {e}", file=sys.stderr)
    
    def _extract_code_blocks(self, content: str) -> str:
        """Extract code blocks from literate Agda markdown."""
        # Extract ```agda code blocks and <!-- ```agda --> blocks
        code_blocks = []
        
        # Pattern 1: ```agda ... ``` blocks
        agda_blocks = re.findall(r'```agda\n(.*?)```', content, re.DOTALL)
        code_blocks.extend(agda_blocks)
        
        # Pattern 2: <!-- ```agda ... ``` --> blocks (hidden imports)
        hidden_blocks = re.findall(r'<!--\s*```agda\n(.*?)```\s*-->', content, re.DOTALL)
        code_blocks.extend(hidden_blocks)
        
        return '\n'.join(code_blocks)
    
    def find_foundational_modules(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Find foundational modules (those with few or no dependencies)."""
        modules_by_import_count = []
        
        for name, module in self.modules.items():
            # Count only imports that are in our module set
            internal_imports = len([imp for imp in module.imports if imp in self.modules])
            modules_by_import_count.append((name, internal_imports))
        
        # Sort by import count (ascending)
        modules_by_import_count.sort(key=lambda x: x[1])
        return modules_by_import_count[:limit]
    
    def find_hub_modules(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Find hub modules (those imported by many others)."""
        modules_by_dependent_count = []
        
        for name in self.modules:
            dependent_count = len(self.reverse_deps.get(name, set()))
            modules_by_dependent_count.append((name, dependent_count))
        
        # Sort by dependent count (descending)
        modules_by_dependent_count.sort(key=lambda x: x[1], reverse=True)
        return modules_by_dependent_count[:limit]
    
    def calculate_dependency_chains(self) -> Dict[str, int]:
        """Calculate the maximum dependency chain length for each module."""
        # Use topological sort with dynamic programming
        chain_lengths = {}
        visited = set()
        
        def dfs(module_name: str, path: Set[str]) -> int:
            if module_name in chain_lengths:
                return chain_lengths[module_name]
            
            if module_name not in self.modules:
                return 0
            
            # Detect cycles
            if module_name in path:
                return 0
            
            module = self.modules[module_name]
            path.add(module_name)
            
            max_depth = 0
            for imported in module.imports:
                if imported in self.modules:
                    depth = dfs(imported, path)
                    max_depth = max(max_depth, depth + 1)
            
            path.remove(module_name)
            chain_lengths[module_name] = max_depth
            return max_depth
        
        for module_name in self.modules:
            if module_name not in chain_lengths:
                dfs(module_name, set())
        
        return chain_lengths
    
    def analyze_dependency_patterns(self) -> Dict[str, any]:
        """Analyze overall dependency patterns."""
        chain_lengths = self.calculate_dependency_chains()
        
        # Categorize modules by depth
        shallow = []  # depth 0-5
        medium = []   # depth 6-15
        deep = []     # depth 16+
        
        for module_name, depth in chain_lengths.items():
            if depth <= 5:
                shallow.append((module_name, depth))
            elif depth <= 15:
                medium.append((module_name, depth))
            else:
                deep.append((module_name, depth))
        
        return {
            'chain_lengths': chain_lengths,
            'shallow': sorted(shallow, key=lambda x: x[1]),
            'medium': sorted(medium, key=lambda x: x[1]),
            'deep': sorted(deep, key=lambda x: x[1], reverse=True),
            'max_depth': max(chain_lengths.values()) if chain_lengths else 0,
            'avg_depth': sum(chain_lengths.values()) / len(chain_lengths) if chain_lengths else 0
        }
    
    def generate_markdown_report(self, output_file: str):
        """Generate a markdown report of the dependency analysis."""
        foundational = self.find_foundational_modules(20)
        hubs = self.find_hub_modules(20)
        patterns = self.analyze_dependency_patterns()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Agda Module Dependency Analysis Report\n\n")
            f.write(f"**Generated for:** 1lab repository\n\n")
            f.write(f"**Total modules analyzed:** {len(self.modules)}\n\n")
            
            # Overview statistics
            f.write("## Overview Statistics\n\n")
            f.write(f"- **Maximum dependency depth:** {patterns['max_depth']}\n")
            f.write(f"- **Average dependency depth:** {patterns['avg_depth']:.2f}\n")
            f.write(f"- **Shallow modules (depth 0-5):** {len(patterns['shallow'])}\n")
            f.write(f"- **Medium modules (depth 6-15):** {len(patterns['medium'])}\n")
            f.write(f"- **Deep modules (depth 16+):** {len(patterns['deep'])}\n\n")
            
            # Foundational modules
            f.write("## Foundational Modules\n\n")
            f.write("These modules have the fewest dependencies and form the foundation of the library:\n\n")
            f.write("| Module | Import Count |\n")
            f.write("|--------|-------------|\n")
            for name, count in foundational:
                f.write(f"| `{name}` | {count} |\n")
            f.write("\n")
            
            # Hub modules
            f.write("## Hub Modules\n\n")
            f.write("These modules are imported by many others and serve as central concepts:\n\n")
            f.write("| Module | Dependent Count |\n")
            f.write("|--------|----------------|\n")
            for name, count in hubs:
                f.write(f"| `{name}` | {count} |\n")
            f.write("\n")
            
            # Deep dependency chains
            f.write("## Deep Dependency Chains\n\n")
            f.write("Modules with the longest dependency chains:\n\n")
            f.write("| Module | Chain Depth |\n")
            f.write("|--------|------------|\n")
            for name, depth in patterns['deep'][:20]:
                f.write(f"| `{name}` | {depth} |\n")
            f.write("\n")
            
            # Module categories
            f.write("## Module Organization\n\n")
            
            categories = defaultdict(int)
            for module_name in self.modules:
                # Get top-level category
                parts = module_name.split('.')
                if len(parts) > 0:
                    categories[parts[0]] += 1
            
            f.write("Module distribution by top-level category:\n\n")
            f.write("| Category | Count |\n")
            f.write("|----------|-------|\n")
            for category in sorted(categories.keys()):
                f.write(f"| `{category}/` | {categories[category]} |\n")
        
        print(f"Markdown report generated: {output_file}")
    
    def generate_dot_graph(self, output_file: str, max_nodes: int = 100):
        """Generate a DOT graph visualization of dependencies."""
        # Select most important modules for visualization
        hubs = self.find_hub_modules(max_nodes // 2)
        foundational = self.find_foundational_modules(max_nodes // 4)
        patterns = self.analyze_dependency_patterns()
        deep = patterns['deep'][:max_nodes // 4]
        
        # Combine and deduplicate
        important_modules = set()
        for name, _ in hubs:
            important_modules.add(name)
        for name, _ in foundational:
            important_modules.add(name)
        for name, _ in deep:
            important_modules.add(name)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("digraph AgdaDependencies {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box, style=rounded];\n")
            f.write("  overlap=false;\n")
            f.write("  splines=true;\n\n")
            
            # Color nodes by category
            category_colors = {
                '1Lab': '#e8f4f8',
                'Prim': '#f0e8f8',
                'Cat': '#f8f0e8',
                'Algebra': '#e8f8f0',
                'Data': '#f8e8f0',
                'Order': '#f0f8e8',
                'Homotopy': '#f8f8e8',
            }
            
            chain_lengths = patterns['chain_lengths']
            
            for module_name in important_modules:
                if module_name not in self.modules:
                    continue
                
                # Determine category and color
                category = module_name.split('.')[0]
                color = category_colors.get(category, '#ffffff')
                
                # Determine if foundational/hub
                is_foundational = module_name in [n for n, _ in foundational[:10]]
                is_hub = module_name in [n for n, _ in hubs[:10]]
                
                # Style based on importance
                if is_foundational:
                    style = 'filled,bold'
                elif is_hub:
                    style = 'filled,bold'
                else:
                    style = 'filled'
                
                # Simplify label for readability
                label = module_name.split('.')[-1] if '.' in module_name else module_name
                depth = chain_lengths.get(module_name, 0)
                
                f.write(f'  "{module_name}" [label="{label}\\n(d:{depth})", ')
                f.write(f'fillcolor="{color}", style="{style}"];\n')
            
            f.write("\n")
            
            # Add edges
            for module_name in important_modules:
                if module_name not in self.modules:
                    continue
                
                module = self.modules[module_name]
                for imported in module.imports:
                    if imported in important_modules:
                        # Make public imports bold
                        if imported in module.public_imports:
                            f.write(f'  "{module_name}" -> "{imported}" [style=bold];\n')
                        else:
                            f.write(f'  "{module_name}" -> "{imported}";\n')
            
            # Add legend
            f.write("\n  // Legend\n")
            f.write('  subgraph cluster_legend {\n')
            f.write('    label="Legend";\n')
            f.write('    style=filled;\n')
            f.write('    color=lightgrey;\n')
            f.write('    "Foundational\\nModule" [style=filled,fillcolor="#e8f4f8",shape=box];\n')
            f.write('    "Hub\\nModule" [style=filled,fillcolor="#f8e8f0",shape=box];\n')
            f.write('  }\n')
            
            f.write("}\n")
        
        print(f"DOT graph generated: {output_file}")
        print(f"To render: dot -Tpng {output_file} -o dependency_graph.png")
        print(f"Or: dot -Tsvg {output_file} -o dependency_graph.svg")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze semantic dependencies in Agda modules"
    )
    parser.add_argument(
        '--src-dir',
        default='src',
        help='Source directory containing Agda modules (default: src)'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for reports (default: current directory)'
    )
    parser.add_argument(
        '--max-graph-nodes',
        type=int,
        default=100,
        help='Maximum number of nodes in DOT graph (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = DependencyAnalyzer(args.src_dir)
    
    # Scan modules
    analyzer.scan_modules()
    
    # Generate reports
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    md_report = output_dir / 'dependency_report.md'
    dot_graph = output_dir / 'dependency_graph.dot'
    
    analyzer.generate_markdown_report(str(md_report))
    analyzer.generate_dot_graph(str(dot_graph), args.max_graph_nodes)
    
    print("\n✓ Analysis complete!")
    print(f"  - Report: {md_report}")
    print(f"  - Graph: {dot_graph}")


if __name__ == '__main__':
    main()
