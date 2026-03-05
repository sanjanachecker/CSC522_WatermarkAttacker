# Adversarial Watermark: Current Code (Simple + In-Depth)

This document explains the **current main pipeline** in `compute_lipschitz_metrics.ipynb`:

- build a **high-`L` adversarial base image** with latent-space PGD,
- then apply a **standard invisible watermark seal** (`DwtDctSvd` or `RivaGAN`) so detection is reliable before attack.

The goal is to keep the best parts of both worlds:

1. strong adversarial amplification (`L`), and  
2. strong pre-attack watermark detectability.

---

## Simple Explanation

Think of the method as a two-layer design:

1. **Adversarial layer**:
   - Start from a clean image.
   - Add a carefully optimized perturbation that makes the attacker model’s latent embedding change a lot.
   - This raises the measured `L` value.

2. **Watermark layer (seal)**:
   - Take that adversarial image and apply a normal invisible watermarking method (`dwtDctSvd` or `rivaGan`).
   - This ensures the watermark is still readable before attack with a known decoder.

Then for each image, the code tries a few settings and keeps the candidate that:

- passes pre-attack detectability and quality gates,
- and has a high `L`.

After that, it runs the regeneration attack and reports:

- before-attack detection,
- after-attack detection,
- pre- and post-attack image quality,
- and `L` statistics.

---

## In-Depth Explanation

### 1. Pipeline Structure

The notebook now uses this per-image loop:

1. Load clean image tensor `x_clean`.
2. Generate adversarial base with `pgd_latent_only(...)`.
3. Seal base image with each classic watermark method:
   - `dwtDctSvd`
   - `rivaGan`
4. Evaluate candidate (pre-attack detectability + `L` + quality).
5. Keep best candidate.
6. Run one regen attack on selected candidate.
7. Record all metrics.

This is implemented in the main generation cell (`Step 4`).

### 2. Adversarial Base (`pgd_latent_only`)

`pgd_latent_only(x_clean, vae, epsilon_total, alpha, steps)` performs PGD to maximize latent displacement:

\[
\max \|\phi(x_{adv}) - \phi(x_{clean})\|^2
\]

with projection/clamping constraints per step (bounded perturbation and valid image range).

Why this matters:

- `L` scales with latent distance over pixel perturbation.
- Maximizing latent distance makes the watermarked image more adversarial to the regeneration attacker.

### 3. Final Watermark Seal

After producing `x_adv_base`, the code applies:

- `InvisibleWatermarker('test', 'dwtDctSvd')` and
- `InvisibleWatermarker('test', 'rivaGan')`.

Then it decodes with the same standard decoder (`detect_watermark(...)`) and computes:

- detection boolean (threshold on bit matches),
- bit accuracy,
- p-value.

This is the key design decision: detectability uses a mature, fixed watermark decoder rather than a custom learned/differentiable detector.

### 4. Candidate Gating and Ranking

A candidate is only considered if it meets pre-attack quality and detectability constraints (current tuned gates in notebook), then scored.

Current ranking idea:

- detectability gate first,
- then score weighted toward larger `L`.

This is intentionally different from earlier versions that over-prioritized watermark margin terms and reduced `L`.

### 5. Attack Evaluation

For selected candidates, the code runs regen attack with:

- `VAEWMAttacker('bmshj2018-factorized', quality=1, ...)`

and computes:

- post-attack detection (secondary),
- attacked-image quality vs original (`PSNR/SSIM/MS-SSIM`).

This supports the practical argument: even when watermark gets removed, the regenerated image quality can degrade substantially.

### 6. Why This Version Exists

Earlier variants showed two failure modes:

1. very high `L`, poor pre-attack detectability, or
2. good detectability, but weak `L`.

Current dual-layer version is meant to break that deadlock:

- adversarial objective handled by latent-only optimizer,
- detection objective handled by standard watermark seal.

### 7. Reported Outputs and Interpretation

The notebook reports:

- `adversarial_results`: mean/std `L`, pre-attack quality,
- `detection_before_attack`: primary objective,
- `detection_after_regen_vae`: secondary,
- `attacked_image_quality`: utility after attack,
- `violation_ratio`: adversarial `L` over baseline `L`.

How to explain to peers:

- If pre-attack detection is high and `L` is much larger than baseline, the method succeeds at constructing an adversarially amplified watermark.
- If attacked-image quality is poor while removing/damaging watermark, the attacker’s practical usefulness is reduced.

### 8. Practical Tradeoff

The main tradeoff in tuning is:

- larger adversarial budget (`epsilon_total`, steps) usually increases `L`,
- but can reduce pre-attack image quality and sometimes hurt watermark decoding.

Current code balances this with:

- small hyperparameter grid,
- hard pre-attack gates,
- and `L`-weighted ranking after gates.

---

## One-Line Summary for Presentation

The current method creates an adversarial image that maximizes latent sensitivity first, then seals it with a standard invisible watermark so it remains detectable before attack while still achieving significantly elevated `L`.
