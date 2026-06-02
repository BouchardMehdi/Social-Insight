from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

import spacy
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOP_WORDS
from spacy.language import Language

from app.schemas.nlp import AnalyzeResponse, Sentiment


class NLPAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> AnalyzeResponse:
        """Analyze language, sentiment and keywords for a text."""


@dataclass(slots=True)
class SpacyNLPAnalyzer(NLPAnalyzer):
    """Rule-based spaCy analyzer designed to be replaced by a richer model later."""

    max_keywords: int = 8
    nlp: Language = field(init=False, repr=False)
    stop_words: set[str] = field(init=False, repr=False)

    positive_terms: ClassVar[set[str]] = {
        "ameliore",
        "améliore",
        "excellent",
        "fort",
        "genial",
        "génial",
        "innovation",
        "innovant",
        "opportunite",
        "opportunité",
        "positif",
        "reussi",
        "réussi",
        "transforme",
        "utile",
    }
    negative_terms: ClassVar[set[str]] = {
        "bug",
        "crise",
        "decevant",
        "décevant",
        "difficile",
        "echec",
        "échec",
        "lent",
        "mauvais",
        "negatif",
        "négatif",
        "probleme",
        "problème",
        "risque",
    }
    french_markers: ClassVar[set[str]] = {
        "avec",
        "dans",
        "des",
        "du",
        "elle",
        "entreprises",
        "est",
        "les",
        "pour",
        "une",
        "transforme",
    }

    def __post_init__(self) -> None:
        self.nlp = spacy.blank("fr")
        self.stop_words = {self._normalize(word) for word in FR_STOP_WORDS}

    def analyze(self, text: str) -> AnalyzeResponse:
        doc = self.nlp(text)
        normalized_tokens = [
            self._normalize(token.text)
            for token in doc
            if token.is_alpha and len(token.text.strip()) > 1
        ]
        language = self._detect_language(normalized_tokens)
        sentiment = self._detect_sentiment(normalized_tokens)
        keywords = self._extract_keywords(normalized_tokens)
        return AnalyzeResponse(language=language, sentiment=sentiment, keywords=keywords)

    def _detect_language(self, tokens: list[str]) -> str:
        if not tokens:
            return "unknown"
        french_hits = sum(1 for token in tokens if token in self.french_markers or token in self.stop_words)
        return "fr" if french_hits / len(tokens) >= 0.15 else "en"

    def _detect_sentiment(self, tokens: list[str]) -> Sentiment:
        positive_score = sum(1 for token in tokens if token in self.positive_terms)
        negative_score = sum(1 for token in tokens if token in self.negative_terms)
        if positive_score > negative_score:
            return "positive"
        if negative_score > positive_score:
            return "negative"
        return "neutral"

    def _extract_keywords(self, tokens: list[str]) -> list[str]:
        candidates = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        keywords: list[str] = []

        for size in (3, 2):
            for index in range(0, max(len(candidates) - size + 1, 0)):
                phrase = " ".join(candidates[index : index + size])
                if phrase not in keywords:
                    keywords.append(phrase)

        for token in candidates:
            if token not in keywords:
                keywords.append(token)

        return keywords[: self.max_keywords]

    @staticmethod
    def _normalize(value: str) -> str:
        return value.casefold().strip(" '’\".,;:!?()[]{}")
