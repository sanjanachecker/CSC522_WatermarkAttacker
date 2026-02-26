from PIL import Image, ImageEnhance
import numpy as np
import cv2
import torch
import os
from skimage.util import random_noise
import matplotlib.pyplot as plt
from torchvision import transforms
from tqdm import tqdm
from bm3d import bm3d_rgb
from compressai.zoo import bmshj2018_factorized, bmshj2018_hyperprior, mbt2018_mean, mbt2018, cheng2020_anchor


class WMAttacker:
    def attack(self, imgs_path, out_path):
        raise NotImplementedError


class VAEWMAttacker(WMAttacker):
    """Implements Regen-VAE attack from the paper.
    
    Uses VAE encoder φ and decoder A to instantiate equation (1): x̂ = A(φ(x_w) + N(0,σ²I_d))
    The VAE encoder maps images to latent space, noise is added via quality parameter,
    and decoder reconstructs the image. Lower quality = higher σ (more noise).
    
    Design rationale: CompressAI models (Bmshj2018, Cheng2020) provide pre-trained VAE
    architectures that serve as the embedding function φ and reconstruction algorithm A.
    """
    def __init__(self, model_name, quality=1, metric='mse', device='cpu'):
        # Quality parameter controls noise level σ: lower quality = more compression = more noise
        # This directly implements the destructive process in equation (1)
        if model_name == 'bmshj2018-factorized':
            self.model = bmshj2018_factorized(quality=quality, pretrained=True).eval().to(device)
        elif model_name == 'bmshj2018-hyperprior':
            self.model = bmshj2018_hyperprior(quality=quality, pretrained=True).eval().to(device)
        elif model_name == 'mbt2018-mean':
            self.model = mbt2018_mean(quality=quality, pretrained=True).eval().to(device)
        elif model_name == 'mbt2018':
            self.model = mbt2018(quality=quality, pretrained=True).eval().to(device)
        elif model_name == 'cheng2020-anchor':
            self.model = cheng2020_anchor(quality=quality, pretrained=True).eval().to(device)
        else:
            raise ValueError('model name not supported')
        self.device = device

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path).convert('RGB')
            img = img.resize((512, 512))
            img = transforms.ToTensor()(img).unsqueeze(0).to(self.device)
            out = self.model(img)
            out['x_hat'].clamp_(0, 1)
            rec = transforms.ToPILImage()(out['x_hat'].squeeze().cpu())
            rec.save(out_path)


class GaussianBlurAttacker(WMAttacker):
    def __init__(self, kernel_size=5, sigma=1):
        self.kernel_size = kernel_size
        self.sigma = sigma

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = cv2.imread(img_path)
            img = cv2.GaussianBlur(img, (self.kernel_size, self.kernel_size), self.sigma)
            cv2.imwrite(out_path, img)


class GaussianNoiseAttacker(WMAttacker):
    def __init__(self, std):
        self.std = std

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            image = cv2.imread(img_path)
            image = image / 255.0
            # Add Gaussian noise to the image
            noise_sigma = self.std  # Vary this to change the amount of noise
            noisy_image = random_noise(image, mode='gaussian', var=noise_sigma ** 2)
            # Clip the values to [0, 1] range after adding the noise
            noisy_image = np.clip(noisy_image, 0, 1)
            noisy_image = np.array(255 * noisy_image, dtype='uint8')
            cv2.imwrite(out_path, noisy_image)


class BM3DAttacker(WMAttacker):
    def __init__(self):
        pass

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path).convert('RGB')
            y_est = bm3d_rgb(np.array(img) / 255, 0.1)  # use standard deviation as 0.1, 0.05 also works
            plt.imsave(out_path, np.clip(y_est, 0, 1), cmap='gray', vmin=0, vmax=1)


class JPEGAttacker(WMAttacker):
    def __init__(self, quality=80):
        self.quality = quality

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path)
            img.save(out_path, "JPEG", quality=self.quality)


class BrightnessAttacker(WMAttacker):
    def __init__(self, brightness=0.2):
        self.brightness = brightness

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness)
            img.save(out_path)


class ContrastAttacker(WMAttacker):
    def __init__(self, contrast=0.2):
        self.contrast = contrast

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.contrast)
            img.save(out_path)


class RotateAttacker(WMAttacker):
    def __init__(self, degree=30):
        self.degree = degree

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path)
            img = img.rotate(self.degree)
            img.save(out_path)


class ScaleAttacker(WMAttacker):
    def __init__(self, scale=0.5):
        self.scale = scale

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path)
            w, h = img.size
            img = img.resize((int(w * self.scale), int(h * self.scale)))
            img.save(out_path)


class CropAttacker(WMAttacker):
    def __init__(self, crop_size=0.5):
        self.crop_size = crop_size

    def attack(self, image_paths, out_paths):
        for (img_path, out_path) in tqdm(zip(image_paths, out_paths)):
            img = Image.open(img_path)
            w, h = img.size
            img = img.crop((int(w * self.crop_size), int(h * self.crop_size), w, h))
            img.save(out_path)


