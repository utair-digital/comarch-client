|License|

Сomarch SOAP client
===================


Async client for comarch loyalty management.

Main purpose of this library to support comarch soap api.

Install
-------
.. code-block:: sh

    $ pip install git+https://github.com/utair-digital/comarch-client


Basic Example
-------------

.. code-block:: python

    async with ComarchSOAPAsyncClient(username="", password="", uri="") as client:
            response = await client.get_balance("000000000")




Supported Comarch methods
-------------------------

+------------------------------+------------------------------------------------------------------------------------+
| name                         | description                                                                        |
+==============================+====================================================================================+
| get_balance                  | retrieving points balance                                                          |
+------------------------------+------------------------------------------------------------------------------------+
| get_customer                 | retrieving customer data                                                           |
+------------------------------+------------------------------------------------------------------------------------+
| get_transactions             | finding transactions                                                               |
+------------------------------+------------------------------------------------------------------------------------+
| get_account_summary          | retrieving points balance and basic customer profile data like name or elite tier  |
+------------------------------+------------------------------------------------------------------------------------+
| merge_account                | Method for merging two accounts                                                    |
+------------------------------+------------------------------------------------------------------------------------+
| enroll                       | Method used for enrolling new program member.                                      |
+------------------------------+------------------------------------------------------------------------------------+
| non_airline_accrual          | Non-airline products point accrual                                                 |
+------------------------------+------------------------------------------------------------------------------------+
| reverse_non_airline_accrual  | Deduct previously accrued points based on provided products list and value fields  |
+------------------------------+------------------------------------------------------------------------------------+

Requirements
------------

* Python_ 3.8+
* xmltodict_ 0.12.0
* aiohttp_ 3.6.2


.. _Python: https://www.python.org
.. _xmltodict: https://github.com/martinblech/xmltodict
.. _aiohttp: https://docs.aiohttp.org/en/stable/


License
=======

GNU General Public License v3.0


.. |License| image:: https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg
   :target: LICENSE
   :alt: Repository License
