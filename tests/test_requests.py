import tornado

from app import make_app


class TestApp(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_request(self):
        for path, options, status_code in [
            # REQUEST: tuple = (path: str, options: dict, status_code: int),
            ("/foo", {"method": "GET"}, 200),
            ("/bar", {"method": "GET"}, 200),
            ("/blast", {"method": "HEAD"}, 405),
            ("/blast", {"method": "OPTIONS"}, 405),
            ("/blast", {"method": "DELETE"}, 405),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            # Check response body for expected values
            if status_code == 200:
                self.assertEqual(response.body, b"Hello, World!\n")
