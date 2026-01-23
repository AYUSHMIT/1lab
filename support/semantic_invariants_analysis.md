# Semantic Invariants Analysis: Hub Modules

This document analyzes the implicit invariants and semantic assumptions relied upon by downstream modules in the 1lab repository. Based on the dependency analysis, we focus on the top 10 most-imported modules and extract their critical invariants.

## Methodology

For each hub module, we identify:
1. **Implicit invariants** - What must remain true for the ecosystem to function
2. **Encoding method** - Whether explicitly stated as lemmas, structurally encoded in types, or merely conventional
3. **Breaking examples** - Downstream modules that would silently fail if invariants were weakened

This analysis focuses on semantic properties, not definitional content.

---

## 1. Cat.Prelude (472 dependents)

**Hub Status**: Imported by 66% of the codebase; central prelude for category theory

### Semantic Invariants

#### Invariant 1.1: Category Laws Coherence
- **Property**: Identity and associativity laws (`idr`, `idl`, `assoc`) must hold definitionally for base composition
- **Encoding**: Explicit - required fields in `Precategory` record (from Cat.Base)
- **Rationale**: 472 dependents assume these without re-checking; composition chains collapse without them

**Breaking Example**: If `assoc` were weakened to hold only up to isomorphism:
- **Downstream impact**: `Cat.Functor.Compose` would need explicit coherence data for triple compositions
- **Silent failures**: All `_⟩∘⟨_` reasoning combinators would produce incorrect associativity brackets
- **Affected modules**: Every module using `Cat.Reasoning` (302 modules) would fail to type-check

#### Invariant 1.2: Hom-Set Property
- **Property**: Morphism spaces are sets (h-level 2), not higher groupoids
- **Encoding**: Structural - `Hom-set` field requires `is-set (Hom x y)`
- **Rationale**: Enables proof-irrelevance for morphism equality proofs

