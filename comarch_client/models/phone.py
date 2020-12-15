from dataclasses import dataclass
from typing import Optional


@dataclass
class PhoneData:
    """ Customer phone object """

    phone_number: str
    phone_type: Optional[str] = None  # from docs:  H – home, B – business, M – mobile
    alt_phone_number: Optional[str] = None
    alt_phone_type: Optional[str] = None
    fax: Optional[str] = None

    def to_comarch(self) -> dict:
        res = dict(
            phoneNumber=self.phone_number,
            phoneType=self.phone_type,
            altPhoneNumber=self.alt_phone_number,
            altPhoneType=self.alt_phone_type,
            fax=self.fax,
        )
        return {k: v for k, v in res.items() if v is not None}
