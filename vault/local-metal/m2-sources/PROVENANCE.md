# Local Metal — Module 2 Source Provenance

Cited-resource record for Module 2 ("Linux and CUDA"). Per the authoring directive, every external
resource a lesson cites is captured here as tracked ore: the URL, what it grounds, the source type,
and the retrieval date. The shipped book cites the URLs; this manifest preserves the underlying fact
against link rot. Retrieved 2026-06-21 by the M2 authoring fleet (Sonnet workers + conductor),
grounded via the Microsoft Learn connector (primary for this module), NVIDIA docs, and Ubuntu docs.

## Dual partition vs WSL2 (Lesson 1: the-dual-partition-plan)

| Fact grounded | Source | Type |
|---|---|---|
| WSL is designed for inner-loop development; utility VM auto-shuts-down; GPU via `/dev/dxg`; virtualized network IP | https://learn.microsoft.com/windows/wsl/faq#can-i-use-wsl-for-production-scenarios | MS-Learn (authoritative) |
| WSL2 GPU compute (CUDA/Docker/PyTorch) works for development | https://learn.microsoft.com/windows/wsl/tutorials/gpu-compute | MS-Learn |
| CUDA in WSL setup | https://learn.microsoft.com/windows/ai/directml/gpu-cuda-in-wsl | MS-Learn |

## Distro selection + install (Lesson 2: choosing-and-installing-linux)

| Fact grounded | Source | Type |
|---|---|---|
| Ubuntu desktop install walkthrough | https://ubuntu.com/tutorials/install-ubuntu-desktop | Ubuntu (authoritative) |
| Ubuntu 24.04 LTS release / kernel 6.8 | https://documentation.ubuntu.com/release-notes/24.04/ | Ubuntu |
| Ubuntu 24.04 "Noble Numbat" release details | https://canonical.com/blog/canonical-releases-ubuntu-24-04-noble-numbat | Canonical blog |
| WSL install/setup (cross-reference) | https://learn.microsoft.com/windows/wsl/install , https://learn.microsoft.com/windows/wsl/setup/environment | MS-Learn |

## Driver + CUDA install (Lesson 3: nvidia-drivers-and-cuda)

| Fact grounded | Source | Type |
|---|---|---|
| apt CUDA install path; cuda-keyring for ubuntu2404/x86_64 | https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ | NVIDIA (authoritative) |
| Driver/toolkit version matrix (CUDA 12.x >= driver 525; CUDA 13.x >= 580) | https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html | NVIDIA |
| `cuda-drivers` / `nvidia-open` apt package names | https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/latest/ubuntu.html | NVIDIA |
| `ubuntu-drivers install/list`; Secure Boot signed-module guarantee | https://ubuntu.com/server/docs/how-to/graphics/install-nvidia-drivers/ | Ubuntu |
| Secure Boot MOK enrollment; silent failure when an unsigned `.run` module is blocked | https://packetrealm.io/posts/nvidia-driver-secureboot/ | community (corroboration) |

## Verification (Lesson 4: verify-the-gpu-is-visible)

| Fact grounded | Source | Type |
|---|---|---|
| nvidia-smi reference | https://docs.nvidia.com/deploy/nvidia-smi/index.html | NVIDIA (authoritative) |
| CUDA install guide (driver/toolkit compatibility) | https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ | NVIDIA |
| CUDA Samples `deviceQuery` (Result = PASS end-to-end proof) | https://github.com/NVIDIA/cuda-samples | NVIDIA (repo) |
| CUDA install verification procedure | https://xcat-docs.readthedocs.io/en/stable/advanced/gpu/nvidia/verify_cuda_install.html | community (corroboration) |

The representative `nvidia-smi` capture used in the lessons (RTX 4060 Ti, driver 550.90.12, CUDA 12.4,
`16380MiB`) traces to the real Ubuntu 24.04 readout recorded in M1's source set
(`vault/local-metal/m1-sources/PROVENANCE.md`).
