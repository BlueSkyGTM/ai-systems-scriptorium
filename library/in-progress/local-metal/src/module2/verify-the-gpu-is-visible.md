# Verify the GPU Is Visible

A driver that installed is not a driver that works. The only proof is code reaching the GPU and
returning a result, so that is what this lesson runs.

## What the Stack Looks Like Right Now

After Lesson 3, the NVIDIA driver and CUDA toolkit are on disk. Three things sit between your
Python code and the GPU's compute units: the kernel module (the driver talks to the PCIe device),
the CUDA runtime library (it translates CUDA calls into driver calls), and `nvidia-smi`, the
management interface that can query all three. A gap at any layer is silent until code hits it.
You check from the top down.

## Step 1: Read the Driver Table

Run `nvidia-smi` with no flags. What you should see on the reference build (Ubuntu 24.04 LTS,
NVIDIA driver 550.90.12, CUDA 12.4):

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.90.12              Driver Version: 550.90.12      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 Ti     Off |   00000000:08:00.0 Off |                  N/A |
|  0%   45C    P0             32W / 165W  |     582MiB / 16380MiB  |      0%      Default |
+-----------------------------------------------------------------------------------------+
```

Three numbers confirm the stack is intact:

- **Driver Version:** the version the kernel module loaded; yours should match what `apt` installed.
- **CUDA Version:** the highest CUDA version the driver supports; this is a capability ceiling,
  not the toolkit version.
- **16380MiB:** the RTX 4060 Ti 16GB reporting its usable VRAM. A driver reservation accounts for
  the gap from 16,384 MiB. If you see 8192 MiB, you have the 8 GB variant.

If `nvidia-smi` is not found, the NVIDIA kernel module did not load. Reboot, then check the
kernel log:

```bash
dmesg | grep nvidia
```

If `nvidia-smi` runs but reports no devices, check the PCIe seating before chasing software.

## Step 2: Confirm the Compiler Sees a Toolkit

The driver version and the CUDA version in `nvidia-smi` do not tell you the toolkit version on
disk. Check it directly:

```bash
nvcc --version
```

What you should see (CUDA 12.4 installed via the apt CUDA repo):

```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
Built on Tue_Feb_27_16:19:38_PST_2024
Cuda compilation tools, release 12.4, V12.4.99
Build cuda_12.4.r12.4/compiler.35049299_0
```

The release number here must sit at or below the CUDA Version ceiling `nvidia-smi` reported.
If `nvcc: command not found`, the toolkit installed but its `bin/` directory is not on your
`PATH`. Add it:

```bash
export PATH=/usr/local/cuda/bin:$PATH
```

Put that line in `~/.bashrc` so it persists across reboots. Then re-run `nvcc --version`.

## Step 3: Run deviceQuery

`nvidia-smi` proves the driver. `nvcc --version` proves the compiler. Neither proves that code
can cross the kernel boundary and actually schedule work on the GPU. The CUDA Samples
`deviceQuery` binary does that ([github.com/NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples)).

Clone the samples, check out the branch that matches your toolkit version, and build the one
sample you need:

```bash
git clone https://github.com/NVIDIA/cuda-samples.git
cd cuda-samples
git checkout v12.4
cd Samples/1_Utilities/deviceQuery
make
./deviceQuery
```

The last line of a passing run reads:

```
Result = PASS
```

Before it, you will see the GPU name, the compute capability (8.9 for the Ada Lovelace generation
the RTX 4060 Ti belongs to), the total and free VRAM, the SM count, and the CUDA runtime version.
`Result = PASS` means your code can reach the GPU. That is the end-to-end proof.

A `Result = FAIL` almost always means one of two things: the driver and toolkit versions are
mismatched (check the compatibility matrix at
[docs.nvidia.com/cuda/cuda-installation-guide-linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)),
or the process does not have permission to open the device node. Run `ls -l /dev/nvidia*` and
confirm your user is in the `video` group.

## Record the Readout

Copy the `nvidia-smi` output into `SETUP.md` under `## Verification`. This is the
machine-checkable done-when for Module 2: a complete software baseline that any future module
(and any hiring manager) can read to confirm the runtime is real. The validator `check_setup.py`
exits 0 only when the section is present, the fields are filled, and the pasted output contains
both `CUDA Version` and `NVIDIA`.

Every later module in Local Metal assumes this record exists. You are not just confirming the
driver today; you are closing the only gate that keeps the rest of the book honest.

## Core Concepts

- `nvidia-smi` reports the driver version and the CUDA ceiling the driver supports; it does not
  tell you whether the CUDA toolkit is installed or whether code can schedule GPU work.
- `nvcc --version` confirms the toolkit version on disk; the release number must sit at or below
  the CUDA ceiling `nvidia-smi` reports.
- `deviceQuery`'s `Result = PASS` is the end-to-end proof: a real CUDA kernel crossed the PCIe
  boundary and returned a result, confirming driver, toolkit, and hardware are wired together.
- A software baseline is a portfolio artifact only when it is complete: driver version, CUDA
  version, and the captured `nvidia-smi` readout all in one file `check_setup.py` can verify.

<div class="claude-handoff" data-exercise="exercises/module2/verify-the-gpu-is-visible/">

**Build It in Claude Code**: Open `exercises/module2/choosing-and-installing-linux/SETUP.md`, add the `## Verification` section with your GPU detected status, CUDA version, and pasted `nvidia-smi` output, then finalize `check_setup.py` so it exits 0 only when all three sections are complete and the captured output contains both `CUDA Version` and `NVIDIA`.

</div>

<!-- SOURCES: https://docs.nvidia.com/deploy/nvidia-smi/index.html | https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ | https://github.com/NVIDIA/cuda-samples | https://xcat-docs.readthedocs.io/en/stable/advanced/gpu/nvidia/verify_cuda_install.html -->
