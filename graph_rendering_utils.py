import typing

from window import Window, BLACK, WHITE


def evaluate(equation: tuple[str, str], x: float, y: float) -> bool:
    """
    Evaluate if lhs>=rhs at a given (x,y)
    """
    try:
        return eval(equation[0]) >= eval(equation[1])
    except:
        return False  # TODO: Do this better

def get_if_in_array(x, y, array):
    """
    If (x, y) is a valid coordinate then return array[x][y], else return True.
    """
    if 0 < x < len(array):
        if 0 < y < len(array[x]):
            return array[x][y]
    return True

def render_equation(equation: tuple[str, str], view_left: float, view_right: float, view_top: float, view_bottom: float, canvas_width: int, canvas_height: int):
    """
    Render the given equation to a string of the dimensions (canvas_width,canvas_height), with lines separated by newlines.
    An empty space will be returned as " ".
    The given bounding box will be rendered.

    This assumes that positive x is left, and positive y is up.

    The returned array will be array[y][x]
    """
    # This will first render with width + 2, height + 2 to ensure that the edges are drawn correctly.


    # First figure out what is 'above' and 'below' the curve. We render with 1 pixel extra on each edge which is cropped off later
    view_width = view_right - view_left
    view_height = view_top - view_bottom
    step_x = view_width / (canvas_width - 1)
    step_y = view_height / (canvas_height - 1)
    above_below_map = [[evaluate(equation, view_left + step_x * (x - 1), view_top - step_y * (y - 1)) for y in range(canvas_width + 2)] for x in
                       range(canvas_width + 2)]

    # Now where 'above' switches to 'below' is where we should draw the line. If we have [False, True, True], we will get [False, True, False]
    result = [[
        (above_below_map[x][y] and not (  # If we are true and any adjacent is not true
                get_if_in_array(x - 1, y, above_below_map) and
                get_if_in_array(x, y - 1, above_below_map) and
                get_if_in_array(x, y + 1, above_below_map) and
                get_if_in_array(x + 1, y, above_below_map)
        )) for x in range(canvas_width + 2)] for y in range(canvas_height + 2)]  # Still use extra padding

    # Crop off the padding on the edges we added and return
    return [
        list(("#" if char else " ") for char in result[y + 1][1:canvas_width + 1]) for y in range(canvas_height)
    ]

def render_equations(equations: list[tuple[str, str]], window: "Window", view_left: float, view_right: float, view_top: float, view_bottom: float, canvas_x: int, canvas_y: int, canvas_width: int, canvas_height: int):
    """
    View parameters are floats, they are the bounding box of the graph world we want to see.
    Canvas parameters are how it should be drawn onto the window.

    This will render all the equations to the given window.
    """

    window.draw_rectangle(canvas_x, canvas_y, canvas_width, canvas_height, BLACK)  # Reset canvas cause we will draw transparent images on top of each other.
    for equation in equations:
        result = render_equation(equation, view_left, view_right, view_top, view_bottom, canvas_width, canvas_height)
        window.overlay_text(canvas_x, canvas_y, result, WHITE, BLACK)  # Overlay so we can easily draw multiple graphs and color each separately
