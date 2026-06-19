# Module 2 · Generative AI — Phase 08 Extract

> Source: `phases/08-generative-ai/` (15 lessons, 01–14 + 19). Phase README is a stub; all content lives in per-lesson `docs/en.md`.
> **Seam note:** This phase is largely antilibrary for the AI-Engineering-from-Scratch core. Per CONTEXT.md Target 4, only `08-controlnet-lora-conditioning` and `14-evaluation-fid-clip-score` are seam-relevant; every other lesson is flagged `[CHECK: possibly antilibrary]` — kept for reference, likely outside the core sequence.
> Tag legend: `[CHECK: possibly antilibrary]` = generative-media lesson outside the LLM/agent seam.

## Lessons

### 01 · Generative Models — Taxonomy & History — **Learn** · Python · ~45 minutes [CHECK: possibly antilibrary]
This lesson categorizes the history of generative modeling into five families—explicit density (autoregressive, flows), explicit approximate (VAE, diffusion), implicit density (GAN), score-based, and token-based autoregressive—explaining the mathematical trade-offs like tractability and inference speed. It covers key algorithms including PixelCNN, RealNVP, VAE, DDPM, GAN, and flow matching, charting their evolution from 2013 to 2026. The student builds a visualization script fitting a 1-D mixture-of-Gaussians to concretely demonstrate the distinction between explicit density estimation and implicit generation.
**Tools/APIs:** Python, PixelCNN, WaveNet, RealNVP, Glow, VAE, DDPM, GAN, StyleGAN, Flow Matching

### 02 · Autoencoders & Variational Autoencoders (VAE) — **Build** · Python · ~75 minutes [CHECK: possibly antilibrary]
This lesson teaches the architecture of Variational Autoencoders (VAEs), contrasting the unstructured latent space of standard autoencoders with the Gaussian distribution enforced by the VAE's KL divergence penalty. Students implement a VAE from scratch using only the Python standard library—eschewing NumPy and PyTorch—to encode, reconstruct, and generate 8-dimensional synthetic data. The code covers the reparameterization trick $z = \mu + \sigma\cdot\epsilon$, the ELBO loss calculation, and manual backpropagation through single-layer MLPs. The final artifact is a generative model that can sample new data points by decoding from the prior distribution $N(0, I)$.
**Tools/APIs:** MNIST, Stable Diffusion VAE, Flux VAE, Encodec, Diffusers

### 03 · GANs — Generator vs Discriminator — **Build** · Python · ~75 minutes [CHECK: possibly antilibrary]
This lesson implements Generative Adversarial Networks (GANs) from scratch, training a generator and discriminator on a 1-D mixture of Gaussians to demonstrate adversarial training and failure modes like mode collapse. Students construct a custom training loop using non-saturating loss and produce a debugging protocol for failing GAN runs. The lesson reviews key variants including DCGAN, WGAN, and StyleGAN, highlighting the algorithm's role in sharp generation and perceptual losses.
**Tools/APIs:** DCGAN, WGAN, WGAN-GP, Spectral normalization, Progressive GAN, StyleGAN, StyleGAN2, StyleGAN3, StyleGAN-XL, R3GAN, Pix2Pix, CycleGAN, ControlNet, SDXL-Turbo, SD3-Turbo, LCM

### 04 · Conditional GANs & Pix2Pix — **Build** · Python · ~75 minutes [CHECK: possibly antilibrary]
This lesson teaches the architecture and training of Conditional GANs (cGANs), specifically focusing on the Pix2Pix framework for paired image-to-image translation tasks like sketch-to-photo. It explains the use of a U-Net generator with skip connections and a PatchGAN discriminator for local realism, employing a combined adversarial and L1 loss function. Students implement a tiny 1-D conditional GAN in `code/main.py` that generates samples conditioned on class labels by appending one-hot encoded inputs to both the generator and discriminator.
**Tools/APIs:** Conditional GAN, U-Net, PatchGAN

### 05 · StyleGAN — **Build** · Python · ~45 minutes [CHECK: possibly antilibrary]
The lesson covers the StyleGAN architecture, which disentangles the latent space by mapping a random vector $z$ to an intermediate code $w$ through an MLP and injecting it into the synthesis network via Adaptive Instance Normalization (AdaIN). It explains the components of the generator, including constant input, upsampling blocks, per-layer noise for stochastic details, and the truncation trick for inference. Students implement a simplified 1-D "style-GAN lite" model in `code/main.py` to demonstrate affine modulation outperforming direct latent input. The lesson also surveys architectural advancements in StyleGAN2 and StyleGAN3, such as weight demodulation and alias-free convolutions, along with inversion techniques like e4e.
**Tools/APIs:** StyleGAN, StyleGAN2, StyleGAN3, StyleGAN-XL, e4e, ReStyle, HyperStyle, InterFaceGAN

