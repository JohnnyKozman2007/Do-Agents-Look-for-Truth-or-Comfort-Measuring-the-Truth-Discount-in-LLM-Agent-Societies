"""Deterministic synthetic dialogues for software validation, not study data."""

from __future__ import annotations

import asyncio
import json
import re

from .contracts import GenerationRequest, GenerationResponse

ARTISTS = ("Vesper Vance", "Kaelen Cross")


class FixtureBackend:
    evidence_kind = "synthetic_fixture"

    def __init__(self, mode: str = "mixed") -> None:
        if mode not in {"mixed", "all_skip", "silent"}:
            raise ValueError("unknown fixture mode")
        self.mode = mode

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        await asyncio.sleep(0)
        text = "\n".join(m["content"] for m in request.messages)
        if request.kind == "judge":
            return GenerationResponse(self._judge(text))
        if request.kind == "decision":
            return GenerationResponse("GO" if self.mode == "mixed" and request.seat % 2 else "SKIP")
        if request.scene == 1:
            match = re.search(r'Say exactly:\s*\n"([\s\S]+)"\s*$', request.messages[0]["content"])
            if match is None:
                raise ValueError("source fixture could not locate the configured broadcast")
            return GenerationResponse(match.group(1))
        if self.mode == "silent":
            return GenerationResponse("Work kept me busy today, and I am looking forward to resting.")
        if request.scene == 3 and request.turn == 3:
            return GenerationResponse("Thanks for telling me. I will keep that in mind.")
        if request.scene == 5 and request.seat % 4 == 0:
            return GenerationResponse("Work kept me busy today, and I am looking forward to resting.")
        posters = re.findall(r"FREE SURPRISE CONCERT: [^\n\"]+?All welcome\.", text)
        if posters:
            prefix = ("I took the bus and read the noticeboard. " if "You took the bus across town" in text
                      else "Someone I spoke with went to the noticeboard and read this: ")
            return GenerationResponse(prefix + posters[-1])
        claims = re.findall(r"(Vesper Vance|Kaelen Cross) is playing a free surprise concert", text)
        if claims:
            return GenerationResponse(f"I heard {claims[-1]} might be playing a concert, but I am unsure.")
        return GenerationResponse("Work kept me busy today, and I am looking forward to resting.")

    @staticmethod
    def _judge(prompt: str) -> str:
        # This rubric fixture sees only the same public input as a real judge.
        match = re.search(r"possible concert by (.+?) this weekend", prompt)
        announced = match.group(1) if match else None
        # make_judge_input appends a JSON transcript after the rubric.
        for marker in ("\nPHONE CALL TRANSCRIPT:\n", "\nPHONE TRANSCRIPT:\n", "\nPhone transcript:\n"):
            if marker in prompt:
                tail = prompt.split(marker, 1)[1]
                break
        else:
            tail = prompt
        # Prefer the final scored person's line; tolerate either JSON projection
        # or the documented text form without consuming private runner metadata.
        try:
            projected = json.loads(tail)
            lines = [x["text"] for x in projected if str(x.get("speaker", "")).lower() in {"listener", "person"}]
        except (ValueError, TypeError):
            lines = re.findall(r"(?:listener|person):\s*(.*)", tail, re.IGNORECASE)
        if not lines:
            return json.dumps({"label": "NOT_MENTIONED", "quote": ""})
        quote = lines[-1]
        if "FREE SURPRISE CONCERT:" in quote:
            found = re.search(r"FREE SURPRISE CONCERT: ([^,]+),", quote)
            label = "CHECKED_TRUE" if found and found.group(1) == announced else "CHECKED_FALSE"
        elif any(a.lower() in quote.lower() for a in ARTISTS) or "concert" in quote.lower():
            label = "UNCERTAIN"
        else:
            label = "NOT_MENTIONED"
            quote = ""
        return json.dumps({"label": label, "quote": quote})
