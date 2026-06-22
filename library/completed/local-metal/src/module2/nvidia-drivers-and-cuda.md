# NVIDIA Drivers and CUDA

A freshly installed Ubuntu system sees the RTX 4060 Ti as an unknown PCI device. Two packages fix
that: the NVIDIA driver, which gives the kernel a module that speaks to the GPU, and the CUDA
toolkit, which gives your code a path to run on it. Install them in the wrong order, or reach for
the wrong version, and the stack breaks in ways that are quiet until you try to run a model.

## Why the apt Path Beats the Runfile

NVIDIA ships two installer formats. The `.run` file bundles driver and toolkit together, compiles
kernel modules from source on your machine, and drops everything under `/usr/local/cuda`. That
sounds clean. The problem surfaces on the next kernel update: the compiled module no longer matches
the new kernel headers, DKMS either rebuilds it or silently fails, and `nvidia-smi` returns an
error instead of a version string.

The apt path installs pre-built, signed kernel modules from NVIDIA's own repository. When a new
kernel lands, the package manager rebuilds the modules via DKMS against the new headers and signs
them. The driver stays current without you touching it.

Reach for the `.run` installer only when the apt repository does not yet carry a driver branch you
specifically need, or when a corporate environment blocks external apt sources. In those cases,
accept that you own the module maintenance yourself.

## The Version Matrix

CUDA is not a single thing: it is a toolkit version layered on top of a driver version, and the
driver sets a ceiling on which toolkit versions the machine can run. NVIDIA publishes the
constraint explicitly in the release notes.

The numbers that matter for the reference build:

- CUDA 12.x requires a driver at or above **525**
- CUDA 13.x requires a driver at or above **580**

Ubuntu 24.04's default repositories carry driver branch 535 or 550. Both support CUDA 12 cleanly.
When you install a pinned toolkit version later (PyTorch and Ollama each express a minimum CUDA
requirement), check the release notes before upgrading the driver. Upgrading the toolkit without
checking the driver floor is the most common way to break a working stack.

## Install the Driver

Add NVIDIA's package repository, then let `ubuntu-drivers` pick the recommended signed driver for
your hardware.

```bash
sudo ubuntu-drivers install
```

If you want to pin a specific branch, query what is available first.

```bash
sudo ubuntu-drivers list
```

The output lists branches by number (535, 550, and so on). To install a specific branch:

```bash
sudo ubuntu-drivers install nvidia:550
```

Ubuntu's `ubuntu-drivers` tool is the right choice when Secure Boot is enabled: it installs
pre-built, pre-signed modules. The kernel will load a signed module without complaint. An unsigned
module compiled from a `.run` installer will be blocked at boot, and `nvidia-smi` will return
nothing. If your BIOS has Secure Boot on and you installed via `.run`, this silence is the symptom.

## Add the CUDA Toolkit Repository

The driver is now on the machine. The toolkit lives in a separate NVIDIA repository. Add it with
the CUDA keyring package.

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
```

With the repository live, install the toolkit. `cuda-toolkit` pulls the compiler, libraries, and
headers for the current release; it does not pull a second copy of the driver.

```bash
sudo apt install cuda-toolkit
```

After installation, wire the toolkit binaries into your PATH and LD_LIBRARY_PATH. Add these lines
to your `~/.bashrc` (adjust the version number to match what installed):

```bash
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

Then reload:

```bash
source ~/.bashrc
```

## Confirm the Versions

After a reboot, two commands confirm the stack is coherent: `nvidia-smi` for the driver, `nvcc --version` for the toolkit.

```bash
nvidia-smi
nvcc --version
```

The driver version shown in `nvidia-smi` must be at or above the minimum the toolkit requires.
If `nvcc --version` reports CUDA 12.x and `nvidia-smi` reports a driver below 525, the toolkit
will fail at link time. Fix the driver first, then recheck.

The next lesson proves the GPU is reachable from code. This one stops at the version check because
the right question at this stage is not "can I run a model?" but "is the version matrix satisfied?"
Getting that right once is what keeps every module above it from fighting its own environment.

## Core Concepts

- The apt-based CUDA repository installs pre-built, signed kernel modules that survive kernel
  updates automatically; the `.run` installer compiles modules on your machine and breaks on the
  next kernel upgrade unless you manage DKMS yourself.
- Every CUDA toolkit version requires a minimum NVIDIA driver version: CUDA 12.x needs driver
  >= 525, CUDA 13.x needs driver >= 580; installing the toolkit without checking the floor is
  how a working stack breaks.
- Secure Boot blocks unsigned kernel modules silently: `ubuntu-drivers` installs signed drivers
  that load cleanly; a `.run`-compiled module will not load and `nvidia-smi` will return nothing.
- `ubuntu-drivers install` picks the recommended signed driver; `cuda-toolkit` installs the
  toolkit from NVIDIA's own apt repository; these two commands do not conflict.

<div class="claude-handoff" data-exercise="exercises/module2/nvidia-drivers-and-cuda/">

**Build It in Claude Code**: Open `exercises/module2/choosing-and-installing-linux/SETUP.md` and add the `## GPU Driver and CUDA` section, then extend `check_setup.py` with a `check_gpu_driver_and_cuda` function that validates all three fields are present and non-empty.

</div>

<!-- SOURCES: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ | https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html | https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/latest/ubuntu.html | https://ubuntu.com/server/docs/how-to/graphics/install-nvidia-drivers/ | https://packetrealm.io/posts/nvidia-driver-secureboot/ -->
