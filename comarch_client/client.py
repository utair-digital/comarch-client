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

        query = {
            method: {
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

    async def enroll(self, customer: Customer, is_complete: bool = False):
        """
        Method for enrolling a new program member.

        :param customer: new customer data
        :param is_complete: "False" indicates that it is "quick enrollment" (see Comarch docs)

        :return:
        """
        request = dict(
            customer=customer.to_comarch(),
            incompleteData="N" if is_complete else "Y")
        return await self._make_request("enroll", request)
