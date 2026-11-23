# Hanna's OEIS A389475, Formulas (4.a)–(4.b): integral lifting and extensions

Haobo Ma — ChronoAI Pte Ltd, Singapore  
Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore

## Statements

`note.tex` proves OEIS A389475, Formulas (4.a)–(4.b), with integral
existence and uniqueness of the normalized rational series. It also proves
A389474, Formulas (3)–(4), the two residue-class conjectures in A389472's
COMMENTS, and the explicitly identified algebraic consequences in the
coverage table. The A389472 congruences are alternative proofs of results
of Adrian Perez Fontelles (August 31, 2026, parity) and Horace Dong
(September 26, 2026, modulo three); the bibliography links their exact sources.
Congruences are coefficientwise in the integer power-series
ring. Each series has its own normalization; A389472 uses both seeds 1, 1.

For every odd integer `q` and even integer `c`, the inverse of the normalized
solution of `f(q*x^2)=(q-1)*x^2+f^2+c*f^3` satisfies
`g^2 ≡ x^2+c*x^3 (mod q^2)`. With `h=x^2+x^3` and
`E=x*product(j>=0,1+h^(iterate j))`, the solutions of A389472's equation
are exactly `D=x+t*E^2`. Here `E` is A350432; its product is Hanna's
Formula (3), not a new source identity. Both entries' stated radius
`(sqrt(5)-1)/2` is proved in the note. The algebraic formulas of A389472
and A350432 also follow, with explicit substitutions.
The same product construction for `h=x^m*(1+epsilon*x)` proves the related
identities of A350431, A350433 and A350434. In A273162, the displayed
product represents the inverse `B`, as its EXAMPLE already states, not
the generating function `A`: their coefficients of `x^2` are −1 and +1.
Prime-degree lifting also covers A274396, and a signed quadratic version
covers A273320; their inverse and iterate identities follow explicitly.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively use a current LaTeX installation:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded in the TeX source. There are no external
figures, bibliography databases or generated TeX inputs.

## Exact coefficient checks

Python 3.10 or later and its standard library suffice:

```sh
python3 verify.py > checks.json
```

The default degree is 96. `checks.json` gives the exact finite scope:
the defining equations, congruences, inverse identity and power exponents,
the 23/24/41-term OEIS prefixes, an independent rational recursion through
degree 24, sixteen integral-family examples and the sharpness coefficients
3, 15, 9, 6. It also checks twenty square-modulus parameter pairs through
degree 32, the companion product and free-second-coefficient identities,
and exact rational bounds certifying all 51 displayed fractional digits
of A389472 at `1/2`, `2/5`, `1/3`, `1/4`, `1/5`.
Six order/sign product-family examples are checked through degree 32,
with explicit coefficients distinguishing the product and its inverse.
Three prime-degree examples are checked through coefficient degree 24,
and the signed A273320 equation is checked through degree 33.
The all-indices conclusions follow from the written proofs,
not from extrapolating these finite calculations.

## Formal statements

The PDF links the exact `.lean` sources at commit
`074df09ddbbef1843ddb383577bfaa827f753e36`. Its coverage section maps each
declaration to its statement and hypotheses. The general integral family,
inverse identities, Catalan comparison, companion product, parameter
classification and radius have written proofs; the finite coefficient
identities and rational bounds are checked by `verify.py`.
The four linked Lean files cover the precise congruence statements and
the normalized integer A389472 recurrence, as specified in the PDF.

## License

The note and accompanying original material are licensed under Creative
Commons Attribution 4.0 International (CC BY 4.0).
The OEIS entries cited in the note retain their own terms.
