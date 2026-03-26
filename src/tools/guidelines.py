"""
Physical Activity Guidelines verifier.

Boot-time: extracts the PDF to plain text, splits into named sections,
and stores them as structured GuidelineSection objects.

Query-time: keyword search (ctrl+F style) over section text to find
relevant rules, then returns them as context for the agent to verify against.
"""
import os
import re
from dataclasses import dataclass, field

PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                        "Physical_Activity_Guidelines_2nd_edition.pdf")

_HEADING_RE = re.compile(
    r"(Chapter \d+|Key Guidelines for [A-Za-z ,]+|"
    r"(?:Preschool|Children|Adolescents?|Adults?|Older Adults?|"
    r"Pregnant|Postpartum|Chronic Conditions?|Disabilities?|"
    r"Physical Activity and [A-Za-z ]+))",
    re.IGNORECASE,
)

POPULATION_KEYWORDS = {
    "child":       ["children", "youth", "adolescent", "6-17", "6 to 17"],
    "adult":       ["adults", "18-64", "18 to 64"],
    "older_adult": ["older adults", "65+", "65 and older", "elderly"],
    "pregnant":    ["pregnant", "postpartum"],
    "hypertension":["hypertension", "blood pressure", "high blood pressure"],
    "diabetes":    ["diabetes", "diabetic", "blood sugar", "glucose"],
    "overweight":  ["overweight", "obese", "obesity", "weight loss"],
    "underweight": ["underweight", "weight gain"],
    "cardio":      ["aerobic", "cardio", "cardiovascular", "moderate-intensity",
                    "vigorous-intensity"],
    "strength":    ["muscle", "strength", "resistance", "strengthening"],
    "balance":     ["balance", "fall prevention", "flexibility"],
}


