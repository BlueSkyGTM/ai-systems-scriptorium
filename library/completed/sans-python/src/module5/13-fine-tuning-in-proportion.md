# Fine-Tuning, in Practice and in Proportion

An interviewer asks how you would make a model better at your company's domain, and "fine-tune it" is the answer that sounds expert and is usually wrong. Fine-tuning is the most expensive, slowest, and least reversible of the three ways to change model behavior, and a candidate who reaches for it first reveals they have not costed the alternatives. The skill this lesson builds is not how to run a training job; it is how to know when not to, and how to speak precisely about the case where you would.

This is the one place the curriculum lets you touch Path A; the model-centric, training-heavy track it otherwise leaves alone. We touch it on purpose and we keep the touch proportionate: enough to make the right decision and speak to the rest, not a from-scratch training course.

## Three Levers, in Order of Cost

You have three ways to make a model behave the way your application needs, and they are not peers. They form a ladder you climb only when the rung below it runs out.

**Prompting** changes behavior with words: a system prompt, few-shot examples, a tighter instruction. It is instant, free to iterate, and reversible; you edit text. It is the first move for almost every behavior problem, and it is astonishing how far a good prompt and a few examples get you. Reach past it only when you have a concrete reason.

**Retrieval** changes behavior by changing what the model *knows* at inference time; the RAG system from Module 2, the Docling-fed index from lesson 11. When the gap is knowledge, facts the model was never trained on, a private corpus, anything that changes faster than a training cycle, retrieval is the answer, because you update an index, not a model, and the update is near-instant and cheap. Most "the model doesn't know our stuff" problems are retrieval problems wearing a fine-tuning costume.

**Fine-tuning** changes the model's weights by training it further on your examples. It is the right lever for a narrow thing: teaching a durable *behavior* or *form* that prompting cannot reliably hold and retrieval cannot supply; a consistent output format, a domain's tone and structure, a classification the base model is shaky at. It is not how you add knowledge; a fine-tuned model will still hallucinate facts it was not retrieved. And it carries a tail prompting and retrieval do not: you need a curated, labeled dataset of meaningful size, GPU compute, a training and evaluation pipeline, and a versioned artifact to serve and roll back. Module 2 framed this decision from the prompt-and-retrieval side; here is the rule from the fine-tuning side; **fine-tune for behavior and form, retrieve for knowledge, prompt for everything you can.**

The decision discipline mirrors the rest of the module: measure first. Establish an eval baseline with prompting, see how far retrieval moves it, and only then ask whether fine-tuning earns its cost against the number that remains. Microsoft's own guidance frames fine-tuning the same way; as the step you take after you understand when it is warranted, not a default.

## What Modern Fine-Tuning Is: LoRA and QLoRA

When fine-tuning *is* the answer, you almost never retrain the whole model, and knowing why is the literacy bar an interview probes. Full fine-tuning updates every weight in a multi-billion-parameter model; ruinous in memory and compute, and it produces a full-size copy per task. The field moved to **PEFT**, parameter-efficient fine-tuning: adapt a large pretrained model to a task by training only a small number of extra parameters while leaving the original frozen, getting performance comparable to full fine-tuning at a fraction of the cost.

The dominant PEFT method is **LoRA** (Low-Rank Adaptation). Its idea is clean: freeze the original weight matrix and represent the *update* to it as the product of two much smaller matrices, a low-rank decomposition, and train only those two. You train megabytes of adapter instead of gigabytes of model. Better, the adapters stay separate: you can keep one frozen base model in memory and swap task-specific adapters on top of it, or merge an adapter into the base when you want a standalone model. That is the architecture behind multi-tenant adapter serving, many customers' fine-tunes riding one shared base, and it is why "fine-tuning" no longer implies a model copy per use.

