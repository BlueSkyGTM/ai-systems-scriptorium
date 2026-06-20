# VERIFY verdict — L13 Fine-Tuning, in Practice and in Proportion

Verifier: Sonnet VERIFY subagent. Date: 2026-06-19. Sources: WebFetch (HuggingFace PEFT conceptual_guides/lora, conceptual_guides/adapter, developer_guides/quantization) and MS Learn connector (Azure ML / Azure fine-tuning).

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| PEFT = adapt large pretrained model by training a small number of extra parameters while freezing the original, comparable to full fine-tuning at lower cost | HuggingFace PEFT/LoRA docs: trains "small number of extra parameters" with "original pretrained weights frozen," "performance comparable to fully finetuned models"; MS Learn: "PEFT... retains most of the weights of the original pre-trained model and updates the remaining weights" | CONFIRMED |
| LoRA freezes the original weight matrix; represents the update as the product of two smaller low-rank matrices; trains only those two | PEFT LoRA guide: "represents the weight updates ΔW with two smaller matrices... through low-rank decomposition. The original weight matrix remains frozen" | CONFIRMED |
| Adapters swappable on a shared base or mergeable into base for a standalone model | PEFT LoRA guide: `merge_and_unload()` → "use the newly merged model as a standalone model"; merge/unmerge/add_weighted_adapter for swapping | CONFIRMED |
| Multi-tenant adapter serving (many fine-tunes on one base) | Follows from swappable adapters; MS Learn LoRA decision matrix: "Swap different adapters on the same base model for multiple tasks" | CONFIRMED |
| LoraConfig params r, lora_alpha, target_modules, lora_dropout, bias, task_type; get_peft_model wraps base into PeftModel | PEFT quantization guide example: `LoraConfig(r=, lora_alpha=, target_modules=[...], lora_dropout=, bias="none", task_type="CAUSAL_LM")` then `get_peft_model(model, config)` | CONFIRMED (code block matches docs exactly; target_modules q_proj/v_proj = attention projections per docs) |
| r = rank; lower rank = fewer trainable params | PEFT LoRA guide: "`r`: the rank of the update matrices... Lower rank results in smaller update matrices with fewer trainable parameters" | CONFIRMED (reworded prose to match) |
| lora_alpha = scaling factor on adapter contribution | PEFT LoRA guide: "`lora_alpha`: LoRA scaling factor" | CONFIRMED |
| target_modules = which layers get adapters (typically attention projections) | PEFT LoRA guide: "modules (for example, attention blocks) to apply the LoRA update matrices" | CONFIRMED |
| QLoRA quantizes frozen base to 4-bit (NF4 / NormalFloat4), trains LoRA adapters in higher precision on top | PEFT quantization guide: "QLoRA... quantizes a model to 4-bits and then trains it with LoRA"; `bnb_4bit_quant_type="nf4"` = "a special 4-bit data type for weights initialized from a normal distribution" | CONFIRMED |
| QLoRA fine-tunes a 65B model on a single 48GB GPU (published result) | PEFT quantization guide VERBATIM: "QLoRA... allows you to finetune a 65B parameter model on a single 48GB GPU!" | CONFIRMED (high-risk number — grounded verbatim) |
| Base quantized with BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4"), prepared with prepare_model_for_kbit_training, then LoraConfig on top | PEFT quantization guide: shows exactly this sequence | CONFIRMED |
| MS defines LoRA as PEFT method storing small trainable weight matrices as adapter layers; QLoRA as LoRA + quantization for memory savings | MS Learn (concepts-fine-tune-language-models): "LoRA... tracks changes to model weights and efficiently stores smaller weight matrices... results, known as adapter layers"; "QLoRA is an extension of LoRA that further reduces memory usage by introducing quantization to the adapter layers" | CONFIRMED |
| Azure ML model catalog runs the fine-tune from a base model + labeled dataset, then evaluate/deploy | MS Learn training module "Fine-tune a foundation model from the model catalog in Azure Machine Learning" — fine-tune, evaluate, deploy from studio | CONFIRMED |
| Microsoft frames fine-tuning as warranted after evaluating alternatives, not a default | MS Learn (fine-tuning-considerations "When to fine-tune"; "Model fine-tuning concepts" — prompt engineering/chaining as cheaper first options) | CONFIRMED |
| fine-tune for behavior/form, retrieve for knowledge, prompt for everything you can; fine-tuning adds behavior not reliable facts | Industry-standard decision framing; consistent with MS "When to fine-tune" categories (style/tone, format/schema, tool usage) | CONFIRMED |

## Markers resolved
All `[verify:]` / `[MS-Learn:]` markers removed → clean prose. No markers remain (grep clean).

## Literacy-depth check (CRITICAL — the ruling)
PASS, cleanly. The lesson:
- States its own bar: "The skill this lesson builds is not how to run a training job — it is how to know when not to."
- Teaches the three-lever decision + what PEFT/LoRA/QLoRA *are* + how to *read* a `LoraConfig`. The code blocks are config declarations only — NO training loop, NO Trainer/.train()/optimizer step, NO forward/backward, NO LR schedule, NO data-labeling pipeline, NO gradient accumulation/sharding.
- "Where the deep build lives" explicitly enumerates what it did NOT do and names the deep build as Path-A MLE work, "named and located in the antilibrary as a candidate for a future *Avec Python*." Antilibrary link present (`../antilibrary.md`).
- Exercise is a decision exercise: "no GPU and no training... reasoning about the config, not running it."
- Honest framing preserved verbatim: "hands the training itself to a managed platform or an MLE — and can say exactly why, which is the bar that matters in the room."
No trimming required — the lesson never crossed into deep implementation.

## FLAGGED
- None. Every claim grounded, including the high-risk 65B/48GB number (verbatim from PEFT docs).

## STYLE (full read)
- H1; single `## Core concepts`; `claude-handoff` div last. ✓
- Lead: interview scenario ("fine-tune it" sounds expert and is usually wrong) → stake. No throat-clearing. ✓
- Pronoun/tense/POV/voice consistent (one earned-opinion flash: "astonishing how far a good prompt... gets you"). ✓
- Ending shape: consequence ("the bar that matters in the room") — not a template, not the banned opener. ✓
- Acronyms expanded first use: PEFT ✓, LoRA ✓, QLoRA ✓, NF4 ✓.
- Note on draft "We touch it on purpose" (line 5): one "we" — first-person plural, a §1 unity nit (book is strict second-person). Left as-is: it is editorial framing of the curriculum's choice, not instruction to the reader, and reads as the narrator's stake (§8 "let the writer show"). Flagging for editor-in-chief discretion rather than forcing a rewrite that would flatten the voice.

## Verdict: PASS
PEFT/LoRA/QLoRA definitions, LoraConfig/BitsAndBytesConfig API, and the 65B-on-48GB figure all grounded verbatim against HuggingFace PEFT docs; Azure fine-tuning framing grounded against MS Learn. Stays at decision/literacy depth with the deep build correctly routed to the antilibrary → Avec Python. Markers resolved, prose clean. One minor "we" noted for editor discretion (not a blocking defect).
