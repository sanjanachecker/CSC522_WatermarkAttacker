To demonstrate that the Local Watermark-Specific Lipschitz property ($L_{x,w}$) is violated, one must experimentally prove that a small change in the input pixels (the watermark) results in a disproportionately large change in the internal representation (the embedding) of the model used for the attack.

Experimental Process to Test the Lipschitz Property
1. Setup: Select the Embedding Model ($\phi$) Choose a deep neural network embedding function $\phi$ typically used in regeneration attacks. According to the paper, valid candidates include:

The encoder of a Variational Autoencoder (VAE) (e.g., those from the CompressAI library like Bmshj2018 or Cheng2020).
The forward diffusion process of a Latent Diffusion Model (e.g., Stable Diffusion v2.1) which maps an image to its latent representation $z_0$.

2. Step 1: Establish a Baseline with Standard Watermarks First, measure the Lipschitz constant $L_{x,w}$ for "standard" invisible watermarks to see how the property behaves under normal conditions.

Action: Apply standard watermarking schemes (e.g., DwtDctSvd, RivaGAN, or SSL) to a set of cover images $x$ to create watermarked images $x_w$.
Measurement: For each image, calculate two distances:
Pixel Distance: The Euclidean distance in the pixel space: $|| x_w - x ||$.
Latent Distance: The Euclidean distance in the embedding space: $|| \phi(x_w) - \phi(x) ||$.
Calculation: Compute the ratio $L_{x,w} \approx \frac{|| \phi(x_w) - \phi(x) ||}{|| x_w - x ||}$.
Expected Result: As shown in the paper's empirical data (Figure 5), for standard watermarks, the latent distance usually remains comparable to or smaller than the pixel distance, implying a small, stable $L_{x,w}$.

3. Step 2: Construct an "Adversarial" Watermark To prove the violation of the property, you must deliberately engineer a watermark that exploits the sensitivity of the neural network embedding $\phi$. The authors explicitly state that $L_{x,w}$ might become much larger than 1 due to "widely observed adversarial examples".

Action: Instead of using a standard watermarking algorithm, use an adversarial attack method (such as Projected Gradient Descent or PGD) to generate a perturbation $\delta$.
Objective: Maximize the distance in the latent space $|| \phi(x + \delta) - \phi(x) ||$ while keeping the pixel perturbation constrained within the invisibility limit ($|| \delta || \le \Delta$).
Context: This simulates a "carefully designed" watermark where the injected noise is aligned with the gradients of the attacker's embedding network.

4. Step 3: Measure the Violation Apply this adversarial perturbation to the clean images to create globally "invisible" but locally "adversarial" watermarked images ($x_{adv}$).

Calculation: Re-calculate the ratio: $L_{adv} = \frac{|| \phi(x_{adv}) - \phi(x) ||}{|| x_{adv} - x ||}$.
Analysis: Compare $L_{adv}$ against the baseline $L_{x,w}$.
How to Interpret the Results
The Lipschitz property is considered violated in this context if $L_{adv}$ is orders of magnitude larger than 1 (or the baseline).

If the Property Holds: The ratio $L_{adv}$ remains small. This would imply the embedding function $\phi$ is robust and "compresses" the perturbations, meaning the watermarked image and original image remain close in the latent space.
If the Property is Violated: The ratio $L_{adv}$ explodes ($\gg 1$). This means a tiny, invisible change in pixels caused a massive jump in the latent space.

Consequences of Violation: If the experiment shows $L_{adv} \gg 1$, the paper's theoretical guarantee for watermark removal fails. The method relies on adding noise $\sigma$ to bridge the gap between the watermarked and clean distributions. If the gap (latent distance) is massive due to a high Lipschitz constant, the attacker would have to increase the noise $\sigma$ to a level that destroys the image quality to successfully remove the watermark, thereby rendering the attack useless.

