from http import HTTPStatus
import logging
from typing import Iterable, Any, Sequence
from unittest import TestCase

from asserts import assert_equal, assert_raises, assert_is_instance, \
    assert_regex, assert_in

from werkzeug.exceptions import Conflict
from werkzeug.wrappers import Request

from rouver.exceptions import ArgumentsError
from rouver.router import Router, LOGGER_NAME
from rouver.types import \
    StartResponse, WSGIEnvironment, WSGIResponse, WSGIApplication

from rouver_test.util import TestingStartResponse, default_environment


def handle_success(_: WSGIEnvironment, start_response: StartResponse) \
        -> Iterable[bytes]:
    start_response("200 OK", [])
    return [b""]


def handle_empty_path(environ: WSGIEnvironment,
                      start_response: StartResponse) -> Iterable[bytes]:
    assert_equal([], environ["rouver.path_args"])
    start_response("200 OK", [])
    return [b""]


def fail_if_called(_: WSGIEnvironment, __: StartResponse) -> Iterable[bytes]:
    raise AssertionError("handler should not be called")


class RouterTest(TestCase):
    def setUp(self) -> None:
        self.router = Router()
        self.router.error_handling = False
        self.start_response = TestingStartResponse()
        self.environment = default_environment()
        self.disable_logger()

    def disable_logger(self) -> None:
        logging.getLogger(LOGGER_NAME).disabled = True

    def _create_path_checker(self, expected_path: str) -> WSGIApplication:
        def handle(environ: WSGIEnvironment, sr: StartResponse) \
                -> Sequence[bytes]:
            assert_equal(expected_path, environ["PATH_INFO"])
            sr("200 OK", [])
            return []

        return handle

    def handle_wsgi(self, method: str = "GET", path: str = "/") \
            -> Iterable[bytes]:
        self.environment["REQUEST_METHOD"] = method
        self.environment["PATH_INFO"] = path
        return self.router(self.environment, self.start_response)

    def test_not_found_response_page(self) -> None:
        response = self.handle_wsgi("GET", "/foo/bar")
        html = b"".join(response).decode("utf-8")
        assert_equal("""<!DOCTYPE html>
<html>
    <head>
        <title>404 &mdash; Not Found</title>
    </head>
    <body>
        <h1>404 &mdash; Not Found</h1>
        <p>Path &#x27;/foo/bar&#x27; not found.</p>
    </body>
</html>
""", html)

    def test_not_found_escape_path(self) -> None:
        response = self.handle_wsgi("GET", "/foo/<bar")
        html = b"".join(response).decode("utf-8")
        assert_in("<p>Path &#x27;/foo/&lt;bar&#x27; not found.</p>", html)

    def test_no_routes(self) -> None:
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)
        self.start_response.assert_header_equals("Content-Type",
                                                 "text/html; charset=utf-8")

    def test_handler_request(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal("test.example.com", environ["SERVER_NAME"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_routes([
            ("", "GET", handle),
        ])
        self.environment["SERVER_NAME"] = "test.example.com"
        self.handle_wsgi("GET", "")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_empty_route(self) -> None:
        self.router.add_routes([
            ("", "GET", handle_empty_path),
        ])
        self.handle_wsgi("GET", "")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_root_route(self) -> None:
        self.router.add_routes([
            ("", "GET", handle_empty_path),
        ])
        self.handle_wsgi("GET", "/")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_first_level(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal("", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return []

        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_first_level__trailing_slash(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal("/", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return []

        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_first_level_wrong_path(self) -> None:
        self.router.add_routes([
            ("foo", "GET", handle_empty_path),
        ])
        self.handle_wsgi("GET", "/bar")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_level_mismatch_1(self) -> None:
        self.router.add_routes([
            ("foo/bar", "GET", handle_empty_path),
        ])
        self.handle_wsgi("GET", "/foo")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_level_mismatch_2(self) -> None:
        self.router.add_routes([
            ("foo", "GET", handle_empty_path),
        ])
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    # Method Handling

    def test_wrong_method_response_page(self) -> None:
        self.router.add_routes([
            ("foo", "GET", fail_if_called),
            ("foo", "PUT", fail_if_called),
        ])
        response = self.handle_wsgi("POST", "/foo")
        html = b"".join(response).decode("utf-8")
        assert_equal("""<!DOCTYPE html>
<html>
    <head>
        <title>405 &mdash; Method Not Allowed</title>
    </head>
    <body>
        <h1>405 &mdash; Method Not Allowed</h1>
        <p>Method &#x27;POST&#x27; not allowed. Please try GET or PUT.</p>
    </body>
</html>
""", html)

    def test_wrong_method_escape_method(self) -> None:
        self.router.add_routes([
            ("foo", "GET", fail_if_called),
        ])
        response = self.handle_wsgi("G<T", "/foo")
        html = b"".join(response).decode("utf-8")
        assert_in(
            "<p>Method &#x27;G&lt;T&#x27; not allowed. Please try GET.</p>",
            html)

    def test_wrong_method(self) -> None:
        self.router.add_routes([
            ("foo", "GET", fail_if_called),
            ("foo", "PUT", fail_if_called),
        ])
        self.handle_wsgi("POST", "/foo")
        self.start_response.assert_status(HTTPStatus.METHOD_NOT_ALLOWED)
        self.start_response.assert_header_equals("Allow", "GET, PUT")

    def test_wrong_method__multiple_matches(self) -> None:
        self.router.add_routes([
            ("foo", "GET", fail_if_called),
            ("foo", "GET", fail_if_called),
        ])
        self.handle_wsgi("POST", "/foo")
        self.start_response.assert_status(HTTPStatus.METHOD_NOT_ALLOWED)
        self.start_response.assert_header_equals("Allow", "GET")

    def test_call_right_method(self) -> None:
        self.router.add_routes([
            ("foo", "GET", fail_if_called),
            ("foo", "POST", handle_success),
            ("foo", "PUT", fail_if_called),
        ])
        self.handle_wsgi("POST", "/foo")
        self.start_response.assert_status(HTTPStatus.OK)

    # Path Templates

    def test_unknown_template(self) -> None:
        with assert_raises(KeyError):
            self.router.add_routes([
                ("foo/{unknown}/bar", "GET", fail_if_called),
            ])

    def test_no_template(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal([], environ["rouver.path_args"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_routes([
            ("foo/bar", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_template(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal(["xyzxyz"], environ["rouver.path_args"])
            start_response("200 OK", [])
            return [b""]

        def handle_path(request: Request, paths: Sequence[Any], path: str) \
                -> str:
            assert_is_instance(request, Request)
            assert_equal([], paths)
            return path * 2

        self.router.add_template_handler("handler", handle_path)

        self.router.add_routes([
            ("foo/{handler}/bar", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/xyz/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_multiple_templates(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal(["xyz", 123], environ["rouver.path_args"])
            start_response("200 OK", [])
            return [b""]

        def handle_path(_: Request, paths: Sequence[Any], __: str) -> int:
            assert_equal(["xyz"], paths)
            return 123

        self.router.add_template_handler("handler1", lambda _, __, ___: "xyz")
        self.router.add_template_handler("handler2", handle_path)

        self.router.add_routes([
            ("foo/{handler1}/bar/{handler2}", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/xyz/bar/abc")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_template_value_error(self) -> None:
        def raise_value_error(_: Request, __: Sequence[str], ___: str) -> None:
            raise ValueError()

        self.router.add_template_handler("handler", raise_value_error)

        self.router.add_routes([
            ("foo/{handler}/bar", "GET", fail_if_called),
        ])
        self.handle_wsgi("GET", "/foo/xyz/bar")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_template_multiple_matches(self) -> None:
        def raise_value_error(_: Request, __: Sequence[str], ___: str) -> None:
            raise ValueError()

        self.router.add_template_handler("handler1", raise_value_error)
        self.router.add_template_handler("handler2", lambda _, __, ___: None)

        self.router.add_routes([
            ("foo/{handler1}/bar", "GET", fail_if_called),
            ("foo/{handler2}/bar", "GET", handle_success),
        ])
        self.handle_wsgi("GET", "/foo/xyz/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_template_multiple_matches__match_first(self) -> None:
        self.router.add_template_handler("handler1", lambda _, __, ___: None)
        self.router.add_template_handler("handler2", lambda _, __, ___: None)

        self.router.add_routes([
            ("foo/{handler1}/bar", "GET", handle_success),
            ("foo/{handler2}/bar", "GET", fail_if_called),
        ])
        self.handle_wsgi("GET", "/foo/xyz/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_template_call_once_per_value(self) -> None:
        calls = 0

        def increase_count(_: Request, __: Sequence[str], ___: str) -> None:
            nonlocal calls
            calls += 1

        self.router.add_template_handler("handler", increase_count)

        self.router.add_routes([
            ("foo/{handler}/bar", "GET", fail_if_called),
            ("foo/{handler}/baz", "GET", handle_success),
        ])
        self.handle_wsgi("GET", "/foo/xyz/baz")
        assert_equal(1, calls)

    def test_template_call_twice_for_differing_values(self) -> None:
        calls = 0

        def increase_count(_: Request, __: Sequence[str], ___: str) -> None:
            nonlocal calls
            calls += 1

        self.router.add_template_handler("handler", increase_count)

        self.router.add_routes([
            ("foo/{handler}/bar", "GET", fail_if_called),
            ("foo/xyz/{handler}", "GET", handle_success),
        ])
        self.handle_wsgi("GET", "/foo/xyz/baz")
        assert_equal(2, calls)

    # Wildcard Paths

    def test_no_wildcard_path(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal("", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_routes([
            ("foo/bar", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_wildcard_path__no_trailing_slash(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal([], environ["rouver.path_args"])
            assert_equal("", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_routes([
            ("foo/bar/*", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_wildcard_path__with_trailing_slash(self) -> None:
        def handle(environ: WSGIEnvironment,  start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal([], environ["rouver.path_args"])
            assert_equal("/", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_routes([
            ("foo/bar/*", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/bar/")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_wildcard_path__additional_path(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal([], environ["rouver.path_args"])
            assert_equal("/abc/def", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_routes([
            ("foo/bar/*", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/bar/abc/def")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_wildcard_path__with_template(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal(["value"], environ["rouver.path_args"])
            assert_equal("/abc/def", environ["rouver.wildcard_path"])
            start_response("200 OK", [])
            return [b""]

        self.router.add_template_handler("bar", lambda *args: "value")
        self.router.add_routes([
            ("foo/{bar}/*", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo/unknown/abc/def")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_wildcard_path__too_short(self) -> None:
        self.router.add_routes([
            ("foo/bar/*", "GET", handle_success),
        ])
        self.handle_wsgi("GET", "/foo")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_wildcard_path__does_not_match(self) -> None:
        self.router.add_routes([
            ("foo/bar/*", "GET", handle_success),
        ])
        self.handle_wsgi("GET", "/foo/wrong")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_wildcard_path__not_at_end(self) -> None:
        with assert_raises(ValueError):
            self.router.add_routes([
                ("foo/*/bar", "GET", handle_success),
            ])

    def test_wildcard__before_more_specific(self) -> None:
        self.router.add_routes([
            ("foo/*", "GET", handle_success),
            ("foo/bar", "GET", fail_if_called),
        ])
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_wildcard__after_more_specific(self) -> None:
        self.router.add_routes([
            ("foo/bar", "GET", handle_success),
            ("foo/*", "GET", fail_if_called),
        ])
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    # Sub routers

    def test_sub_router(self) -> None:
        sub = Router()
        sub.error_handling = False
        sub.add_routes([
            ("sub", "GET", self._create_path_checker("/sub")),
        ])
        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/bar/sub")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__no_match(self) -> None:
        sub = Router()
        sub.error_handling = False
        sub.add_routes([
            ("sub", "GET", fail_if_called),
        ])
        self.router.add_sub_router("foo", sub)
        self.handle_wsgi("GET", "/wrong/sub")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_sub_router__base_with_slash(self) -> None:
        sub = Router()
        sub.error_handling = False
        sub.add_routes([
            ("", "GET", self._create_path_checker("/")),
        ])
        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/bar/")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__base_without_slash(self) -> None:
        sub = Router()
        sub.error_handling = False
        sub.add_routes([
            ("", "GET", self._create_path_checker("")),
        ])
        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/bar")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__path_info_encoding(self) -> None:
        expected_path = "/föo".encode("utf-8").decode("latin-1")

        def app(env: WSGIEnvironment, sr: StartResponse) -> Iterable[bytes]:
            assert_equal(expected_path, env["PATH_INFO"])
            sr("200 OK", [])
            return []

        self.router.error_handling = False
        self.router.add_sub_router("sub", app)
        self.handle_wsgi("GET", "/sub/föo".encode("utf-8").decode("latin-1"))
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__template_in_super_router(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal([], environ["rouver.path_args"])
            start_response("200 OK", [])
            return []

        def tmpl(_: Request, path: Sequence[str], v: str) -> str:
            assert_equal([], path)
            return v * 2

        sub = Router()
        sub.error_handling = False
        sub.add_template_handler("tmpl", tmpl)
        sub.add_routes([
            ("sub", "GET", handle),
        ])
        self.router.add_template_handler("tmpl", tmpl)
        self.router.add_sub_router("foo/{tmpl}", sub)
        self.handle_wsgi("GET", "/foo/bar/sub")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__template_in_sub_router(self) -> None:
        def handle(environ: WSGIEnvironment, start_response: StartResponse) \
                -> Iterable[bytes]:
            assert_equal(["xyzxyz"], environ["rouver.path_args"])
            start_response("200 OK", [])
            return []

        def tmpl(_: Request, path: Sequence[str], v: str) -> str:
            assert_equal([], path)
            return v * 2

        sub = Router()
        sub.error_handling = False
        sub.add_template_handler("tmpl", tmpl)
        sub.add_routes([
            ("{tmpl}", "GET", handle),
        ])
        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/bar/xyz")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__path_component(self) -> None:
        sub = Router()
        sub.error_handling = False
        sub.add_routes([
            ("sub", "GET", handle_success),
        ])
        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/barsub")
        self.start_response.assert_status(HTTPStatus.NOT_FOUND)

    def test_sub_router__match_after_other_routes(self) -> None:
        sub = Router()
        sub.error_handling = False
        sub.add_routes([
            ("sub", "GET", fail_if_called),
        ])
        self.router.add_routes([("foo/bar/sub", "GET", handle_success)])
        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/bar/sub")
        self.start_response.assert_status(HTTPStatus.OK)

    def test_sub_router__accepts_any_wsgi_app(self) -> None:
        def sub(environ: WSGIEnvironment, sr: StartResponse) -> WSGIResponse:
            assert_equal("/sub", environ["PATH_INFO"])
            sr("204 No Content", [])
            return []

        self.router.add_sub_router("foo/bar", sub)
        self.handle_wsgi("GET", "/foo/bar/sub")
        self.start_response.assert_status(HTTPStatus.NO_CONTENT)

    # Error Handling

    def test_internal_error_page(self) -> None:
        def handle(_: WSGIEnvironment, __: StartResponse) -> Iterable[bytes]:
            raise KeyError("Custom < error")

        self.router.error_handling = True
        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        response = self.handle_wsgi("GET", "/foo")
        html = b"".join(response).decode("utf-8")
        assert_equal("""<!DOCTYPE html>
<html>
    <head>
        <title>500 &mdash; Internal Server Error</title>
    </head>
    <body>
        <h1>500 &mdash; Internal Server Error</h1>
        <p>Internal server error.</p>
    </body>
</html>
""", html)

    def test_template_key_error_with_error_handling(self) -> None:
        def raise_key_error(_: Request, __: Sequence[str], ___: str) -> None:
            raise KeyError()

        self.router.add_template_handler("handler", raise_key_error)

        self.router.add_routes([
            ("foo/{handler}/bar", "GET", fail_if_called),
        ])
        self.router.error_handling = True
        self.handle_wsgi("GET", "/foo/xyz/bar")
        self.start_response.assert_status(HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_template_key_error_without_error_handling(self) -> None:
        def raise_key_error(_: Request, __: Sequence[str], ___: str) -> None:
            raise KeyError()

        self.router.add_template_handler("handler", raise_key_error)

        self.router.add_routes([
            ("foo/{handler}/bar", "GET", fail_if_called),
        ])
        self.router.error_handling = False
        with assert_raises(KeyError):
            self.handle_wsgi("GET", "/foo/xyz/bar")

    def test_handler_key_error_with_error_handling(self) -> None:
        def handle(_: WSGIEnvironment, __: StartResponse) -> Iterable[bytes]:
            raise KeyError()

        self.router.error_handling = True
        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        self.handle_wsgi("GET", "/foo")
        self.start_response.assert_status(HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_handler_key_error_without_error_handling(self) -> None:
        def handle(_: WSGIEnvironment, __: StartResponse) -> Iterable[bytes]:
            raise KeyError()

        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        self.router.error_handling = False
        with assert_raises(KeyError):
            self.handle_wsgi("GET", "/foo")

    def test_http_error(self) -> None:
        def handle(_: WSGIEnvironment, __: StartResponse) -> Iterable[bytes]:
            raise Conflict("Foo < Bar")

        self.router.error_handling = False
        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        response = self.handle_wsgi("GET", "/foo")
        self.start_response.assert_status(HTTPStatus.CONFLICT)
        html = b"".join(response).decode("utf-8")
        assert_equal("""<!DOCTYPE html>
<html>
    <head>
        <title>409 &mdash; Conflict</title>
    </head>
    <body>
        <h1>409 &mdash; Conflict</h1>
        <p>Foo &lt; Bar</p>
    </body>
</html>
""", html)

    def test_arguments_error(self) -> None:
        def handle(_: WSGIEnvironment, __: StartResponse) -> Iterable[bytes]:
            raise ArgumentsError({"foo": "bar"})

        self.router.add_routes([
            ("foo", "GET", handle),
        ])
        response = self.handle_wsgi("GET", "/foo")
        self.start_response.assert_status(HTTPStatus.BAD_REQUEST)
        html = b"".join(response).decode("utf-8")
        assert html.startswith("<!DOCTYPE html>")
        assert_regex(html, r'<li class="argument">\s*'
                     r'<span class="argument-name">foo</span>:\s*'
                     r'<span class="error-message">bar</span>\s*'
                     r'</li>')
