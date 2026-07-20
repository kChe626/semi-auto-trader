from dataclasses import dataclass, field


@dataclass
class PreflightResult:
    approved: bool
    reasons: list[str] = field(default_factory=list)