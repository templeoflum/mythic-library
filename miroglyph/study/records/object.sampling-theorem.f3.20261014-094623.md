---
name: sampling-theorem
type: object
object-type: theorem
essence: a finite-energy low-pass signal bandlimited to B hertz is reconstructible from uniform samples at rate f_s >= 2B; unrestricted band-edge sinusoids require separate treatment
field: ["[[field.digital-signal-processing]]", "[[field.information-theory]]", "[[field.fourier-analysis]]"]
status: proven
state: settled
attribution: rate bound Nyquist (1928); stated & proved Shannon (1949); earlier formulations Whittaker (1915) & Kotelnikov (1933) — hence "Whittaker–Kotelnikov–Shannon (WKS) theorem"
formalized: true
source: ["[[source.shannon-1949]]", "[[source.nyquist-1928]]", "[[source.whittaker-1915]]", "[[source.kotelnikov-1933]]"]
depends-on: ["[[object.fourier-transform]]", "[[object.fourier-series]]"]
used-by: ["[[object.aliasing-in-rendering]]", "[[object.spatial-anti-aliasing]]", "[[object.stochastic-sampling]]", "[[object.supersampling]]"]
---

**statement (plain)** — for finite-energy signals with no frequencies outside −B to B hertz, uniform samples at rate 2B or higher determine the continuous signal. This is an ideal infinite-sample result; finite records and practical reconstruction filters introduce additional issues.

**statement (formal; modern finite-energy formulation)** — let B > 0 and x belong to L²(R), using its continuous bandlimited representative, and let X(f) = 0 almost everywhere for |f| > B. For T = 1/f_s and f_s >= 2B,

  x(t) = Σ_{n=−∞}^{∞} x(nT) · sinc((t − nT)/T),  sinc(u) = sin(πu)/(πu), sinc(0) = 1.

The series reconstructs x in L² and uniformly. The threshold rate 2B is the **Nyquist rate**; f_s/2 is the **Nyquist frequency**. This finite-energy formulation makes the signal class explicit rather than claiming unconditional recovery for every bandlimited generalized signal.

**boundary case / check** — equality is not universally valid or universally invalid. For the finite-energy class above, spectral contact at isolated endpoints does not cause overlap on a set of positive measure. If persistent sinusoids are allowed instead, x(t) = sin(2πBt) has x(n/(2B)) = 0 for every integer n and is indistinguishable from zero at that sampling rate. It is not in L²(R). This counterexample is an editorial mathematical check, not a quotation from Shannon. Sampling below 2B loses the general reconstruction guarantee for the full low-pass class; this does not mean every particular signal fails.

**proof / method** — Shannon's Section II, Theorem 1, starts with the continuous [[object.fourier-transform]], identifies the samples with coefficients of a [[object.fourier-series]] on the bounded spectral interval, and then gives sinc reconstruction in equations (6)–(7). These are the direct dependencies of the proof recorded here. The finite [[object.discrete-fourier-transform]] is not a prerequisite. The function-space wording above is a modern formulation, not a verbatim historical statement. The modern finite-energy qualification above is consistent with J. M. Whittaker's convergence analysis: [1927 paper, opening discussion and Theorem 2](https://doi.org/10.1017/S0013091500007318).

**lineage** — the following mathematical and communications threads are associated with the compound name **Whittaker–Kotelnikov–Shannon (WKS)**:
- H. Nyquist (1928), [[source.nyquist-1928]] — the rate bound: 2B independent pulses per second through a bandwidth-B channel; did not treat reconstruction of a continuous signal. **[confirmed]**
- E. T. Whittaker (1915), [[source.whittaker-1915]] — the cardinal interpolation series, as a problem in interpolation theory, without the radio/communication framing. **[confirmed]**
- V. A. Kotelnikov (1933), [[source.kotelnikov-1933]] — Theorems I–II give a sampling expansion and transmission at intervals 1/(2f₁), in a communications setting. The inspected historical proof assumes Dirichlet conditions and integrability; it is not the modern L² formulation above. **[confirmed from primary text]** Absolute priority and a precise date of recognition outside the USSR are not established by this check.
- C. E. Shannon (1949), [[source.shannon-1949]] — the statement-plus-proof that reached engineers and tied it to channel capacity; Shannon cites J. M. Whittaker (1935), Nyquist, Bennett, and Gabor in Section II, notes 3–6. **[confirmed]**
- The sampling result is **Theorem 1** in Section II of the 1949 paper (1998 reprint, p. 448); the reconstruction formula is equation (7). **[confirmed from primary text]**

**door** — Oppenheim & Schafer (codification) [[source.oppenheim-schafer-1975]]; Smith, *The Scientist and Engineer's Guide to DSP*, ch. on sampling [[source.smith-dspguide]].
