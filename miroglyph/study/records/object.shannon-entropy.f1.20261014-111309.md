---
name: shannon-entropy
type: object
object-type: definition
essence: expected surprisal of a discrete random variable — H(X) = -Σ p log₂ p bits; a lower bound on average lossless prefix-code length
field: ["[[field.information-theory]]"]
status: established
state: settled
attribution: Claude E. Shannon (1948); precursors Nyquist (1924), Hartley (1928)
formalized: true
source: ["[[source.shannon-1948]]", "[[source.shannon-weaver-1949]]", "[[source.cover-thomas-1991]]", "[[source.mackay-itila]]", "[[source.nyquist-1924]]", "[[source.hartley-1928]]"]
depends-on: []
used-by: ["[[object.source-coding-theorem]]", "[[object.mutual-information]]", "[[object.noisy-channel-coding-theorem]]", "[[object.kullback-leibler-divergence]]"]
---

**statement (plain)** — entropy measures uncertainty about a random outcome. A fair coin has 1 bit of entropy; a two-headed coin has 0. For a fixed finite set of possible outcomes, entropy is largest when all are equally likely. It bounds the best average number of binary questions needed for exact identification; that average need not equal the entropy.

**statement (formal)** — for a discrete random variable X with probabilities p(x),
H(X) = −Σ_x p(x) log₂ p(x) = E[−log₂ p(X)],
with 0 log 0 = 0. Base-2 logarithms give **bits**; base e gives **nats**. The formula permits countably many outcomes, with H possibly infinite. The finite-alphabet properties and coding statements below have their narrower stated scope.

**operational meaning (finite alphabet)** — let L* be the smallest expected number of arbitrary, noiseless yes/no questions that always identify X, equivalently the optimal expected length of a binary prefix code on its positive-probability outcomes. A certain outcome needs zero questions and may use the empty codeword. Then H(X) ≤ L* < H(X) + 1, with equality on the left exactly when every positive probability is 2^−ℓ for an integer ℓ ≥ 0. In general there is an integer-codeword-length overhead. For independent, identically distributed blocks of N symbols, optimal expected length per symbol approaches H(X). This is a modern coding interpretation of [[object.source-coding-theorem]], not an assertion that every individual outcome or finite message requires exactly H bits. Shannon's §9, Theorem 9 and its second proof give the block-coding approach to the entropy limit [[source.shannon-1948]].

**check (editorial example)** — for probabilities (0.9, 0.1), H ≈ 0.468996 bits. One noiseless binary question is still required to distinguish the two possible outcomes with certainty. Thus L* = 1, not H. For dependent sequences, the relevant asymptotic quantity is their entropy rate, which need not equal the entropy of a single symbol.

**status / uniqueness** — entropy is a definition. Shannon's §6, Theorem 2, characterizes the finite-distribution form under continuity, increasing uncertainty for equiprobable outcomes, and the weighted grouping axiom: H = −K Σ p log p with K > 0. K is a positive scale factor for a fixed logarithm base; choosing bits and H(1/2, 1/2) = 1 fixes the normalization. The proof is in Appendix 2 [[source.shannon-1948]].

**properties** — H(X) ≥ 0; for a distribution on n outcomes, H ≤ log₂ n, with equality for the uniform distribution. H = 0 exactly for a point mass, and H is concave in the probability vector.

**lineage** — the logarithmic measure predates Shannon: [[source.nyquist-1924]] and [[source.hartley-1928]] are precursors named in his introduction. Shannon develops the probability-weighted measure and its coding interpretation. His §6 explicitly connects its form to statistical mechanics. The frequently repeated von Neumann naming anecdote is not established by the primary text inspected here and is not used as confirmed attribution.

**door** — Cover & Thomas, *Elements of Information Theory*, ch. 2 [[source.cover-thomas-1991]]; MacKay, *Information Theory, Inference, and Learning Algorithms* [[source.mackay-itila]].

**primary text checked** — Shannon's [corrected reprint](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf), §6 and Theorem 2 (reprint pp. 10–11), §7 (source entropy), §9 and Theorem 9 (pp. 16–17), Appendix 2 (pp. 28–29). These are the reprint's printed page numbers, not the original journal pagination. The bounds, example, and qualifications above use modern notation; they are not verbatim historical theorem statements.
