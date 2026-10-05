# Dimensional Analysis & Physical Unit Homogeneity

In engineering mechanics, chemical thermodynamics, and electrical systems, every physical law obeys the **Principle of Dimensional Homogeneity**: only commensurate physical quantities with identical dimensions can be added or compared.

---

## 1. 7-Dimensional SI Base Vector Space

Every derived physical quantity $Q$ possesses a unique integer exponent vector $\mathbf{d} \in \mathbb{Z}^7$ over the base dimensions:

$$
[Q] = [M]^\alpha [L]^\beta [T]^\gamma [\Theta]^\delta [I]^\epsilon [N]^\zeta [J]^\eta
$$

| Dimension | Symbol | SI Base Unit |
|---|---|---|
| Mass | $[M]$ | kilogram ($\text{kg}$) |
| Length | $[L]$ | meter ($\text{m}$) |
| Time | $[T]$ | second ($\text{s}$) |
| Temperature | $[\Theta]$ | Kelvin ($\text{K}$) |
| Electric Current | $[I]$ | Ampere ($\text{A}$) |
| Substance Amount | $[N]$ | mole ($\text{mol}$) |
| Luminous Intensity | $[J]$ | candela ($\text{cd}$) |

---

## 2. Invariant Physical Operations

1. **Addition / Subtraction:**
   $$[A + B] \implies [A] \equiv [B]$$
   If $[A] \ne [B]$, the expression is physically nonsensical and flagged as `DIMENSIONAL_HOMOGENEITY_VIOLATION`.

2. **Multiplication / Division:**
   $$[A \cdot B] = [A] \otimes [B] = \mathbf{d}_A + \mathbf{d}_B$$
   $$[A / B] = [A] \oslash [B] = \mathbf{d}_A - \mathbf{d}_B$$

3. **Powers & Exponentiation:**
   $$[A^k] = k \cdot \mathbf{d}_A, \quad k \in \mathbb{Q}$$
   The exponent $k$ itself must be strictly dimensionless: $[k] = \mathbf{0}$.

4. **Transcendental Arguments:**
   Functions including $\sin(x), \cos(x), \exp(x), \ln(x)$ admit Taylor series expansions $\sum_{n=0}^\infty c_n x^n$. Because infinite polynomial sums require $[x]^n \equiv [x]^0$, arguments to transcendental functions must be strictly dimensionless:
   $$[x] \equiv \mathbf{0}$$

---

## 3. Detecting Reasoning Step Hallucinations

When evaluating intermediate reasoning steps of an AI agent:
- An agent might produce a formula that appears superficially plausible (e.g. $F = m \cdot v$) but fails dimensional checks ($[M][L][T]^{-1} \ne [M][L][T]^{-2}$).
- The dimensional unit checker identifies these non-physical derivations immediately, localizing the hallucination to the exact intermediate step before downstream arithmetic occurs.
