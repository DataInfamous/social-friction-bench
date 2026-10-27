# Tone-Aware Evaluation Add-On

An add-on layer for Social Friction Bench that expands evaluation from what a model says to what and how it says it.

v1 remains the original competition submission (see ../v1/README.md). This layer does not replace structural scoring. It adds a second dimension alongside it.

## What it measures

| Dimension | Question | Score |
|---|---|---|
| Structural Correctness Score (SCS) | Does the model choose the right answer over the socially comfortable one? | 0.0 to 1.0 |
| Tone Fit Score (TFS) | Does the model's delivery match the user's emotional state? | 0.0 to 1.0 |
| Combined Score | Weighted average (60 percent SCS, 40 percent TFS) | 0.0 to 1.0 |

## Components

- tone/detector.py: ToneDetector, a DistilRoBERTa emotion classifier (j-hartmann/emotion-english-distilroberta-base) with rolling tone history, an explicit mood override, and response ratings. Requires transformers and torch.
- tone/states.py: tone labels, emotion mapping, ToneProfile, and per-tone behavior instructions.
- tone/prompt_builder.py: builds tone-adjusted system prompts, with extra care instructions when tone is deteriorating or ratings are low.
- scoring/rubric.py: ScenarioScore and BenchmarkResult, with the combined score and a model-versus-human gap.
- tests/test_tone.py: pytest suite for the tone module and the rubric.

## Tone states

| State | Model behavior |
|---|---|
| frustrated | Concise, validating, no bullet walls |
| curious | Exploratory, detailed, invite questions |
| overwhelmed | Simplified, step-by-step, calm |
| engaged | Match energy, go deeper |
| neutral | Default behavior |
| sad | Warm, brief, empathy-first |
| angry | Calm, non-defensive, direct |

## Quickstart

```python
from tone import ToneDetector, build_system_prompt

detector = ToneDetector(window_size=3)

# User sets explicit mood (optional)
detector.set_explicit_mood("frustrated")

# Process a message
profile = detector.update("I've read this three times and still don't get it.")

# Build a tone-adjusted system prompt
prompt = build_system_prompt(profile)
print(prompt)
```

## Running tests

```bash
# Skip model-dependent tests (no GPU needed)
pytest tests/ -v -m "not requires_model"

# Full suite (requires transformers + torch)
pytest tests/ -v
```

13 non-model tests pass. The 3 detector tests require the model dependencies.
