from PIL import Image
import torch
import math
from pytorch_msssim import ssim, ms_ssim
from torchvision import transforms


def compute_psnr(a, b):
    """Compute Peak Signal-to-Noise Ratio for image quality assessment.
    
    Used in CONTEXT.md Phase 3 to measure utility destruction: when attacker increases
    noise σ to remove adversarial watermark, PSNR drops, proving image is ruined.
    Goal: Show PSNR is too low when watermark is finally removed.
    """
    mse = torch.mean((a - b) ** 2).item()
    if mse == 0:
        return 100
    return -10 * math.log10(mse)


def compute_msssim(a, b):
    return ms_ssim(a, b, data_range=1.).item()


def compute_ssim(a, b):
    """Compute Structural Similarity Index for perceptual image quality.
    
    Used alongside PSNR in CONTEXT.md Phase 3 to demonstrate that when the
    adversarial watermark is removed, SSIM is so low the image is visually ruined.
    This proves the paper's method fails to maintain 'comparable quality to original'.
    """
    return ssim(a, b, data_range=1.).item()


def eval_psnr_ssim_msssim(ori_img_path, new_img_path):
    """Evaluate image quality metrics between original and attacked images.
    
    Critical for CONTEXT.md Phase 3: Measure utility destruction when attacker
    increases σ to remove watermark. Low PSNR/SSIM proves the attack fails the
    paper's requirement to maintain image quality.
    """
    ori_img = Image.open(ori_img_path).convert('RGB')
    new_img = Image.open(new_img_path).convert('RGB')
    if ori_img.size != new_img.size:
        new_img = new_img.resize(ori_img.size)
    ori_x = transforms.ToTensor()(ori_img).unsqueeze(0)
    new_x = transforms.ToTensor()(new_img).unsqueeze(0)
    return compute_psnr(ori_x, new_x), compute_ssim(ori_x, new_x), compute_msssim(ori_x, new_x)


def bytearray_to_bits(x):
    """Convert bytearray to a list of bits for watermark detection.
    
    Used to decode watermark messages and compute bit accuracy for TPR@FPR=0.01
    measurement (CONTEXT.md Phase 3). High bit accuracy = watermark survived attack.
    """
    result = []
    for i in x:
        bits = bin(i)[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result
