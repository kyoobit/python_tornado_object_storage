import pytest

import tornado

from app import make_app


class TestApp(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True)

    def test_ping(self):
        # Make the HTTP request
        response = self.fetch("/ping", method="GET")

        # Check response code for the expected value
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b"pong\n")

    @pytest.mark.skip(reason="test requires specific access")
    def test_image(self):
        # Make the HTTP request
        response = self.fetch("/img/pork-stamp.jpg")

        # Check response code for the expected value
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/jpeg")
        self.assertIsNotNone(response.headers.get("Etag"))
        self.assertIsNotNone("Last-Modified")
        self.assertEqual(
            len(response.body), int(response.headers.get("Content-Length"))
        )

        # Make the HTTP request with If-None-Match Etag
        response = self.fetch(
            "/img/pork-stamp.jpg",
            headers={"If-None-Match": response.headers.get("Etag")},
        )

        # Check response code for the expected value
        self.assertEqual(response.code, 304)
