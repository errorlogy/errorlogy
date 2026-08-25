# TRN-

`src/trn_sim/` (`model.py`, `metrics.py`, `graph.py`, `config.py`). : \(t=0,1,\ldots,T\), \(\Delta t\) (`dt`).

---

## 1.

### 1.1.

\[
\mathcal{A}=\{a_1,\ldots,a_N\},\quad G=(V,E),\quad V=\mathcal{A},\quad |V|=N.
\]

\(W=[w_{ij}]_{N\times N}\):

\[
w_{ij}\ge 0,\quad \sum_{j=1}^N w_{ij}=1\quad \forall i.
\]

\(W\) `graph.normalize_rows`; \(w_{ii}=1\).

(`graph_type`): `ring_lattice`, `watts_strogatz`, `erdos_renyi` — . `graph.py`.

### 1.2.

\[
x_i(t)=
\begin{bmatrix}
b_i(t) \\
e_i(t) \\
q_i(t) \\
r_i(t) \\
m_i(t) \\
\alpha_i \\
h_i \\
z_i
\end{bmatrix}.
\]

| | () | Role |
|---|---|---|
| \(b_i\) | \([-1,1]\) | / |
| \(e_i\) | \([0,1]\) | |
| \(q_i\) | \([0,1]\) | (L4) |
| \(r_i\) | \([0,1]\) | (L5) |
| \(m_i\) | \([0,1]\) | (L2–L3) |
| \(\alpha_i\) | \([0,1]\) | |
| \(h_i\) | \([0.05,1.2]\) | bounded confidence |
| \(z_i\) | \([0,1)\) | ipolar- |

\(q,r,m,\alpha,h\) /Beta- `q_mean`, `r_mean`, `m_mean`, `alpha_mean`, `confidence_h_mean` (`TRNSimulation.__init__`).

### 1.3.

\[
\mathbf{x}(t)=\bigl(x_1(t),\ldots,x_N(t)\bigr)\in\mathcal{X}\subseteq [-1,1]^N\times[0,1]^{4N}\times[0,1]^N\times[0.05,1.2]^N.
\]

: \(\theta=(N,T,\Delta t,\texttt{graph\_type},\ldots)\in\Theta\) — . `TRNParams`.

---

## 2. \(P_i(t)\)

`narrative_pole()`; `narrative_mode`:

### 2.1.

\[
P_i(t)=p_0=\texttt{constant\_pole}\in[-1,1].
\]

### 2.2. ipolar-

\[
P_i(t)=
\begin{cases}
-1, & z_i<0.5,\\
+1, & z_i\ge 0.5.
\end{cases}
\]

\(z_i\) \(T\). «» , — .

### 2.3. -

\[
\bar b_i(t)=\sum_j w_{ij}b_j(t),\qquad
P_i(t)=\tanh\!\bigl(\chi\,\bar b_i(t)\bigr),\quad \chi=\texttt{echo\_chi}\ge 0.
\]

**:** `narrative_mode='bipolar'` \(\chi\) ** ** ; sweep \(\chi\) `stress_config` ( `outputs/stress/chi_h_sweep.csv`).

---

## 3. (bounded confidence)

\[
S_i(t)=\alpha_i\sum_{j=1}^N w_{ij}\,\kappa_{ij}(t)\,\bigl(b_j(t)-b_i(t)\bigr),
\]

\[
\kappa_{ij}(t)=\exp\!\left(-\frac{\bigl(b_j(t)-b_i(t)\bigr)^2}{2h_i^2}\right).
\]

: `social_term()` — `diff[i,j]=b_j-b_i`.

**:** \(h_i\) « » → ; \(h_i\) — (Deffuant–Hegselmann–Krause ).

**:** \(q_i,r_i\) **** \(S_i\); \(q,r\) TRN- \(I_i\).

---

## 4. TRN-

\[
I_i(t)=\lambda\,m_i(1-r_i)(1-q_i)\,A_i(t)\,\bigl(P_i(t)-b_i(t)\bigr),
\]

\[
A_i(t)=\sigma\!\bigl(\beta_0+\beta_1 e_i(t)+\beta_2|P_i(t)-b_i(t)|\bigr),\qquad
\sigma(z)=\frac{1}{1+e^{-z}}.
\]

: \(\lambda=\texttt{lambda\_trn}\ge 0\), \(\beta_0,\beta_1,\beta_2\) — . `TRNParams`.

** susceptibility:** \(\phi_i=m_i(1-r_i)(1-q_i)\in[0,1]\) — «» . \(r_i,q_i\) TRN; \(m_i\) .

