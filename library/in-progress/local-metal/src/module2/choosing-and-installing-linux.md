# Choosing and Installing Linux

The distro you choose is the ground the rest of this build stands on. Get it wrong and you will spend your evenings fighting kernel modules instead of running models.

## The Criteria That Actually Matter

Most distro debates are about preference. For an inference host, four criteria cut through the noise.

**LTS kernel stability.** NVIDIA drivers bind to specific kernel interfaces; a kernel upgrade that breaks the driver binding takes your GPU with it. A Long-Term Support release pins the kernel to a stable series and receives targeted security backports without gratuitous version jumps.

**CUDA documentation depth.** NVIDIA's official install guides, Stack Overflow answers, and GitHub issues all cluster around a handful of distros. The thinner the community, the fewer solved problems you can find when something goes sideways at midnight.

**Community size.** You will hit an unfamiliar error during setup. The question is whether someone else already solved it and posted the fix.

**Package freshness.** A base system that ships recent versions of Python, Docker, and system libraries means less time backporting or adding third-party repos.

Ubuntu 24.04 LTS (Noble Numbat) scores well on all four. It ships kernel 6.8 at release, carries the deepest NVIDIA and CUDA install documentation of any Linux distribution, and has by far the largest community. Pop!_OS, made by System76, bundles NVIDIA drivers out of the box and is worth a look if you want the NVIDIA setup handled for you; Ubuntu is the book's default because the documentation and community are simply larger.

## Writing the USB

Download the Ubuntu 24.04 LTS ISO from [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop). Then write it to a USB drive using balenaEtcher: open Etcher, select the ISO, select the drive, and click Flash. This is not a file copy; Etcher writes a bootable image that overwrites everything on the drive.

```
Tool: balenaEtcher (https://etcher.balena.io)
Input: ubuntu-24.04.x-desktop-amd64.iso
Target: USB drive (8 GB minimum, all data will be erased)
```

## The Install Path

Shut the machine down, plug in the USB, and power on. Hold F12 at the POST screen to open the boot menu; select the USB. The Ubuntu live environment loads.

Choose **Try or Install Ubuntu**, then **Install Ubuntu**. When the installer reaches the disk setup screen, choose **Install Ubuntu alongside another operating system**. This is the dual-boot path. A slider lets you drag the partition boundary; set it so Ubuntu gets roughly half the 2 TB drive. On the reference build the drive was split in Module 1's plan, so the Linux partition is already the right size: point the installer at that free space.

The partition step is the one place to slow down. The installer writes to whatever you tell it. Confirm the target device is the NVMe drive and the Windows partition is untouched before continuing.

```
Installer screen: "Disk setup"
Choose: Install Ubuntu alongside another operating system
Partition: select the unallocated space reserved in lesson 1
```

## First Boot

After install the machine reboots into GRUB, the bootloader that now manages both partitions. Select Ubuntu. You land at the login screen; create your credentials if you have not done so yet. At the terminal, confirm the kernel:

```bash
uname -r
```

On a fresh Ubuntu 24.04 LTS install this returns the 6.8 kernel (the exact patch level varies with point releases and HWE updates). You also have the package manager and nothing else; no GPU driver, no CUDA toolkit. Those come next.

```bash
lsb_release -a
```

Both commands print the software baseline you will record in the exercise. That is all this lesson sets up. Driver install is lesson 3.

## Core Concepts

- LTS kernel stability, CUDA documentation depth, community size, and package freshness are the four selection criteria for an inference-host distro; taste is not one of them.
- Ubuntu 24.04 LTS is the book's default because it scores well on all four criteria; Pop!_OS is the NVIDIA-batteries-included alternative.
- The dual-boot installer path is "Install Ubuntu alongside another operating system"; the critical step is confirming the target partition before writing.
- After first boot, `uname -r` and `lsb_release -a` give you the kernel and distro version that will go into `SETUP.md`.

<div class="claude-handoff" data-exercise="exercises/module2/choosing-and-installing-linux/">

**Build It in Claude Code**: Create `SETUP.md` with the `## Operating System` section filled in, then build `check_setup.py` v1 that validates every field is present and no placeholder remains.

</div>

<!-- SOURCES: https://ubuntu.com/tutorials/install-ubuntu-desktop | https://documentation.ubuntu.com/release-notes/24.04/ | https://canonical.com/blog/canonical-releases-ubuntu-24-04-noble-numbat | https://learn.microsoft.com/windows/wsl/install | https://learn.microsoft.com/windows/wsl/setup/environment -->
