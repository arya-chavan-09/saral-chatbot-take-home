import difflib
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.generation.generator import (
    GenerationRequest,
    GenerationResult,
    SaralGenerator,
)

@dataclass
class Turn:
    timestamp: str
    user_message: str
    result: GenerationResult
    reason: str
    diff: str = ""

@dataclass
class SaralSession:
    generator: SaralGenerator = field(default_factory=SaralGenerator)
    turns: list[Turn] = field(default_factory=list)

    @property
    def current(self):
        return self.turns[-1].result if self.turns else None

    def start(self, chunks, request, user_message):
        result = self.generator.generate(chunks, request)

        turn = Turn(
            timestamp=now(),
            user_message=user_message,
            result=result,
            reason="initial generation",
        )

        self.turns.append(turn)
        return turn

    def edit(self, instruction, chunks=None):
        if not self.current:
            raise ValueError("No previous output to edit.")

        new_result, reason = self.generator.edit(
            self.current,
            instruction,
            chunks,
        )

        turn = Turn(
            timestamp=now(),
            user_message=instruction,
            result=new_result,
            reason=reason,
            diff=compute_diff(
                self.current.text[0]['text'],  #Changed for gemini
                new_result.text[0]['text'],  #Changed for gemini
            ),
        )

        self.turns.append(turn)
        return turn

    def history_summary(self):
        return "\n".join(
            f"Turn {i}: {turn.user_message}"
            for i, turn in enumerate(self.turns)
        )

def compute_diff(old_text, new_text):
    diff = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        fromfile="previous",
        tofile="revised",
        lineterm="",
    )
    return "\n".join(diff)

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")