import asyncio
import json
import logging
import os
import socket
from datetime import datetime
from random import randint

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector, AsyncResolver
from marshmallow import Schema

from .exceptions import PriceCypherError, RateLimitError

UNKNOWN_ERROR = 'pricecypher.sdk.internal.unknown'


class RestClientOptions(object):
    """
    Configuration object for RestClient.
    Used for configuring additional RestClient options, such as rate-limit retries.

    :param float or tuple[float,float] timeout: (optional) Change the requests connect and read timeout (in seconds).
        Pass a tuple to specify both values separately or a float to set both to it.
        (defaults to 300.0 (5 minutes) for both)
    :param int retries: (optional) In the event an API request returns a 429 response header (indicating rate-limit
        has been hit), the RestClient will retry the request this many times using an exponential backoff strategy,
        before raising a RateLimitError exception.
        (defaults to 3)
    """

    def __init__(self, timeout=None, retries=None, tcp_limit=None):
        self.timeout = 300.0
        self.retries = 3
        self.verify = True
        self.nameservers = ['1.1.1.1', '8.8.8.8']  # CloudFlare & Google DNS
        self.tcp_limit = 50

        if timeout is not None:
            self.timeout = timeout

        if retries is not None:
            self.retries = retries

        if 'SSL_VERIFY' in os.environ:
            self.verify = os.environ.get('SSL_VERIFY').lower() == 'true'

        if 'DNS_NAMESERVERS' in os.environ:
            self.nameservers = os.environ.get('DNS_NAMESERVERS').split(',')

        if tcp_limit is not None:
            self.tcp_limit = tcp_limit


