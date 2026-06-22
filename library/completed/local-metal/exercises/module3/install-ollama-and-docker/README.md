# Exercise: Install Ollama and Docker

**Goal:** Build `stack_check.py` (stdlib only): a probe that GETs the Ollama version
endpoint and reports whether the serving layer is alive, with a `--selftest` mode that
validates the logic offline.

## Why

You want a one-command answer to "is Ollama up?" that you can run from any terminal without
opening a browser or reading service logs. The `--selftest` flag makes the probe useful even
before the rig is running: it validates the parsing logic and the endpoint constant offline,
so readers without hardware yet can still verify their code is correct.

> **Note for readers without hardware yet:** `python stack_check.py --selftest` validates
> the parsing and endpoint logic offline and always passes. Live mode (`python stack_check.py`
> with no flags) requires a running Ollama instance.

## Steps

1. Create the file `exercises/module3/install-ollama-and-docker/stack_check.py`.

2. Paste the following code exactly into that file:

   ```python
   #!/usr/bin/env python3
   """
   stack_check.py: probe the local Ollama serving layer.

   Usage:
     python stack_check.py             # live: GET /api/version, report the server version
     python stack_check.py --selftest  # offline: validate the probe logic, no server needed
   """

   import argparse
   import json
   import sys
   import urllib.error
   import urllib.request

   VERSION_URL = "http://localhost:11434/api/version"


   def parse_version(body):
       """Pull the version string from an /api/version JSON body."""
       data = json.loads(body)
       return data["version"]


   def probe(url=VERSION_URL):
       """GET the version endpoint and return the server version string."""
       with urllib.request.urlopen(url, timeout=5) as response:
           return parse_version(response.read().decode("utf-8"))


   def selftest():
       """Validate parsing and the endpoint offline. No server required."""
       sample = '{"version": "0.5.1"}'
       assert parse_version(sample) == "0.5.1", "version parse failed"
       assert VERSION_URL.endswith("/api/version"), "probe URL is wrong"
       print("selftest passed: version parsing and endpoint are correct")
       return 0


   def main():
       parser = argparse.ArgumentParser(description="Probe the local Ollama server.")
       parser.add_argument("--selftest", action="store_true", help="validate logic offline")
       args = parser.parse_args()

       if args.selftest:
           sys.exit(selftest())

       try:
           version = probe()
       except urllib.error.URLError as exc:
           print(f"Ollama not reachable at {VERSION_URL}: {exc}", file=sys.stderr)
           print("start it with: sudo systemctl start ollama", file=sys.stderr)
           sys.exit(1)
       print(f"Ollama is up. Server version: {version}")


   if __name__ == "__main__":
       main()
   ```

3. Run the selftest to confirm the logic is correct:

   ```
   python stack_check.py --selftest
   ```

4. If Ollama is installed and running on your rig, run the live probe:

   ```
   python stack_check.py
   ```

   If Ollama is not running, the script tells you exactly what to do:

   ```
   start it with: sudo systemctl start ollama
   ```

## Done When

`python stack_check.py --selftest` exits 0 and prints the selftest confirmation.
`python stack_check.py` (live, with Ollama running) exits 0 and prints the server version.
`python stack_check.py` (live, with Ollama stopped) exits 1 with a message naming the
endpoint and the recovery command.

## Expected Output Shape

Selftest:

```
selftest passed: version parsing and endpoint are correct
```

Live (server up):

```
Ollama is up. Server version: 0.30.10
```

Live (server down):

```
Ollama not reachable at http://localhost:11434/api/version: <URLError reason>
start it with: sudo systemctl start ollama
```

## Stretch

Extend `stack_check.py` to also GET `http://localhost:11434/api/tags` after a successful
version check. Parse the response and print how many models are currently installed on the
server. A system with no models pulled yet should print `0 models installed`; one with a
model pulled should print something like `1 model installed: qwen2.5-coder:14b`.
