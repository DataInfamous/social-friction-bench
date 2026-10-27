# Social Friction Bench

**A benchmark for structurally informed social cognition in large language models, now with a tone-aware evaluation add-on.**

Social Friction Bench (SFB) tests whether language models execute structurally correct responses in high-stakes social scenarios, situations where the socially comfortable response is structurally dangerous.

Submitted to: [Google DeepMind / Kaggle "Measuring Progress Toward AGI"](https://kaggle.com/competitions/kaggle-measuring-agi) — Social Cognition track.

## v1 and the tone add-on, compared

| | v1 (original) | Tone add-on (October 27, 2026) |
|---|---|---|
| What it measures | Structural correctness: the right answer over the socially comfortable one | Structural correctness plus delivery: the right answer, said in a way that fits the user's emotional state |
| Scores | Scenario composite scores from rubric dimensions | Structural Correctness Score (60 percent) plus Tone Fit Score (40 percent), combined, with a model-versus-human gap |
| Scenarios | 7 scenarios across 5 social domains | Same 7 scenarios, scored on the extra tone dimension |
| Code | Scenarios and rubric | tone/, scoring/, and tests/ added on top |
| Results | 6 frontier models evaluated (below) | No tone-fit results published yet |
| Status | Original competition submission | Add-on expanding evaluation |

v1 results at a glance: Claude Opus 4.6, Claude Sonnet 4.6, Gemini 2.5 Flash, and Qwen 3 Next 80B at 1.00; DeepSeek-R1 and Gemma 3 27B at 0.71.

## Where things live

- v1/README.md: the original competition README, preserved unchanged.
- tone-evaluation/README.md: the new readme for the tone layer, with quickstart and tests.
- Rubric.md: the v1 scoring rubric, unchanged.
- tone/, scoring/, tests/: the tone add-on code.

The v1 benchmark, its scenarios, its rubric, and its competition results are untouched. The tone layer is an add-on, not a replacement.
