# Multi-Step Benchmark Harness & Telemetry Formulation

Evaluating complex reasoning agents requires fine-grained milestone tracking rather than simple binary final-answer scoring.

---

## 1. Multi-Step Milestone Decomposition

Each engineering benchmark task is partitioned into sequential derivation milestones:
1. **Governing Equation Formulation:** Deriving the primary physical differential or balance relationship.
2. **Boundary Condition & Parametric Reduction:** Expressing the intermediate target variable algebraically.
3. **Dimensional Normalization:** Checking units and intermediate scaling.
4. **Final Algebraic & Numeric Resolution:** Computing the exact closed form and floating-point answer.

---

## 2. Pass@k Unbiased Estimator

Following Chen et al. (Codex / HumanEval), when generating $n$ sample attempts per problem with $c$ correct solutions:
$$
\text{pass}@k = \mathbb{E}\left[ 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}} \right]
$$
This unbiased combinatorial estimator computes the probability that at least one of $k$ randomly selected attempts succeeds, avoiding high-variance Monte Carlo sampling.

---

## 3. Step Hallucination Rate & Token Efficiency Index

### Step Hallucination Rate:
$$
H_{\text{step}} = \frac{\sum_{i=1}^M \mathbf{1}_{\{\text{Step } i \text{ has algebraic/dimensional error}\}}}{M_{\text{total}}} \times 100\%
$$

### Token Efficiency Index (Compute Ratio):
Measures average reasoning token expenditure per verified correct derivation step:
$$
\text{TEI} = \frac{\text{Total Reasoning Tokens}}{\text{Total Verified Correct Steps}}
$$
Lower TEI indicates compact, direct mathematical reasoning without verbose chain-of-thought wandering.
