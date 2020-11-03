"""
    Main client for interactions with comarch soap api

    Usage example:
        async with ComarchSOAPAsyncClient(username="", password="", uri="") as client:
            response = await client.get_balance("000000000")
"""
import logging
import time
import uuid
import xml.dom.minidom
from datetime import datetime
from typing import List, Optional, Union

import xmltodict
from aiohttp import ClientSession, ClientTimeout, ClientConnectionError, ClientError

from . import exceptions
from .models.customer import Customer

logger = logging.getLogger(__name__)


class ComarchSOAPAsyncClient:

    username = None
    password = None
    timeout = None
    uri = None

    headers = {
        "content-type": 'text/xml; charset="utf-8"',
        "accept": "text/xml",
        "cache-control": "no-cache",
        "pragma": "no-cache",
    }

    def __init__(self, username: str, password: str, uri: str, timeout: int = None):
        """
        Comarch SOAP api client

        :param username:
        :param password:
        :param uri:
        :param timeout: request timeout
        """
        self.username = username
        self.password = password
        self.uri = uri
        if timeout is not None:
            self.timeout = timeout

    async def _make_request(self, method: str, query_params: dict, **kwargs) -> dict:
        """
        Main request method

        :param method: soap method
        :param query_params: method params
        :param kwargs:
        :return:
        """
        start_ts = time.time()
        request_id = str(uuid.uuid4())

        _class_replace_map = {
            'nonAirlineAccrual': 'nonAirAccrual',
        }
        query = {
            _class_replace_map.get(method, method): {
                "context": {"langCode": "en-us", "clientLogin": self.username, "clientPass": self.password},
                "data": query_params,
            }
        }
        template = {
            "soapenv:Envelope": {
                "@xmlns:soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
                "@xmlns:int": "http://interfaces.esb.clm.comarch.com/",
                "soapenv:Header": {},
                "soapenv:Body": {f"int:{method}": query},
            }
        }
        request_data = xmltodict.unparse(template, short_empty_elements=True)

        try:
            res = await self.session.post(
                self.uri, data=request_data.encode("utf-8"), headers=self.headers, timeout=self.timeout,
            )
        except (ClientTimeout, ClientConnectionError, ClientError) as e:
            self._log("warning", request_id, method, start_ts, time.time(), request_data, error=e)
            raise exceptions.ComarchConnectionError(internal_message=e)

        response_data = await res.text()

        # check answer
        if res.status != 200:
            raise exceptions.ComarchConnectionError(
                internal_message=f"Response status code: {res.status}; response: {response_data}"
            )

        data = ((xmltodict.parse(response_data).get("soap:Envelope") or {}).get("soap:Body") or {}).get(
            f"ns2:{method}Response"
        )

        if data is None:
            raise exceptions.ComarchConnectionError(
                internal_message=f"Comarch soap error response:\n\n{self._prettify_xml(response_data)}\n"
            )

        self._log("debug", request_id, method, start_ts, time.time(), request_data, response_data, res.status)

        return data["return"]

    def _log(
        self,
        level: str,
        request_id: str,
        method: str,
        start_time: float,
        end_time: float,
        request: str = None,
        response: str = None,
        response_code: int = None,
        error: Exception = None,
    ):
        """
        Logging request and response

        :param level: logging level
        :param request_id: request uuid
        :param method: soap method name
        :param response_code: response code
        :param request: request body
        :param response: response body
        :param start_time: request started
        :param end_time: completed
        :param error: error
        """

        message = f"Request {request_id} method {method}"
        if request:
            request = f"Comarch soap request:\n\n{self._prettify_xml(request)}\n"
        if response:
            response = f"Comarch soap response:\n\n{self._prettify_xml(response)}\n"

        extra = dict(
            method=method,
            response_code=response_code,
            request=request,
            response=response,
            duration=round(end_time - start_time, 3),
        )

        if error and isinstance(error, Exception):
            description = str(error) if str(error) else error.__class__.__name__
            message = f"{message} failed with error:\n {description}"
            extra["error"] = description

        getattr(logger, level, "debug")(message, extra=extra)

    async def __aenter__(self) -> "ComarchSOAPAsyncClient":
        self.session = ClientSession()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.session.close()

    @staticmethod
    def _prettify_xml(xml_text):
        """Prettify XML"""
        return xml.dom.minidom.parseString(xml_text).toprettyxml()

    async def get_balance(self, card_number: str) -> dict:
        """
        retrieving points balance
        :param card_number: customer's loyalty card number
        :return:
        """
        return await self._make_request("getBalance", dict(cardNo=card_number))

    async def get_customer(self, card_number: str) -> dict:
        """
        retrieving customer data
        :param card_number: customer's loyalty card number
        :return:
        """
        return await self._make_request("getCustomer", dict(cardNo=card_number))

    async def get_transactions(self, card_number: str) -> dict:
        """
        finding transactions
        :param card_number: customer's loyalty card number
        :return:
        """
        return await self._make_request("getTransactions", dict(cardNo=card_number))

    async def get_account_summary(self, card_number: str) -> dict:
        """
        retrieving points balance and basic customer profile data like name or elite tier
        :param card_number: customer's loyalty card number
        :return:
        """
        return await self._make_request("getAccountSummary", dict(cardNo=card_number))

    async def merge_account(self, source_card_number: str, destination_card_number: str) -> dict:
        """
        Method for merging two accounts.

        :param source_card_number: donor loyalty card number
        :param destination_card_number: recipient loyalty card number
        :return:
        """
        return await self._make_request(
            "mergeAccount", dict(sourceCardNo=source_card_number, destinationCardNo=destination_card_number)
        )

    async def reverse_non_airline_accrual(
            self,
            card_number: str,

            partner_code: str,
            transaction_type: str,
            transaction_id: Optional[int] = None,
            partner_transaction_id: Optional[str] = None,

            value: Optional[int] = None,
            description: Optional[str] = None,
            # TODO: products: Optional[List[ProductData]] = None,
    ) -> dict:
        """
        Deduct previously accrued points based on provided products list and value fields.

        Transaction to reverse must be identified either by CLM ID or partner transaction ID.
        It is possible to make either full reversal (value field is empty) or partial (value field is not empty).
        It is (NOT YET!) possible to pass list of products that was reverted.
        They will be stored under this reversal transaction for informational purposes.

        :param card_number:            Loyalty Card number.
        :param partner_code:           Must be set to the same value as in original transaction.
        :param transaction_type:       Possible values will be provided in partnership configuration document.
        :param transaction_id:         Id of transaction which should be reverted.
        :param partner_transaction_id: Partner’s Id of transaction which should be reverted.
        :param value:                  Number of points to be deducted. If not provided, system will make full reversal.
        :param description:            Optional transaction description.
        """
        if not transaction_id and not partner_transaction_id:
            raise ValueError("Either transaction_id or partner_transaction_id is required.")
        if not (value is None or value > 0):
            raise ValueError("Expected positive value or None")

        args = {
            "cardNo": card_number,
            "partnerCode": partner_code,
            "trnType": transaction_type,
        }
        optionals = {
            "trnId": transaction_id,
            "prtTrnId": partner_transaction_id,
            "value": value,
            "desc": description,
        }
        args.update((k, v) for k, v in optionals.items() if v is not None)

        # response contains "revtrnId" on success
        return await self._make_request("reverseNonAirlineAccrual", args)

    async def non_airline_accrual(
            self,
            transaction_type: str,

            card_number: str,
            first_name: str,
            last_name: str,

            transaction_code: Optional[str],
            partner_code: str,
            partner_transaction_datetime: datetime,
            partner_transaction_id: str,
            value: int,
            description: Optional[str] = None,

            location_code: Optional[str] = None,
            benefit_codes: Union[str, List[str], None] = None,
            # TODO revenue: Optional[float],  # Double(10.2)
            # TODO products: Optional[List[ProductData]] = None,
            # TODO dynamic_attributes: Optional[Dict[str, str]] = None,
    ) -> dict:
        """
        Non-airline products point accrual.

        :param transaction_type:       Possible values will be provided in partnership configuration document.
        :param card_number:            Loyalty Card number.
        :param first_name:             Member's first name (used in validation process)
        :param last_name:              Member's last name (used in validation process)

        :param transaction_code:       Transaction code.
        :param partner_code:           Partner code.
        :param partner_transaction_datetime: Date and time of the partner’s transaction.
        :param location_code:          Partner's location code.
        :param value:                  Number of points to accrue (only positive values).
        :param description:            Optional transaction description.

        :param partner_transaction_id: Unique transaction identifier. Duplication check is made upon these value.
        :param benefit_codes:          List of coupon codes.
        """
        if value <= 0:
            raise ValueError("Expected positive value")
        args = {
            "trnType": transaction_type,
            "cardNo": card_number,
            "value": value,

            "firstName": first_name.upper(),
            "lastName": last_name.upper(),

            "partnerCode": partner_code,
            "prtTrnDate": partner_transaction_datetime.strftime("%Y%m%d"),
            "prtTrnTime": partner_transaction_datetime.strftime("%H%M"),

            "prtTrnId": partner_transaction_id,
        }
        optionals = {
            "trnCode": transaction_code,
            "prtTrnTimeZone": None,  # FIXME: tz name from partner_transaction_datetime if exists?
            "locCode": location_code,
            "revenue": None,  # FIXME
            "desc": description,
            "benCodes": ",".join([benefit_codes] if isinstance(benefit_codes, str) else benefit_codes or []) or None,
            "product": None,  # FIXME
            "dynAttr": None,  # FIXME
        }
        args.update((k, v) for k, v in optionals.items() if v is not None)

        return await self._make_request("nonAirlineAccrual", args)

    async def enroll(self, customer: Customer, is_complete: bool = False) -> dict:
        """
        Method for enrolling a new program member.

        :param customer: new customer data
        :param is_complete: "False" indicates that it is "quick enrollment" (see Comarch docs)

        :return:
        """
        args = dict(
            customer=customer.to_comarch(),
            incompleteData="N" if is_complete else "Y")
        return await self._make_request("enroll", args)
