# Orange Book — Structure (TOC)

> Source: `Loop-Engineering-The-Complete-Guide-v260615.pdf` (37 pages). Structure only — TOC, parts, and section headings with start pages. No embedded outline (Chromium export); recovered from the Contents page + per-page scan.

## Table of Contents


### Part 1 · What It Is
- §01  Stop Asking: What Loop Engineering Really Is  _(p. 3)_
- §02  From Prompt to Context to Loop  _(p. 6)_

### Part 2 · How It Turns
- §03  The Five Moves of One Loop  _(p. 9)_
- §04  Six Parts: What a Loop Is Built From  _(p. 13)_
- §05  Generator and Evaluator: Why an AI Can't Grade Its Own Code  _(p. 17)_

### Part 3 · Where It Runs, What It Costs
- §06  Loops That Run While You Sleep: Three Real Ones  _(p. 21)_
- §07  The Costs: Verification Debt, Comprehension Rot, Token Blowout  _(p. 25)_

### Part 4 · How You Start
- §08  Stay the Engineer, Not Just the One Who Presses Go  _(p. 29)_
- §09  Build Your First Loop Today  _(p. 32)_


---

## README (preamble)

**Summary:** This book covers loop engineering — the practice of designing autonomous outer systems that run on timers, spawn helper agents, verify work, and decide next steps without human prompting. Across nine sections and four parts, it covers the definition and origin of the concept, the mechanics of how loops operate, real-world examples and costs, and practical guidance for building your first loop.

### `README.md` (verbatim)

**English** | [中文版 README](README_zh.md)

<p align="center">
  <img src="banner.jpg" alt="Loop Engineering Orange Book" width="80%" />
</p>

# Loop Engineering: Stop Asking Me What It Is

> 橙皮书 (Orange Book) Series · by HuaShu (花叔)

A plain-language field guide to **loop engineering** — the term that blew up in a single week of June 2026, when [Peter Steinberger](https://x.com/steipete/status/2063697162748260627), Boris Cherny (head of Claude Code at Anthropic), and Google's [Addy Osmani](https://addyosmani.com/blog/loop-engineering/) all pointed at the same shift and gave it a name.

The one-line version: **stop being the person who prompts the agent. Design the system that does it for you.**

<p align="center">
  <img src="screenshots/page-cover.png" width="45%" />
  <img src="screenshots/page-toc.png" width="45%" />
</p>

## Download

| Edition | PDF |
|---------|-----|
| 中文版 (Chinese) | **[PDF Download](https://github.com/alchaincyf/loop-engineering-orange-book/raw/main/Loop-Engineering橙皮书-v260615.pdf)** |
| English | **[PDF Download](https://github.com/alchaincyf/loop-engineering-orange-book/raw/main/Loop-Engineering-The-Complete-Guide-v260615.pdf)** |

## What This Book Covers

Loop engineering sits **one floor above the harness**. If harness engineering equips a single agent run — which tools it gets, what counts as "done" — loop engineering is the outer system that runs on a timer, spawns its own helpers, verifies the work, remembers what it did, and decides what to do next. You build it once and let it poke the agents instead of you.

If you've read the **Harness Engineering** Orange Book, this is the next floor up. It stands on its own — you don't need the previous one.

**9 sections across 4 parts:**

| Part | Content | Sections |
|------|---------|----------|
| 1. What It Is | The definition, the one-week origin story, and the prompt → context → harness → loop stack | §01–02 |
| 2. How It Turns | The five moves of one loop, the six parts you build it from, and why an AI can't grade its own code | §03–05 |
| 3. Where It Runs, What It Costs | Three real loops (Addy's morning triage, Stripe's Minions, the scheduling reality) and the four costs — verification debt, comprehension rot, token blowout, cognitive surrender | §06–07 |
| 4. How You Start | Staying the engineer, and building your first loop today | §08–09 |

<p align="center">
  <img src="screenshots/page-ch01.png" width="45%" />
  <img src="screenshots/page-ch03.png" width="45%" />
</p>

## Who Is This For

- Developers already using Claude Code / Codex / Cursor who still drive the agent prompt by prompt, and want to climb one level up
- AI power users curious why "you shouldn't be prompting your agents anymore" went viral
- Anyone who read the Harness Engineering Orange Book and wants the outer loop

All sources are public and first-hand: Addy Osmani's founding post, Anthropic's harness-design engineering blog, Stripe's Minions, and the official Claude Code / Codex docs.

## 橙皮书 (Orange Book) Series

Part of the 橙皮书 series — free, practical guides on AI tools. Other titles include Claude Code, Harness Engineering, Agent Skills, OpenClaw, and more.

All books free to download: **[huasheng.ai/orange-books](https://www.huasheng.ai/orange-books)**

## About the Author

**HuaShu (花叔)** · AI Native Coder · Indie Developer

An AI content creator with 500K+ followers across platforms. Built every product — including an App Store #1 paid iOS app — entirely with AI tools, never writing a line of code by hand. Open-sourced Nuwa.skill, huashu-design, and more.

- X/Twitter: [@AlchainHust](https://x.com/AlchainHust)
- YouTube: [@Alchain](https://www.youtube.com/@Alchain)
- Bilibili: [花叔v](https://space.bilibili.com/14097567/)
- WeChat Official Account: 花叔
- Website: [huasheng.ai](https://www.huasheng.ai/)

## Version

- **v260615** — First edition, written the week loop engineering emerged (June 2026), based on Addy Osmani's founding post and the official Claude Code / Codex docs.
- AI tools evolve fast — refer to each product's official documentation for the latest.

## License

[MIT License](LICENSE) — free to use, copy, modify, and distribute, including commercially. Attribution appreciated but not required.


> Note: a Chinese translation `README_zh.md` and the Chinese PDF (`Loop-Engineering橙皮书-v260615.pdf`) carry the same content.