---

## 5.

### 5.1.

\[
b_i(t+1)=\mathrm{clip}_{[-1,1]}\!\Bigl[b_i(t)+\Delta t\,\bigl(S_i(t)+I_i(t)+\eta_i(t)\bigr)\Bigr],
\]

\[
\eta_i(t)\sim\mathcal{N}(0,\sigma_b^2),\quad \sigma_b=\texttt{opinion\_noise}.
\]

### 5.2.

\[
e_i(t+1)=\mathrm{clip}_{[0,1]}\!\Bigl[e_i(t)+\Delta t\,\bigl(\rho|P_i-b_i|-\delta e_i+\xi_i(t)\bigr)\Bigr],
\]

\[
\xi_i(t)\sim\mathcal{N}(0,\sigma_e^2),\quad \sigma_e=\texttt{emotion\_noise}.
\]

\(|P_i-b_i|\) \(e_i\); \(\delta e_i\) . \(e_i\) \(\beta_1\) \(A_i\) → « → → TRN».

### 5.3. (`step()`)

1. \(P(t)\).
2. \(S(t)\), \(I(t)\); \(b(t+1)\).
3. Refresh \(e(t+1)\) ( \(P(t)\)).
4. (`record()`).

— `step()` (`run()` `record()` \(t=0\)).

### 5.4.

- \(\Delta t=0.08\).
- (`clip`) — plectic; \(T\le 200\) .
- : \(b,e\); RNG — `numpy.random.Generator(seed)`.
- ** :** `step()` = \(t\to t+1\); \(\Delta t\) .

---

## 6.

: `metrics.calculate_metrics(b, params)`.

### 6.1.

\[
\mathrm{Pol}(t)=\mathrm{std}\bigl(b_1(t),\ldots,b_N(t)\bigr),
\]

\[
C(t)=\max\bigl(0,\,1-\mathrm{Pol}(t)\bigr).
\]

### 6.2.

\[
\mathrm{Ext}(t)=\frac{1}{N}\sum_{i=1}^N \mathbf{1}\bigl(|b_i(t)|>\theta_{\mathrm{ext}}\bigr),\quad
\theta_{\mathrm{ext}}=0.65\ \text{()}.
\]

### 6.3.

\(b\) 20 \([-1,1]\), \(p_k\) — :

\[
H(t)=-\sum_{k:\,p_k>0} p_k\log p_k.
\]

### 6.4. risk TRN

\[
R_{\mathrm{TRN}}=\frac{\lambda\,\bar m\,(1-\bar r)\,(1-\bar q)\,\chi}{\bar h+\varepsilon},\quad
\varepsilon=10^{-6},
\]

\(\bar m,\bar r,\bar q,\bar h\) — ** ** (`m_mean`, `r_mean`, `q_mean`, `confidence_h_mean`), .

**Meaning:** « »; \(\mu\) Errorlogy.

### 6.5.

\[
\mathcal{A}(t)=\mathbf{1}\Bigl[C(t)<0.45\ \land\ \mathrm{Pol}(t)>0.44\ \land\ \mathrm{Ext}(t)>0.35\Bigr]\in\{0,1\}.
\]

** :** \(C=1-\mathrm{Pol}\) \(C<0.45\) \(\mathrm{Pol}>0.55\), \(\mathrm{Pol}>0.44\) automatically. :

\[
\mathcal{A}(t)=1 \iff C(t)<0.45\ \land\ \mathrm{Ext}(t)>0.35.
\]

\(\mathrm{Pol}>0.44\) \(C\).

** :** ipolar stress- (. §10). \(\theta_{\mathrm{ext}}=0.65\) «» (\(|b|\le 0.65\)) \(\mathrm{Pol}\approx 0.55\).

** :** \(K_{\mathrm{clusters}}\ge 3\) — \(b\).

---

## 7.

### 7.1. TRN (\(\lambda=0\))

:

\[
b_i(t+1)\approx b_i(t)+\Delta t\,S_i(t)+\eta_i.
\]

\(h_i\) Deffuant: \(b_i\) \(b^\*\) (). \(b^\*\):

\[
\Delta b_i \leftarrow \Delta t\,\alpha_i\sum_j w_{ij}(b_j-b_i).
\]

\(\dot{\mathbf{b}}=-L_W\mathbf{b}\) (), \(L_W\) — laplacian- . : ( ) \(\Delta t\,\alpha_{\max}<2/\lambda_{\max}(L)\).

