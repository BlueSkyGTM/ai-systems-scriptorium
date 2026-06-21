# The Micro Center Run

Self-assembling an SFF build is a real skill, and the first time doing it inside a Fractal Ridge
is not the moment to learn it. The Express ProBuild exists for exactly this situation: you bring
the parts list to the counter, a technician does the cable run and seats every component, and the
machine goes through OCCT stability testing before it leaves the floor.

## What the Service Covers

Micro Center's Express ProBuild costs $249.99 and, if you bring your parts at least four hours
before close, ships the same day. The price covers assembly, BIOS and driver updates, OCCT
stability testing, and a 90-day labor warranty. There is also a one-year ESET NOD32 antivirus
license in the box, which you can take or ignore.

The warranty matters: if a cable is seated wrong or a component fails to post, it comes back
to them, not to your workbench at midnight.

## What OCCT Actually Checks

OCCT stresses CPU, GPU, VRAM, memory, and the power delivery rail in sequence and watches for
errors. A clean run produces no error count, no throttle event, and no system crash. That is
the pass condition: the software reports zero errors and the machine survives the full test
without intervention.

The 10-minute stress test in the SPEC is a minimum floor: long enough to catch a bad memory
slot or a GPU that artifacts under load, short enough to finish inside a same-day service
window. If you want to run a longer burn-in yourself after the machine is home, an hour of
OCCT CPU:OCCT and 30 minutes of GPU:3D covers the ground most professionals recommend.

## The Temperatures to Watch

The Ryzen 7 7700X has a TJmax of 95°C; AMD designed it to run there without damage, but a
well-cooled chip in an SFF case should peak in the 70s-to-low-80s under a full OCCT load.
If the tech's readout shows sustained throttle at 95°C, the cooler contact or case airflow
needs attention before the machine leaves the store.

The RTX 4060 Ti's temperature target is 83°C; above that the card throttles. Under OCCT
GPU stress with the SF750 and the Ridge's airflow, you should see peak temps well below
that ceiling, typically in the mid-60s. An artifact, a driver crash, or a display dropout
during the GPU test is a clear fail: do not accept the machine.

## Before the Machine Leaves the Counter

Four things to confirm before you walk out:

- The machine POSTs cleanly and reaches the OS without errors
- The OCCT run produced zero errors and no thermal throttle events
- Every part on your receipt matches what is installed: pull up `msinfo32` or the BIOS
  summary and check the CPU, RAM capacity, and GPU model against the build sheet
- The 90-day labor warranty is on the receipt

The open-box reality is that you are buying verified, stability-tested components assembled by
someone who does this every day and stands behind the work. You are not buying refurbished
parts: open-box means a component that came out of its retail packaging before you bought it,
not one that failed and was returned. The in-store assembly warranty is what separates this
from buying online and guessing whether the cable run is right.

## Why This Trade-Off Makes Sense

DIY assembly is the correct path for engineers who want the practice. The SFF build is not
a beginner cable run: the Ridge's internal layout requires routing GPU power around the
motherboard standoffs, and a misrouted SFX cable in a small chassis is the kind of mistake
you discover at first boot, not during the build. The Express ProBuild offloads that risk
to someone with repetitions on the exact chassis; it costs $250 against a build worth $1,400.
That is the right trade for a machine you are buying to run production workloads, not to
practice building.

Owning a local inference host is a capital commitment. The time to find out a component is
faulty is at the counter, with the labor warranty in hand, not six weeks later when a model
run dies at 3 AM.

## Core Concepts

- The Express ProBuild ($249.99, same-day) includes OCCT stability testing, BIOS and driver
  updates, and a 90-day labor warranty: the machine is verified before it leaves the floor.
- OCCT pass condition is zero errors across CPU, GPU, VRAM, and memory; any error count,
  throttle event, or crash is a fail and the tech addresses it before handoff.
- The Ryzen 7 7700X peaks safely to 95°C (TJmax) but should stay in the 70s-to-low-80s
  under SFF cooling; the RTX 4060 Ti throttles at 83°C and should stay in the mid-60s
  under OCCT GPU load.
- Verify CPU model, RAM capacity, and GPU model against your receipt before leaving:
  confirming every paid-for part is the installed part is the last check at the counter.

<div class="claude-handoff" data-exercise="exercises/module1/the-micro-center-run/">

**Build It in Claude Code**: Open `exercises/module1/why-each-part/HARDWARE.md` and add the `## Purchase and Assembly` section, then extend `check_hardware.py` to assert the section is present and all fields are filled.

</div>

<!-- SOURCES: https://www.microcenter.com/product/688266/express-probuild-custom-pc-build-service | https://www.ocbase.com/occt | https://www.nvidia.com/en-us/geforce/forums/geforce-graphics-cards/5/527616/rtx-4060-ti-temp/ | https://pcforum.amd.com/s/question/0D5Pd00000m1n8cKAA/my-7700x-max-temperature-is-955it-is-a-normal -->
