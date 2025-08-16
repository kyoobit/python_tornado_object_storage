import argparse
import logging
import sys

from configparser import ConfigParser
from datetime import datetime
from urllib.parse import unquote_plus

from app import main


__version__ = "0.0.1a"


# -----------------------------------------------------------------------------
def handle_config(argv: argparse.Namespace, remaining_argv: list) -> dict:
    """Use a configuration file to update/override argparse options"""

    # Make sure `argv' is the correct type or escape
    if not isinstance(argv, argparse.Namespace):
        return argv, remaining_argv

    # Make sure a `config' option was provided or escape
    if not getattr(argv, "config", False):
        return argv, remaining_argv

    # Import and parse the configuration file raising errors as needed
    config = ConfigParser()
    config.read(argv.config)

    # NOTE: `section' name will use is the hostname in uppercase format as the
    # default section if the `section' option was not passed in `argv'.
    if hasattr(argv, "section"):
        section = str(argv.section).upper()
        # Continue ONLY if there is a matching `section' in the configuration file.
        if section not in config.sections():
            print(f"Section {section!r} not found in: {argv.config!r}")
            return argv, remaining_argv

    # Set the values in `argv' to the values parsed from the configuration file
    # ONLY if the value is None. Non-None values are ass-u-me-d to be set by
    # the command-line and intended to override some value set in the
    # configuration file
    for key, value in config[section].items():
        # Debug message
        if getattr(argv, "debug", False):
            print(
                f"DEBUG: argv.{key} {type(getattr(argv, key))}: {getattr(argv, key)!r} (before)"
            )
        # Set values only when None
        if not hasattr(argv, key) or getattr(argv, key) is None:
            # Convert `values' to known data types
            setattr(argv, key, to_type(value.split("#")[0].strip()))
        # Debug message
        if getattr(argv, "debug", False):
            print(f"DEBUG: conf.{key} {type(value)}: {value!r}")
            print(
                f"DEBUG: argv.{key} {type(getattr(argv, key))}: {getattr(argv, key)!r} (after)"
            )

    # Return the updated `argv' and pass-through `remaining_argv' as-is
    return argv, remaining_argv


# -----------------------------------------------------------------------------
def to_type(value: str, **kwargs):
    """Convert a string value to another type"""
    if not isinstance(value, str):
        return value
    # Convert to a specified type.
    if kwargs.get("as_type", False):
        return kwargs.get("as_type")(value)
    # Try converting to a standard type
    match unquote_plus(value):
        # Float
        case v if v.find(".") != -1 and v.replace(".", "").isdigit():
            return float(v)
        # Integer
        case v if v.replace(".", "").isdigit():
            return int(v)
        # Boolean
        case v if v.lower() in ["true"]:
            return True
        case v if v.lower() in ["false"]:
            return False
        # NoneType ('none', 'nil', 'null', '')
        case v if v.lower() in ["none", "nil", "null", ""]:
            return None
    # Try converting from an ISO string to a datetime object
    # ISO Datetime: YYYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]
    # https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass
    return value


if __name__ == "__main__":
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description="A Python Tornado HTTP Web \
        service which provides access to a remote object storage service using \
        an AWSv4 signature for authentication."
    )

    parser.add_argument(
        "--config",
        metavar="<file>",
        default=False,
        help="Use a configuration file for settings. \
        NOTE: Command-line arguments will override settings in a configuration file.",
    )
    parser.add_argument(
        "--section",
        metavar="<NAME>",
        default="production",
        help="Use a specific section in a configuration file (Default: PRODUCTION)",
    )

    # NOTE: Arguments should have a default value of `None' here or the value
    # in the DEFAULT section of a configuration file will NOT override the
    # setting.

    # Object storage service specific arguments
    parser.add_argument(
        "--key",
        "-k",
        metavar="<key>",
        dest="access_key",
        help="Set the API access key to use",
    )
    parser.add_argument(
        "--secret",
        "-s",
        metavar="<key>",
        dest="secret_key",
        help="Set the API secret key to use",
    )
    parser.add_argument(
        "--endpoint", "-e", metavar="<host>", help="Set the endpoint to use"
    )
    parser.add_argument("--bucket", "-b", metavar="<str>", help="Set the bucket to use")
    parser.add_argument("--service", metavar="<str>", help="Set the service to use")
    parser.add_argument("--region", metavar="<str>", help="Set the region to use")
    parser.add_argument("--scheme", metavar="<str>", help="Set the scheme to use")

    # Miscellaneous application settings
    parser.add_argument(
        "--port",
        default=8888,
        metavar="<N>",
        type=int,
        help="Set the port this HTTP service will listen on",
    )
    parser.add_argument(
        "--admin", action="store_true", help="Enable administrative endpoints."
    )
    parser.add_argument(
        "--auth-only",
        action="store_true",
        default=None,
        dest="auth_only",
        help="Enable authentication only.",
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"version {__version__}"
    )
    parser.add_argument(
        "--systemd",
        action="store_true",
        default=None,
        help="Run with systemd service mode enabled",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=None,
        help="Run with verbose messages enabled",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=None,
        help="Run with noisy debug messages enabled",
    )
    # Parse all arguments
    argv, remaining_argv = handle_config(*parser.parse_known_args())

    # Pass the program __version__ in as an attribute
    argv.version = __version__

    # Configure logging
    # https://docs.python.org/3/howto/logging.html
    if argv.debug:
        log_level = logging.DEBUG
    elif argv.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    # Do not include the date when systemd service is True
    # Logs are collected to journalctl which already includes a date
    if argv.systemd:
        log_format = "[app=tornado_awsv4] %(levelname)s - %(message)s"
    else:
        log_format = "[%(asctime)s] %(levelname)s - %(message)s"
    log_datefmt = "%Y-%m-%d %H:%M:%S %Z"
    logging.basicConfig(
        format=log_format,
        datefmt=log_datefmt,
        level=log_level,
    )
    logging.debug(f"{__name__} - sys.argv: {sys.argv}")
    logging.debug(f"{__name__} - argv: {argv}")

    # Debug argv attributes
    if argv.debug:
        for key, value in vars(argv).items():
            logging.debug(f"{__name__} - argv.{key} {type(value)}: {value!r}")

    # Run the program
    try:
        # Pass all parsed arguments to the main function as key word arguments
        main(**vars(argv))
    except Exception as err:
        logging.error(f"{sys.exc_info()[0]}; {err}")
        # Cause the program to exit on error when running in debug mode
        if hasattr(argv, "debug") and argv.debug:
            raise