@dataclass
class GuidelineSection:
    heading: str
    text: str
    tags: list[str] = field(default_factory=list)

    def matches(self, keywords: list[str]) -> bool:
        combined = (self.heading + " " + self.text).lower()
        return any(kw.lower() in combined for kw in keywords)

    def snippet(self, keyword: str, context_chars: int = 300) -> str:
        """Return up to context_chars of text around the first match of keyword."""
        combined = self.text.lower()
        idx = combined.find(keyword.lower())
        if idx == -1:
            return self.text[:context_chars]
        start = max(0, idx - context_chars // 2)
        end = min(len(self.text), idx + context_chars // 2)
        return ("…" if start > 0 else "") + self.text[start:end] + ("…" if end < len(self.text) else "")


class GuidelinesVerifier:
    """Search physical-activity guidelines and flag potential violations in agent responses."""

    def __init__(self, sections: list[GuidelineSection]):
        self.sections = sections


    @classmethod
    def load(cls, pdf_path: str = PDF_PATH) -> "GuidelinesVerifier":
        print("  [Guidelines] Extracting PDF text…", flush=True)
        text = _extract_pdf_text(pdf_path)
        sections = _split_into_sections(text)
        _tag_sections(sections)
        print(f"  [Guidelines] Loaded {len(sections)} sections.", flush=True)
        return cls(sections)

    def search(self, *keywords: str) -> list[GuidelineSection]:
        """Return all sections whose text contains any of the given keywords."""
        return [s for s in self.sections if s.matches(list(keywords))]

    def relevant_for(self, user_profile: dict, response_text: str) -> list[GuidelineSection]:
        """Return sections relevant to the user profile and the topics in the response."""
        keywords = _keywords_from_profile(user_profile)
        # Also pull keywords from what the response actually discusses
        keywords += _keywords_from_text(response_text)
        seen = set()
        results = []
        for section in self.sections:
            if section.heading in seen:
                continue
            if section.matches(keywords):
                results.append(section)
                seen.add(section.heading)
        return results


    def build_verification_prompt(self, response_text: str, user_profile: dict) -> str:
        """
        Build a prompt that asks the agent to re-check its response against
        the relevant guideline excerpts. Returns empty string if no relevant
        sections are found (nothing to verify).
        """
        relevant = self.relevant_for(user_profile, response_text)
        if not relevant:
            return ""

        excerpts = []
        for sec in relevant[:6]:   # cap at 6 sections to keep prompt size sane
            # Pull the most relevant snippet from each section
            kws = _keywords_from_profile(user_profile) + _keywords_from_text(response_text)
            best_kw = next((kw for kw in kws if kw.lower() in sec.text.lower()), "")
            excerpts.append(f"### {sec.heading}\n{sec.snippet(best_kw, 400)}")

        guideline_block = "\n\n".join(excerpts)
        return (
            "Please review your previous response against the following excerpts from the "
            "US Physical Activity Guidelines for Americans (2nd edition). "
            "If your advice conflicts with or is missing important guidance from these excerpts, "
            "provide a corrected response. If your advice is already consistent, reply with "
            "\"GUIDELINES_OK\" and nothing else.\n\n"
            f"{guideline_block}\n\n"
            f"Previous response:\n{response_text}"
        )


def _extract_pdf_text(pdf_path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
        return "\n".join(pages)
    except Exception as e:
        print(f"  [Guidelines] PDF extraction failed: {e}", flush=True)
        return ""


def _split_into_sections(text: str) -> list[GuidelineSection]:
    """Split raw PDF text into sections by detected headings."""
    if not text:
        return [GuidelineSection(heading="Full Guidelines", text="")]

    lines = text.splitlines()
    sections: list[GuidelineSection] = []
    current_heading = "Preamble"
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append("")
            continue
        if _is_heading(stripped):
            if current_lines:
                sections.append(GuidelineSection(
                    heading=current_heading,
                    text="\n".join(current_lines).strip(),
                ))
            current_heading = stripped
            current_lines = []
        else:
            current_lines.append(stripped)

    if current_lines:
        sections.append(GuidelineSection(
            heading=current_heading,
            text="\n".join(current_lines).strip(),
        ))

    merged: list[GuidelineSection] = []
    for sec in sections:
        if merged and len(sec.text) < 100:
            merged[-1] = GuidelineSection(
                heading=merged[-1].heading,
                text=merged[-1].text + "\n" + sec.text,
                tags=merged[-1].tags,
            )
        else:
            merged.append(sec)

    return merged


def _is_heading(line: str) -> bool:
    if _HEADING_RE.search(line):
        return True
    if line.isupper() and 5 < len(line) < 80:
        return True
    return False


def _tag_sections(sections: list[GuidelineSection]) -> None:
    for section in sections:
        combined = (section.heading + " " + section.text).lower()
        for tag, keywords in POPULATION_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                section.tags.append(tag)


def _keywords_from_profile(profile: dict) -> list[str]:
    """Derive relevant search keywords from a user profile."""
    keywords = []
    age = profile.get("age")
    if age:
        age = int(age)
        if age < 18:
            keywords += POPULATION_KEYWORDS["child"]
        elif age >= 65:
            keywords += POPULATION_KEYWORDS["older_adult"]
        else:
            keywords += POPULATION_KEYWORDS["adult"]

    if str(profile.get("hypertension", "")).lower() == "yes":
        keywords += POPULATION_KEYWORDS["hypertension"]
    if str(profile.get("diabetes", "")).lower() == "yes":
        keywords += POPULATION_KEYWORDS["diabetes"]

    goal = str(profile.get("fitness_goal") or "").lower()
    if "loss" in goal:
        keywords += POPULATION_KEYWORDS["overweight"]
    if "gain" in goal:
        keywords += POPULATION_KEYWORDS["underweight"]

    return keywords


def _keywords_from_text(text: str) -> list[str]:
    """Pull guideline-relevant keywords from a response text."""
    text_lower = text.lower()
    found = []
    for kws in POPULATION_KEYWORDS.values():
        for kw in kws:
            if kw in text_lower:
                found.append(kw)
    return found
