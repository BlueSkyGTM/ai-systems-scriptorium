# Antilibrary — Training / CUDA / Kernel Chapters (out of seam)

> Chapters 01–14 of the book, kept for reference but outside the inference-serving seam.

| Chapter | Title | Why antilibrary |
|---------|-------|-----------------|
| 01 | Performance Fundamentals | Establishes baseline benchmarking using a training-loop goodput benchmark and a CUDA GEMM kernel case study, both of which concern training and kernel authoring rather than inference deployment. |
| 02 | GPU Hardware Architecture | Centers on systems-query tooling, NVLink validation, and CPU-GPU coherency for low-level hardware optimization that precedes inference-engine configuration. |
| 03 | System Tuning | Covers host-level changes (NUMA pinning, governor tweaks, Kubernetes manifests) that are infrastructure provisioning tasks, not inference-serving benchmarks. |
| 04 | Distributed Communication & Multi-GPU Distribution | Demonstrates multi-GPU scaling via NCCL/NVSHMEM collective tuning and communication overlap, which are distributed-training concerns outside the single-replica inference-serving scope. |
| 05 | Storage and IO Optimization | Focuses on DataLoader worker tuning, preprocessing vectorization, and GPUDirect Storage—training data-feeding concerns distinct from inference request serving. |
| 06 | CUDA Programming Fundamentals | Teaches writing custom CUDA C++ kernels and reasoning about occupancy, launch bounds, and unified memory, which students in this seam do not do. |
| 07 | Memory Access Patterns | Covers coalesced copies, tiled matmuls, async prefetch, and TMA transfers—kernel-level memory optimization skills outside the deploy-and-benchmark scope. |
| 08 | Occupancy, Warp Efficiency & ILP | Concentrates on tuning occupancy, warp divergence, and instruction-level parallelism inside custom kernels, which is kernel-authoring work. |
| 09 | Arithmetic Intensity & Kernel Fusion | Explores roofline optimization, kernel fusion, and CUTLASS/Triton/inline-PTX paths for building high-performance kernels rather than deploying inference servers. |
| 10 | Tensor Core Pipelines & Cluster Features | Applies warp specialization, TMA-powered pipelines, persistent kernels, and thread-block clusters—low-level GPU kernel engineering for Blackwell tensor cores. |
| 11 | Streams & Concurrency | Explains multi-stream overlap using Hyper-Q and warp-specialized pipelines in custom CUDA code rather than configuring inference-engine scheduling. |
| 12 | CUDA Graphs & Dynamic Workloads | Covers conditional capture, graph memory tuning, and dynamic parallelism for custom CUDA workloads, not inference-server request handling. |
| 13 | PyTorch Profiling & Memory Tuning | Focuses on compiled autograd, FSDP, expert parallelism, and training-centric quantization workflows rather than inference serving and benchmarking. |
| 14 | Compiler & Triton Optimization | Highlights `torch.compile`, Triton kernel authoring, and CUTLASS/TMA experimentation—compiler and kernel-development work outside the inference-serving seam. |
