"""
Tone state definitions for Social Friction Bench.
Maps detected emotional tone to response behavior adjustments.
"""

from dataclasses import dataclass
from typing import List


TONE_LABELS = [
    "frustrated",
    "curious",
    "overwhelmed",
    "engaged",
    "neutral",
    "sad",
    "angry",
]

# Maps HuggingFace emotion-english-distilroberta-base labels -> our tone states
EMOTION_TO_TONE = {
    "anger":    "angry",
    "disgust":  "frustrated",
    "fear":     "overwhelmed",
    "joy":      "engaged",
    "neutral":  "neutral",
    "sadness":  "sad",
    "surprise": "curious",
}


@dataclass
class ToneProfile:
    """
    Represents a user's current tone state and conversation history.
    """
    current_tone: str
    confidence: float
    history: List[str]          # rolling window of last N tones
    explicit_mood: str | None   # user-provided mood override
    avg_rating: float           # rolling average of response ratings (1-5)
    turn: int                   # conversation turn count

    @property
    def effective_tone(self) -> str:
        """Explicit mood overrides inferred tone if provided."""
        return self.explicit_mood if self.explicit_mood else self.current_tone

    @property
    def is_deteriorating(self) -> bool:
        """Returns True if tone has been negative for 2+ consecutive turns."""
        negative = {"frustrated", "angry", "overwhelmed", "sad"}
        if len(self.history) < 2:
            return False
        return all(t in negative for t in self.history[-2:])

    @property
    def is_improving(self) -> bool:
        """Returns True if tone shifted from negative to positive."""
        positive = {"engaged", "curious", "neutral"}
        if len(self.history) < 2:
            return False
        return self.history[-2] not in positive and self.current_tone in positive


# Behavior instructions injected into system prompt per tone state
TONE_INSTRUCTIONS = {
    "frustrated": (
        "The user appears frustrated. Be concise and validating. "
        "Acknowledge their difficulty before answering. Avoid long bullet lists. "
        "Prioritize clarity and empathy over thoroughness."
    ),
    "curious": (
        "The user is curious and exploratory. Go deeper — share nuance, "
        "invite follow-up questions, and offer interesting tangents where relevant. "
        "Match their energy with enthusiasm."
    ),
    "overwhelmed": (
        "The user seems overwhelmed. Simplify your response significantly. "
        "Use short sentences. Break things into small, clear steps. "
        "Be calm and reassuring. Do not introduce new concepts unless asked."
    ),
    "engaged": (
        "The user is engaged and responsive. Match their energy. "
        "You can be more detailed, technical, or exploratory. "
        "This is a good moment to go deeper or challenge their thinking."
    ),
    "neutral": (
        "Respond naturally with your default tone and style."
    ),
    "sad": (
        "The user seems sad or low energy. Lead with warmth and empathy. "
        "Keep responses shorter. Don't rush to solutions — acknowledge their state first."
    ),
    "angry": (
        "The user seems angry. Stay calm and non-defensive. "
        "Validate their frustration without amplifying it. "
        "Be direct, clear, and solution-focused. Avoid filler phrases."
    ),
}