class DiffWMAttacker(WMAttacker):
    """Implements Regen-Diffusion attack using Stable Diffusion as described in the paper.
    
    Instantiates equation (1) using Stable Diffusion's architecture:
    - φ(x_w) = √α(t)·E(x_w) where E is VAE encoder (equation 2 from paper)
    - Noise addition: z_t = φ(x_w) + N(0,(1-α(t))I_d) via forward diffusion
    - A = Stable Diffusion's denoising process (backward diffusion)
    
    Design rationale: noise_step parameter controls timestep t, which determines α(t)
    and thus the noise level σ². Higher noise_step = more noise = stronger watermark removal
    but also more image degradation. This is the key trade-off in the paper's CWF guarantee.
    """
    def __init__(self, pipe, batch_size=20, noise_step=60, captions={}):
        self.pipe = pipe
        self.BATCH_SIZE = batch_size
        self.device = pipe.device
        # noise_step controls t in equation (2): higher t means more noise added to latent
        # This directly controls σ² in the paper's impossibility result
        self.noise_step = noise_step
        self.captions = captions
        print(f'Diffuse attack initialized with noise step {self.noise_step} and use prompt {len(self.captions)}')

    def attack(self, image_paths, out_paths, return_latents=False, return_dist=False):
        """Executes the regeneration attack pipeline.
        
        Steps implement the paper's attack:
        1. Encode watermarked image x_w to latent z_0 using VAE encoder (φ)
        2. Add noise via forward diffusion to timestep t (destructive process)
        3. Denoise using Stable Diffusion backward process (constructive process A)
        
        return_latents: Used for Lipschitz constant measurement (CONTRIBUTIONS.md Step 3)
        return_dist: Used to measure latent distance ||φ(x_w) - φ(x)|| for L_x,w calculation
        """
        with torch.no_grad():
            generator = torch.Generator(self.device).manual_seed(1024)
            latents_buf = []
            prompts_buf = []
            outs_buf = []
            # Timestep t controls noise level in equation (2): z_t = √α(t)E(x_w) + N(0,(1-α(t))I_d)
            timestep = torch.tensor([self.noise_step], dtype=torch.long, device=self.device)
            ret_latents = []

            def batched_attack(latents_buf, prompts_buf, outs_buf):
                latents = torch.cat(latents_buf, dim=0)
                images = self.pipe(prompts_buf,
                                   head_start_latents=latents,
                                   head_start_step=50 - max(self.noise_step // 20, 1),
                                   guidance_scale=7.5,
                                   generator=generator, )
                images = images[0]
                for img, out in zip(images, outs_buf):
                    img.save(out)

            if len(self.captions) != 0:
                prompts = []
                for img_path in image_paths:
                    img_name = os.path.basename(img_path)
                    if img_name[:-4] in self.captions:
                        prompts.append(self.captions[img_name[:-4]])
                    else:
                        prompts.append("")
            else:
                prompts = [""] * len(image_paths)

            for (img_path, out_path), prompt in tqdm(zip(zip(image_paths, out_paths), prompts)):
                img = Image.open(img_path)
                img = np.asarray(img) / 255
                img = (img - 0.5) * 2
                img = torch.tensor(img, dtype=self.pipe.vae.dtype, device=self.device).permute(2, 0, 1).unsqueeze(0)
                # Step 1: Map to latent space using VAE encoder E (the φ function in equation 2)
                latents = self.pipe.vae.encode(img).latent_dist
                latents = latents.sample(generator) * self.pipe.vae.config.scaling_factor
                # Step 2: Add Gaussian noise N(0,σ²I_d) - the destructive process
                # This is where the watermark signal is destroyed in the latent space
                noise = torch.randn([1, 4, img.shape[-2] // 8, img.shape[-1] // 8], device=self.device, dtype=self.pipe.vae.dtype)
                if return_dist:
                    # Return latent distance for Lipschitz constant calculation (CONTRIBUTIONS.md)
                    return self.pipe.scheduler.add_noise(latents, noise, timestep, return_dist=True)
                # Apply forward diffusion: z_t = √α(t)·z_0 + √(1-α(t))·ε
                latents = self.pipe.scheduler.add_noise(latents, noise, timestep)
                latents_buf.append(latents)
                outs_buf.append(out_path)
                prompts_buf.append(prompt)
                if len(latents_buf) == self.BATCH_SIZE:
                    # Step 3: Reconstruct image using denoising (the constructive process A)
                    # Stable Diffusion denoises from z_t back to clean latent, then VAE decodes
                    batched_attack(latents_buf, prompts_buf, outs_buf)
                    latents_buf = []
                    prompts_buf = []
                    outs_buf = []
                if return_latents:
                    # Return noisy latents for Lipschitz measurement (CONTRIBUTIONS.md Step 3)
                    ret_latents.append(latents.cpu())

            if len(latents_buf) != 0:
                batched_attack(latents_buf, prompts_buf, outs_buf)
            if return_latents:
                return ret_latents
