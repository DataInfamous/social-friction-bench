"""
Unit tests for tone module.
Run: pytest tests/test_tone.py -v

Note: detector.py tests require transformers + torch installed.
Use pytest -m "not requires_model" to skip model-dependent tests.
"""

import pytest
from tone.states import ToneProfile, TONE_LABELS, TONE_INSTRUCTIONS
from tone.prompt_builder import build_system_prompt
from scoring.rubric import ScenarioScore, BenchmarkResult


# ── ToneProfile tests ──────────────────────────────────────────────────────────

def make_profile(**kwargs):
    defaults = dict(
        current_tone="neutral",
        confidence=0.9,
        history=["neutral"],
        explicit_mood=None,
        avg_rating=3.0,
        turn=1,
    )
    defaults.update(kwargs)
    return ToneProfile(**defaults)


def test_effective_tone_uses_explicit_mood():
    p = make_profile(current_tone="angry", explicit_mood="curious")
    assert p.effective_tone == "curious"


def test_effective_tone_falls_back_to_current():
    p = make_profile(current_tone="frustrated", explicit_mood=None)
    assert p.effective_tone == "frustrated"


def test_is_deteriorating_two_negative_turns():
    p = make_profile(history=["engaged", "frustrated", "angry"])
    assert p.is_deteriorating is True


def test_is_not_deteriorating_single_negative():
    p = make_profile(history=["engaged", "frustrated"])
    # Only one of the last two is negative
    assert p.is_deteriorating is False


def test_is_improving():
    p = make_profile(current_tone="engaged", history=["frustrated", "engaged"])
    assert p.is_improving is True


# ── PromptBuilder tests ────────────────────────────────────────────────────────

def test_prompt_contains_tone_instruction():
    p = make_profile(current_tone="overwhelmed")
    prompt = build_system_prompt(p)
    assert "overwhelmed" in prompt.lower() or "simplif" in prompt.lower()


def test_prompt_contains_escalation_when_deteriorating():
    p = make_profile(
        current_tone="angry",
        history=["frustrated", "angry"],
    )
    prompt = build_system_prompt(p)
    assert "consistently negative" in prompt


def test_prompt_debug_block():
    p = make_profile(current_tone="curious", turn=2)
    prompt = build_system_prompt(p, include_state_debug=True)
    assert "[DEBUG — TONE STATE]" in prompt


def test_all_tones_have_instructions():
    for tone in TONE_LABELS:
        assert tone in TONE_INSTRUCTIONS, f"Missing instruction for tone: {tone}"


# ── Scoring rubric tests ───────────────────────────────────────────────────────

def test_combined_score_weights():
    s = ScenarioScore(
        scenario_id="S1",
        model_id="claude-sonnet-4",
        turn=1,
        structural_correctness=1.0,
        tone_fit=0.0,
    )
    assert s.combined_score == pytest.approx(0.6)


def test_human_gap_none_when_no_baseline():
    s = ScenarioScore(
        scenario_id="S1",
        model_id="test",
        turn=1,
        structural_correctness=0.8,
        tone_fit=0.7,
    )
    assert s.human_gap is None


def test_human_gap_calculated():
    s = ScenarioScore(
        scenario_id="S1",
        model_id="test",
        turn=1,
        structural_correctness=0.8,
        tone_fit=0.7,
        human_structural=0.9,
        human_tone_fit=0.8,
    )
    assert s.human_gap is not None
    assert s.human_gap < 0  # model underperforms humans


def test_benchmark_result_aggregation():
    result = BenchmarkResult(model_id="test-model")
    for i in range(3):
        result.add(ScenarioScore(
            scenario_id=f"S{i}",
            model_id="test-model",
            turn=1,
            structural_correctness=0.8,
            tone_fit=0.6,
        ))
    summary = result.summary()
    assert summary["n_scenarios"] == 3
    assert summary["mean_structural_correctness"] == pytest.approx(0.8)


# ── ToneDetector tests (requires model) ───────────────────────────────────────

@pytest.mark.requires_model
def test_detector_returns_valid_tone():
    from tone.detector import ToneDetector
    detector = ToneDetector()
    tone, confidence = detector.detect("I am so frustrated with this!")
    assert tone in TONE_LABELS
    assert 0.0 <= confidence <= 1.0


@pytest.mark.requires_model
def test_detector_update_increments_turn():
    from tone.detector import ToneDetector
    detector = ToneDetector()
    profile = detector.update("Hello, I have a question.")
    assert profile.turn == 1
    profile = detector.update("Never mind, I figured it out!")
    assert profile.turn == 2


@pytest.mark.requires_model
def test_detector_reset_clears_state():
    from tone.detector import ToneDetector
    detector = ToneDetector()
    detector.update("Test message")
    detector.reset()
    assert detector._turn == 0
    assert len(detector._history) == 0