### 06 · Diffusion Models — DDPM from Scratch — **Build** · Python · ~75 minutes [CHECK: possibly antilibrary]
The lesson implements a Denoising Diffusion Probabilistic Model (DDPM) from scratch, training a neural network to predict Gaussian noise added across a forward Markov chain to learn a reverse denoising process. Students build a 1-D diffusion sampler using a tiny MLP with sinusoidal time embeddings on a two-mode mixture dataset, optimizing via simplified MSE loss. The curriculum covers the closed-form forward schedule, the algebraic reverse step derivation, and sampling logic, while explaining production optimizations like DDIM, cosine schedules, and classifier-free guidance.

**Tools/APIs:** DDPM, U-Net, DiT, DDIM, DPM-Solver, TensorRT-LLM, torch.compile, xformers

### 07 · Latent Diffusion & Stable Diffusion — **Build** · Python · ~75 minutes [CHECK: possibly antilibrary]
The lesson implements the Latent Diffusion Model (LDM) architecture to mitigate the computational expense of pixel-space diffusion by operating within a compressed VAE latent space. Students build a toy two-stage pipeline in `code/main.py` that stacks a simplified 1-D VAE onto a DDPM from Lesson 06, adding classifier-free guidance to demonstrate that diffusion loss functions identically on latent codes as on raw data. The curriculum covers the evolution from U-Net-based backbones (SD 1.5, SDXL) to Diffusion Transformers (DiT, MMDiT) in modern models like SD3 and Flux, detailing cross-attention for text conditioning, latent scaling factors, and inference optimizations like quantization and CPU offloading.
**Tools/APIs:** PyTorch, Hugging Face Diffusers, Stable Diffusion (1.5, 2.1, XL, 3), Flux.1, CLIP, T5-XXL, bitsandbytes

### 08 · ControlNet, LoRA & Conditioning — **Build** · Python · ~75 minutes
This lesson teaches how to extend frozen diffusion backbones using ControlNet for spatial conditioning and LoRA for efficient low-rank adaptation. Students implement 1-D simulations of ControlNet's zero-convolution skip connections and LoRA's matrix decomposition ($W + BA$) to modify model behavior without full retraining. The lesson culminates in a skill artifact that composes production-ready pipelines by stacking SDXL with multiple ControlNets, LoRAs, and IP-Adapters. It covers techniques like zero-initialization, rank-based parameter reduction, and the composability of style versus spatial control signals.

**Tools/APIs:** Stable Diffusion, SDXL, U-Net, ControlNet, LoRA, IP-Adapter, CLIP, HuggingFace Diffusers, DreamBooth, Textual Inversion, T2I-Adapter

### 09 · Inpainting, Outpainting & Image Editing — **Build** · Python · ~75 minutes [CHECK: possibly antilibrary]
This lesson explores diffusion-based inpainting, outpainting, and image editing techniques, contrasting naive mask injection with the 9-channel U-Net architecture that consumes concatenated noisy latents, encoded images, and masks. It covers training-free methods like SDEdit and RePaint, alongside instruction-based models like InstructPix2Pix, to handle tasks such as object removal and canvas extension. Students implement a 1-D DDPM on 5-dimensional data to perform mask-aware reverse diffusion, regenerating masked dimensions while preserving unmasked context. The lesson defines production pipelines that combine segmentation models like SAM with inpainting pipelines for high-fidelity image editing.
**Tools/APIs:** Flux.1-Fill, Stable Diffusion Inpaint, SDXL-Inpaint, DALL-E 3 Edit, Diffusers, ControlNet-Openpose, SAM, SAM 2, InstructPix2Pix, RePaint, SDEdit

