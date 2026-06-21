# Document Your Build

A machine that boots is not a build record. The moment you power it on for the first time is the
moment the evidence starts to disappear: the open-box sticker prices you paid, the stress-test
summary the tech printed, the exact parts the store had in stock. Capture them now, in a file a
hiring manager can read, and that evidence becomes the first portfolio artifact in this repository.

## What First Boot Actually Confirms

Module 2 installs Linux and CUDA. Module 1 stops earlier: you confirm the machine POSTs cleanly,
then use the BIOS or a live USB to verify it reports the components you paid for. Three things to
check before you close the case:

- The CPU the BIOS identifies matches the part on your receipt.
- The GPU is detected and reports the correct VRAM.
- The total RAM matches what you installed.

On the reference build, the BIOS screen reports the AMD Ryzen 7 7700X (8 cores, 4.5 GHz base, per
the AMD product page at
[amd.com](https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7700x.html)),
the RTX 4060 Ti 16GB card, and 64 GB of DDR5 at 6000 MT/s. If any line reads differently, stop:
check the seating before you move on.

Once Linux is running (Module 2), the identity commands are:

```bash
lscpu | grep "Model name"
# Model name: AMD Ryzen 7 7700X 8-Core Processor
```

```bash
free -h | grep Mem
# Mem:            62Gi       ...
```

```bash
nvidia-smi
```

What you should see on the reference build (NVIDIA driver 550.90.12, CUDA 12.4, per the Ubuntu
24.04 install documented at
[github.com/fordnox/538b48ac956341728573786a80e08859](https://gist.github.com/fordnox/538b48ac956341728573786a80e08859)):

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

The `16380MiB` line is what matters: that is the 16 GB card reporting its usable VRAM to the
driver (16,384 MB total minus a small driver reservation). If it reads `8192MiB` instead, you
have the 8 GB variant; return it and get the 16 GB.

## Why the Record Is the Artifact

A GitHub repository that starts with `HARDWARE.md` tells a story no resume can: you selected each
part for an inference reason, you paid for it, and the machine booted clean. The `check_hardware.py`
validator you built across this module proves that story is complete. Together, they are what you
point a hiring manager at when you say you built the inference host.

The prices matter too. The SPEC estimated $1,450 to $1,685; what you actually paid is the honest
number, and the gap between estimate and paid is itself a data point: it shows you bought open-box,
caught a sale, or took what the store had. Record it exactly.

## The Final Validator

`check_hardware.py` finalizes in this exercise to assert all three sections are present and filled:
the Bill of Materials (seven rows, each with a price paid and a rationale), the Purchase and
Assembly record, and now the First Boot identity. It exits 0 only when the entire record is clean.
That exit code is the machine-checkable done-when for Module 1.

## Core Concepts

- First boot confirms the machine reports the parts you paid for; the BIOS check precedes Linux, so
  it requires no driver installed.
- `nvidia-smi` reports VRAM as `16380MiB` for the 16 GB RTX 4060 Ti, not `16384MiB`; the
  difference is a driver reservation, not a defective card.
- A build record is a portfolio artifact only when it is complete: prices paid, stress result, and
  hardware identity all in one file a reader can verify.
- The validator that exits 0 on a complete record and names the gap on a partial one is the
  machine-checkable done-when for the module.

<div class="claude-handoff" data-exercise="exercises/module1/document-your-build/">

**Build It in Claude Code**: Open `exercises/module1/why-each-part/HARDWARE.md`, add the `## First Boot` section with your rig's identity, then finalize `check_hardware.py` so it exits 0 only when all three sections are complete and free of placeholder text.

</div>

<!-- SOURCES: https://docs.nvidia.com/deploy/nvidia-smi/index.html | https://gist.github.com/fordnox/538b48ac956341728573786a80e08859 | https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7700x.html | https://technical.city/en/video/GeForce-RTX-4060-Ti-16-GB -->
