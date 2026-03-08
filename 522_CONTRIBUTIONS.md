## Contribution: Robust Adversarial Watermarks that Violate the Lipschitz Assumption

This project extends the NeurIPS watermark removal impossibility result by constructing watermark techniques that **violate the local Lipschitz assumption** and evaluating their behavior under multiple attacks.

The key idea is to create **adversarially aligned spread-spectrum watermarks** that amplify changes in the latent representation of the image while remaining visually subtle in pixel space. This breaks the smoothness assumption required by the theoretical removal guarantee and allows the watermark signal to survive several common image transformations.

---

## Method Overview

### 1. Adversarial Watermark Construction

We generate watermarked images using a **pairwise spread-spectrum encoding scheme** combined with adversarial optimization.

The pipeline:

1. **Message encoding**
   - A binary message is converted to a bit vector.
   - Each bit is embedded using a pair of latent carriers.

2. **Initial embedding**
   - A small pixel-space perturbation is applied using spread-spectrum embedding.

3. **Adversarial optimization**
   - A projected gradient descent (PGD) procedure modifies the image to:
     - increase the latent amplification of the watermark
     - preserve visual quality
     - maintain detectability before attacks

4. **Lipschitz evaluation**
   - We compute a Lipschitz-style amplification metric

\[
L = \frac{||\phi(x_w) - \phi(x)||}{||x_w - x||}
\]

where  
- \(x\) = original image  
- \(x_w\) = watermarked image  
- \(\phi(\cdot)\) = latent representation from the diffusion model VAE.

Large values of \(L\) indicate that the watermark violates the **local Lipschitz smoothness assumption** required by the theoretical watermark removal guarantee.

---

## Attack Robustness Evaluation

To evaluate the robustness of the adversarial watermark, we apply multiple attack types commonly used in watermark removal and purification pipelines.

### Gaussian Blur (Purification Attack)

Gaussian blur simulates image denoising or purification steps that remove high-frequency perturbations.

Blur radii tested:
r = {2, 4, 6, 8}


Results:

| Blur Radius | Detection Rate | Bit Accuracy |
|-------------|---------------|--------------|
| 2 | 100% | 0.797 |
| 4 | 75% | 0.681 |
| 6 | 65% | 0.631 |
| 8 | 50% | 0.603 |

Observations:

- The watermark remains **fully detectable under mild blur**.
- Detection degrades **gradually rather than catastrophically** as blur increases.
- This indicates that the adversarial watermark signal is not immediately removed by spatial filtering.

---

### JPEG Compression

JPEG compression removes high-frequency information and is a standard destructive transformation used in watermark evaluation.

Compression qualities tested:
q = {90, 70, 50, 30}


Results:

| JPEG Quality | Detection Rate | Bit Accuracy |
|--------------|---------------|--------------|
| 90 | 100% | 0.877 |
| 70 | 100% | 0.858 |
| 50 | 100% | 0.830 |
| 30 | 100% | 0.820 |

Observations:

- The watermark remains **fully detectable even under strong compression**.
- Bit accuracy remains above **0.82 even at quality 30**.
- This indicates strong robustness to compression-based perturbations.

---

## Key Insight

The theoretical watermark removal guarantee assumes that watermarking functions satisfy a **local Lipschitz condition** in the model's latent space.

Our adversarial watermark construction intentionally violates this assumption by:

- aligning perturbations with **latent directions that amplify under encoding**
- producing large latent-space shifts for small pixel perturbations.

Empirically, we observe that such watermarks:

- remain detectable after **Gaussian blur**
- remain detectable after **JPEG compression**
- degrade **gradually under attack rather than being removed entirely**

These results demonstrate that watermark techniques violating the Lipschitz assumption can exhibit **non-trivial robustness to common purification and transformation attacks**.

---

## Summary

This work demonstrates that:

- Adversarially aligned watermark perturbations can **break the Lipschitz assumption** used in watermark removal theory.
- Such watermarks can **remain detectable under multiple image attacks**, including:
  - Gaussian blur
  - JPEG compression
- Robustness degrades **gradually rather than collapsing immediately**, suggesting that adversarial watermark constructions behave differently from watermark schemes covered by the theoretical impossibility result.