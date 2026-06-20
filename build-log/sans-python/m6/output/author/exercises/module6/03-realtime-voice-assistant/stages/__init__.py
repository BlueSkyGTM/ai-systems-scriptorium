"""Pipeline stages.

Each stage is a `FrameProcessor` that consumes one frame and emits the next,
adding a *simulated* per-stage latency. The mock stages are deterministic and
stdlib-only; real providers (Deepgram/Cartesia STT/TTS, Silero VAD) are opt-in
behind guarded imports inside each stage's `try_real_*` helper.
"""
