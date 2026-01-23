# Library Semantic Contracts

This document describes the fundamental semantic invariants that the 1lab library maintains. These are not Agda code requirements, but conceptual guarantees about how the library's mathematical structures behave.

Understanding these contracts is essential for contributors making changes to foundational modules, as violations can silently break hundreds of downstream modules.

## Contract 1: Category Laws Are Strict

**What it guarantees**: All categories satisfy identity and associativity laws definitionally (as definitional equalities), not merely up to isomorphism.

**Where encoded**: Structural — the `Precategory` record (in `Cat.Base`) requires `idr`, `idl`, and `assoc` fields that are strict equalities.

**What breaks if violated**: If category laws held only up to isomorphism (as in bicategories), then:
- **Cat.Reasoning** (302 dependents): All reasoning combinators like `⟩∘⟨` would fail type-checking because they rely on strict associativity to chain compositions
- **Cat.Functor.Compose**: Functor composition would require explicit coherence data
- Impact: 472 modules depend on `Cat.Prelude`, which re-exports these structures

## Contract 2: Equivalences Are Propositional

**What it guarantees**: The property of being an equivalence is proof-irrelevant — any two proofs that `f : A → B` is an equivalence are equal.

**Where encoded**: Structural — the `is-equiv` type is designed to be contractible, ensuring uniqueness via path types.

**What breaks if violated**: If multiple inequivalent `is-equiv` proofs existed:
- **1Lab.Univalence**: The `ua` function would be non-deterministic — different equivalence proofs would yield different paths
- **1Lab.Equiv**: Transport along equivalences would not be canonical
- Impact: All 126 modules depending on `1Lab.Prelude` would lose type-level computation guarantees

## Contract 3: Path Composition Forms a Groupoid

**What it guarantees**: Paths satisfy groupoid laws: composition is associative (`∙-assoc`), has identity (`∙-idl`, `∙-idr`), and has inverses (`∙-invl`, `∙-invr`).

**Where encoded**: Structural — enforced by cubical type theory primitives in `Prim.Interval`; the interval type has built-in composition operations.

**What breaks if violated**: If path composition were non-associative:
- **All modules using `_≡_`**: Transport along composed paths would be inconsistent: `transport (p ∙ q)` would not equal `transport q ∘ transport p`
- **1Lab.Path**: All path induction principles would become unsound
- Impact: The entire codebase relies on this invariant

## Contract 4: Functors Preserve Structure Strictly

**What it guarantees**: Functors preserve identity (`F(id) ≡ id`) and composition (`F(f ∘ g) ≡ F(f) ∘ F(g)`) as definitional equalities.

**Where encoded**: Explicit — the `Functor` record (in `Cat.Functor.Base`) has `F-id` and `F-∘` fields that are strict equality proofs.

**What breaks if violated**: If functors only preserved structure up to natural isomorphism (lax functors):
- **Cat.Functor.Reasoning** (83 dependents): All natural transformation constructions would require 2-cell coherence data
- **Cat.Instances.Functor**: Functor composition would not be strictly associative
- Impact: The library would need to be restructured as bicategory theory

## Contract 5: Hom-Sets Are Sets

**What it guarantees**: For any category, morphism spaces `Hom(A, B)` are h-level 2 (sets), not higher groupoids — equality of morphisms is propositional.

**Where encoded**: Structural — categories require a `Hom-set : ∀ x y → is-set (Hom x y)` field.

**What breaks if violated**: If Hom-spaces were groupoids with non-trivial 2-cells:
- **Cat.Morphism**: The lemma `is-invertible-is-prop` would become false, allowing multiple competing inverse structures
- **All categorical reasoning**: Would need to track coherence data for morphism equalities
- Impact: All 399 modules in `Cat/` assume proof-irrelevance of morphism equalities

## Contract 6: Displayed Categories Respect Base

**What it guarantees**: In displayed categories, displayed morphisms and their composition synchronize with the base category — if `f' : Hom[f] x' y'` then the displayed structure is over the base morphism `f`.

**Where encoded**: Structural — types enforce this via `PathP`, with displayed laws stated as equalities over base paths.

**What breaks if violated**: If displayed composition could occur over arbitrary base morphisms:
- **Cat.Displayed.Total** (51 dependents): The total category construction (Grothendieck construction) would not yield a valid category
- **Cat.Displayed.Cartesian**: Fibered products and pullbacks would lose their universal properties
- Impact: All 79 modules using displayed categories would produce ill-formed structures

## Contract 7: Adjunctions Satisfy Triangle Identities

**What it guarantees**: For an adjunction `L ⊣ R`, the unit `η` and counit `ε` satisfy zig-zag cancellation: `ε(LX) ∘ L(η(X)) ≡ id` and `R(ε(Y)) ∘ η(R(Y)) ≡ id`.

**Where encoded**: Explicit — the `_⊣_` record (in `Cat.Functor.Adjoint`) has `zig` and `zag` fields.

**What breaks if violated**: If only one triangle identity held:
- **Cat.Functor.Adjoint** (81 dependents): Adjunctions would not be unique up to isomorphism
- **Cat.Diagram.Limit.Base**: Limit constructions via adjoints would lose universal properties
- **Cat.Functor.Kan**: Kan extensions and derived adjunctions would fail to compose correctly
- Impact: All representable functors and adjoint functor theorems would need manual coherence tracking

## Contract 8: H-Levels Form a Hierarchy

**What it guarantees**: H-levels are cumulative: contractible types are propositions, propositions are sets, sets are groupoids, etc. Movement up the hierarchy is automatic.

**Where encoded**: Explicit — defined recursively via `is-hlevel` with closure lemmas in `1Lab.HLevel.Closure`.

**What breaks if violated**: If h-levels were non-cumulative:
- **1Lab.HLevel.Closure** (100+ dependents): Automatic closure under products, functions, and Σ-types would fail
- **All type theory**: Would need explicit coercion functions at every h-level boundary
- Impact: Every use of `is-prop`, `is-set`, etc. assumes this hierarchy

## Why These Contracts Matter

The contracts form a *coherence tower*: foundational contracts (paths, categories) are structurally enforced by the type system, while higher-level contracts (adjunctions, h-levels) are explicitly stated but universally relied upon.

**For maintainers**: These contracts cannot be weakened without breaking hundreds of modules. Changes to hub modules (`Cat.Prelude`, `1Lab.Prelude`, etc.) must preserve these guarantees.

**For contributors**: When modifying core modules, verify that these contracts still hold. See the "Semantic Changes" section in `CONTRIBUTING.md` for a checklist.

## Related Documentation

- **Technical analysis**: See `support/semantic_invariants_analysis.md` for detailed invariant extraction and breaking examples
- **Dependency structure**: Run `python3 support/analyze_dependencies.py` to generate current dependency graphs
- **Module statistics**: See `support/dependency_report.md` for quantitative analysis of the codebase structure
