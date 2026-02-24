Here is the context document designed specifically to guide an AI coding agent in building and executing the proposed adversarial watermark experiment. 

# Context & Specifications: Breaking the "Provably Removable" Watermark Guarantee

## 1. Project Objective
This project aims to computationally demonstrate a theoretical limitation in the NeurIPS 2024 paper *Invisible Image Watermarks Are Provably Removable Using Generative AI*. 

The paper establishes a mathematical "impossibility result" claiming that invisible watermarks can be uniformly removed by adding noise to an image's latent embedding and reconstructing it. However, this proof relies on a specific mathematical assumption about the attacker's embedding network. Your goal is to write code that violates this assumption by designing an **adversarial watermark**, proving that such watermarks can resist the paper's proposed attacks unless the attacker completely destroys the image quality.

## 2. Core Paper Concepts & Mathematical Framework
To implement the experiment, you must understand the paper's core attack and theoretical trade-off.

**The Regeneration Attack Pipeline:**
The authors propose removing watermarks by mapping the watermarked image to a latent space, adding Gaussian noise to destroy the watermark signal, and reconstructing the image.
*   **Formula:** $\hat{x} = \mathcal{A}(\phi(x_w) + \mathcal{N}(0, \sigma^2I_d))$.
*   **Variables:** 
    *   $x_w$: The watermarked image.
    *   $\phi$: The neural embedding function (e.g., the encoder of a VAE or a Diffusion model).
    *   $\sigma$: The level of Gaussian noise added to the embedding.
    *   $\mathcal{A}$: The generative reconstruction algorithm (e.g., Diffusion backward process or VAE decoder).

**The Theoretical Guarantee (The Target for Defeat):**
The paper guarantees a state of "Certified Watermark-Free" (CWF) based on this trade-off function between False Positive Rate ($\epsilon_1$) and False Negative Rate ($\epsilon_2$):
*   $f(\epsilon_1) = \Phi \left( \Phi^{-1}(1- \epsilon_1) - \frac{L_{x,w}\Delta}{\sigma} \right)$.

**The Vulnerability ($L_{x,w}$):**
The guarantee entirely depends on $L_{x,w}$, the **Local Watermark-Specific Lipschitz property**. This parameter measures how much the embedding function $\phi$ compresses or amplifies the watermark. 
*   **The Assumption:** The paper assumes $L_{x,w}$ is a small constant.
*   **The Exploit:** Deep neural networks are vulnerable to adversarial examples. The authors admit that if a watermark is "carefully designed such that the injected perturbation is aligned with an adversarial perturbation," the Lipschitz constant $L_{x,w}$ will become $\gg 1$. 
*   **The Consequence:** If $L_{x,w}$ is massive, the term $\frac{L_{x,w}\Delta}{\sigma}$ explodes. To maintain the CWF guarantee, the attacker must increase the noise $\sigma$ to a level that destroys the image.

## 3. Experimental Pipeline to Implement

You will code an experiment that weaponizes this vulnerability using Projected Gradient Descent (PGD).

### Phase 1: Setup and Baselines
*   **Datasets:** Use 500 images from MS-COCO (real photos) or Stable Diffusion Prompt (SDP) datasets to match the paper's benchmarks.
*   **Attacker Model ($\phi$ and $\mathcal{A}$):** Use the pre-trained `Stable Diffusion-v2.1` model (forward process as $\phi$, backward process as $\mathcal{A}$) or VAE models from the CompressAI library (`Bmshj2018` or `Cheng2020`).
*   **Invisibility Constraint ($\Delta$):** Establish an $\ell_2$-distance budget $\Delta$. You can benchmark this against the pixel distance of standard watermarks like `DwtDctSvd` or `SSL`. 

### Phase 2: Generating the Adversarial Watermark (PGD)
Create a post-processing watermarking function that applies a perturbation $\delta$ to a clean image $x$ to create $x_{adv}$.
1.  **Objective:** Treat the attacker's embedding $\phi$ as a white-box model. Write a PGD loop to maximize the latent distance: $J = ||\phi(x + \delta) - \phi(x)||^2$.
2.  **Constraint:** Project $\delta$ back onto the $\ell_2$-ball of radius $\Delta$ at each step to ensure the watermark remains invisible in the pixel space.
3.  **Measurement:** Calculate the new Lipschitz constant: $L_{adv} = \frac{||\phi(x_{adv}) - \phi(x)||}{\Delta}$. Log this value to prove $L_{adv} \gg 1$.

### Phase 3: Executing the Attack & Measuring Resilience
1.  **Standard Attack:** Run the attacked model's regeneration process on $x_{adv}$ using standard noise levels (e.g., $\sigma \approx 1.16\Delta$).
2.  **Detection Metric:** Run a standard watermark detector. Measure the **True Positive Rate at 1% False Positive Rate (TPR@FPR=0.01)**.
    *   *Goal:* The TPR should remain near $1.000$, proving the watermark survived the certified attack.
3.  **Utility Destruction:** Incrementally increase $\sigma$ until the TPR drops (the watermark is removed). At this threshold, measure the image quality using **PSNR** and **SSIM**. 
    *   *Goal:* Show that the PSNR and SSIM are so low that the image is visually ruined, proving the method fails the paper's requirement to maintain "comparable quality to the original".