** (`stress`, \(\lambda=0\)):** \(C_{\mathrm{final}}\approx 0.97\), \(\mathrm{Pol}\approx 0.03\), \(\mathcal{A}=0\).

### 7.2. TRN bipolar-

(, ):

\[
S_i+I_i=0\quad \text{}\quad b_i\in\{-1,+1\}\ \text{( clip)}.
\]

\(\lambda\) \(q,r\): ** ** \(b\approx -1\) \(b\approx +1\) \(P_i\). « », **ipolar lock-in**.

**Lyapunov-:**

\[
V(\mathbf{b})=\frac{1}{N}\sum_i (b_i-P_i)^2
\]

TRN- \(\dot b_i=\lambda\phi_i A_i(P_i-b_i)\). \(V\). ; \(\lambda>\lambda_{\mathrm{crit}}\) TRN → \(V\to 0\) .

### 7.3. (mean-field)

bipolar-. \(b_i\approx 0\) ( \(\mathcal{N}(0,0.18)\)). TRN:

\[
I_i\approx \lambda\,\bar\phi\,\bar A\,P_i,\quad
\bar\phi=\bar m(1-\bar r)(1-\bar q),\quad
\bar A\approx\sigma(\beta_0+\beta_1\bar e+\beta_2).
\]

«» \(\sim \bar\alpha\,\mathrm{Pol}/\bar h\). \(\lambda\) :

\[
\lambda_{\mathrm{crit}}^{\mathrm{MF}}\sim\frac{\bar\alpha\,\bar h}{\bar\phi\,\bar A\,|P|}
\approx\frac{0.55\times 0.35}{0.75^3\times 0.92\times 1}\approx 0.49.
\]

Stress-: \(\bar m=0.75\), \(\bar q=\bar r=0.25\), \(\bar h=0.35\), `narrative_mode=bipolar`.

---

## 8. \(\lambda\)

### 8.1. (`configs/stress_config.json`, `outputs/stress/lambda_sweep.csv`, \(R=3\) )

| \(\lambda\) | \(C_{\mathrm{mean}}\) | \(\mathrm{Pol}_{\mathrm{mean}}\) | \(\mathrm{Ext}_{\mathrm{mean}}\) | \(R_{\mathrm{TRN}}\) | \(\mathcal{A}\)-rate |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 0.970 | 0.030 | 0.000 | 0.00 | 0.0 |
| 0.2 | 0.650 | 0.350 | 0.021 | 0.60 | 0.0 |
| **0.4** | **0.223** | **0.777** | **0.923** | **1.21** | **1.0** |
| 0.6 | 0.103 | 0.897 | 0.991 | 1.81 | 1.0 |
| 1.0 | 0.035 | 0.965 | 1.000 | 3.01 | 1.0 |
| 2.0 | 0.009 | 0.991 | 1.000 | 6.03 | 1.0 |

**:** \(\lambda=0.2\) \(\lambda=0.4\):

\[
\lambda_{\mathrm{crit}}^{\mathrm{emp}}\in(0.2,\,0.4),\quad \text{}\ \lambda_{\mathrm{crit}}\approx 0.35\pm 0.05.
\]

\(\lambda=0.2\) (\(\mathrm{Pol}=0.35\)), \(\mathrm{Ext}<0.35\) → \(\mathcal{A}=0\). \(\lambda=0.4\) → \(\mathcal{A}=1\).

\(R_{\mathrm{TRN}}\): \(R_{\mathrm{TRN}}\approx 1.2\);

\[
R_{\mathrm{TRN}}\gtrsim 1 \quad\Rightarrow\quad \text{ risk (bipolar stress)}.
\]

### 8.2. sweep (`echo`-, `outputs/lambda_sweep.csv`)

`narrative_mode='echo'`, \(\bar q=\bar r=0.45\), \(\bar m=0.55\): \(\lambda=1.2\) — \(C\approx 0.90\), \(\mathcal{A}=0\). ** \(\lambda\)**; susceptibility.

### 8.3. Grid \(q,r\) \(\lambda=0\)

`outputs/stress/qr_grid.csv`: \(C\approx 0.978\), \(\mathcal{A}=0\). \(q,r\) \(\lambda=0\) ( §4). \(q,r\) sweep \(\lambda\ge\lambda_{\mathrm{crit}}^{\mathrm{emp}}\).

---

## 9. (L1–L5)

