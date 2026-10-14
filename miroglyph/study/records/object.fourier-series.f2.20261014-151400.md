---
name: fourier-series
type: object
object-type: definition
essence: a periodic function written as a sum of sines and cosines (its frequency components)
field: ["[[field.fourier-analysis]]", "[[field.real-analysis]]"]
status: established
state: settled
attribution: J. Fourier, Théorie analytique de la chaleur (1822); precursor memoirs 1807 and 1811. Coefficient formulas: Euler–Fourier.
formalized: false
source: ["[[source.fourier-1822]]", "[[source.zygmund-1935]]", "[[source.stein-shakarchi-2003]]"]
depends-on: []
used-by: ["[[object.parseval-plancherel-theorem]]", "[[object.poisson-summation-formula]]", "[[object.fourier-transform]]", "[[object.weyl-equidistribution-theorem]]", "[[object.sampling-theorem]]"]
---

**statement (plain)** — any (sufficiently regular) periodic function can be written as a sum of sines and cosines whose frequencies are integer multiples of the fundamental frequency. The amount of each frequency present is its Fourier coefficient, recovered by integrating the function against that sine or cosine over one period.

**statement (formal)** — for f integrable on (0, 2π) with period 2π, the [[object.fourier-series]] is
  f(x) ∼ a₀/2 + Σ_{k≥1} (a_k cos kx + b_k sin kx),
with the **Euler–Fourier coefficients**
  a_k = (1/π) ∫₀^{2π} f(x) cos kx dx,  b_k = (1/π) ∫₀^{2π} f(x) sin kx dx.
Equivalently in complex exponential form,
  f(x) ∼ Σ_{n=−∞}^{∞} c_n e^{inx},  c_n = (1/2π) ∫₀^{2π} f(x) e^{−inx} dx.
The "∼" is association; equality (and the mode of convergence) is a separate matter handled by convergence theorems. **[confirmed]**

**status** — definitional; convergence is the deep theory (Dirichlet 1829 for piecewise-monotone; Carleson 1966 for L²). The object recorded here is the definition.

**lineage** — the trigonometric-series idea predates Fourier (D. Bernoulli, Euler, Clairaut, d'Alembert on the vibrating string and orbital perturbations). Fourier's contribution was the claim of *generality* — that arbitrary functions admit such an expansion — and the systematic coefficient formulas, advanced for the heat equation in *Théorie analytique de la chaleur* (1822), building on his 1807 memoir and subsequent 1811 submission [[source.fourier-1822]]. The coefficient integrals are the **Euler–Fourier formulas** (Euler had the form earlier; Fourier gave the general method). **[confirmed]**

**door** — Stein & Shakarchi, *Fourier Analysis: An Introduction*, ch. 2–3 [[source.stein-shakarchi-2003]]; the classical reference is Zygmund, *Trigonometric Series* [[source.zygmund-1935]].

**sources** — [[source.fourier-1822]], [[source.zygmund-1935]], [[source.stein-shakarchi-2003]]; statement cross-checked against the Encyclopedia of Mathematics article "Fourier series."

**chronology check** — Fourier's [1822 preliminary discourse](https://fr.wikisource.org/wiki/Page:Fourier_-_Th%C3%A9orie_analytique_de_la_chaleur,_1822.djvu/28), p. xviii, dates the first manuscript to late 1807 and the second submission to 28 September 1811. The Institut de France's [archive commentary](https://www.france-memoire.fr/theorie-du-mouvement-de-la-chaleur-dans-les-corps-solides/) identifies the latter as the competition manuscript and the award as 6 January 1812. The 1807 manuscript should therefore not be labeled the prize memoir. This check repairs that chronology; it does not re-audit priority among the earlier contributors or the modern convergence results.
