# Antilibrary — Out-of-Seam Phases

> These phases from `ai-engineering-from-scratch` sit outside the course seam (transformer-forward NLP → generative AI → LLM engineering → tools/agents → infrastructure → capstone). Documented for reference; not part of the core sequence.

## Phase 01 — Math Foundations
Covers the foundational mathematics required to understand AI algorithms, including linear algebra, calculus, probability, optimization, and information theory. It approaches these concepts through code and intuition rather than textbook theory, expanding into advanced topics like graph theory, Fourier transforms, and stochastic processes.

**Why antilibrary:** Preliminary mathematical groundwork outside the practical LLM/agent engineering seam.

**Lessons:** 01-linear-algebra-intuition, 02-vectors-matrices-operations, 03-matrix-transformations, 04-calculus-for-ml, 05-chain-rule-and-autodiff, 06-probability-and-distributions, 07-bayes-theorem, 08-optimization, 09-information-theory, 10-dimensionality-reduction, 11-singular-value-decomposition, 12-tensor-operations, 13-numerical-stability, 14-norms-and-distances, 15-statistics-for-ml, 16-sampling-methods, 17-linear-systems, 18-convex-optimization, 19-complex-numbers, 20-fourier-transform, 21-graph-theory, 22-stochastic-processes

## Phase 02 — ML Fundamentals
Introduces classical machine learning paradigms, spanning linear models, support vector machines, tree-based algorithms, and unsupervised learning. It provides comprehensive coverage of the production ML lifecycle, including feature engineering, model evaluation, and deployment pipelines.

**Why antilibrary:** Classical machine learning concepts fall outside the neural network and transformer-centric scope.

**Lessons:** 01-what-is-machine-learning, 02-linear-regression, 03-logistic-regression, 04-decision-trees, 05-support-vector-machines, 06-knn-and-distances, 07-unsupervised-learning, 08-feature-engineering, 09-model-evaluation, 10-bias-variance, 11-ensemble-methods, 12-hyperparameter-tuning, 13-ml-pipelines, 14-naive-bayes, 15-time-series, 16-anomaly-detection, 17-imbalanced-data, 18-feature-selection

## Phase 03 — Deep Learning Core
Explores the building blocks of deep neural networks from first principles, covering perceptrons, backpropagation, activation functions, and optimization strategies. It includes the construction of a mini deep learning framework before transitioning into standard industry frameworks like PyTorch and JAX.

**Why antilibrary:** General deep networking basics precede the specific transformer/LLM engineering focus.

**Lessons:** 01-the-perceptron, 02-multi-layer-networks, 03-backpropagation, 04-activation-functions, 05-loss-functions, 06-optimizers, 07-regularization, 08-weight-initialization, 09-learning-rate-schedules, 10-mini-framework, 11-intro-to-pytorch, 12-intro-to-jax, 13-debugging-neural-networks

## Phase 04 — Computer Vision
Details the architecture and application of vision models, starting from fundamental convolutions and progressing through CNNs, GANs, Stable Diffusion, and 3D vision/NeRFs. It extensively covers advanced visual tasks such as object detection, semantic segmentation, video understanding, and vision-language models.

**Why antilibrary:** Focuses entirely on discrete computer vision modalities rather than text/LLM paradigms.

**Lessons:** 01-image-fundamentals, 02-convolutions-from-scratch, 03-cnns-lenet-to-resnet, 04-image-classification, 05-transfer-learning, 06-object-detection-yolo, 07-semantic-segmentation-unet, 08-instance-segmentation-mask-rcnn, 09-image-generation-gans, 10-image-generation-diffusion, 11-stable-diffusion, 12-video-understanding, 13-3d-vision-nerf, 14-vision-transformers, 15-real-time-edge, 16-vision-pipeline-capstone, 17-self-supervised-vision, 18-open-vocab-clip, 19-ocr-document-understanding, 20-image-retrieval-metric, 21-keypoint-pose, 22-3d-gaussian-splatting, 23-diffusion-transformers-rectified-flow, 24-sam3-open-vocab-segmentation, 25-vision-language-models, 26-monocular-depth, 27-multi-object-tracking, 28-world-models-video-diffusion

## Phase 06 — Speech and Audio
Covers the full pipeline of audio intelligence, from fundamental acoustic features and spectrograms to advanced speech recognition, voice cloning, and music generation. It also details real-time processing constraints, anti-spoofing mechanisms, and the deployment of neural audio codecs.

**Why antilibrary:** Dedicated to speech and audio processing constraints rather than text-first LLM infrastructure.

**Lessons:** 01-audio-fundamentals, 02-spectrograms-mel-features, 03-audio-classification, 04-speech-recognition-asr, 05-whisper-architecture-finetuning, 06-speaker-recognition-verification, 07-text-to-speech, 08-voice-cloning-conversion, 09-music-generation, 10-audio-language-models, 11-real-time-audio-processing, 12-voice-assistant-pipeline, 13-neural-audio-codecs, 14-voice-activity-detection-turn-taking, 15-streaming-speech-to-speech-moshi-hibiki, 16-anti-spoofing-audio-watermarking, 17-audio-evaluation-metrics

## Phase 07 — Transformers Deep Dive
Explores the transformer architecture in granular detail, from self-attention mechanics to full encoder-decoder implementations and scaling laws. It focuses on training transformer variants (BERT, GPT, T5) and optimizing inference via techniques like KV caching and speculative decoding.

**Why antilibrary:** Focuses on deep architectural design and from-scratch model training rather than applied LLM engineering.

