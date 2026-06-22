# The Dual-Partition Plan

You have a 2TB NVMe and two jobs for it: gaming on Windows, inference on Linux. How you split
that drive determines whether your model server is a production host or an experiment that breaks
the moment Windows decides to restart.

## Why Two Partitions, Not One

The tempting path is WSL2: install a Linux distribution inside Windows, point CUDA at the GPU,
and call it done. Microsoft's own documentation is honest about the trade-off. The WSL2 FAQ
states that WSL "has been designed and built to use with inner loop development workflows" and
lists the production differences that follow from that design: the utility VM shuts down
automatically when no file handles are open, GPU access routes through a `/dev/dxg` device
rather than talking to the hardware directly, and the networking stack uses virtualized
components that assign the Linux instance a different IP address from the host ([learn.microsoft.com/windows/wsl/faq](https://learn.microsoft.com/windows/wsl/faq#can-i-use-wsl-for-production-scenarios)).

For a coding session or a quick experiment, none of that matters. For a 24/7 model server you
SSH into and leave running, all three matter:

- Auto-shutdown means a server that disappears when you close your terminal session.
- The `/dev/dxg` translation layer sits between CUDA and the GPU; it works, but it is not the
  direct kernel driver path that production NVIDIA tooling expects.
- A virtualized network address complicates any client that needs to reach the host by IP.

A bare Linux partition sidesteps all three. The kernel owns the hardware directly. The NVIDIA
driver loads against the real PCIe device. The machine has one IP address. When you SSH in and
launch Ollama, it runs until you stop it.

Windows stays for the jobs it is genuinely better at: firmware updates, BIOS flashes, and
gaming. NVIDIA still releases the display driver for Windows; flashing the GPU BIOS from Linux
is possible but unnecessary when the other partition already handles it. The dual-boot split
is not a compromise; it is the correct tool assignment.

## Splitting the 2TB Drive

The Crucial T500 (or Inland Performance Plus) ships as a single 2TB partition. You will shrink
the Windows partition during Linux installation and allocate the freed space to Linux. The
exact split depends on three numbers you control:

- **Windows reserve:** enough for the OS, games, and a driver cache. 500GB is a reasonable
  starting floor for a gaming partition; more if you keep large game libraries on-disk.
- **Linux system + swap:** the OS, the CUDA toolkit, Docker images, and running processes.
  50–80GB covers this comfortably on Ubuntu 24.04 LTS.
- **Model storage:** the remainder goes to model weights. A 14B model at Q4 quantization runs
  roughly 8–9GB of VRAM but stores as a ~9GB file on disk. A 32B Q4 model is around 18–20GB.
  Plan for the models you want to keep loaded plus a working buffer.

The goal is a Linux partition large enough that the model budget fits with room to spare. The
exercise below makes this concrete: you encode your numbers as constants and let the script
confirm the math before you touch the partitioner.

## WSL2 Is Still the Right Answer Sometimes

WSL2 is not wrong; it is wrong for this use case. For local development against a remote model
server, for Windows-native tools that need a Linux environment for a build step, for
experimenting with a new framework before you commit disk space to it: WSL2 is fast, easy, and
the correct choice. Microsoft's GPU acceleration guide for WSL2 covers CUDA, Docker, and
PyTorch all running in a WSL2 instance with an NVIDIA card, and it works ([learn.microsoft.com/windows/wsl/tutorials/gpu-compute](https://learn.microsoft.com/windows/wsl/tutorials/gpu-compute)).

The line is serving. If the Linux environment needs to stay up, answer requests autonomously,
and run without a Windows session keeping it alive, a bare partition is the correct substrate.
WSL2's auto-shutdown is a feature for development workflows; it is a defect for a serving host.

## Core Concepts

- A bare Linux partition gives the NVIDIA driver direct PCIe access, a stable IP address, and
  no auto-shutdown: the three properties a 24/7 model server requires that WSL2's design does
  not provide.
- WSL2's FAQ explicitly frames it as an inner-loop development tool; its GPU path routes through
  `/dev/dxg` and its network stack uses a virtualized IP, both deliberate trade-offs for ease
  of setup over production reliability.
- The NVMe split is a deliberate budget: Windows reserve + Linux system + model storage +
  safety margin; encoding it as checked constants before partitioning prevents regret later.
- WSL2 is correct for development and experimentation; the bare partition is correct for
  serving, because serving requires uptime the WSL VM lifecycle was not designed to guarantee.

<div class="claude-handoff" data-exercise="exercises/module2/the-dual-partition-plan/">

**Build It in Claude Code**: Write `partition_plan.py` that encodes your drive budget as constants, computes the Linux partition size, asserts the model storage fits with a safety margin, and prints the Windows/Linux split.

</div>

<!-- SOURCES: https://learn.microsoft.com/windows/wsl/faq#can-i-use-wsl-for-production-scenarios | https://learn.microsoft.com/windows/wsl/tutorials/gpu-compute | https://learn.microsoft.com/windows/ai/directml/gpu-cuda-in-wsl -->
