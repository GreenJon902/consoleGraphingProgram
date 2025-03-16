import curses
import typing

BLACK = curses.COLOR_BLACK
WHITE = curses.COLOR_WHITE

DOWN_ARROW = curses.KEY_DOWN
UP_ARROW = curses.KEY_UP

class Widget:
    """
    An object that can be drawn on the screen and may take events.
    """

    def focus_name(self) -> str:
        """
        The name of this widget to display in the focus switcher.
        :return:
        """
        raise NotImplemented()

    def draw(self, window: "Window"):
        """
        Draw this widget to the given window
        """
        raise NotImplemented()

    def handle_key(self, key_code: int):
        """
        Handle the given key.
        """
        raise NotImplemented()

    def get_current_action_string(self) -> str:
        """
        Returns a string describing what the user would currently be doing if this widget was focussed.
        """
        raise NotImplemented()

    def get_control_descriptions(self) -> dict[str, str]:
        """
        Returns a list of keys and the actions they would do if this widget was focussed.
        """
        raise NotImplemented()


class Window:
    """
    This is the handler for events and drawing to the console.
    This wraps curses up nicely, and provides utilities for drawing.

    This stores a list of widgets. Each frame,
        1. The key event is checked.
            a. If q is pressed then the application exits.
            b. If the focus is changed then the respective widget's focus and un-focus methods will be called.
        2. Each widget's call function will be executed with this Window object as its parameter.
            a. These can then call the window's various drawing functions to complete their task.

    The drawing functions of this window should be safe (checking window edges) as well as working in (columns, rows).
    """

    _widgets: tuple[Widget]
    _current_focus: int
    """
    The index of the currently focussed widget.
    """
    _size: tuple[int, int]
    """
    The size of the window as (rows, columns).
    """
    _stdscr: any  # I don't have a type, this is initialised when _mainloop is called.
    _color_pairs: dict[tuple[int, int], int]
    """
    Stores already allocated color_pairs.
    The key is the (fg, bg), the value is the attribute id.
    Values be unique, and consecutive when ordered, counting from one.
    """


    def __init__(self, widgets: tuple[Widget]):
        """
        Creates a new window with the given widgets.
        The first widget in the given collection will start focussed.
        """
        self._widgets = tuple(widgets)
        self._current_focus = 0
        self._stdscr = None  # Initialised later
        self._color_pairs = {}


    def _mainloop(self, stdscr):
        """
        The actual mainloop of this application, this should be wrapped curses.
        """

        if typing.TYPE_CHECKING:  # So the type hinting is correct
            # noinspection PyArgumentList
            stdscr = curses.newwin()

        stdscr.clear()
        stdscr.refresh()
        curses.curs_set(0)  # Disable cursor

        self._stdscr = stdscr

        last_key = 0  # The last key that was pressed

        while True:
            stdscr.clear()
            self._size = stdscr.getmaxyx()
            stdscr.attron

            # Handle events
            if last_key == ord("q"):
                break
            elif last_key == ord("\t"):
                self._current_focus = (self._current_focus + 1) % len(self._widgets)
            else:
                self._widgets[self._current_focus].handle_key(last_key)

            # Draw widgets
            for widget in self._widgets:
                widget.draw(self)

            # Write the current key code to the bottom right
            self._set_color(BLACK, WHITE)
            self._stdscr.addstr(self._size[0] - 1, self._size[1] - len(str(last_key)) - 2, str(last_key))


            # Update the screen
            stdscr.refresh()
            last_key = stdscr.getch()


    def mainloop(self):
        """
        Hand control of the console and events and drawing to the window and then enter the main event loop.
        """
        curses.wrapper(self._mainloop)

    def get_widgets(self) -> tuple[Widget]:
        return self._widgets

    def query_focussed(self, widget: Widget) -> bool:
        """
        True if the given widget is currently in focus, otherwise false.
        """
        return self._widgets[self._current_focus] == widget

    def get_size(self) -> tuple[int, int]:
        """
        Returns the size of the window in (columns, rows).
        """
        return self._size[1], self._size[0]

    def draw_centered_text(self, x, y, width, height, text, foreground_color, background_color):
        """
        Draws the given text in the center of the given area, with the given colors.
        The given text must only have one line.
        If this has to choose, it will prefer the higher and lefter coordinate to place text (e.g. putting a single char in a two char space).
        """
        assert "\n" not in text, "Text may not contain newlines"
        assert len(text) <= width, "Text is wider than given width"
        assert 0 <= x, "Area overlaps left border"
        assert x + width - 1 < self._size[1], "Area overlaps right border"
        assert 0 <= y, "Area overlaps top border"
        assert y + height - 1 < self._size[0], "Area overlaps bottom border"

        self._set_color(foreground_color, background_color)  # Set the color we want

        self.draw_rectangle(x, y, width, height // 2)  # Draw the bar before the line with text on it
        self._stdscr.addstr(y + height // 2, x, " " * width)  # First draw bar
        self._stdscr.addstr(y + height // 2, x + (width - len(text)) // 2, text)  # Then overlay our text
        self.draw_rectangle(x, y + height // 2 + 1, width, height // 2 - 1)  # Draw the bar after the line with text on it

    def draw_rectangle(self, x, y, width, height, color=None):
        """
        Draws a rectangle of spaces of the given size with the color as the background color.
        If a color is given then it is used for the background color, otherwise the current color is used.
        """
        assert 0 <= x, "Area overlaps left border"
        assert x + width - 1 < self._size[1], "Area overlaps right border"
        assert 0 <= y, "Area overlaps top border"
        assert y + height - 1 < self._size[0], "Area overlaps bottom border"

        if color is not None:
            self._set_color(WHITE, color)

        for row in range(y, y + height):  # Draw the bar before the line with text on it
            self._stdscr.addstr(row, x, " " * width)

    def _set_color(self, foreground_color, background_color):
        """
        Sets the current color pair to the given colors.
        This will reuse color pairs if it can, otherwise it will create a new pair.
        """
        color = (foreground_color, background_color)
        if color not in self._color_pairs:
            curses.init_pair(len(self._color_pairs) + 1, foreground_color, background_color)
            self._color_pairs[color] = len(self._color_pairs) + 1
        self._stdscr.attron(curses.color_pair(self._color_pairs[color]))

    def draw_text(self, x, y, text, foreground_color, background_color):
        """
        Draws the given text at the given location using the given colors.
        The given text must only have one line.
        """
        assert "\n" not in text, "Text may not contain newlines"
        assert 0 <= x, "Area overlaps left border"
        assert x + len(text) - 1 < self._size[1], f"Area overlaps right border {x, len(text)}"
        assert 0 <= y, "Area overlaps top border"

        self._set_color(foreground_color, background_color)
        self._stdscr.addstr(y, x, text)