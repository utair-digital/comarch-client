from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtendedAttribute:
    """List of customer’s extended attributes. Attribute
       layout is statically defined – project specific.
    """

    code: str
    value: Optional[str] = None

    def to_comarch(self) -> dict:
        return dict(code=self.code, value=self.value,)
