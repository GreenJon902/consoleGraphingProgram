import curses

from graph_rendering_utils import render_equations
from window import Window, Widget, BLACK, WHITE, UP_ARROW, DOWN_ARROW


class TopBar(Widget):
    """
    Draws "consoleGraphingProgram.py" in the center in black on a white background that stretches the size of the window.
    """

    def draw(self, window: "Window"):
        window.draw_centered_text(0, 0, window.get_size()[0], 1, "consoleGraphingProgram.py", BLACK, WHITE)

    def handle_key(self, key_code: int):
        pass

    def focus_name(self) -> str:
        return ""

    def get_current_action_string(self) -> str:
        return ""

    def get_control_descriptions(self) -> dict[str, str]:
        return {}


class BottomBar(Widget):
    """
    Lists the focusable widgets, and which one is currently focussed. It also displays the controls.
    """

    def draw(self, window: "Window"):
        y = window.get_size()[1] - 1

        # Draw the background black to draw the list of focus options on
        window.draw_rectangle(0, y, window.get_size()[0] - 1, 1, BLACK)  # -1 from width so we don't draw the last character.

        # Draw the widgets
        x = 0
        focussed_widget = None
        for widget in window.get_widgets():
            focussed = window.query_focussed(widget)
            if focussed:
                focussed_widget = widget
            fg = BLACK if focussed else WHITE
            bg = WHITE if focussed else BLACK
            window.draw_text(x, y, widget.focus_name(), fg, bg)
            x += len(widget.focus_name()) + 1

        # Draw the background white to draw the other information on
        x = EQUATION_EDITOR_WIDTH
        window.draw_rectangle(x, y, window.get_size()[0] - 1 - x, 1, WHITE)  # -1 from width so we don't draw the last character.
        current_action = focussed_widget.get_current_action_string() + ":"
        controls = focussed_widget.get_control_descriptions()
        # Add global controls
        controls["(Tab)"] = "Switch Mode"
        controls["q"] = "Quit"

        x+= 1  # Padding
        window.draw_text(x, y, current_action, BLACK, WHITE)
        x += len(current_action) + 1
        for key, description in controls.items():
            window.draw_text(x, y, key, WHITE, BLACK)
            x += len(key) + 1
            window.draw_text(x, y, description + ", ", BLACK, WHITE)
            x += len(description) + 2

    def handle_key(self, key_code: int):
        pass

    def focus_name(self) -> str:
        return ""

    def get_current_action_string(self) -> str:
        return ""

    def get_control_descriptions(self) -> dict[str, str]:
        return {}

EQUATION_EDITOR_WIDTH = 40

class EquationEditor(Widget):
    """
    A widget to allow for the displaying and editing of equations.
    This takes a reference to a list of equations to allow for sharing it between this and the GraphViewer.
    """

    _equations: list[tuple[str, str]]
    """
    A list of all the equations, storing (lhs, rhs).
    """
    _current_selected: int
    """ 
    The index of the item that is currently being hovered over or being edited.
    """
    _currently_editing: int | None
    """
    The integer of the index of the cursor. Or None if we are not currently editing.
    """

    def __init__(self, equations_list):
        self._equations = equations_list
        self._current_selected = 0
        self._currently_editing = None

    def draw(self, window: "Window"):
        # Draw the background white to draw the other information on
        window.draw_rectangle(0, 1, EQUATION_EDITOR_WIDTH, window.get_size()[1] - 2, WHITE)  # -1 from width so we don't draw the last character.

        # Write equations
        for n, (lhs, rhs) in enumerate(self._equations):
            prefix = str(n + 1) + "."
            window.draw_text(0, n + 1, prefix, BLACK, WHITE)

            equation = lhs + "=" + rhs
            fg = WHITE if self._current_selected == n and window.query_focussed(self) else BLACK
            bg = BLACK if self._current_selected == n and window.query_focussed(self) else WHITE
            window.draw_centered_text(len(prefix), n + 1, EQUATION_EDITOR_WIDTH - len(prefix), 1, equation, fg, bg)


    def handle_key(self, key_code: int):
        if self._currently_editing is None:
            if key_code == UP_ARROW:
                self._current_selected = (self._current_selected - 1) % len(self._equations)
            elif key_code == DOWN_ARROW:
                self._current_selected = (self._current_selected + 1) % len(self._equations)
            elif key_code == ord("+"):
                self._equations.insert(self._current_selected + 1, ("", ""))
            elif key_code == ord("-"):
                self._equations.pop(self._current_selected)
                self._current_selected = self._current_selected % len(self._equations)
            elif key_code == ord("\n"):
                self._currently_editing = 0
        else:
            if key_code == ord("\n"):
                self._currently_editing = None  # Finish editing
            else:
                self._equations[self._current_selected] = (
                    self._equations[self._current_selected][0] + chr(key_code),
                    self._equations[self._current_selected][1]
                )

    def focus_name(self) -> str:
        return "Edit"

    def get_current_action_string(self) -> str:
        return "You are editing an equation" if self._currently_editing is not None else "You are selecting an equation"

    def get_control_descriptions(self) -> dict[str, str]:
        if self._currently_editing is not None:
            return {"↵": "Stop Editing Equation"}
        else:
            return {"⌃⌄": "Select Equation", "↵": "Edit Equation", "+/-": "Add/Remove Equation"}


class GraphViewer(Widget):
    """
    A widget that draws the equations onto a graph, and allows for panning and zooming.
    This takes a reference to a list of equations to allow for sharing it between this and the EquationEditor.
    # TODO: Zooming
    """

    _equations: list[tuple[str, str]]
    """
    A list of all the equations, storing (lhs, rhs).
    """

    def __init__(self, equations_list):
        self._equations = equations_list

    def draw(self, window: "Window"):
        render_equations(self._equations, window, -2, 2, 2, -2, EQUATION_EDITOR_WIDTH, 1, window.get_size()[0] - EQUATION_EDITOR_WIDTH, window.get_size()[1] - 2)

    def handle_key(self, key_code: int):
        pass

    def focus_name(self) -> str:
        return "Pan"

    def get_current_action_string(self) -> str:
        return "You are panning the graph"

    def get_control_descriptions(self) -> dict[str, str]:
        return {"<⌃⌄>": "Pan the graph"}

if __name__ == "__main__":
    equations = [("x - y","0")]#, ("x**2+y**2", "1")]
    window = Window([EquationEditor(equations), TopBar(), BottomBar(), GraphViewer(equations)])
    window.mainloop()
