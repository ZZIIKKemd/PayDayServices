from typing import Union

from api.type.goip import Goip
from api.type.telegram import Telegram
from api.type.unisender import Unisender

ApiType = Union[Unisender, Telegram, Goip]
