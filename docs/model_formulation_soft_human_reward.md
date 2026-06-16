# Multi-Objective Human-Centered Time-Indexed Scheduling Formulation

## 1. Decision Variable

Let

\[
x_{o,r,t} =
\begin{cases}
1, & \text{if operation } o \text{ starts on resource } r \text{ at time } t \\
0, & \text{otherwise}
\end{cases}
\]

where:

- \(o \in \mathcal{O}\): operations
- \(r \in \mathcal{R}\): resources
- \(t \in \mathcal{T}\): discrete time slots

The resource set is decomposed into:

\[
\mathcal{R} = \mathcal{M} \cup \mathcal{H} \cup \mathcal{B}
\]

where:

- \(\mathcal{M}\): machines
- \(\mathcal{H}\): human workers
- \(\mathcal{B}\): robot resources

---

## 2. Baseline Scheduling Objective

The baseline scheduling cost is:

\[
C_{\text{sched}}(x)
=
\sum_{o,r,t}
\left(
\lambda_p c_{o,r}
+
\lambda_t t
\right)
x_{o,r,t}
\]

where:

- \(c_{o,r}\): processing cost of assigning operation \(o\) to resource \(r\)
- \(\lambda_p\): processing-cost weight
- \(\lambda_t\): start-time weight

---

## 3. Human-Centered Burden Cost

Human burden is incurred only when an operation is assigned to a human worker:

\[
C_{\text{human-burden}}(x)
=
\sum_{o,h,t}
\left(
\lambda_w W_o
+
\lambda_e E_o
\right)
x_{o,h,t}
\]

where:

- \(h \in \mathcal{H}\)
- \(W_o\): workload score of operation \(o\)
- \(E_o\): ergonomic risk score of operation \(o\)
- \(\lambda_w\): workload weight
- \(\lambda_e\): ergonomic-risk weight

---

## 4. Robot Safety Cost

Robot-related safety cost is:

\[
C_{\text{safety}}(x)
=
\sum_{o,b,t}
\lambda_s S_o x_{o,b,t}
\]

where:

- \(b \in \mathcal{B}\)
- \(S_o\): safety risk score of operation \(o\)
- \(\lambda_s\): safety-risk weight

---

## 5. Human Involvement Reward

Human involvement is counted as:

\[
H(x)
=
\sum_{o,h,t} x_{o,h,t}
\]

A soft reward for human involvement is introduced as:

\[
R_{\text{human}}(x)
=
\rho H(x)
\]

where:

- \(\rho\): human-involvement reward parameter

Because the solver minimizes the objective, this reward is subtracted from the cost.

---

## 6. Soft Human-Reward Objective

The reward-adjusted objective is:

\[
\min_x
\quad
C_{\text{sched}}(x)
+
C_{\text{human-burden}}(x)
+
C_{\text{safety}}(x)
-
\rho H(x)
+
P(x)
\]

where:

- \(P(x)\): penalty terms for violated constraints
- \(\rho H(x)\): reward for assigning operations to human workers

This objective allows the solver to choose human involvement when the reward is large enough to compensate for the additional workload and ergonomic burden.

---

## 7. Equivalent Trade-Off Interpretation

The soft reward formulation can also be interpreted as a scalarized multi-objective model:

\[
\min_x
\quad
C_{\text{sched}}(x)
+
C_{\text{human-burden}}(x)
+
C_{\text{safety}}(x)
-
\rho H(x)
\]

This represents a trade-off among:

1. Low scheduling cost
2. Low workload and ergonomic burden
3. Desired human involvement

A larger \(\rho\) increases the value of human participation and can shift the solution toward more human-assigned operations.

---

## 8. Core Constraints

### 8.1 Each Operation Starts Exactly Once

\[
\sum_{r,t} x_{o,r,t} = 1
\quad
\forall o \in \mathcal{O}
\]

### 8.2 Skill Compatibility

\[
x_{o,r,t} = 0
\quad
\text{if resource } r \text{ is incompatible with operation } o
\]

### 8.3 Precedence

If operation \(o\) must precede operation \(o'\), then:

\[
\text{start}(o) + p_o \leq \text{start}(o')
\]

where:

\[
\text{start}(o) = \sum_{r,t} t x_{o,r,t}
\]

and

\[
p_o = \sum_{r,t} p_{o,r} x_{o,r,t}
\]

### 8.4 Resource No-Overlap

For each resource \(r\) and each time point \(\tau\):

\[
\sum_{o,t: t \leq \tau < t + p_{o,r}} x_{o,r,t} \leq 1
\]

---

## 9. Pilot Interpretation from sample_4x4

In the sample_4x4 pilot:

- With \(\rho = 0\) or \(\rho = 1\), the solver selected no human assignments.
- With \(\rho = 2\) or \(\rho = 3\), the solver selected one human assignment.
- With \(\rho = 4\), the solver selected two human assignments.
- With \(\rho = 5\), the solver selected three human assignments.

This indicates threshold behavior: human involvement emerges only when the reward is large enough to offset the additional workload and ergonomic burden.

---

## 10. Modeling Insight

The hard human-utilization constraint answers:

> What happens if a minimum level of human involvement is required?

The soft human-reward formulation answers:

> How much reward is needed before the optimizer voluntarily selects human involvement?

Together, these two variants provide complementary pilot evidence for human-centered scheduling trade-offs.

