# Semantic Dependency Analysis for 1lab

## Motivation

The 1lab codebase has grown to over 700 Agda modules with complex interdependencies. Changes to foundational modules (like `Cat.Prelude` with 472 dependents) can silently break hundreds of downstream modules if semantic invariants are violated. Currently, there is no documentation of what these invariants are or tooling to understand the dependency structure.

This PR adds dependency analysis tooling and documentation to make the library's semantic contracts explicit, helping maintainers and contributors understand:
- Which modules are foundational vs derived
- What invariants must be preserved
- How changes propagate through the dependency graph

## What Changed

### Documentation
1. **`docs/SEMANTIC_CONTRACTS.md`** (new): Documents 8 fundamental semantic contracts that the library maintains, including:
   - What each contract guarantees
   - Where it's encoded (structural vs explicit)
   - Concrete examples of what breaks if violated
   - Examples: category laws must be strict, equivalences are propositional, functors preserve structure strictly

2. **`README.md`** (modified): Added "Semantic Contracts" section (6 sentences) explaining why these invariants matter and linking to the detailed documentation

3. **`CONTRIBUTING.md`** (modified): Added "Semantic Changes" section with a 7-item checklist for contributors modifying foundational modules

### Tooling
4. **`support/analyze_dependencies.py`** (new): Python script that analyzes all Agda modules and generates:
   - Dependency report with statistics
   - DOT graph visualization
   - Identifies foundational modules, hubs, and dependency chains

5. **`.github/workflows/dependency-analysis.yml`** (new): Lightweight CI check that runs on PRs touching Agda files. Validates:
   - Module count > 0 (parser didn't fail)
   - Report and graph files are generated
   - DOT file is well-formed
   - Does NOT enforce exact module counts to avoid brittleness

### Supporting Files
6. **`support/semantic_invariants_analysis.md`** (new): Technical deep-dive with detailed invariant extraction for top 10 hub modules
7. **`support/dependency_report.md`** (generated): Generated statistics (716 modules, hub rankings, etc.)
8. **`support/dependency_graph.dot`** (generated): Visualization of 100 key modules

## Why It's Safe

### No Code Changes
- Zero changes to Agda source files
- Only adds documentation and optional tooling
- CI workflow is opt-in (only runs on PRs touching `.agda`/`.lagda.md` files)

### Conservative CI Checks
- Does NOT fail on module count changes (allows natural growth/refactoring)
- Only checks for catastrophic failures (parser errors, missing outputs)
- Uses standard GitHub Actions + Python 3 (no exotic dependencies)
- Uploads analysis artifacts for inspection even on failure

### Incremental Value
- Documentation provides immediate value without requiring tooling
- Tooling can be run manually (`python3 support/analyze_dependencies.py`)
- CI integration is helpful but not mandatory
- All generated files are in `support/` (easy to ignore/remove)

## How to Use

### For Contributors
- Read `docs/SEMANTIC_CONTRACTS.md` before modifying foundational modules
- Use the "Semantic Changes" checklist in `CONTRIBUTING.md`
- Run `python3 support/analyze_dependencies.py` to see your module's impact

### For Maintainers
- Reference semantic contracts when reviewing PRs that touch hub modules
- Use dependency graphs to understand refactoring impact
- CI will catch if dependency analysis tooling breaks

### For Researchers
- Analyze the codebase structure with generated reports
- Visualize module relationships with DOT graphs
- Study semantic invariants as formalization patterns

## Testing Done

- Verified analyzer runs successfully on current codebase (716 modules)
- Checked all generated files are well-formed (Markdown, DOT)
- Validated CI workflow syntax (GitHub Actions YAML)
- Confirmed no Agda source files were modified
- Reviewed documentation for technical accuracy and clarity

## Related Discussion

This work originated from analyzing the dependency structure to understand which modules are truly foundational vs derived, and what assumptions downstream code makes. The semantic contracts document distills 365 lines of technical analysis into 8 maintainer-friendly contracts with concrete breaking examples.
