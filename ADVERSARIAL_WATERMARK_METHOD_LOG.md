# Adversarial Watermark Method Log

This document records the main adversarial watermarking approaches attempted in this project and the reported outcomes, with emphasis on the `L` vs detection-rate tradeoff.

## Metric Notes

- `L` is the local Lipschitz-style amplification metric used in the notebook.
- "Before attack detection" is the primary recoverability metric.
- "After attack detection" is secondary (useful context, not primary success criterion).
- Detection is based on the configured bit threshold in each run.

---

## Iteration 1: Initial PGD Adversarial Perturbation (Latent-Only Emphasis)

### Method

- Start from a standard invisible watermark image.
- Apply PGD to maximize latent distance `||phi(x_adv)-phi(x_clean)||^2`.
- No strong decoder-preservation mechanism.

### Reported Output

- `L = 15.4450 ± 10.7339`
- Before attack detection rate: `0.0%`
- Before attack avg bit accuracy: `0.492`
- Interpretation: high latent amplification but watermark message effectively destroyed.

### Takeaway

- Can produce high `L`.
- Fails the primary requirement (detectable watermark before attack).

---

## Iteration 2: Decoder-Constrained / Attack-Aware PGD (Conservative Constraint)

### Method

- Added decode constraints and candidate checks during optimization.
- Intended to preserve message while increasing latent displacement.

### Reported Output

- `L = 2.1420 ± 2.2327` (collapsed to near baseline)
- Before attack detection rate: `75.0%`
- Before attack avg bit accuracy: `0.869`
- After attack detection rate: `0.0%`
- After attack avg bit accuracy: `0.502`

### Takeaway

- Detection improved compared to Iteration 1.
- `L` amplification collapsed; adversarial effect became weak.

---

## Iteration 3: Latent Preconditioning + Method Selection (Classic Watermarkers)

### Method

- Latent-boost preconditioning then watermark embedding.
- Tried multiple classic watermark methods (`dwtDctSvd`, `rivaGan`, `dwtDct`) and selected candidates.

### Reported Output

- Method usage: `rivaGan 16/20`, `dwtDctSvd 4/20`
- `L = 3.9370 ± 2.7838`
- Before attack detection rate: `100.0%`
- Before attack avg bit accuracy: `0.986`
- After attack detection rate: `0.0%`
- After attack avg bit accuracy: `0.530`

### Takeaway

- Excellent pre-attack detectability.
- `L` only modestly above baseline; limited adversarial amplification.

---

## Iteration 4: Joint Spread-Spectrum (SS) + Latent Optimization

### Method

- Custom differentiable SS embed/decode with joint objective:
  - increase latent displacement,
  - preserve SS bit margins.

### Reported Output

- `L = 53.9676 ± 65.7544`
- Before attack detection rate: `0.0%`
- Before attack avg bit accuracy: `0.500`
- After attack detection rate: `0.0%`
- After attack avg bit accuracy: `0.477`

### Takeaway

- Very high `L`.
- Detection collapsed to chance; likely embedding/decoder mismatch/calibration issue.

---

## Iteration 5: Two-Stage SS Constrained Optimization + Objective-Aligned Reporting

### Method

- Two-stage optimization:
  1. watermark imprint stage,
  2. constrained latent-boost stage.
- Added attacked-image quality metrics and objective checks.

### Reported Output

- `L = 49.9653 ± 63.2594`
- Before attack detection rate: `0.0%`
- Before attack avg bit accuracy: `0.556`
- After attack detection rate: `30.0%`
- After attack avg bit accuracy: `0.559`
- Attacked quality: `PSNR 21.92`, `SSIM 0.6749`

### Takeaway

- Strong `L` and strong attack utility degradation.
- Primary objective (pre-attack detectability) still failed.

---

## Iteration 6: Pairwise SS Detector + Runtime Reduction

### Method

- Pairwise carriers per bit with differential decode (`corr(c1)-corr(c0)`).
- Smaller sweep and one attack evaluation per selected candidate to reduce runtime.

### Reported Output

- `L = 5.0419 ± 4.0154`
- Before attack detection rate: `40.0%`
- Before attack avg bit accuracy: `0.684`
- After attack detection rate: `55.0%`
- After attack avg bit accuracy: `0.605`

### Takeaway

- Detection improved compared to earlier SS variants.
- `L` dropped too much; not enough adversarial amplification.

---

## Iteration 7: Dual-Layer Strategy (High-L Base + Classic Detectable Seal)

### Method

- First generate high-`L` adversarial base (latent-only PGD).
- Then apply a classic detectable watermark as a "seal" layer.

### Reported Output

- `L = 12.8096 ± 4.5654`
- Before attack detection rate: `100.0%`
- Before attack avg bit accuracy: `1.000`
- After attack detection rate: `5.0%`
- After attack avg bit accuracy: `0.506`
- Pre-attack quality: `PSNR 32.75`, `SSIM 0.9470`
- Attacked quality: `PSNR 21.84`, `SSIM 0.6700`

### Takeaway

- Best pre-attack detectability so far.
- `L` improved meaningfully but still lower than the highest-`L` SS runs.
- Represents a practical middle ground.

---

## Iteration 8: Retuned Dual-Layer (More L-Dominant Selection)

### Method

- Wider `epsilon_total`, more latent steps.
- Strict pre-attack detectability gate, then L-dominant ranking.
- Single attack eval per selected candidate to keep runtime reasonable.

### Status

- Implemented, awaiting a full run output report after tuning.

---

## Summary of Tradeoff Pattern

- **High `L`, low detection**:
  - Joint/custom SS variants achieved very high `L` (`~50-68`) but often near-chance pre-attack bit accuracy (`~0.50-0.56`).
- **High detection, moderate `L`**:
  - Classic-method-based approaches (especially with final sealing) gave excellent pre-attack detection (`~100%`) with moderate `L` (`~4-13`).
- **Best practical compromise so far**:
  - Dual-layer high-`L` base + classic watermark seal.

---

## Recommendations for Discussion

When presenting results, frame methods in two categories:

1. **Adversarial-dominant methods** (maximize `L`):
   - Pro: strongly violate small-`L` assumption.
   - Con: watermark recoverability can collapse if decoder calibration lags.

2. **Detection-dominant methods** (maximize pre-attack recoverability):
   - Pro: reliable watermark detection before attack.
   - Con: smaller `L` gains unless adversarial component is pushed harder.

This directly supports your narrative: there is a measurable tension between maximizing latent adversarial amplification and preserving robust message detectability.

