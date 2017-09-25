"""
PitchClock
==========

PitchClock is a Python library for generating tone clocks for the visualization of tonal structures.
"""

from typing import Tuple, NewType, Union, Iterable, Set, Dict, Optional
from fractions import Fraction
from math import log, pi, sin, cos, ceil

import gizeh


__author__ = 'Aaron Hosford'
__author_email__ = 'hosford42@gmail.com'
__version__ = '0.0.2'
__license__ = 'MIT'
__url__ = 'https://hosford42.github.io/pitchclock'


Ratio = Union[int, float, Fraction]
Angle = NewType('Angle', Ratio)
Count = NewType('Count', int)
RelativePitch = NewType('RelativePitch', Union[Ratio, 'ETInterval'])
Distance = NewType('Distance', Ratio)
Point = NewType('Point', Tuple[Distance, Distance])
FontSize = NewType('FontSize', Ratio)
Scale = NewType('Scale', Ratio)


TAU = pi * 2
RIGHT_ANGLE = pi / 2
FLOAT_TOLERANCE = .001

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)

DEFAULT_RADIUS = 64
DEFAULT_FONT = "FF DIN"
DEFAULT_FONT_SIZE = 12
DEFAULT_QUANTIZATION = TAU / (12 * 4)


class ETInterval:
    """
    A relative interval expressed as a number of steps in an equal temperament tuning.
    """

    def __init__(self, steps: Union[int, float, Fraction]):
        self._steps = steps

    def __str__(self) -> str:
        return '[%s]' % self._steps

    def __hash__(self) -> int:
        return hash(self._steps)

    def __eq__(self, other: 'RelativePitch'):
        if isinstance(other, ETInterval):
            return self._steps == other._steps
        else:
            return False

    def __ne__(self, other: 'RelativePitch'):
        if isinstance(other, ETInterval):
            return self._steps != other._steps
        else:
            return True

    def __lt__(self, other: 'RelativePitch'):
        if isinstance(other, ETInterval):
            return self._steps < other._steps
        else:
            return True

    def __le__(self, other: 'RelativePitch'):
        if isinstance(other, ETInterval):
            return self._steps <= other._steps
        else:
            return True

    def __gt__(self, other: 'RelativePitch'):
        if isinstance(other, ETInterval):
            return self._steps > other._steps
        else:
            return False

    def __ge__(self, other: 'RelativePitch'):
        if isinstance(other, ETInterval):
            return self._steps >= other._steps
        else:
            return False

    @property
    def steps(self) -> Union[int, float, Fraction]:
        """The number of equal temperament steps."""
        return self._steps

    def to_relative_pitch(self, octave=2, steps_per_octave=12) -> float:
        """Convert the interval to a frequency ratio."""
        return octave ** (self._steps / steps_per_octave)


