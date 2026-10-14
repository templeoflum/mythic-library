---
name: fourier-transform
type: object
object-type: definition
essence: the continuous-frequency analogue of the Fourier series — a function rewritten as a superposition of all frequencies
field: ["[[field.fourier-analysis]]", "[[field.real-analysis]]"]
status: established
state: settled
attribution: J. Fourier (1822), as the integral limit of the Fourier series; integral form developed by Fourier, Cauchy, Poisson
formalized: false
source: ["[[source.fourier-1822]]", "[[source.stein-shakarchi-2003]]", "[[source.stein-weiss-1971]]"]
depends-on: ["[[object.fourier-series]]"]
used-by: ["[[object.parseval-plancherel-theorem]]", "[[object.convolution-theorem]]", "[[object.poisson-summation-formula]]", "[[object.sampling-theorem]]"]
---

**statement (plain)** — the Fourier transform describes a function's frequency content. Under suitable conditions an inverse transform recovers it. Its connection with the [[object.fourier-series]] can be motivated by increasing the period, but that limiting argument requires hypotheses; it is not an unconditional convergence claim.

**statement (formal; definition)** — for f ∈ L¹(ℝⁿ), define
  f̂(ξ) = (Ff)(ξ) = (2π)^{−n/2} ∫_{ℝⁿ} f(x) e^{−i x·ξ} dx.
This integral is absolutely convergent for every ξ. L¹ membership alone does not guarantee that f̂ is integrable.

**inversion / domains** — if both f and f̂ belong to L¹(ℝⁿ), then
  f(x) = (2π)^{−n/2} ∫_{ℝⁿ} f̂(ξ) e^{+i x·ξ} dξ
for almost every x. The right side is a continuous representative of f; equality holds at every point where the chosen f is continuous. For a Schwartz function f, both transforms are Schwartz and the identity holds everywhere. The ordinary absolutely convergent inverse integral must not be asserted for every L¹ input without an extra condition or a specified summation procedure.

The symmetric (2π)^{−n/2} normalization is retained here. The references below use e^{−2πi x·ξ} without a prefactor; changing frequency variables gives the displayed convention.

**check (editorial counterexample)** — in one dimension, f = 1_[−1,1] is integrable, but
  f̂(ξ) = √(2/π) sin(ξ)/ξ,
with its continuous value √(2/π) at ξ = 0. The absolute integral of this transform diverges. This blocks the general absolutely convergent inverse integral; it does not preclude reconstruction by an appropriate improper or regularized limit.

**status / extensions** — the transform is a definition; inversion is a theorem with domain conditions. The unitary L² transform is obtained by completion from the dense Schwartz class (or L¹ ∩ L²) using [[object.parseval-plancherel-theorem]]. It agrees with the integral transform on L¹ ∩ L². General L² inversion is an L² identity, not an automatic pointwise absolutely convergent integral. The tempered-distribution extension is defined by duality.

**lineage** — present implicitly in Fourier's 1822 treatise as the limiting integral form of the series for non-periodic functions [[source.fourier-1822]]; the integral-pair form was developed in the same era by Fourier, Cauchy, and Poisson. The rigorous L²-theoretic foundation came with Plancherel (1910) — see [[object.parseval-plancherel-theorem]]. **[confirmed]**

**door** — Stein & Shakarchi, *Fourier Analysis: An Introduction*, ch. 5 [[source.stein-shakarchi-2003]]; for the n-dimensional Euclidean theory, Stein & Weiss [[source.stein-weiss-1971]].

**sources** — [[source.fourier-1822]], [[source.stein-shakarchi-2003]], [[source.stein-weiss-1971]]; definition cross-checked against the Encyclopedia of Mathematics article "Fourier transform."

**checked access / scope** — Wolff's [editor-hosted March 2002 lecture notes](https://personal.math.ubc.ca/~ilaba/wolff/notes_march2002.pdf), Theorem 3.4 (p. 15), give the L¹ inversion hypotheses; Corollary 3.6 (p. 17) treats Gaussian-regularized inversion. Tao's [author-hosted lecture notes 2](https://www.math.ucla.edu/~tao/247a.1.06f/notes2.pdf), §7, pp. 19–20, give Schwartz inversion and the L² extension. These are modern mathematical checks, not historical priority evidence. The existing historical summary and general-reading references above were not freshly audited. The indicator example and normalization conversion are editorial derivations.
