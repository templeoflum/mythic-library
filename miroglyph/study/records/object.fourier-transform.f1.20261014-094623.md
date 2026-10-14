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

**statement (plain)** — the Fourier transform takes a function of one variable (say time) and produces a function of frequency that records "how much of each frequency" the original contains. It is the continuous-frequency limit of the [[object.fourier-series]]: as the period grows to infinity, the discrete spectrum of coefficients fills out into a continuous spectrum. An inverse transform rebuilds the original from its frequency content.

**statement (formal)** — for f suitable (e.g. f ∈ L¹(ℝⁿ), or a Schwartz function), the Fourier transform is the integral
  f̂(ξ) = (Ff)(ξ) = (2π)^{−n/2} ∫_{ℝⁿ} f(x) e^{−i x·ξ} dx,
with inverse
  f(x) = (F⁻¹f̂)(x) = (2π)^{−n/2} ∫_{ℝⁿ} f̂(ξ) e^{+i x·ξ} dξ.
(Conventions vary in the placement of 2π and the sign; the symmetric (2π)^{−n/2} convention is one standard. Other common conventions put e^{−2πi x·ξ} with no prefactor.) **[confirmed]**

**status** — definitional; the spaces on which it acts and the convergence of the inverse are the substance (extends from L¹ to L² by [[object.parseval-plancherel-theorem]], to tempered distributions by duality).

**lineage** — present implicitly in Fourier's 1822 treatise as the limiting integral form of the series for non-periodic functions [[source.fourier-1822]]; the integral-pair form was developed in the same era by Fourier, Cauchy, and Poisson. The rigorous L²-theoretic foundation came with Plancherel (1910) — see [[object.parseval-plancherel-theorem]]. **[confirmed]**

**door** — Stein & Shakarchi, *Fourier Analysis: An Introduction*, ch. 5 [[source.stein-shakarchi-2003]]; for the n-dimensional Euclidean theory, Stein & Weiss [[source.stein-weiss-1971]].

**sources** — [[source.fourier-1822]], [[source.stein-shakarchi-2003]], [[source.stein-weiss-1971]]; definition cross-checked against the Encyclopedia of Mathematics article "Fourier transform."