class RestClient(object):
    """
    Provides simple methods for handling all RESTful api endpoints.

    :param str jwt: JWT token used to authorize requests to the APIs.
    :param RestClientOptions options: (optional) Pass an instance of RestClientOptions to configure additional
        RestClient options, such as rate-limit retries.
    """

    def __init__(self, jwt, options=None):
        if options is None:
            options = RestClientOptions()

        tcp_lim = options.tcp_limit
        timeout = ClientTimeout(total=options.timeout)
        resolver = AsyncResolver(nameservers=options.nameservers)
        connector = TCPConnector(limit=tcp_lim, resolver=resolver, verify_ssl=options.verify, family=socket.AF_INET)

        self.session = ClientSession(timeout=timeout, connector=connector, trust_env=True)
        self.options = options
        self.jwt = jwt

        self._metrics = {'retries': 0, 'backoff': []}
        self._skip_sleep = False

        self.base_headers = {
            'Authorization': f'Bearer {self.jwt}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    async def close(self):
        await self.session.close()

    # Returns the maximum amount of jitter to introduce in milliseconds (100ms)
    def MAX_REQUEST_RETRY_JITTER(self):
        return 100

    # Returns the maximum delay window allowed (1000ms)
    def MAX_REQUEST_RETRY_DELAY(self):
        return 1000

    # Returns the minimum delay window allowed (100ms)
    def MIN_REQUEST_RETRY_DELAY(self):
        return 100

    async def _retry(self, make_request):
        response = None
        # Track the API request attempt number
        attempt = 0

        # Reset the metrics tracker
        self._metrics = {'retries': 0, 'backoff': []}

        # Floor the retries at 0.
        retries = max(0, self.options.retries)

        while True:
            wait = None
            # Increment attempt number
            attempt += 1

            # Issue the request
            try:
                response = await make_request()

                if response.status != 429:
                    break

                logging.debug('Got 429 Too Many Attempts response.')

                # Try to find Retry After header in response, which specifies the number of seconds we should wait.
                wait = response.headers.get('Retry-After')
            except aiohttp.ClientConnectionError:
                logging.warning("Encountered a connection error.")

            # break iff no retry needed
            if retries <= 0 or attempt > retries:
                break

            if wait is not None:
                # Wait for at least 1 second and convert seconds to milliseconds.
                wait = 1000 * (int(wait) + 1)
            else:
                # No Retry After header. Apply an exponential backoff for subsequent attempts, using this formula:
                # max(
                #   MIN_REQUEST_RETRY_DELAY,
                #   min(
                #       MAX_REQUEST_RETRY_DELAY,
                #       (100ms * (2 ** attempt - 1)) + random_between(1, MAX_REQUEST_RETRY_JITTER)
                #   )
                # )

                # Increases base delay by (100ms * (2 ** attempt - 1))
                wait = 100 * 2 ** (attempt - 1)

                # Introduces jitter to the base delay; increases delay between 1ms to MAX_REQUEST_RETRY_JITTER (100ms)
                wait += randint(1, self.MAX_REQUEST_RETRY_JITTER())

                # Is never more than MAX_REQUEST_RETRY_DELAY (1s)
                wait = min(self.MAX_REQUEST_RETRY_DELAY(), wait)

                # Is never less than MIN_REQUEST_RETRY_DELAY (100ms)
                wait = max(self.MIN_REQUEST_RETRY_DELAY(), wait)

            logging.debug(f"Retrying in {wait} ms...")

            self._metrics['retries'] = attempt
            self._metrics['backoff'].append(wait)

            # Skip calling sleep() when running unit tests
            if self._skip_sleep is False:
                # sleep expects value in seconds, so convert the milliseconds formula above accordingly
                await asyncio.sleep(wait / 1000)

        # Return the final response, if available.
        return response

    async def get(self, url, params=None, schema: Schema = None):
        headers = self.base_headers.copy()
        response = await self._retry(lambda: self.session.get(url, params=params, headers=headers))

        return await self._process_response(response, schema)

    async def post(self, url, data=None, schema: Schema = None):
        headers = self.base_headers.copy()
        response = await self._retry(lambda: self.session.post(url, json=data, headers=headers))

        return await self._process_response(response, schema)

    async def patch(self, url, data=None):
        headers = self.base_headers.copy()

        response = await self._retry(lambda: self.session.patch(url, json=data, headers=headers))
        return await self._process_response(response)

    async def put(self, url, data=None):
        headers = self.base_headers.copy()

        response = await self._retry(lambda: self.session.put(url, json=data, headers=headers))
        return await self._process_response(response)

    async def delete(self, url, params=None, data=None):
        headers = self.base_headers.copy()

        response = await self._retry(lambda: self.session.delete(url, headers=headers, params=params or {}, json=data))
        return await self._process_response(response)

    async def _process_response(self, response, schema=None):
        parsed = await self._parse(response, schema)
        return parsed.content()

    async def _parse(self, response, schema=None):
        try:
            content = await response.json()

            if content is None:
                return EmptyResponse(response.status)

            return JsonResponse(content, response, schema)
        except ValueError:
            return PlainResponse(response, await response.text())


class Response(object):
    def __init__(self, status_code, content, headers):
        self._status_code = status_code
        self._content = content
        self._headers = headers

    def content(self):
        if self._is_error():
            if self._status_code == 429:
                reset_at = int(self._headers.get('x-ratelimit-reset', '-1'))
                raise RateLimitError(error_code=self._error_code(),
                                     message=self._error_message(),
                                     reset_at=reset_at)

            raise PriceCypherError(status_code=self._status_code,
                                   error_code=self._error_code(),
                                   message=self._error_message())
        else:
            return self._content

    def _is_error(self):
        return self._status_code is None or self._status_code >= 400

    # Force implementation in subclasses
    def _error_code(self):
        raise NotImplementedError

    def _error_message(self):
        raise NotImplementedError


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class JsonResponse(Response):
    def __init__(self, content, response, schema: Schema = None):
        if schema is not None and response.status < 400:
            content = schema.load(content)

        super(JsonResponse, self).__init__(response.status, content, response.headers)

    def _error_code(self):
        if 'errorCode' in self._content:
            return self._content.get('errorCode')
        elif 'error' in self._content:
            return self._content.get('error')
        else:
            return UNKNOWN_ERROR

    def _error_message(self):
        message = self._content.get('message', '')
        if message is not None and message != '':
            return message
        return self._content.get('error', '')


class PlainResponse(Response):
    def __init__(self, response, text):
        super(PlainResponse, self).__init__(response.status, text, response.headers)

    def _error_code(self):
        return UNKNOWN_ERROR

    def _error_message(self):
        return self._content


class EmptyResponse(Response):
    def __init__(self, status_code):
        super(EmptyResponse, self).__init__(status_code, '', {})

    def _error_code(self):
        return UNKNOWN_ERROR

    def _error_message(self):
        return ''
