# TRN (stress-)

`configs/stress_config.json`:

- `narrative_mode=bipolar`
- \(\bar q=\bar r=0.25\), \(\bar m=0.75\), \(\bar h=0.35\), \(\chi=2.5\)
- \(N=300\), \(T=200\), \(\Delta t=0.08\), \(R=3\)

: `outputs/stress/lambda_sweep.csv` ( 2026-06-13).

---

## 1. : \(\lambda\) ( TRN)

```
C ()
  1.0 |*
      |
  0.8 |
      |
  0.6 |  *
      |
  0.4 |---- λ_crit ≈ 0.3–0.4 ----
      |
  0.2 |      *
      |
  0.0 |            * * * * *
      +--+--+--+--+--+--+--+--→ λ
         0  .2  .4  .6  .8  1.0  1.2  2.0

Ext ( |b|>0.65)
  1.0 |            *********
      |
  0.5 |
      |
0.35| - - - - - - - - -
      |  *
  0.0 |*
      +--+--+--+--+--+--+--+--→ λ
         0  .2  .4  ...

A-rate ()
  1.0 |      ***************
      |
  0.0 |***
      +--+--+--+--+--+--+--+--→ λ
         0  .2  .4  ...
```

---

## 2.

| Zone | \(\lambda\) | \(C\) | \(\mathrm{Pol}\) | \(\mathrm{Ext}\) | \(\mathcal{A}\) | |
|---|---:|---:|---:|---:|---:|---|
| I | 0 | 0.97 | 0.03 | 0.00 | 0 | |
| II | 0.2 | 0.65 | 0.35 | 0.02 | 0 | |
| III | ≥ 0.4 | ≤ 0.22 | ≥ 0.78 | ≥ 0.92 | 1 | Bipolar anticonsensus |

---

## 3. \(R_{\mathrm{TRN}}\) \(\lambda\)

Stress-: \(\bar\phi=0.75^3=0.422\), \(\chi=2.5\), \(\bar h=0.35\).

\[
R_{\mathrm{TRN}}(\lambda)=\lambda\cdot\frac{0.422\cdot 2.5}{0.35}\approx 3.01\,\lambda.
\]

| \(\lambda\) | \(R_{\mathrm{TRN}}\) | \(\mathcal{A}\)-rate |
|---:|---:|---:|
| 0.2 | 0.60 | 0.0 |
| 0.4 | 1.21 | 1.0 |
| 1.0 | 3.01 | 1.0 |

** stress-:** \(R_{\mathrm{TRN}}\gtrsim 1 \Leftrightarrow\) \(\bar q,\bar r,\bar m,\bar h\).

---

## 4. stress-sweep

### 4.1. Grid \(q\times r\) \(\lambda=0\)

16 : \(C\approx 0.978\), \(\mathcal{A}=0\). \(q,r\) ** ** TRN.

**:** grid \(\lambda\in\{0.5,0.8\}\).

### 4.2. Sweep \(\chi\times h\) `bipolar`

\(\chi\) \(P_i\); \(\chi\). \(\bar h\) \(S_i\):

| \(\bar h\) | \(C\) ( \(\chi\)) |
|---:|---:|
| 0.15 | 0.912 |
| 0.35 | 0.979 |
| 0.80 | 0.979 |

bipolar + \(\lambda=0\) \(h\) ; .

**:** sweep \(\chi\times h\) `narrative_mode='echo'` \(\lambda>0\).

---

## 5. trast: echo- (`outputs/lambda_sweep.csv`)

`narrative_mode=echo`, \(\bar q=\bar r=0.45\), \(\bar m=0.55\):

| \(\lambda\) | \(C\) | \(\mathcal{A}\) |
|---:|---:|---:|
| 0 | 0.96 | 0 |
| 1.2 | 0.90 | 0 |

Echo + \(q,r\) **** : \(\lambda\) observes \(\lambda=1.2\).

---

## 6. ()

```
λ ( TRN)
                 low              high
              ┌─────────────┬──────────────┐
    high      │  CONSENSUS  │  (no data)│
    q,r       │  echo mode  │              │
              ├─────────────┼──────────────┤
    low       │ SOFT POL    │ ANTICONSENS  │
    q,r       │ (λ≈0.2)     │ (λ≥0.4)      │
    bipolar   │             │ bipolar lock │
              └─────────────┴──────────────┘
                    ↑
              λ_crit ≈ 0.35
```

2D-sweep \((\lambda,\bar q)\) \((\lambda,\bar\phi)\).
