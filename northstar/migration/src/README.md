# Introduction

The problem with how people learn to build AI systems is not the material. It is the order.

The standard path starts with mathematics, then machine learning theory, then deep learning, then — many
months in, if you have not quit — something you can actually ship. It front-loads a wall. It teaches the
inside of a model to people whose job is to build *around* models. By the time the useful part arrives, the
beginner has spent their best energy on gradients they will never compute again.

This course inverts that. You start on day one with the work itself: calling a model, grounding it in your
data, wrapping it in an agent, putting that agent into production. The thesis is simple — **the bottleneck
is sequencing, not content** — and once you fix the order, most of the wall disappears.

It disappears because the gate was never real. The high-leverage work is **orchestration** — decomposing a
problem, designing the agents and tools, knowing when *not* to add an agent. You direct it in plain language,
but the skill is the orchestration, not the prose, and it does not require Python syntax to start. A technical
limitation is no longer a reason to wait. So Python here is *literacy* you read — plus a narrow track of
*Python you will write* (eval scripts, serving glue) that arrives late, once you are past the gate. The
writing stack is **TypeScript** for the product layer and **Rust** for the serving layer, each taught the
moment you first need it, never as an upfront tax. That is why the course is called *Sans Python*: not without
Python, but **get started without it** — the gate comes down.

The job at the end of the path is **AI Platform Engineering**: the infrastructure that MLOps engineers and
application developers *use*. It sits at the seam where building and deploying converge — serving engines,
agent fleets, gateways, cost controls, the layer that holds under production load. It is its own discipline,
not a blend of two, and its core bet is that **inference-platform engineering matters more than model
training** for the work you will actually do — you carry enough ML literacy to reason about training and
evals, but you build the platform, not the model. A perfect fit to either the Build track or the Deploy track is a
commodity hire. The engineer who owns the seam is not.

The shape is eight modules. The first five teach: foundations, LLM engineering, single agents, multi-agent
systems, and deployment with performance engineering. The last three are proof — you build single agents,
compose them into governed teams, and turn the team loose to build a production system as your final exam.
The artifacts compound; each one is a portfolio piece that solves a real business problem.

You will not learn everything about AI. You will learn to do one job well, and you will have built the
evidence to prove it.

Turn the page. Module 1 starts with the setup, and the first thing you install is the habit of building.
