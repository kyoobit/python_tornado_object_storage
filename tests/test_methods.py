import tornado

import pytest

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerMethods(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True)

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods

    @pytest.mark.xfail(reason="CONNECT not supported")
    def test_HTTP_method_CONNECT(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="CONNECT")
        # Check response code for the expected value
        self.assertEqual(response.code, -1)

    def test_HTTP_method_DELETE(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="DELETE")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_GET(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="GET")
        # Check response code for the expected value
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b"pong\n")

    def test_HTTP_method_HEAD(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="HEAD")
        # Check response code for the expected value
        self.assertEqual(response.code, 200)

    def test_HTTP_method_OPTIONS(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="OPTIONS")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_PATCH(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="PATCH", body="test")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_POST(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="POST", body="test")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_PUT(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="PUT", body="test")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    @pytest.mark.xfail(reason="TRACE not supported")
    def test_HTTP_method_TRACE(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="TRACE")
        # Check response code for the expected value
        self.assertEqual(response.code, -1)


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerAdminMethods(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, admin=True)

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods

    @pytest.mark.xfail(reason="CONNECT not supported")
    def test_HTTP_method_CONNECT(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="CONNECT")
        # Check response code for the expected value
        self.assertEqual(response.code, -1)

    def test_HTTP_method_DELETE(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="DELETE")
        # Check response code for the expected value
        self.assertEqual(response.code, 200)

    def test_HTTP_method_GET(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="GET")
        # Check response code for the expected value
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b"pong\n")

    def test_HTTP_method_HEAD(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="HEAD")
        # Check response code for the expected value
        self.assertEqual(response.code, 200)

    def test_HTTP_method_OPTIONS(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="OPTIONS")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_PATCH(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="PATCH", body="test")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_POST(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="POST", body="test")
        # Check response code for the expected value
        self.assertEqual(response.code, 405)

    def test_HTTP_method_PUT(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="PUT", body="test")
        # Check response code for the expected value
        self.assertEqual(response.code, 200)

    @pytest.mark.xfail(reason="TRACE not supported")
    def test_HTTP_method_TRACE(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="TRACE")
        # Check response code for the expected value
        self.assertEqual(response.code, -1)
