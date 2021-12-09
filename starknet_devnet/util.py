from enum import Enum, auto
import argparse
from typing import Union

from starkware.starkware_utils.error_handling import StarkException
from . import __version__

class TxStatus(Enum):
    """
    According to: https://www.cairo-lang.org/docs/hello_starknet/intro.html#interact-with-the-contract
    """

    PENDING = auto()
    """The transaction passed the validation and is waiting to be sent on-chain."""

    NOT_RECEIVED = auto()
    """The transaction has not been received yet (i.e., not written to storage"""

    RECEIVED = auto()
    """The transaction was received by the operator."""

    REJECTED = auto()
    """The transaction failed validation and thus was skipped."""

    ACCEPTED_ONCHAIN = auto()
    """The transaction was accepted on-chain."""

def custom_int(arg: str) -> str:
    base = 16 if arg.startswith("0x") else 10
    return int(arg, base)

def fixed_length_hex(arg: int) -> str:
    """
    Converts the int input to a hex output of fixed length
    """

    return f"0x{arg:064x}"


def fork_name(name: str):
    if name == "alpha":
        return "https://alpha4.starknet.io"
    elif name == "alpha-mainnet":
        return "https://alpha-mainnet.starknet.io"
    # otherwise a URL; perhaps check validity
    return name

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5000
def parse_args():
    parser = argparse.ArgumentParser(description="Run a local instance of Starknet devnet")
    parser.add_argument(
        "-v", "--version",
        help="Print the version",
        action="version",
        version=__version__
    )
    parser.add_argument(
        "--host",
        help=f"Specify the address to listen at; defaults to {DEFAULT_HOST}" +
             f"(use the address the program outputs on start)",
        default=DEFAULT_HOST
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        help=f"Specify the port to listen at; defaults to {DEFAULT_PORT}",
        default=DEFAULT_PORT
    )
    parser.add_argument(
        "--fork", "-f",
        type=fork_name,
        help=f"Specify the network to fork: can be a URL (e.g. https://alpha-mainnet.starknet.io) " +
             f"or network name (alpha or alpha-mainnet)",
    )

    return parser.parse_args()

class StarknetDevnetException(StarkException):
    def __init__(self, code=500, message=None):
        super().__init__(code=code, message=message)
