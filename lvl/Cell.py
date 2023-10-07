from dataclasses import dataclass

from .util import to_hex


@dataclass
class Color:
    code: str

    @classmethod
    def from_google(cls, data: dict):
        return cls(f'#{to_hex(data["red"]):02s}{to_hex(data["green"]):02s}{to_hex(data["blue"]):02s}')


@dataclass
class Style:
    background: Color
    bold: bool
    italic: bool
    underline: bool

    @classmethod
    def from_google(cls, data: dict):
        text_style = data['textFormat']

        return cls(
            background = Color.from_google(data['backgroundColor']),
            bold = text_style['bold'],
            italic = text_style['italic'],
            underline = text_style['underline']
        )


class Cell:
    def __init__(self, text: str, style: Style):
        self.text = text
        self.style = Style

    @classmethod
    def from_google(cls, data: dict):
        return cls(
            text = str(tuple(data['userEnteredValue'].values())[0]) if 'userEnteredValue' in data else None,
            style = Style.from_google(data['effectiveFormat']) if 'effectiveFormat' in data else None
        )

    @classmethod
    def empty(cls):
        return cls(None, None)
