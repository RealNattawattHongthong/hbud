# Python and DBus compatibility
# See:  https://www.freedesktop.org/wiki/Specifications/mpris-spec/metadata/
from __future__ import annotations
from random import choices
from typing import Any, Callable, Optional
from functools import wraps
import logging

from ..base import VALID_CHARS, RAND_CHARS, NAME_PREFIX, \
  DbusObj
from .metadata import Metadata, DbusMetadata, DbusTypes, \
  DbusTypes, METADATA_TYPES
from ..types import Final


DBUS_NAME_MAX: Final[int] = 255
START_WITH: Final[str] = "_"
FIRST_CHAR: Final[int] = 0

# following must be subscriptable to be used with random.choices()
VALID_CHARS_SUB: Final[tuple[str, ...]] = \
  tuple(VALID_CHARS)
INTERFACE_CHARS: Final[set[str]] = \
  {*VALID_CHARS, '-'}


ReturnsStr = Callable[..., str]


def random_name() -> str:
  chars = choices(VALID_CHARS_SUB, k=RAND_CHARS)
  rand = ''.join(chars)

  return NAME_PREFIX + rand


def enforce_dbus_length(func: ReturnsStr) -> ReturnsStr:
  @wraps(func)
  def new_func(*args, **kwargs) -> str:
    val: str = func(*args, **kwargs)
    return val[:DBUS_NAME_MAX]

  return new_func


@enforce_dbus_length
def get_dbus_name(
  name: Optional[str] = None,
  is_interface: bool = False
) -> str:
  if not name:
    return get_dbus_name(random_name())

  # interface names can contain hyphens
  valid_chars = INTERFACE_CHARS if is_interface else VALID_CHARS

  # new name shouldn't have spaces
  new_name = name.replace(' ', '_')

  # new name should only contain D-Bus valid chars
  new_name = ''.join(
    char
    for char in new_name
    if char in valid_chars
  )

  # D-Bus names can't start with numbers
  if new_name and new_name[FIRST_CHAR].isnumeric():
    # just stick an underscore in front of the number
    return START_WITH + new_name

  # but they can start with letters or underscores
  elif new_name:
    return new_name

  # if there is no name left after normalizing,
  # then make a random one and validate it
  return get_dbus_name(random_name())


@enforce_dbus_length
def get_track_id(name: str) -> DbusObj:
  return f'/track/{get_dbus_name(name)}'
