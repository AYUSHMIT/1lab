# Agda Module Dependency Analysis

This directory contains a tool for analyzing semantic dependencies between Agda modules in the 1lab repository.

## Tool: `analyze_dependencies.py`

A Python script that traverses all Agda modules and produces a comprehensive semantic dependency map.

### Features

The analyzer identifies:

1. **Foundational Definitions**: Modules with the fewest dependencies that form the base of the library
2. **Hub Concepts**: Modules that are imported by many others and serve as central concepts
3. **Dependency Chain Lengths**: How deep the dependency tree is for each module
4. **Shallow vs Deep Dependencies**: Categorizes modules by their dependency depth

### Output

The tool generates two main outputs:

1. **Markdown Report** (`dependency_report.md`): A comprehensive analysis including:
   - Overview statistics (total modules, max/average depth)
   - Top 20 foundational modules (fewest dependencies)
   - Top 20 hub modules (most dependents)
   - Deep dependency chain analysis
   - Module organization by category

2. **DOT Graph** (`dependency_graph.dot`): A visual graph showing:
   - Most important modules (hubs, foundational, and deep modules)
   - Import relationships between modules
   - Public imports (shown in bold)
   - Modules colored by top-level category
   - Dependency depth for each module

### Usage

```bash
# Basic usage - analyzes src/ directory
python3 support/analyze_dependencies.py

# Specify custom directories
python3 support/analyze_dependencies.py \
  --src-dir /path/to/agda/sources \
  --output-dir /path/to/output

# Adjust graph complexity
python3 support/analyze_dependencies.py --max-graph-nodes 150
```

### Options

- `--src-dir`: Source directory containing Agda modules (default: `src`)
- `--output-dir`: Output directory for reports (default: current directory)
- `--max-graph-nodes`: Maximum number of nodes in DOT graph (default: 100)

### Rendering the Graph

The DOT graph can be rendered using Graphviz:

```bash
# PNG format
dot -Tpng dependency_graph.dot -o dependency_graph.png

# SVG format (recommended for large graphs)
dot -Tsvg dependency_graph.dot -o dependency_graph.svg

# PDF format
dot -Tpdf dependency_graph.dot -o dependency_graph.pdf
```

### How It Works

1. **Module Discovery**: Scans for all `.agda` and `.lagda.md` files
2. **Import Parsing**: Extracts import statements from both:
   - Regular code in `.agda` files
   - Code blocks in literate `.lagda.md` files (including hidden imports in HTML comments)
3. **Dependency Analysis**:
   - Builds forward dependency graph (imports)
   - Builds reverse dependency graph (dependents)
   - Calculates dependency chain depths using DFS
4. **Report Generation**: Produces statistics and visualizations

### Focus on Semantic Dependencies

The analyzer focuses on **meaning-level dependencies** by:

- Tracking which modules import which other modules
- Distinguishing between regular and public imports (re-exports)
- Calculating transitive dependency depths
- Identifying which concepts are most foundational vs most derived
- Ignoring external libraries (only analyzing modules within the repository)

### Example Insights

From analyzing the 1lab repository, the tool reveals:

**Foundational Modules** (depth 0-5):
- `Prim.Type` - The most primitive module with 0 imports
- `Meta.*` modules - Metaprogramming utilities with minimal dependencies
- `Cat.Strict`, `Cat.Groupoid` - Basic categorical structures

**Hub Modules** (most dependents):
- `Cat.Prelude` - Imported by 472 modules
- `Cat.Reasoning` - Imported by 302 modules
- `1Lab.Prelude` - Imported by 126 modules

**Deep Modules** (depth 80+):
- `Elephant` - 84 levels deep
- `Cat.Instances.Sheaves` - 83 levels deep
- Advanced topos theory and sheaf constructions

### Requirements

- Python 3.6 or later (no external dependencies)
- Optional: Graphviz for rendering DOT graphs

### Notes

- The analyzer handles both regular `.agda` files and literate `.lagda.md` files
- It extracts code from markdown code blocks (both visible and HTML-commented)
- Cycle detection prevents infinite loops in dependency calculations
- The graph visualization selects the most "important" modules to avoid clutter
