import base64
import datetime
import hashlib
import hmac
import logging
import sys
import os

from mimetypes import guess_type

# https://www.tornadoweb.org/
# python3 -m pip install --upgrade pip tornado
import tornado.httpclient
import tornado.httpserver
import tornado.web

__version__ = '0.0.1a'

# f-string support
NL = '\n'
TB = '\t'
CR = '\r'

class AWSv4Handler(tornado.web.RequestHandler):
    """Handle making HTTP requests using the AWSv4 signature

    See Also:
      https://www.tornadoweb.org/en/stable/web.html
      https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
    """

    def initialize(self, **kwargs):
        name = 'AWSv4Handler.initialize'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")


    async def delete(self, **kwargs):
        """Handle HTTP DELETE requests

        See Also:
          https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html
        """
        name = 'AWSv4Handler.delete'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        # This method requires admin
        if not self.settings.get('admin', False):
            self.set_status(405)
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            return

        if self.request.path.endswith('/ping'):
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            self.write('pong\n')
            return

        return await self.fetch(**kwargs)


    async def head(self, **kwargs):
        """Handle HTTP HEAD requests

        See Also:
          https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html
        """
        name = 'AWSv4Handler.head'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        if self.request.path.endswith('/ping'):
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            return

        return await self.fetch(**kwargs)

    async def get(self, **kwargs):
        """Handle HTTP GET requests

        See Also:
          https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
        """
        name = 'AWSv4Handler.get'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        if self.request.path.endswith('/ping'):
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            self.write('pong\n')
            return

        return await self.fetch(**kwargs)


    async def put(self, **kwargs):
        """Handle HTTP PUT requests

        See Also:
          https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html
        """
        name = 'AWSv4Handler.put'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        # This method requires admin
        if not self.settings.get('admin', False):
            self.set_status(405)
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            return

        if self.request.path.endswith('/ping'):
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            self.write('pong\n')
            return

        return await self.fetch(**kwargs)


    @staticmethod
    def _sign(key:bytes, msg:str) -> str:
        """Return a new HMAC SHA256 digest"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


    def _get_aws4_signature(self, secret_key:str, date:str, region:str, service:str) -> str:
        """Return a AWSv4 signature"""
        w_date = self._sign(('AWS4' + secret_key).encode('utf-8'), date)
        w_region = self._sign(w_date, region)
        w_service = self._sign(w_region, service)
        aws4_signature = self._sign(w_service, 'aws4_request')
        return aws4_signature


    async def fetch(self, **kwargs):
        """Request an object using a AWSv4 signature

        See Also:
          https://www.tornadoweb.org/en/stable/httpclient.html
        """
        name = 'AWSv4Handler.fetch'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")
        request_url, request_headers = self.sign_request(**kwargs)
        logging.debug(f"{name} - request_url: {request_url!r}")
        logging.debug(f"{name} - request_headers: {request_headers!r}")

        # When `auth_only' is enabled, return the signed headers in the 
        # response WITHOUT making a request upstream.
        logging.debug(f"{name} - auth_only: {self.settings.get('auth_only', False)!r}")
        logging.debug(f"{name} - X-Auth-Only: {self.request.headers.get('X-Auth-Only', False)!r}")
        if self.settings.get('auth_only', False) \
        or self.request.headers.get('X-Auth-Only', False):
            # Include the expected cache-key location for the file
            url = 'https://us-east-1.s3.amazonaws.com/test/img/whoops.png'
            m = hashlib.new('md5', request_url.encode()).hexdigest()
            cache_key = '/data/nginx/'
            if request_url.find('_thumb') != -1:
                cache_key += 'thumb_cache/'
            else:
                cache_key += 'longtail_cache/'
            cache_key += f"{m[-1]}/{m[-3:-1]}/{m}"
            self.set_header('X-Cache-Key', cache_key)
            # With auth-only never cache
            self.set_header('Cache-Control', 'private, no-store')
            self.set_header('Content-Type', 'text/plain')
            x_host, x_uri_path = request_url.split('://', 1)[-1].split('/', 1)
            self.set_header('X-Host', x_host)
            self.set_header('X-URL', request_url)
            self.set_header('X-URI-Path', f"/{x_uri_path}")
            for name, value in request_headers.items():
                self.set_header(name, value)
            return

        # Allow some request headers to pass through
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests#validators
        for header_name in [
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified
            'If-Modified-Since',
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-None-Match
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag
            'If-None-Match',
            ]:
            header_value = self.request.headers.get(header_name)
            logging.debug(f"{name} - {header_name}: {header_value!r}")
            if (
                header_name is not None
                and header_value is not None
            ):
                request_headers[header_name] = str(header_value)
        logging.debug(f"{name} - request_headers: {request_headers!r}")

        # HTTP client request parameters
        # https://www.tornadoweb.org/en/stable/httpclient.html#request-objects
        request = {
            'url': request_url,
            'method': self.request.method,
            'headers': request_headers,
            'connect_timeout': int(self.settings.get('connect_timeout', 6)),
            'request_timeout': int(self.settings.get('request_timeout', 12)),
        }
        # Additional options for some HTTP methods
        if self.request.method in ['PUT', 'POST']:
            # Include body data for some HTTP methods
            request.update(body = self.request.body)

            # Set the Content-Type
            # https://docs.python.org/3/library/mimetypes.html#mimetypes.guess_type
            content_type, encoding = guess_type(self.request.path)
            if content_type is None:
                content_type = 'application/octet-stream'
            logging.debug(f"{name} - content_type {type(content_type)}: {content_type!r}")
            request['headers']['Content-Type'] = content_type

        # Create the HTTP client request object
        # https://www.tornadoweb.org/en/stable/httpclient.html#request-objects
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_request = tornado.httpclient.HTTPRequest(**request)

        # Make the HTTP request
        try:
            response = await http_client.fetch(http_request)
            request_time = 1000.0 * getattr(response, 'request_time', 0)
            logging.info('{status} {method} {full_url} {duration:0.2f}ms {size}B'.format(
                status = response.code,
                method = response.request.method,
                full_url = response.effective_url,
                duration = request_time,
                size = len(response.body),
                ))

            logging.debug(f"{name} - response.headers: {response.headers!r}")
            if self.settings.get('debug', False):
                print('================ response.headers ================')
                for header_name, header_value in response.headers.items():
                    print(f"{header_name}: {header_value}")
                print('================ response.headers ================')

            self.set_header('Content-Type', response.headers.get('Content-Type', 'application/octet-stream'))
            if response.headers.get('Etag') is not None:
                self.set_header('Etag', response.headers.get('Etag'))
            if response.headers.get('Last-Modified') is not None:
                self.set_header('Last-Modified', response.headers.get('Last-Modified'))
            self.set_status(response.code)
            if response.body and len(response.body) > 0:
                self.write(response.body)

        except tornado.httpclient.HTTPError as err:
            response = err.response
            request_time = 1000.0 * getattr(response, 'request_time', 0)
            logging.warning('{status} {method} {full_url} {duration:0.2f}ms {size}B'.format(
                status = response.code,
                method = response.request.method,
                full_url = response.effective_url,
                duration = request_time,
                size = len(response.body),
                ))

            logging.debug(f"{name} - response.headers: {response.headers!r}")
            if self.settings.get('debug', False):
                print('================ response.headers ================')
                for header_name, header_value in response.headers.items():
                    print(f"{header_name}: {header_value}")
                print('================ response.headers ================')
                print('================ response.body ================')
                print(response.body)
                print('================ response.body ================')

            self.set_status(response.code)

        finally:
            http_client.close()


    def sign_request(self, **kwargs):
        """Sign a request with a AWSv4 signature"""
        name = 'AWSv4Handler.sign_request'
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        algorithm = 'AWS4-HMAC-SHA256'
        now = datetime.datetime.utcnow()
        amzdate = now.strftime('%Y%m%dT%H%M%SZ')
        date = now.strftime('%Y%m%d')

        # 
        logging.debug(f"{name} - self.request.body {type(self.request.body)}: length={len(self.request.body)}")
        request_body_hash = hashlib.sha256(self.request.body).hexdigest()
        logging.debug(f"{name} - request_body_hash: {request_body_hash!r}")

        canonical_headers = '\n'.join([
            f"host:{self.settings.get('endpoint')}",
            f"x-amz-content-sha256:{request_body_hash}",
            f"x-amz-date:{amzdate}",
            ]) + '\n' # include a trailing line break
        logging.debug(f"{name} - canonical_headers: {canonical_headers!r}")

        # This should match the header names used in canonical_headers
        signed_headers = 'host;x-amz-content-sha256;x-amz-date'

        canonical_request = '\n'.join([
                self.request.method,
                f"/{self.settings.get('bucket')}{self.request.path}",
                '', # query string
                canonical_headers,
                signed_headers,
                request_body_hash,
            ])
        logging.debug(f"{name} - canonical_request: {canonical_request!r}")
        if self.settings.get('debug', False):
            print('================ canonical_request ================')
            print(canonical_request)
            print('================ canonical_request ================')

        credential_scope = '/'.join([
            date,
            self.settings.get('region'),
            self.settings.get('service'),
            'aws4_request',
            ])
        logging.debug(f"{name} - credential_scope: {credential_scope!r}")
        if self.settings.get('debug', False):
            print('================ credential_scope ================')
            print(credential_scope)
            print('================ credential_scope ================')

        string_to_sign = '\n'.join([
            algorithm,
            amzdate,
            credential_scope,
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest(),
            ])
        logging.debug(f"{name} - string_to_sign: {string_to_sign!r}")
        if self.settings.get('debug', False):
            print('================ string_to_sign ================')
            print(string_to_sign)
            print('================ string_to_sign ================')

        aws4_signature_key = self._get_aws4_signature(
            secret_key=self.settings.get('secret_key'),
            date=date,
            region=self.settings.get('region'),
            service=self.settings.get('service'),
            )
        logging.debug(f"{name} - aws4_signature_key: {aws4_signature_key!r}")

        aws4_signature = hmac.new(aws4_signature_key,
            (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
        logging.debug(f"{name} - aws4_signature: {aws4_signature!r}")

        authorization_header = ' '.join([
            algorithm,
            f"Credential={self.settings.get('access_key')}/{credential_scope},",
            f"SignedHeaders={signed_headers},"
            f"Signature={aws4_signature}",
            ])
        logging.debug(f"{name} - authorization_header: {authorization_header!r}")

        request_headers = {
            'x-amz-date': amzdate,
            'x-amz-content-sha256': request_body_hash,
            'Authorization': authorization_header,
            }
        logging.debug(f"{name} - request_headers: {request_headers!r}")
        if self.settings.get('debug', False):
            print('================ request_headers ================')
            for header_name, header_value in request_headers.items():
                print(f"{header_name}: {header_value}")
            print('================ request_headers ================')

        request_url = ''.join([
            self.settings.get('scheme'),
            '://',
            self.settings.get('endpoint'),
            f"/{self.settings.get('bucket')}{self.request.path}",
            ])
        logging.debug(f"{name} - request_url: {request_url!r}")

        return request_url, request_headers
