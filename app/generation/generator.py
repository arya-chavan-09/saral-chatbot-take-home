from dataclasses import dataclass

from langchain_core.documents import Document

from app.generation.llm_provider import get_llm_provider
from app.generation.prompts import (
    build_generation_prompt,
    build_edit_prompt,
)
from app.provenance.citation import (
    split_into_claims,
    citation_coverage,
)

@dataclass
class GenerationRequest:
    audience: str
    fmt: str
    style: str = "technical"
    length: str | None = None
    n_items: int = 7
    topic: str = ""
    extra_instructions: str = ""
    source_file: str | None = None

@dataclass
class GenerationResult:
    text: str
    request: GenerationRequest
    chunks_used: list[Document]

class SaralGenerator:
    def __init__(self):
        self.llm = get_llm_provider()

    def generate(
        self,
        chunks: list[Document],
        request: GenerationRequest,
    ) -> GenerationResult:
        system_prompt, user_prompt = build_generation_prompt(
            chunks=chunks,
            audience=request.audience,
            fmt=request.fmt,
            style=request.style,
            length=request.length,
            n_items=request.n_items,
            topic=request.topic,
            extra_instructions=request.extra_instructions,
        )

        text = self.llm.complete(
            system_prompt,
            user_prompt,
        )

        return GenerationResult(
            text=text,
            request=request,
            chunks_used=chunks,
        )

    def edit(
        self,
        previous: GenerationResult,
        instruction: str,
        chunks: list[Document] | None = None,
    ):
        chunks = chunks or previous.chunks_used

        system_prompt, user_prompt = build_edit_prompt(
            chunks=chunks,
            previous_output=previous.text,
            edit_instruction=instruction,
            audience=previous.request.audience,
            style=previous.request.style,
            fmt=previous.request.fmt,
            topic=previous.request.topic,
            n_items=previous.request.n_items,
        )

        text = self.llm.complete(
            system_prompt,
            user_prompt,
        )

        claims = split_into_claims(text)
        coverage = citation_coverage(claims)

        if coverage < 1.0:
            repair_prompt = f"""
The output violated citation requirements.

Current citation coverage: {coverage:.2%}

Rewrite the output.

Requirements:
- Every factual sentence must have a citation.
- No standalone citation section.
- No '(Citation: ...)' blocks.
- Use only citations provided in source material.

Output:

{text}
"""

            text = self.llm.complete(
                system_prompt,
                repair_prompt,
            )

        request = GenerationRequest(
            audience=previous.request.audience,
            fmt=previous.request.fmt,
            style=previous.request.style,
            length=previous.request.length,
            n_items=previous.request.n_items,
            topic=previous.request.topic,
            extra_instructions=previous.request.extra_instructions,
            source_file=previous.request.source_file,
        )

        result = GenerationResult(
            text=text,
            request=request,
            chunks_used=chunks,
        )

        reason = f"Applied edit: {instruction}"

        return result, reason