| | | `TRNParams` | |
|---|---|---|---|
| L1 Reactive | \(e_i\), \(\rho,\delta\) | `rho`, `delta`, `emotion_noise` | \(A_i\) → \(I_i\); \(\rho\) TRN- |
| L2 Mimetic | \(m_i\), \(\alpha_i\) | `m_mean`, `m_std`, `alpha_mean` | \(m\) — \(I\); \(\alpha\) — |
| L3 Narrative | \(P_i\), \(\chi\) | `narrative_mode`, `echo_chi`, `constant_pole` | ; \(\chi\) `echo` |
| L4 Reflective | \(q_i\) | `q_mean`, `q_std` | \(I_i\) \((1-q_i)\) |
| L5 Strategic | \(r_i\) | `r_mean`, `r_std` | \(I_i\) \((1-r_i)\) |
| | \(w_{ij}\) | `graph_type`, `k_neighbors`, `rewiring_p` | \(h\) + |
| Bounded confidence | \(h_i\) | `confidence_h_mean`, `confidence_h_std` | \(\bar h\) → \(S_i\) ; \(R_{\mathrm{TRN}}\) |
| TRN- | \(\lambda\) | `lambda_trn` | |
| | \(\beta_0,\beta_1,\beta_2\) | | strengthened \(A_i\) |

---

## 10. Link to Errorlogy (EGD)

: `bridge/egd_stub.py` ( MAS).

| MAS EGD () | TRN- | |
|---|---|---|
| `echo_room_pressure` \(\in[0,1]\) | \(\lambda\), \(\chi\) | : \(\lambda=0.15+0.85\cdot\)pressure, \(\chi=0.5+3.5\cdot\)pressure |
| `hidden_signal_prior` \(\in[0,1]\) | \(\bar h\) | : \(h=\max(0.15,\,0.55-0.35\cdot\)prior\()\) |

** :** \(R_{\mathrm{TRN}}\), \(\mu\) v16 MAS — . TRN- .

---

## 11. CLI

1. **ponent ** — `sample_metrics.csv`, `*_raw.csv`; `data/output_schema.json`; `TRNSimulation.final_report()`.
2. ** sweep** — `lambda_sweep.csv`, `qr_grid.csv`, `chi_h_sweep.csv`; `experiments.aggregate()`.

: `python scripts/validate_outputs.py outputs --recursive`.

---

## 12. alsifiable

| # | | , |
|---|---|---|
| H1 | \(\lambda_{\mathrm{crit}}\) \(\bar m(1-\bar r)(1-\bar q)\) | Grid \(q,r\) ** ** \(\lambda=0.5\); : \(q,r\) |
| H2 | \(R_{\mathrm{TRN}}>1\) \(\mathcal{A}=1\) bipolar stress | counterexample: \(\lambda,\bar m,\bar q,\bar r,\chi,\bar h\) \(R_{\mathrm{TRN}}>1\) \(\mathcal{A}=0\) |
| H3 | Echo- \(\chi\uparrow\) \(\lambda>0\) | Sweep \(\chi\) `narrative_mode='echo'`, \(\lambda\in\{0.4,0.6\}\) |
| H4 | 0.45/0.44/0.35 | ROC «/» \(N,T,\theta_{\mathrm{ext}}\) |
| H5 | \(\lambda=0\) \(h\to 0.05\) | Sweep \(\bar h\) \(\lambda=0\); : \(\mathrm{Pol}\) TRN |

**Next steps :** (1) \(K_{\mathrm{clusters}}\); (2) sweep \(q,r\) \(\lambda>0\); (3) `egd_stub` ; (4) \(R\) 30 (. `EXPERIMENT_PROTOCOL.md`).

---

## A. ( = )

\[
\boxed{
\begin{aligned}
b_i^+ &= \mathrm{clip}_{[-1,1]}\Bigl[b_i+\Delta t\bigl(\alpha_i\sum_j w_{ij}e^{-(b_j-b_i)^2/(2h_i^2)}(b_j-b_i)+\lambda m_i(1-r_i)(1-q_i)A_i(P_i-b_i)+\eta_i\bigr)\Bigr],\\
e_i^+ &= \mathrm{clip}_{[0,1]}\Bigl[e_i+\Delta t\bigl(\rho|P_i-b_i|-\delta e_i+\xi_i\bigr)\Bigr],\\
A_i &= \sigma(\beta_0+\beta_1 e_i+\beta_2|P_i-b_i|).
\end{aligned}
}
\]

: `model.py` (), `metrics.py` (), `graph.py` (\(W\)), `config.py` ( ).