**Breaking Example**: If Hom-sets were groupoids:
- **Downstream impact**: `Cat.Morphism` invertibility would need 2-cells for coherence
- **Silent failures**: `is-invertible-is-prop` lemma becomes false; multiple inverse structures possible
- **Affected modules**: 399 Cat/* modules rely on morphism uniqueness

---

## 2. Cat.Reasoning (302 dependents)

**Hub Status**: Provides reasoning combinators; core infrastructure for equational proofs

### Semantic Invariants

#### Invariant 2.1: Reassociation Coherence
- **Property**: `reassocl`/`reassocr` provide equivalences between path spaces via `∙-pre-equiv`/`∙-post-equiv`
- **Encoding**: Structural - derived from path groupoid structure + category laws
- **Rationale**: Allows rewriting composition chains without explicit `ap` applications

**Breaking Example**: If reassociation were only surjective (not invertible):
- **Downstream impact**: Could enter "one-way" reasoning states; unable to undo associativity changes
- **Silent failures**: Proofs using `⟩∘⟨` chains would lose reversibility
- **Affected modules**: All 302 dependents would need explicit path manipulations

#### Invariant 2.2: Identity Elimination Canonicity
- **Property**: `eliml`/`elimr` work definitionally when `f ≡ id` is provided
- **Encoding**: Structural - relies on `idr`/`idl` being strict equalities
- **Rationale**: Enables tactic-style automated rewriting

**Breaking Example**: If identity laws held only propositionally:
- **Downstream impact**: Would need explicit transport steps in every identity-involving equation
- **Silent failures**: All diagram chasing would require manual identity management
- **Affected modules**: `Cat.Diagram.*` (100+ modules) would become verbose

---

## 3. 1Lab.Prelude (126 dependents)

**Hub Status**: Foundation for HoTT reasoning; universal prelude

### Semantic Invariants

#### Invariant 3.1: Path Groupoid Structure
- **Property**: Paths form a groupoid with associativity (`∙-assoc`), identity (`∙-idl`, `∙-idr`), inverse (`∙-invl`, `∙-invr`)
- **Encoding**: Structural - enforced by cubical type theory primitives (`Prim.Interval`)
- **Rationale**: All equational reasoning assumes path algebra coherence

**Breaking Example**: If path composition were non-associative:
- **Downstream impact**: Transport along composed paths would be inconsistent: `transport (p ∙ q)` ≠ `transport q ∘ transport p`
- **Silent failures**: All uses of `subst`, `coe`, `transp` would produce incorrect results
- **Affected modules**: Entire codebase (every module using `_≡_`)

#### Invariant 3.2: Univalence Coherence
- **Property**: `ua : A ≃ B → A ≡ B` and `transport (ua f) ≡ f` (uaβ rule)
- **Encoding**: Explicit - `ua` is a postulated primitive with computational rule
- **Rationale**: Type equivalences are treated as type equalities; enables structure transport

**Breaking Example**: If `ua` were not strictly inverse to `path→equiv`:
- **Downstream impact**: Type-level computations would diverge from term-level equivalences
- **Silent failures**: `Iso→Path` and `Path→Iso` would not roundtrip
- **Affected modules**: All 126 dependents using type families would lose canonicity

#### Invariant 3.3: H-Level Stability
- **Property**: H-levels are cumulative: `is-contr → is-prop → is-set → ...`
- **Encoding**: Explicit - defined recursively in `is-hlevel` with closure lemmas
- **Rationale**: Allows level coercion without explicit proofs

**Breaking Example**: If h-levels were non-cumulative:
- **Downstream impact**: Would need explicit coercion functions at every level boundary
- **Silent failures**: Automatic closure under products/functions would fail
- **Affected modules**: `1Lab.HLevel.Closure` dependents (100+ modules)

---

## 4. 1Lab.Type (100 dependents)

**Hub Status**: Defines universe hierarchy and polymorphism

### Semantic Invariants

#### Invariant 4.1: Universe Cumulativity
- **Property**: `Type ℓ : Type (lsuc ℓ)` with `Lift` allowing explicit level raising
- **Encoding**: Structural - built into Agda's universe hierarchy
- **Rationale**: Prevents Russell's paradox while allowing polymorphism

**Breaking Example**: If universes were non-cumulative (à la intensional type theory):
- **Downstream impact**: All polymorphic definitions would need explicit level parameters
- **Silent failures**: Cannot form types like `Type ℓ → Type ℓ`
- **Affected modules**: All 100 dependents would need `Lift` everywhere

#### Invariant 4.2: Level Arithmetic Associativity
- **Property**: `(ℓ ⊔ ℓ') ⊔ ℓ'' ≡ ℓ ⊔ (ℓ' ⊔ ℓ'')` (max is associative)
- **Encoding**: Structural - enforced by `Level` primitive
- **Rationale**: Enables level inference without ambiguity

**Breaking Example**: If max were non-associative:
- **Downstream impact**: Type inference would be order-dependent
- **Silent failures**: Proofs would depend on level parenthesization
- **Affected modules**: All dependents would have non-canonical level assignments

---

## 5. Cat.Functor.Reasoning (83 dependents)

**Hub Status**: Provides functor equation combinators

### Semantic Invariants

#### Invariant 5.1: Functor Homomorphism
- **Property**: `F-id : F(id) ≡ id` and `F-∘ : F(f ∘ g) ≡ F(f) ∘ F(g)`
- **Encoding**: Explicit - required fields in `Functor` record
- **Rationale**: Ensures functors preserve categorical structure

**Breaking Example**: If functors only preserved identity/composition up to isomorphism (lax functors):
- **Downstream impact**: All natural transformations would need coherence 2-cells
- **Silent failures**: Functor composition would not be strictly associative
- **Affected modules**: All 83 dependents would become bicategorical

---

## 6. 1Lab.Path (81 dependents)

**Hub Status**: Core path type infrastructure

### Semantic Invariants

#### Invariant 6.1: Path Induction Principle
- **Property**: `J : (P : (y : A) → x ≡ y → Type) → P x refl → (y : A) (p : x ≡ y) → P y p`
- **Encoding**: Structural - derived from cubical interval elimination
- **Rationale**: Fundamental elimination principle for paths

**Breaking Example**: If J were not definitionally satisfied:
- **Downstream impact**: All inductive proofs on paths would fail
- **Silent failures**: Transport would not compute on `refl`
- **Affected modules**: All 81 dependents would need explicit case analysis

#### Invariant 6.2: Symmetry Involution
- **Property**: `sym (sym p) ≡ p` (not just propositional, but definitional)
- **Encoding**: Structural - enforced by cubical symmetry operator
- **Rationale**: Enables bidirectional reasoning

**Breaking Example**: If symmetry were only propositionally involutive:
- **Downstream impact**: Double-symmetry would not compute away
- **Silent failures**: Proofs using `sym` repeatedly would accumulate symmetry terms
- **Affected modules**: All path-heavy modules (e.g., `1Lab.Path.Groupoid`)

---

## 7. Cat.Functor.Adjoint (81 dependents)

**Hub Status**: Defines adjunctions and their properties

### Semantic Invariants

#### Invariant 7.1: Zig-Zag Identities
- **Property**: `ε(L(A)) ∘ L(η(A)) ≡ id` and `R(ε(B)) ∘ η(R(B)) ≡ id`
- **Encoding**: Explicit - `zig` and `zag` fields in `_⊣_` record
- **Rationale**: Characterizes adjunction uniquely

**Breaking Example**: If only one triangle identity held:
- **Downstream impact**: Adjunctions would not be unique up to isomorphism
- **Silent failures**: Limit constructions would lose universal properties
- **Affected modules**: 81 dependents including Kan extensions, (co)limits

#### Invariant 7.2: Naturality of Unit/Counit
- **Property**: `η` and `ε` are natural transformations (not just collections of morphisms)
- **Encoding**: Structural - defined via `_=>_` natural transformation type
- **Rationale**: Ensures adjunction commutes with functoriality

**Breaking Example**: If unit/counit were not natural:
- **Downstream impact**: Adjunction wouldn't lift to functor categories
- **Silent failures**: All derived adjoints (via Kan extensions) would fail
- **Affected modules**: Monad constructions, reflective subcategories

---

## 8. Cat.Displayed.Base (79 dependents)

**Hub Status**: Infrastructure for displayed/fibered categories

### Semantic Invariants

#### Invariant 8.1: Displayed Composition Over Base
- **Property**: If `f' : Hom[f] x' y'` and `g' : Hom[g] y' z'`, then `f' ∘' g' : Hom[f ∘ g] x' z'`
- **Encoding**: Structural - types enforce base composition synchronization
- **Rationale**: Displayed categories are fibered over base

**Breaking Example**: If displayed composition could be over any base morphism:
- **Downstream impact**: Total categories would not be categories
- **Silent failures**: Projections to base would not be functorial
- **Affected modules**: All 79 displayed category constructions

#### Invariant 8.2: Displayed Laws Over Base Laws
- **Property**: `id' ∘' f' ≡[idl] f'` (equality over base identity law)
- **Encoding**: Structural - uses `PathP` to state equality over paths
- **Rationale**: Ensures vertical structure respects base structure

**Breaking Example**: If displayed laws were independent of base laws:
- **Downstream impact**: Grothendieck construction would not preserve composition
- **Silent failures**: Fibered products would lose universality
- **Affected modules**: All displayed limit constructions

---

## 9. Cat.Instances.Functor (72 dependents)

**Hub Status**: Functor categories and natural transformations

### Semantic Invariants

#### Invariant 9.1: Vertical Composition of Natural Transformations
- **Property**: If `α : F => G` and `β : G => H`, then `β ∘nt α : F => H` with componentwise composition
- **Encoding**: Explicit - defined via `_∘nt_` with naturality proofs
- **Rationale**: Natural transformations form 2-cells in Cat

**Breaking Example**: If vertical composition were not associative:
- **Downstream impact**: Functor categories would not be categories
- **Silent failures**: All higher categorical constructions fail
- **Affected modules**: All 72 dependents including 2-categories, bicategories

#### Invariant 9.2: Whiskering Coherence
- **Property**: `F ◂ α : F ∘ G => F ∘ H` and `α ▸ G : G ∘ F => H ∘ F` satisfy interchange
- **Encoding**: Structural - interchange law is a consequence of functoriality
- **Rationale**: Enables 2-dimensional reasoning

**Breaking Example**: If whiskering did not satisfy interchange:
- **Downstream impact**: Cannot form functor bicategories
- **Silent failures**: String diagrams would not commute
- **Affected modules**: All higher-dimensional category theory

---

## 10. Cat.Functor.Base (71 dependents)

**Hub Status**: Basic functor definitions

### Semantic Invariants

#### Invariant 10.1: Functoriality Laws
- **Property**: `F-id : F(id_X) ≡ id_F(X)` and `F-∘ : F(f ∘ g) ≡ F(f) ∘ F(g)`
- **Encoding**: Explicit - record fields with proof obligations
- **Rationale**: Defines structure-preserving maps between categories

**Breaking Example**: If only `F-∘` held (not `F-id`):
- **Downstream impact**: Identity functors would not exist
- **Silent failures**: All functor compositions would accumulate identity discrepancies
- **Affected modules**: All 71 dependents would need to track identity corrections

#### Invariant 10.2: Functor Equality is Natural Isomorphism
- **Property**: In univalent categories, `F ≡ G` iff there exists a natural isomorphism `F ≅ G`
- **Encoding**: Structural - via univalence for functor categories
- **Rationale**: Enables equivalence-based reasoning about functors

**Breaking Example**: If functor equality were strict:
- **Downstream impact**: Cannot use `subst` for functor properties
- **Silent failures**: Yoneda lemma would not transport correctly
- **Affected modules**: All representation theorems

---

## Cross-Cutting Invariants

### Global Invariant G.1: Proof Irrelevance of Properties
- **Property**: All `is-*` predicates are propositions (h-level 1)
- **Encoding**: Explicit - every `is-*` has a corresponding `*-is-prop` lemma
- **Rationale**: Enables extensionality: structures equal if underlying data equal

**Breaking Example**: If `is-category` were not a prop:
- **Downstream impact**: Univalent categories would have non-unique univalence structures
- **Silent failures**: All categorical reasoning would need to track which univalence proof is used
- **Affected modules**: All uses of univalent categories (300+ modules)

### Global Invariant G.2: Transport Preserves Structure
- **Property**: `transport (ua f)` preserves all structure (functors, natural transformations, etc.)
- **Encoding**: Structural - consequence of univalence + structure identity principle
- **Rationale**: Enables structure transport via equivalence

**Breaking Example**: If transport did not preserve structure:
- **Downstream impact**: All structure theorems (e.g., equivalence of categories) would fail
- **Silent failures**: Cannot transfer properties along equivalences
- **Affected modules**: All modules using `Iso→Path` or structure theorems

---

## Summary: Invariant Dependency Graph

```
Prim.Type (universe laws)
    ↓
1Lab.Path (path groupoid) → 1Lab.Equiv (equiv is prop) → 1Lab.Univalence
    ↓                              ↓                              ↓
1Lab.HLevel (h-level hierarchy)   ↓                              ↓
    ↓                              ↓                              ↓
1Lab.Prelude (combines all) ←─────┴──────────────────────────────┘
    ↓
Cat.Base (category laws)
    ↓
Cat.Reasoning (combinator coherence) → Cat.Functor.Base (functoriality)
    ↓                                          ↓
Cat.Prelude (re-exports) ←────────────────────┴─ Cat.Functor.Adjoint (triangle ids)
    ↓                                          ↓
    └────────→ Cat.Displayed.Base (over base) ─┴─→ Cat.Instances.Functor (vertical comp)
```

**Key Insight**: These invariants form a *coherence tower* where:
1. **Bottom layer** (Prim, Path): Enforced by primitives
2. **Middle layer** (HLevel, Equiv, Univalence): Propositional uniqueness
3. **Top layer** (Category, Functor): Explicitly stated laws
4. **Reasoning layer** (Reasoning, Displayed): Derived coherence

Breaking any level cascades upward, making the system *brittle by design* - this rigidity ensures correctness.

---

## Recommendations

### For Library Maintainers
1. **Never weaken foundational laws** - Even making them hold "up to isomorphism" breaks hundreds of modules
2. **Preserve proof irrelevance** - All `is-*-is-prop` lemmas are load-bearing
3. **Maintain definitional equalities** - Many invariants rely on strict equality, not propositional

### For Library Users
1. **Assume hom-sets are sets** - Don't expect higher categorical structure in standard categories
2. **Rely on transport coherence** - Structure transport is automatic via univalence
3. **Use provided combinators** - Reasoning combinators encode invariants; manual proofs may violate them

### For Future Work
1. **Document conventional invariants** - Some assumptions (e.g., functors preserving limits) are conventional, not enforced
2. **Make implicit invariants explicit** - Consider adding "safety" types for delicate invariants
3. **Test invariant violation** - Create negative tests showing what breaks when invariants fail
