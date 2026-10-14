---
name: aliasing-in-rendering
type: object
object-type: concept
essence: jagged edges, false texture patterns, and unstable detail caused by inadequately filtered sampling of an image signal
field: ["[[field.digital-signal-processing]]"]
status: established
state: settled
attribution: sampling-theory treatment for shaded rendering by Franklin C. Crow (1976 report; 1977 article), alongside contemporary graphics work; no absolute priority claim
formalized: false
source: ["[[source.crow-1977]]", "[[source.foley-vandam-1982]]", "[[source.glassner-1995]]"]
depends-on: ["[[object.sampling-theorem]]"]
used-by: ["[[object.spatial-anti-aliasing]]", "[[object.supersampling]]", "[[object.stochastic-sampling]]"]
---

**statement (plain)** — sampling a sharp edge, thin object, or fine texture too coarsely can produce false patterns: jagged edges, moiré, and small features that appear or disappear as the scene moves. Different continuous image patterns can give the same samples, so the samples alone cannot determine which pattern was present. Filtering before sampling reduces this ambiguity for the image one intends to reconstruct.

**statement (uniform-grid model)** — in one dimension, frequencies separated by an integer multiple of the sample rate produce identical complex-exponential samples:

  exp(2πi(f + k f_s)n/f_s) = exp(2πifn/f_s), for integers n and k.

This is an editorial algebraic explanation of aliasing, not a theorem quoted from Crow. On a rectangular two-dimensional grid, the same identity holds in each coordinate. The usual low-pass Nyquist region has half-sample-rate limits on each frequency component; a single radial cutoff is not the general two-dimensional rule. See [[object.sampling-theorem]] for its signal-class and endpoint qualifications.

**scope / limits** — sampling below the low-pass Nyquist rate removes the general unique-reconstruction guarantee for that signal class. It does not establish that every particular signal, or a signal with additional prior constraints, is unrecoverable. Ideal sharp discontinuities are not bandlimited, so merely choosing a sufficiently high finite rate is not a universal cure. Spatial aliasing can shimmer in animation; aliasing caused by sampling time too coarsely is a further temporal-sampling issue, not determined by spatial resolution alone.

**basis** — Crow's [1977 paper](https://users.cs.northwestern.edu/~ago820/cs395/Papers/Crow_1977.pdf), pp. 799–800, relates jagged edges and disappearing detail to sampling and motivates prefiltering. Figure 2 (p. 800) illustrates two frequencies with identical samples. The paper develops practical approximate convolution and a filtering tiler; it does not prove that every finite-support practical filter eliminates all aliasing. See [[object.spatial-anti-aliasing]]. Its conclusion (p. 805) discusses the visibility of aliasing in animation. [[source.crow-1977]]

**lineage / checked attribution** — Crow's published title is *The Aliasing Problem in Computer-Generated Shaded Images*. His reference 2 (p. 805) identifies the earlier March 1976 report UTEC-CSc-76-015 with *Computer-Synthesized* in its title. That is an earlier report version, not simply an alternative title for the 1977 journal item. Blinn and Newell's [1976 paper](https://www.microsoft.com/en-us/research/wp-content/uploads/1976/10/p542-blinn.pdf), *Texture and Reflection in Computer Generated Images*, pp. 542–543, already explains rendering aliasing and prefiltering, credits Crow's filter on p. 543, and cites his 1976 report in reference 3 (p. 547). This supports a contemporary lineage; it does not settle absolute priority for introducing aliasing into graphics or for the word itself.

**sources / scope of this check** — the two primary graphics papers above were inspected for the stated passages. Foley & van Dam [[source.foley-vandam-1982]] and Glassner [[source.glassner-1995]] remain general reading references; their full treatments were not re-audited here. The algebraic identity and the scope qualifications are editorial mathematical explanations. No source PDF is included in this record.