### 10 · Video Generation — **Build** · Python · ~45 minutes [CHECK: possibly antilibrary]
This lesson teaches video generation using Diffusion Transformers (DiT) on spatiotemporal latents to solve the compute intensity and temporal coherence issues of pixel-space diffusion. Students build a pure Python simulation of a spatiotemporal DiT that patches a synthetic video, applies 3D positional embeddings, and performs joint denoising across the sequence to enforce temporal structure. The curriculum covers 3D VAEs, factorized attention (splitting spatial and temporal attention), and text conditioning, comparing production models like Sora against open-weights alternatives such as CogVideoX and HunyuanVideo.
**Tools/APIs:** Python, Hugging Face diffusers, T5-XXL, CogVideoX

### 11 · Audio Generation — **Build** · Python · ~45 minutes [CHECK: possibly antilibrary]
This lesson teaches how modern production audio models transform waveforms into discrete tokens using neural codecs like Encodec and SoundStream via residual vector quantization. Students build a tiny next-token transformer to generate synthetic audio token sequences conditioned on style, illustrating the transition from raw audio to generative modeling. The lesson contrasts token-autoregressive approaches like VALL-E and MusicGen with latent diffusion and flow matching systems like Stable Audio 2.5.
**Tools/APIs:** Encodec, SoundStream, DAC, VALL-E, MusicGen, Stable Audio 2.5, AudioLDM 2, ElevenLabs, HuggingFace transformers

### 12 · 3D Generation — **Learn** · Python · ~45 minutes [CHECK: possibly antilibrary]
The lesson teaches the modern generative 3D pipeline that separates multi-view diffusion from 3D reconstruction, utilizing models like MVDream and SV3D alongside techniques such as 3D Gaussian Splatting and NeRFs. It analyzes the challenges of 3D data scarcity and memory, contrasting differentiable Gaussian rendering with slower NeRF integration methods. Students implement a 2D Gaussian splatting toy example in `code/main.py`, optimizing splat positions, colors, and covariances via gradient descent to reconstruct a synthetic target image.

**Tools/APIs:** 3D Gaussian Splatting, NeRF, Zero123, MVDream, SV3D, CAT3D, DreamFusion, Shap-E, LRM, InstantMesh, TripoSR, Meshy 4, Rodin Gen-1.5, Hunyuan3D 2.0, Gsplat, Nerfstudio, Scaniverse, Blender, Unity, Unreal, xformers

### 13 · Flow Matching & Rectified Flows — **Build** · Python · ~45 minutes [CHECK: possibly antilibrary]
This lesson teaches Flow Matching and Rectified Flow, techniques that train neural vector fields on straight-line interpolants between noise and data to enable faster, lower-step inference than curved diffusion paths. It covers the conditional flow matching loss formulation and the reflow process for iteratively straightening trajectories. Students implement a 1-D flow matching model on a two-mode Gaussian mixture using a tiny MLP, training via simulation-free regression and performing multi-step Euler integration. The produced artifact compares sample quality across 1, 2, 4, and 20 inference steps to demonstrate efficiency gains.
**Tools/APIs:** MLP, Euler sampler, Flux.1, Stable Diffusion 3, AudioCraft 2, SDXL-Turbo

### 14 · Evaluation — FID, CLIP Score, Human Preference — **Build** · Python · ~45 minutes
This lesson teaches the evaluation of generative models using three core metrics: sample quality via Fréchet Inception Distance (FID), prompt adherence via CLIP score, and overall preference via Elo aggregation. It covers the mathematical formulation of FID as a distance between Gaussians in Inception feature space, cosine similarity for image-text binding, and the Bradley-Terry model for pairwise comparisons. The student produces a Python script implementing these algorithms on synthetic feature vectors and generates a structured evaluation plan document.
**Tools/APIs:** Inception-v3, CLIP, FID, CMMD, HPSv2, ImageReward, PickScore, PartiPrompts, DINOv2

### 19 · Visual Autoregressive Modeling (VAR): Next-Scale Prediction — **Build** · Python (with PyTorch) · ~90 minutes [CHECK: possibly antilibrary]
This lesson implements Visual Autoregressive Modeling (VAR), a next-scale prediction architecture that generates images by predicting token grids from low resolution (1x1) to high resolution in parallel steps. It covers the design of a multi-scale residual VQ-VAE tokenizer and a Transformer that enforces causality across scales while allowing parallel generation within a scale. Students build a complete VAR pipeline on synthetic 2D data, training the model to predict increasingly detailed token grids and decoding them to verify the scale-structured generation mechanism. The lesson demonstrates how VAR achieves GPT-style scaling laws for image generation and improves inference speed over diffusion models.
**Tools/APIs:** PyTorch, Multi-scale VQ-VAE, Transformer