A LoRA config has a handful of knobs worth recognizing on sight:

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=8,                  # rank: size of the adapter matrices; lower = fewer trainable params
    lora_alpha=16,        # scaling factor applied to the adapter's contribution
    target_modules=["q_proj", "v_proj"],  # which layers get adapters (typically attention projections)
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(base_model, config)   # wraps the frozen base in a trainable PeftModel
```

The `r` (rank) is the dial that trades capacity against parameter count; lower rank means smaller update matrices and fewer trainable parameters; `target_modules` names the layers, commonly the attention projections, that receive adapters; `lora_alpha` is the scaling factor applied to the adapter's contribution. You do not need to derive these. You need to read a config and know what each line buys, which is precisely the conceptual-fluency bar an applied role is hired against.

**QLoRA** (Quantized LoRA) is the move that put fine-tuning on a single consumer GPU. It quantizes the frozen base model down to 4-bit precision, using a data type called NF4, NormalFloat4, and then trains LoRA adapters in higher precision on top of that compressed base. The frozen base is what dominates memory, so shrinking it 4× is what makes the whole job fit; the published QLoRA result fine-tunes a 65-billion-parameter model on one 48GB GPU. The base is quantized with a `BitsAndBytesConfig` (`load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`), prepared with `prepare_model_for_kbit_training`, and then the same `LoraConfig` rides on top.

This is the vocabulary, and the vocabulary is the deliverable. Microsoft's platform documentation defines the same terms the same way, LoRA as a PEFT method that tracks weight changes in small matrices and produces swappable adapter layers, QLoRA as LoRA plus quantization for further memory savings, which is a useful check that this is settled industry literacy, not a framework's marketing. Azure ML's model catalog will run the actual fine-tune for you from a base model and a labeled dataset, which is how this looks when a managed platform owns the training loop.

## Where the Deep Build Lives

Notice what this lesson did not do. It did not write a training loop, tune a learning-rate schedule, build a data-labeling pipeline, or reason about gradient accumulation and distributed sharding. That is deliberate and it is the scope line for the whole curriculum. The deep, from-scratch fine-tuning build, the training pipelines, the dataset engineering, the optimization internals, is Path-A, model-centric machine-learning engineering. It is real, it is valuable, and it is left to a focused companion book that picks up what this book consciously leaves out. The honest position is the proportionate one: an Production AI Engineer decides whether to fine-tune, specifies the LoRA or QLoRA approach, reads the config, and hands the training itself to a managed platform or an MLE; and can say exactly why, which is the bar that matters in the room.

## Core Concepts

- The three levers are a cost ladder, not peers: prompt for everything you can (instant, reversible), retrieve for knowledge (update an index, not a model), and fine-tune only for durable behavior and form that the cheaper rungs cannot hold; fine-tuning adds behavior, never reliable facts.
- Modern fine-tuning is PEFT, not full retraining: LoRA freezes the base model and trains two small low-rank adapter matrices, so adapters are megabytes, swappable on a shared base, and mergeable; which is why fine-tuning no longer means a model copy per task.
- QLoRA quantizes the frozen base to 4-bit (NF4) and trains LoRA adapters on top, collapsing the memory cost enough to fine-tune a multi-billion-parameter model on a single GPU; recognizing a `LoraConfig`'s `r`, `lora_alpha`, and `target_modules` is the conceptual-fluency bar, not deriving them.
- The deep, from-scratch training build is Path-A MLE work, left to a focused companion; the Production AI Engineer's job is to make the fine-tune-vs-RAG-vs-prompt decision, specify the approach, and speak to it precisely; not to hand-build the training loop.

<div class="claude-handoff" data-exercise="exercises/module5/13-fine-tuning-in-proportion/">

**Build It in Claude Code**: A decision exercise, no GPU and no training. Given a written scenario, argue fine-tune vs RAG vs prompt against cost, data, latency, and reversibility, and write a short defense of the call. If the answer is fine-tune, sketch a minimal `LoraConfig` (or QLoRA variant) and justify each parameter in a comment; reasoning about the config, not running it.

</div>
