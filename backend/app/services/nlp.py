import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

import spacy
from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOP_WORDS
from spacy.language import Language

from app.schemas.nlp import AnalyzeResponse, Sentiment


class NLPAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> AnalyzeResponse:
        """Analyze language, sentiment and keywords for a text."""


@dataclass(slots=True)
class SpacyNLPAnalyzer(NLPAnalyzer):
    """Deterministic bilingual NLP baseline with explainable sentiment rules."""

    model_version: str = "spacy-rules-fr-en-v2"
    max_keywords: int = 8
    nlp: Language = field(init=False, repr=False)
    fr_stop_words: set[str] = field(init=False, repr=False)
    en_stop_words: set[str] = field(init=False, repr=False)
    stop_words: set[str] = field(init=False, repr=False)

    positive_terms: ClassVar[set[str]] = {
        "adore",
        "ameliore",
        "bon",
        "bonne",
        "excellent",
        "fast",
        "fiable",
        "fort",
        "genial",
        "geniale",
        "good",
        "great",
        "happy",
        "helpful",
        "innovant",
        "innovation",
        "innovative",
        "love",
        "opportunite",
        "positif",
        "rapide",
        "reliable",
        "reussi",
        "satisfait",
        "satisfaction",
        "success",
        "succes",
        "transforme",
        "useful",
        "utile",
    }
    negative_terms: ClassVar[set[str]] = {
        "bad",
        "bug",
        "crise",
        "decevant",
        "deteste",
        "difficile",
        "disappointing",
        "echec",
        "erreur",
        "failed",
        "failure",
        "hate",
        "insatisfait",
        "issue",
        "lent",
        "mauvais",
        "negatif",
        "nul",
        "panne",
        "problem",
        "probleme",
        "retard",
        "risk",
        "risque",
        "slow",
        "terrible",
    }
    negations: ClassVar[set[str]] = {
        "aucun",
        "jamais",
        "ne",
        "never",
        "no",
        "not",
        "pas",
    }
    intensifiers: ClassVar[set[str]] = {
        "extremely",
        "really",
        "super",
        "tellement",
        "totalement",
        "tres",
        "very",
        "vraiment",
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
    }
    english_markers: ClassVar[set[str]] = {
        "and",
        "are",
        "for",
        "from",
        "is",
        "of",
        "the",
        "this",
        "to",
        "with",
    }

    def __post_init__(self) -> None:
        self.nlp = spacy.blank("fr")
        self.fr_stop_words = {self._normalize(word) for word in FR_STOP_WORDS}
        self.en_stop_words = {self._normalize(word) for word in EN_STOP_WORDS}
        self.stop_words = self.fr_stop_words | self.en_stop_words

    def analyze(self, text: str) -> AnalyzeResponse:
        doc = self.nlp(text)
        tokens = [
            self._normalize(token.text)
            for token in doc
            if token.is_alpha and len(token.text.strip()) > 1
        ]
        language, language_confidence = self._detect_language(tokens)
        sentiment, sentiment_confidence = self._detect_sentiment(tokens)
        return AnalyzeResponse(
            language=language,
            language_confidence=language_confidence,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence,
            keywords=self._extract_keywords(tokens),
            model_version=self.model_version,
            analysis_status="completed",
        )

    def _detect_language(self, tokens: list[str]) -> tuple[str, float]:
        if not tokens:
            return "unknown", 0.0
        french_hits = sum(
            1 for token in tokens if token in self.french_markers or token in self.fr_stop_words
        )
        english_hits = sum(
            1 for token in tokens if token in self.english_markers or token in self.en_stop_words
        )
        if french_hits == english_hits == 0:
            return "unknown", 0.0
        language = "fr" if french_hits >= english_hits else "en"
        confidence = 0.5 + abs(french_hits - english_hits) / (
            2 * max(1, french_hits + english_hits)
        )
        return language, round(min(confidence, 1.0), 3)

    def _detect_sentiment(self, tokens: list[str]) -> tuple[Sentiment, float]:
        positive_score = 0.0
        negative_score = 0.0

        for index, token in enumerate(tokens):
            if token not in self.positive_terms and token not in self.negative_terms:
                continue
            context = tokens[max(0, index - 2) : index]
            weight = 1.5 if context and context[-1] in self.intensifiers else 1.0
            negated = any(candidate in self.negations for candidate in context)

            is_positive = token in self.positive_terms
            if negated:
                is_positive = not is_positive
            if is_positive:
                positive_score += weight
            else:
                negative_score += weight

        total_score = positive_score + negative_score
        difference = positive_score - negative_score
        if difference > 0:
            sentiment: Sentiment = "positive"
        elif difference < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        if total_score == 0:
            confidence = 0.5
        elif difference == 0:
            confidence = min(0.9, 0.55 + 0.05 * total_score)
        else:
            signal_ratio = abs(difference) / total_score
            confidence = min(0.99, 0.55 + 0.25 * signal_ratio + 0.04 * abs(difference))
        return sentiment, round(confidence, 3)

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
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        without_accents = "".join(
            char for char in decomposed if not unicodedata.combining(char)
        )
        return without_accents.strip(" '’\".,;:!?()[]{}")