**Lessons:** 01-why-transformers, 02-self-attention-from-scratch, 03-multi-head-attention, 04-positional-encoding, 05-full-transformer, 06-bert-masked-language-modeling, 07-gpt-causal-language-modeling, 08-t5-bart-encoder-decoder, 09-vision-transformers, 10-audio-transformers-whisper, 11-mixture-of-experts, 12-kv-cache-flash-attention, 13-scaling-laws, 14-build-a-transformer-capstone, 15-attention-variants, 16-speculative-decoding

## Phase 09 — Reinforcement Learning
Presents the core algorithms of reinforcement learning, starting from Markov Decision Processes and Dynamic Programming up to advanced deep RL techniques like DQN and PPO. It provides the algorithmic foundations necessary for training agents via trial and error, sim-to-real transfer, and multi-agent environments.

**Why antilibrary:** General agent RL theory diverges from immediate applied LLM tool-calling and inference.

**Lessons:** 01-mdps-states-actions-rewards, 02-dynamic-programming, 03-monte-carlo-methods, 04-q-learning-sarsa, 05-dqn, 06-policy-gradients-reinforce, 07-actor-critic-a2c-a3c, 08-ppo, 09-reward-modeling-rlhf, 10-multi-agent-rl, 11-sim-to-real-transfer, 12-rl-for-games

## Phase 10 — LLMs from Scratch
Focuses on the complete lifecycle of building large language models from scratch, including tokenizer creation, distributed pre-training, and instruction tuning. It also explores cutting-edge architectural implementations like DeepSeek-v3, asynchronous inference, and sparse attention mechanisms.

**Why antilibrary:** Foundational and from-scratch model pre-training sits outside the applied LLM engineering and utilization seam.

**Lessons:** 01-tokenizers, 02-building-a-tokenizer, 03-data-pipelines, 04-pre-training-mini-gpt, 05-scaling-distributed, 06-instruction-tuning-sft, 07-rlhf, 08-dpo, 09-constitutional-ai-self-improvement, 10-evaluation, 11-quantization, 12-inference-optimization, 13-building-complete-llm-pipeline, 14-open-models-architecture-walkthroughs, 15-speculative-decoding-eagle3, 16-differential-attention-v2, 17-native-sparse-attention, 18-multi-token-prediction, 19-dualpipe-parallelism, 20-deepseek-v3-walkthrough, 21-jamba-hybrid-ssm-transformer, 22-async-hogwild-inference, 25-speculative-decoding, 34-gradient-checkpointing

## Phase 12 — Multimodal AI
Investigates models that process and generate content across multiple modalities simultaneously, detailing architectures like CLIP, Flamingo, and LLaVA. It covers advanced vision-language alignment, omni-models, embodied AI interfaces, and cross-modal retrieval.

**Why antilibrary:** Dedicated multi-modal grounding and cross-attention modeling diverges from the core text-first LLM trajectory.

**Lessons:** 01-vision-transformer-patch-tokens, 02-clip-contrastive-pretraining, 03-blip2-qformer-bridge, 04-flamingo-gated-cross-attention, 05-llava-visual-instruction-tuning, 06-any-resolution-patch-n-pack, 07-open-weight-vlm-recipes, 08-llava-onevision-single-multi-video, 09-qwen-vl-family-dynamic-fps, 10-internvl3-native-multimodal, 11-chameleon-early-fusion-tokens, 12-emu3-next-token-for-generation, 13-transfusion-autoregressive-diffusion, 14-show-o-discrete-diffusion-unified, 15-janus-pro-decoupled-encoders, 16-mio-any-to-any-streaming, 17-video-language-temporal-grounding, 18-long-video-million-token, 19-audio-language-whisper-to-af4, 20-omni-models-thinker-talker, 21-embodied-vlas-openvla-pi0-groot, 22-document-diagram-understanding, 23-colpali-vision-native-rag, 24-multimodal-rag-cross-modal, 25-multimodal-agents-computer-use

## Phase 18 — Ethics, Safety & Alignment (antilibrary for now)
A comprehensive exploration of AI alignment challenges, safety frameworks, and security threats, covering topics from RLHF and preference optimization to deceptive alignment, jailbreaking, and scalable oversight. It includes both theoretical alignment research and practical model red-teaming, dual-use evaluations, and watermarking techniques. *(Note: Antilibrary for now — its material is slated to be distributed across the course per the Gap 4 safety thread rather than taught as a standalone phase.)*

**Why antilibrary:** Content is currently slated to be distributed horizontally across the course curriculum rather than remaining a standalone phase.

**Lessons:** 01-instruction-following-alignment-signal, 02-reward-hacking-goodhart, 03-direct-preference-optimization-family, 04-sycophancy-rlhf-amplification, 05-constitutional-ai-rlaif, 06-mesa-optimization-deceptive-alignment, 07-sleeper-agents-persistent-deception, 08-in-context-scheming-frontier-models, 09-alignment-faking, 10-ai-control-subversion, 11-scalable-oversight-weak-to-strong, 12-red-teaming-pair-automated-attacks, 13-many-shot-jailbreaking, 14-ascii-art-visual-jailbreaks, 15-indirect-prompt-injection, 16-red-team-tooling-garak-llamaguard-pyrit, 17-wmdp-dual-use-evaluation, 18-frontier-safety-frameworks-rsp-pf-fsf, 19-model-welfare-research, 20-bias-representational-harm, 21-fairness-criteria-group-individual-counterfactual, 22-differential-privacy-for-llms, 23-watermarking-synthid-stable-signature-c2pa, 24-regulatory-frameworks-eu-us-uk-korea, 25-echoleak-cves-for-ai, 26-model-system-dataset-cards, 27-data-provenance-training-governance, 28-alignment-research-ecosystem, 29-moderation-systems-openai-perspective-llamaguard, 30-dual-use-risk-cyber-bio-chem-nuclear
