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


@dataclass
class Cell:
    text: str
    style: Style

    @classmethod
    def from_google(cls, data: dict):
        return cls(
            text = str(tuple(data['userEnteredValue'].values())[0]),
            style = Style.from_google(data['effectiveFormat'])
        )
