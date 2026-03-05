# Adversarial Watermark: Simple and In-Depth Explanation

## Simple Explanation

The code creates a watermark that does two things at once:

1. It puts a secret message into the image.
2. It makes the image very sensitive in the attacker's latent space, so the measured Lipschitz constant `L` becomes large.

How it works in plain terms:

- It first converts the secret text (like `"test"`) into bits.
- For each bit, it creates two random watermark patterns (a 0-pattern and a 1-pattern).
- It builds a "watermark template" by selecting the 0-pattern or 1-pattern for each bit and adds that template to the clean image (small perturbation, constrained by epsilon).
- Then it runs gradient-based optimization to push the image farther away in VAE latent space (to increase `L`) while forcing the watermark bits to stay decodable.
- It tries a few parameter settings and picks the candidate with the best tradeoff:
  - high pre-attack watermark bit accuracy (primary),
  - high `L`,
  - good image quality before attack.
- Finally, it runs one regeneration attack for the selected candidate and records quality/detection metrics.

Why this is adversarial:

- The perturbation is intentionally aligned with model sensitivity, so small pixel changes cause large latent changes.
- This can force the attacker to add more destructive noise to remove watermark signals, hurting regenerated image quality.

---

## In-Depth Explanation

### 1. Core Objective

The notebook optimizes an image perturbation under norm constraints to satisfy:

- **Watermark objective**: embed a recoverable bitstring before attack.
- **Adversarial objective**: maximize latent displacement in attacker embedding (`vae.encode`), increasing
  \[
  L_{x,w} \approx \frac{\|\phi(x_w)-\phi(x)\|}{\|x_w-x\|}.
  \]
- **Quality objective**: keep pre-attack image quality high (PSNR/SSIM thresholds).

This is a constrained multi-objective search, with pre-attack detectability weighted highest during candidate selection.

### 2. Pairwise Spread-Spectrum Watermark (Implementation Fix)

The current code uses a **pairwise carrier scheme** rather than single-carrier correlation.

- For each bit `i`, it builds two pseudo-random carriers:
  - `c0_i` represents bit 0,
  - `c1_i` represents bit 1.
- Decode uses **differential correlation**:
  \[
  \text{logit}_i = \langle x, c1_i \rangle - \langle x, c0_i \rangle.
  \]
- Predicted bit is `1` if `logit_i > 0`, else `0`.

Why this helps:

- Differential decoding cancels part of host-image bias and stabilizes bit decisions.
- It is usually more robust than absolute-sign correlation on one carrier.

### 3. Seed Embedding Stage

`pair_seed_embed(...)` builds a deterministic initial watermark:

- It chooses the correct carrier (0 or 1) per bit and sums them into a normalized template.
- It adds the template to the clean image within an `L2`-style projection step controlled by `epsilon_seed`.

This gives a strong initial decodable watermark before adversarial latent optimization starts.

### 4. Constrained Latent Boost Stage

`pgd_latent_boost_constrained(...)` then performs PGD-like steps:

- **Latent term**: maximize latent distance from clean image (`-||z_adv - z_clean||^2` loss form).
- **Watermark margin term**: enforce positive signed margins for target bits under lightweight augmentations.
- **Projection**: each update is projected back near the clean image (`epsilon_total`) and clamped to valid range.

The combined loss is:
\[
\mathcal{L} = -\|z_{adv} - z_{clean}\|^2 + \lambda_{wm}\cdot \mathcal{L}_{margin}.
\]

This maintains bit decodability pressure while increasing `L`.

### 5. Candidate Search and Selection

For each image, the code evaluates a small hyperparameter grid (runtime-optimized):

- `epsilon_seed` in a short list,
- `epsilon_total` in a short list,
- fixed or narrow `lambda_wm` settings,
- reduced optimization steps (`40`) for speed.

For each candidate it computes:

- pre-attack detection stats (bit accuracy, p-value, detection flag),
- Lipschitz proxy metrics (`L`, pixel distance, latent distance),
- pre-attack image quality metrics (PSNR/SSIM/MS-SSIM).

Score emphasizes pre-attack detection first, then adversarial effect:

\[
\text{score} = 40\cdot \text{bit\_acc}_{pre} + 0.7\cdot L + 0.5\cdot \text{margin}_{pre}.
\]

### 6. Runtime Optimization

To keep runtime practical:

- Candidate sweep is reduced.
- PGD steps are reduced (`40` instead of larger values).
- Regen attack is not run for every candidate.
- Regen attack is run once on the selected best candidate per image.

This cuts the largest bottleneck while preserving core evaluation.

### 7. Metrics Recorded

The notebook records:

- `adversarial_results`: `L`, pixel/latent distances, pre-attack PSNR/SSIM/MS-SSIM.
- `detection_before_attack`: primary watermark detectability metric.
- `detection_after_regen_vae`: secondary metric.
- `attacked_image_quality`: original vs attacked/regenerated quality.
- `selected_hyperparams`: mean chosen settings.

### 8. Interpretation of Results

- If pre-attack detection is high and `L` is high, the watermark is successfully embedded and adversarial.
- If attacked image quality drops strongly (low PSNR/SSIM), the removal attack becomes practically costly.
- If pre-attack detection is still low, the problem is likely in embedding/detector calibration (carrier scale, margin target, thresholds), not only ranking.

