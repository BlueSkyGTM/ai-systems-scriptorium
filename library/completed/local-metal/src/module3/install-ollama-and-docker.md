# Install Ollama and Docker

Module 2 left a GPU that answers to code. Nothing is serving yet, and that gap is the whole
point of this lesson: the serving layer is the software that loads a model file, holds it in
VRAM, and answers requests. Without it, you have a fast card attached to silence.

## Step 1: Install Ollama Natively

Ollama is the serving layer for this book. It handles model loading, quantization-aware
memory planning, and the HTTP endpoint your tooling will call. Install it with the official
one-liner:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The script installs the `ollama` binary, creates an `ollama` system user, and registers a
systemd service. After it finishes, confirm the service is running and set to start on boot:

```bash
sudo systemctl status ollama
sudo systemctl enable ollama
```

What you should see from `systemctl status ollama`: a green `active (running)` line. The
service file at `/etc/systemd/system/ollama.service` sets `ExecStart=/usr/bin/ollama serve`
and runs the process as the `ollama` user, which keeps the daemon unprivileged.

Source: [docs.ollama.com/linux](https://docs.ollama.com/linux)

## Step 2: Confirm the Endpoint

Ollama binds to `127.0.0.1:11434` by default. Verify it is listening:

```bash
curl http://localhost:11434/api/version
```

What you should see: a small JSON body reporting the server version.

```json
{"version":"0.30.10"}
```

Your version number will differ; the shape is what matters. If the request times out, check
that the service is running (`sudo systemctl start ollama`) and try again. The bind address
is `127.0.0.1:11434`; to expose Ollama on a different interface or port, set the
`OLLAMA_HOST` environment variable before starting the service.

Source: [docs.ollama.com/api/introduction](https://docs.ollama.com/api/introduction)

## Step 3: Point Model Storage at the Linux Partition

By default, Ollama stores downloaded models at `/usr/share/ollama/.ollama/models` when
installed as a systemd service (the `ollama` user's home); a plain user install without the
service defaults to `~/.ollama/models` instead. Either way, that path lives on whichever
partition your root filesystem occupies, which may be small. The
model library you build through this book will outgrow a modest root partition quickly.

Override the storage location with the `OLLAMA_MODELS` environment variable. The right way
to set it persistently for a systemd service is through a drop-in override:

```bash
sudo systemctl edit ollama.service
```

Add these lines in the editor that opens:

```ini
[Service]
Environment="OLLAMA_MODELS=/your/linux/partition/path/models"
```

Save, then reload and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

The Linux partition you sized in Module 2 is the right destination. The goal is to keep
model weights off the root filesystem entirely, so the root partition's free space never
constrains a download.

Source: [docs.ollama.com/faq](https://docs.ollama.com/faq)

## Step 4: Install Docker

Later modules need Docker for containerized tooling. Install Docker Engine on Ubuntu via
the official apt repository rather than the snap or convenience script, because the apt
path gives you a stable, upgradeable installation that integrates cleanly with the rest of
the system.

The full steps are at
[docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/).
In summary: add Docker's GPG key and the official apt repository, then install the package
group:

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

After installation, add your user to the `docker` group so you can run containers without
`sudo`:

```bash
sudo usermod -aG docker $USER
```

Log out and back in for the group change to take effect.

## Step 5: The GPU Bridge for Docker

Docker containers cannot reach the GPU unless the NVIDIA Container Toolkit is installed.
The toolkit configures the NVIDIA container runtime, which is what makes
`docker run --gpus=all ...` work. Install it following the guide at
[docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

In this book, Ollama runs natively, not inside a container. The native path is simpler and
gives the GPU direct access with no runtime translation layer. The "Ollama in Docker"
option exists and is worth knowing:

```bash
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

That command is named here because you will encounter it in documentation. It is not the
path this book takes. Native Ollama serves faster on a dedicated rig, and the throughline
artifact you build in this module assumes the native service is the source of truth.

Source: [docs.ollama.com/docker](https://docs.ollama.com/docker)

---

Two pieces are now in place: a model server ready to load weights and answer HTTP requests,
and a container runtime that later modules can hand work to. The rig went from an attached
card to a stack with a live endpoint; that endpoint is what every module after this one
calls.

## Core Concepts

- Ollama installs as a systemd service (`ollama.service`) running as an unprivileged
  `ollama` user; `sudo systemctl enable ollama` ensures it survives reboots.
- The default endpoint is `http://localhost:11434`; `curl /api/version` returning a JSON
  version string is the proof the server is up, not just installed.
- Model storage defaults to `/usr/share/ollama/.ollama/models` (systemd service) or
  `~/.ollama/models` (plain user install); either belongs on the roomy Linux partition,
  set via `OLLAMA_MODELS` in a `systemctl edit` drop-in.
- In this book Ollama runs natively for direct GPU access; the `--gpus=all` Docker image
  exists and is named here, but the native service is the path we take.

<div class="claude-handoff" data-exercise="exercises/module3/install-ollama-and-docker/">

**Build It in Claude Code**: Create `exercises/module3/install-ollama-and-docker/stack_check.py`, a stdlib-only probe that GETs `http://localhost:11434/api/version` and reports the server version, with a `--selftest` mode that validates the logic offline.

</div>

<!-- SOURCES: https://docs.ollama.com/linux | https://docs.ollama.com/api/introduction | https://docs.ollama.com/faq | https://docs.docker.com/engine/install/ubuntu/ | https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html | https://docs.ollama.com/docker -->
