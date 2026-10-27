"""
ToneDetector — uses j-hartmann/emotion-english-distilroberta-base
to classify user message tone and maintain conversation state.

Install dependencies:
    pip install transformers torch
"""

from __future__ import annotations
from collections import deque
from typing import Optional
import warnings

from tone.states import (
    EMOTION_TO_TONE,
    TONE_LABELS,
    ToneProfile,
)


class ToneDetector:
    """
    Detects emotional tone from text using DistilRoBERTa fine-tuned
    on emotion classification. Maintains a rolling tone history across
    conversation turns.

    Usage:
        detector = ToneDetector(window_size=3)
        profile = detector.update("I'm so confused by all of this")
        print(profile.effective_tone)  # -> "overwhelmed"
    """

    MODEL_ID = "j-hartmann/emotion-english-distilroberta-base"

    def __init__(self, window_size: int = 3):
        self.window_size = window_size
        self._history: deque[str] = deque(maxlen=window_size)
        self._ratings: deque[float] = deque(maxlen=5)
        self._explicit_mood: Optional[str] = None
        self._turn: int = 0
        self._pipeline = None  # lazy load

    def _load_model(self):
        """Lazy-load the HuggingFace pipeline on first use."""
        if self._pipeline is None:
            try:
                from transformers import pipeline
                self._pipeline = pipeline(
                    "text-classification",
                    model=self.MODEL_ID,
                    top_k=1,
                    truncation=True,
                    max_length=512,
                )
            except ImportError:
                raise ImportError(
                    "transformers and torch are required. "
                    "Run: pip install transformers torch"
                )

    def detect(self, text: str) -> tuple[str, float]:
        """
        Run inference on a single text input.

        Returns:
            (tone_label, confidence) e.g. ("frustrated", 0.87)
        """
        self._load_model()
        results = self._pipeline(text)

        # pipeline returns [[{'label': ..., 'score': ...}]]
        top = results[0][0] if isinstance(results[0], list) else results[0]
        emotion = top["label"].lower()
        confidence = round(top["score"], 4)

        tone = EMOTION_TO_TONE.get(emotion, "neutral")
        return tone, confidence

    def set_explicit_mood(self, mood: Optional[str]):
        """
        Set a user-provided mood override. Pass None to clear.
        mood must be one of TONE_LABELS or None.
        """
        if mood is not None and mood not in TONE_LABELS:
            warnings.warn(f"Unknown mood '{mood}', ignoring. Valid: {TONE_LABELS}")
            return
        self._explicit_mood = mood

    def add_rating(self, rating: float):
        """
        Record a user satisfaction rating (1.0–5.0) for the last response.
        Used to track whether tone adjustments are landing.
        """
        if not 1.0 <= rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")
        self._ratings.append(rating)

    def update(self, text: str) -> ToneProfile:
        """
        Process a new user message and return the updated ToneProfile.

        Args:
            text: Raw user message text

        Returns:
            ToneProfile with current tone, history, and metadata
        """
        self._turn += 1
        tone, confidence = self.detect(text)
        self._history.append(tone)

        avg_rating = (
            sum(self._ratings) / len(self._ratings)
            if self._ratings else 3.0
        )

        return ToneProfile(
            current_tone=tone,
            confidence=confidence,
            history=list(self._history),
            explicit_mood=self._explicit_mood,
            avg_rating=avg_rating,
            turn=self._turn,
        )

    def reset(self):
        """Reset conversation state (use between sessions)."""
        self._history.clear()
        self._ratings.clear()
        self._explicit_mood = None
        self._turn = 0