class ToneClockStyle:
    """
    Governs the presentation style of a tone clock. Styles are represented as
    separate objects to make it easy to reuse them on multiple tonal
    structures.
    """

    # TODO: Load a style from a config file.
    # TODO: Add controls for marking colors.

    def __init__(self):
        self._visible_circle = True  # type: bool
        self._octave = 2  # type: RelativePitch
        self._hours = 12  # type: Count
        self._radius = DEFAULT_RADIUS  # type: Distance
        self._font_family = DEFAULT_FONT  # type: str
        self._font_size = DEFAULT_FONT_SIZE  # type: FontSize
        self._quantization = DEFAULT_QUANTIZATION  # type: Angle
        self._quantize_labels = True  # type: bool
        self._quantize_non_labels = True  # type: bool

    def copy(self) -> 'ToneClockStyle':
        """Make a (deep) copy of the style."""
        result = ToneClockStyle()
        result._visible_circle = self._visible_circle
        result._octave = self._octave
        result._hours = self._hours
        result._radius = self._radius
        result._font_family = self._font_family
        result._font_size = self._font_size
        result._quantization = self._quantization
        result._quantize_labels = self._quantize_labels
        result._quantize_non_labels = self._quantize_non_labels
        return result

    @property
    def visible_circle(self) -> bool:
        """Whether a circle is drawn. Default is True."""
        return self._visible_circle

    @visible_circle.setter
    def visible_circle(self, value: bool) -> None:
        """Whether a circle is drawn. Default is True."""
        if value not in (0, 1):  # This will match 0, 1, False, and True.
            raise TypeError(value)
        self._visible_circle = bool(value)

    @property
    def octave(self) -> RelativePitch:
        """The octave size. Default is 2."""
        return self._octave

    @octave.setter
    def octave(self, value: Ratio) -> None:
        """The octave size. Default is 2."""
        if not isinstance(value, (int, float, Fraction)):
            raise TypeError(value)
        if value <= 0:
            raise ValueError(value)
        self._octave = value

    @property
    def hours(self) -> Count:
        """The number of hours the clock is divided into. Default is 12. Set to 0 for no hour marks."""
        return self._hours

    @hours.setter
    def hours(self, value: Count) -> None:
        """The number of hours the clock is divided into. Default is 12. Set to 0 for no hour marks."""
        if not isinstance(value, int):
            raise TypeError(value)
        if value < 0:
            raise ValueError(value)
        self._hours = value

    @property
    def radius(self) -> Distance:
        """Radius of the circle. Default is 256."""
        return self._radius

    @radius.setter
    def radius(self, value: Distance) -> None:
        """Radius of the circle. Default is 256."""
        if not isinstance(value, (int, float, Fraction)):
            raise TypeError(value)
        if value <= 0:
            raise ValueError(value)
        self._radius = value

    @property
    def font_family(self) -> str:
        """The name of the font family used for generating labels."""
        return self._font_family

    @font_family.setter
    def font_family(self, value: str) -> None:
        """The name of the font family used for generating labels."""
        if not isinstance(value, str):
            raise TypeError(value)
        if not value:
            raise ValueError(value)
        self._font_family = value

    @property
    def font_size(self) -> FontSize:
        """The size of the font used for generating labels. Note that the font size also controls the sizes of the
        other pitch markings."""
        return self._font_size

    @font_size.setter
    def font_size(self, value: FontSize) -> None:
        """The size of the font used for generating labels. Note that the font size also controls the sizes of the
        other pitch markings."""
        if not isinstance(value, (int, float, Fraction)):
            raise TypeError(value)
        if value <= 0:
            raise ValueError(value)
        self._font_size = float(value)

    @property
    def quantization(self) -> Angle:
        """The size of the bins used for pitch quantization. Set to zero for no quantization."""
        return self._quantization

    @quantization.setter
    def quantization(self, value: Optional[Angle]) -> None:
        """The size of the bins used for pitch quantization. Set to zero for no quantization."""
        if not isinstance(value, (int, float, Fraction)):
            raise TypeError(value)
        if value < 0:
            raise ValueError(value)
        self._quantization = value

    @property
    def quantize_labels(self) -> bool:
        """Whether to apply quantization to labels."""
        return self._quantize_labels

    @quantize_labels.setter
    def quantize_labels(self, value: bool) -> None:
        """Whether to apply quantization to labels."""
        if value not in (0, 1):  # This will match 0, 1, False, and True.
            raise TypeError(value)
        self._quantize_labels = bool(value)

    @property
    def quantize_non_labels(self) -> bool:
        """Whether to apply quantization to non-label marks."""
        return self._quantize_non_labels

    @quantize_non_labels.setter
    def quantize_non_labels(self, value: bool) -> None:
        """Whether to apply quantization to non-label marks."""
        if value not in (0, 1):  # This will match 0, 1, False, and True.
            raise TypeError(value)
        self._quantize_non_labels = bool(value)

    @property
    def marking_scale(self) -> Scale:
        """The (relative) scale for the pitch markings, determined by the font size."""
        return self._font_size / DEFAULT_FONT_SIZE

    @property
    def center(self) -> Point:
        """The center of the circle within the containing image."""
        return self._radius * 2, self._radius * 2

    @property
    def dimensions(self) -> Point:
        """The expected dimensions of the containing image."""
        return int(ceil(self._radius * 4)), int(ceil(self._radius * 4))

    def dot(self, pitch: RelativePitch, filled: bool = True) -> 'PitchDot':
        """Return a properly initialized PitchDot instance."""
        return PitchDot(self, pitch, filled, quantize=self._quantize_non_labels)

    def angle(self, pitch: RelativePitch) -> 'PitchAngle':
        """Return a properly initialized PitchAngle instance."""
        return PitchAngle(self, pitch, quantize=self._quantize_non_labels)

    def line(self, pitch: RelativePitch) -> 'PitchLine':
        """Return a properly initialized PitchLine instance."""
        return PitchLine(self, pitch, quantize=self._quantize_non_labels)

    def label(self, pitch: RelativePitch, label: str) -> 'PitchLabel':
        """Return a properly initialized PitchLabel instance."""
        return PitchLabel(self, pitch, label, quantize=self._quantize_labels)

    def quantize(self, rotation: Angle) -> Angle:
        """Quantize an angle according to the style's quantization settings."""
        if not self._quantization:
            return rotation
        full = self._quantization
        half = full / 2
        return (((rotation + half) // full) * full) % TAU


class PitchMark(object):
    """Abstract base class for pitch markings (dots, angles, and labels)."""

    def __init__(self, style: ToneClockStyle, pitch: RelativePitch, quantize: bool):
        self._style = style
        self._pitch = pitch

        rotation = self.get_mark_rotation(quantized=False)
        if quantize:
            rotation = style.quantize(rotation)
        self._quantized_pitch = style.octave ** ((rotation + RIGHT_ANGLE) / TAU)

    @property
    def pitch(self) -> RelativePitch:
        """The pitch this mark is associated with."""
        return self._pitch

    @property
    def quantized_pitch(self) -> float:
        """The pitch after quantization settings have been applied."""
        return self._quantized_pitch

    def get_mark_rotation(self, quantized: bool = True) -> Angle:
        """Calculate the rotation of the mark from the pitch and style settings."""
        # The logarithm of the pitch, with the octave as the base, modulo 1, times 2 pi, minus pi/2.
        if quantized:
            pitch = self._quantized_pitch
        else:
            pitch = self._pitch
        if isinstance(pitch, ETInterval):
            pitch = pitch.to_relative_pitch(self._style.octave, self._style.hours)
        return (log(pitch, self._style.octave) % 1) * TAU - RIGHT_ANGLE

    def get_mark_point(self, elevation: Distance = 0.0, rush: Distance = 0.0, quantized: bool = True) -> Point:
        """Calculate the location of the mark from the pitch and style settings."""
        # The elevation is the additional distance from the center after the radius of the circle is applied.
        # The rush is the angle (in radians) ahead or behind the pitch.
        rotation = self.get_mark_rotation(quantized=quantized)
        radius = self._style.radius + elevation
        x, y = self._style.center
        x += cos(rotation) * radius + cos(rotation + RIGHT_ANGLE) * rush
        y += sin(rotation) * radius + sin(rotation + RIGHT_ANGLE) * rush
        return x, y

    def draw(self, surface: gizeh.Surface) -> None:
        """Draw the mark on the surface."""
        raise NotImplementedError()


class PitchDot(PitchMark):
    """Represents a pitch as a dot on the tone clock."""

    def __init__(self, style: ToneClockStyle, pitch: RelativePitch, filled: bool, quantize: bool = True):
        super(PitchDot, self).__init__(style, pitch, quantize)
        self._filled = filled

    @property
    def filled(self) -> bool:
        """Whether the dot is filled or empty."""
        return self._filled

    def draw(self, surface: gizeh.Surface) -> None:
        """Draw the pitch's representative dot."""
        scale = self._style.marking_scale
        if self._filled:
            gizeh.circle(r=5 * scale, xy=self.get_mark_point(), fill=BLACK).draw(surface)
        else:
            gizeh.circle(r=7 * scale, xy=self.get_mark_point(), stroke=BLACK, stroke_width=scale).draw(surface)


class PitchAngle(PitchMark):
    """Represents a pitch as an angle marking on the tone clock."""

    def __init__(self, style: ToneClockStyle, pitch: RelativePitch, quantize: bool = True):
        super(PitchAngle, self).__init__(style, pitch, quantize)

    def draw(self, surface: gizeh.Surface) -> None:
        """Draw the pitch's representative angle marking."""
        scale = self._style.marking_scale
        left = self.get_mark_point(elevation=10 * scale, rush=-5 * scale)
        center = self.get_mark_point(elevation=15 * scale)
        right = self.get_mark_point(elevation=10 * scale, rush=5 * scale)
        gizeh.polyline(points=[left, center, right], close_path=False, stroke=BLACK, stroke_width=scale).draw(surface)


class PitchLine(PitchMark):
    """Represents a pitch as a line on the tone clock."""

    def __init__(self, style: ToneClockStyle, pitch: RelativePitch, quantize: bool = True):
        super(PitchLine, self).__init__(style, pitch, quantize)

    def draw(self, surface: gizeh.Surface) -> None:
        """Draw the line on the tone clock."""
        scale = self._style.marking_scale
        lower = self.get_mark_point(elevation=-10 * scale)
        upper = self.get_mark_point(elevation=10 * scale)
        gizeh.polyline(points=[lower, upper], stroke=BLACK, stroke_width=scale).draw(surface)


class PitchLabel(PitchMark):
    """Labels a pitch on the tone clock."""

    def __init__(self, style: ToneClockStyle, pitch: RelativePitch, label: str, quantize: bool = False):
        super(PitchLabel, self).__init__(style, pitch, quantize)
        self._label = str(label)

    def __add__(self, other: 'PitchLabel') -> 'PitchLabel':
        if not isinstance(other, PitchLabel) or self._style != other._style:
            return NotImplemented
        distance = abs(self.get_mark_rotation() - other.get_mark_rotation())
        if FLOAT_TOLERANCE <= distance < TAU - FLOAT_TOLERANCE:
            print(self.get_mark_rotation(), other.get_mark_rotation(), distance, FLOAT_TOLERANCE)
            return NotImplemented
        return PitchLabel(self._style, self._pitch, self._label + ', ' + other._label)

    def draw(self, surface: gizeh.Surface) -> None:
        """Draw the pitch's label on the tone clock."""
        scale = self._style.marking_scale
        rotation = self.get_mark_rotation() % TAU

        # TODO: Rotation of labels appears to be broken. Revisit this and add a style flag to turn rotation on/off,
        #       with off being the default.
        # label_rotation = rotation % pi

        if abs(rotation - (pi + RIGHT_ANGLE)) < FLOAT_TOLERANCE:  # Top center (12 o'clock)
            v_align = "top"
            h_align = "center"
        elif abs(rotation - RIGHT_ANGLE) < FLOAT_TOLERANCE:  # Bottom center (6 o'clock)
            v_align = "bottom"
            h_align = "center"
        elif rotation < FLOAT_TOLERANCE or TAU - rotation < FLOAT_TOLERANCE:  # Center right (3 o'clock)
            v_align = "center"
            h_align = "left"
        elif abs(rotation - (TAU - RIGHT_ANGLE)) < FLOAT_TOLERANCE:  # Center left (9 o'clock)
            v_align = "center"
            h_align = "right"
        elif rotation < RIGHT_ANGLE:  # Bottom right quadrant (3 to 6)
            v_align = "bottom"
            h_align = "left"
        elif rotation < pi:  # Bottom left quadrant (6 to 9)
            v_align = "bottom"
            h_align = "right"
        elif rotation < pi + RIGHT_ANGLE:  # Top left quadrant (9 to 12)
            v_align = "top"
            h_align = "right"
        else:  # Top right quadrant (12 to 3)
            v_align = "top"
            h_align = "left"

        xy = self.get_mark_point(elevation=20 * scale)
        gizeh.text(
            self._label,
            self._style.font_family,
            self._style.font_size,
            # angle=label_rotation,
            xy=xy,
            fill=BLACK,
            stroke=BLACK,
            stroke_width=1,
            v_align=v_align,
            h_align=h_align
        ).draw(surface)


class ToneClock:
    """A tone clock object, consisting of a clock circle, plus various pitch markings and labels."""

    # TODO: Individualize controls for each marking. This will be especially important once colors are introduced.

    def __init__(self, filled_dots: Iterable[RelativePitch] = None, empty_dots: Iterable[RelativePitch] = None,
                 angles: Iterable[RelativePitch] = None, labels: Iterable[Tuple[RelativePitch, str]] = None,
                 style: ToneClockStyle = None, additional_marks: Iterable[PitchMark] = None):
        if filled_dots is None:
            filled_dots = set()
        elif not isinstance(filled_dots, set):
            filled_dots = set(filled_dots)

        if empty_dots is None:
            empty_dots = set()
        elif not isinstance(empty_dots, set):
            empty_dots = set(empty_dots)

        if angles is None:
            angles = set()
        elif not isinstance(angles, set):
            angles = set(angles)

        if labels is None:
            labels = {}
        elif not isinstance(labels, dict):
            labels = dict(labels)

        if style is None:
            style = ToneClockStyle()

        if additional_marks is None:
            additional_marks = set()
        elif not isinstance(additional_marks, set):
            additional_marks = set(additional_marks)

        self._filled_dots = filled_dots  # type: Set[RelativePitch]
        self._empty_dots = empty_dots  # type: Set[RelativePitch]
        self._angles = angles  # type: Set[RelativePitch]
        self._labels = labels  # type: Dict[RelativePitch, str]
        self._additional_marks = additional_marks  # type: Set[PitchMark]
        self._style = style  # type: ToneClockStyle

    def copy(self) -> 'ToneClock':
        """Make a (deep) copy of the tone clock."""
        return ToneClock(
            self._filled_dots.copy(),
            self._empty_dots.copy(),
            self._angles.copy(),
            self._labels.copy(),
            self._style.copy(),
            self._additional_marks.copy()
        )

    @property
    def filled_dots(self) -> Set[RelativePitch]:
        """The set of pitches that are marked with filled dots."""
        return self._filled_dots

    @property
    def empty_dots(self) -> Set[RelativePitch]:
        """The set of pitches that are marked with empty dots."""
        return self._empty_dots

    @property
    def angles(self) -> Set[RelativePitch]:
        """The set of pitches that are marked with angles."""
        return self._angles

    @property
    def labels(self) -> Dict[RelativePitch, str]:
        """A mapping from pitches to labels."""
        return self._labels

    @property
    def style(self) -> ToneClockStyle:
        """The style the tone clock is drawn in."""
        return self._style

    @style.setter
    def style(self, value: ToneClockStyle) -> None:
        """The style the tone clock is drawn in."""
        self._style = value

    @property
    def additional_marks(self) -> Set[PitchMark]:
        return self._additional_marks

    def draw(self, surface: gizeh.Surface) -> None:
        """Draw the tone clock according to its style settings."""
        if self._style.visible_circle:
            gizeh.circle(r=self._style.radius, xy=self._style.center, stroke=BLACK, stroke_width=1).draw(surface)
        if self._style.hours:
            for hour in range(self._style.hours):
                pitch = self._style.octave ** (hour / self._style.hours)
                self._style.line(pitch).draw(surface)
        for pitch in self._filled_dots:
            self._style.dot(pitch, filled=True).draw(surface)
        for pitch in self._empty_dots:
            self._style.dot(pitch, filled=False).draw(surface)
        for angle in self._angles:
            self._style.angle(angle).draw(surface)

        labels = {}
        for pitch, text in sorted(self._labels.items()):
            label = self._style.label(pitch, text)
            if label.quantized_pitch in labels:
                labels[label.quantized_pitch] += label
            else:
                labels[label.quantized_pitch] = label
        for label in labels.values():
            label.draw(surface)

        for mark in self._additional_marks:
            mark.draw(surface)

    def save(self, path: str) -> None:
        """Create a surface, draw the clock, and save it to the requested path."""
        surface = gizeh.Surface(*self._style.dimensions, bg_color=WHITE)
        self.draw(surface)
        surface.write_to_png(path)


# TODO: Use this to build command-line, TUI, and GUI interfaces.
def parse_pitch(text: str) -> RelativePitch:
    """Parse a string representation of a relative pitch."""
    original_text = text
    text = text.strip()
    if text.startswith('[') and text.endswith(']'):
        is_et = True
        text = text[1:-1].strip()
    else:
        is_et = False
    for type_ in int, Fraction, float:
        try:
            value = type_(text)
            break
        except ValueError:
            pass
    else:
        raise ValueError(original_text)
    if is_et:
        return ETInterval(value)
    else:
        return value


def test():
    """A simple function for visually testing the library's generated outputs."""

    save_path = './test.png'
    save_path_scaled = './test_scaled.png'

    filled_dots = [
        ETInterval(12), 1,
        9,
        ETInterval(3),
        5,
        Fraction(1, 3),
        ETInterval(6),
        3,
        ETInterval(9), Fraction(5, 3),
        ETInterval(-1), 15,
    ]
    empty_dots = [
        ETInterval(0),
        ETInterval(1),
        ETInterval(2),
        Fraction(3, 5)
    ]
    angles = [1]
    labels = {p: p for p in filled_dots + empty_dots}
    clock = ToneClock(filled_dots, empty_dots, angles, labels)
    clock.save(save_path)

    clock2 = clock.copy()
    clock2.style.radius *= 4
    clock2.style.font_size *= 2
    clock.save(save_path_scaled)

    et_major_scale = [ETInterval(s) for s in [0, 2, 4, 5, 7, 9, 11]]
    ji_major_scale = [Fraction(*pair) for pair in [(1, 1), (9, 8), (5, 4), (4, 3), (3, 2), (5, 3), (15, 8)]]
    filled_dots = et_major_scale
    empty_dots = ji_major_scale
    angles = [et_major_scale[0], ji_major_scale[0]]
    labels = {p: p for p in et_major_scale + ji_major_scale}
    ms_clock = ToneClock(filled_dots, empty_dots, angles, labels)
    ms_clock.style.radius *= 1.5
    ms_clock.style.quantize_non_labels = False
    ms_clock.save('images/major_comparison.png')
