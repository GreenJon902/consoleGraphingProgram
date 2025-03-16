def get_if_in_array(x, y, array):
    """
    If (x, y) is a valid coordinate then return array[x][y], else return True.
    """
    if 0 < x < len(array):
        if 0 < y < len(array[x]):
            return array[x][y]
    return True

class Equation:
    lhs: str
    rhs: str

    def __init__(self, lhs: str, rhs: str):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, x: float, y: float) -> bool:
        """
        So change our equation from the form `f(x,y)=g(x,y)` to `f(g,y)>=g(x,y)`, and return the result of that
        """
        return eval(self.lhs) >= eval(self.rhs)

    def render(self, x1: float, y1: float, x2: float, y2: float, width: int, height: int) -> [bool]:
        """
        Given the window we want to display (x1,y1) to (x2,y2), render a map of floats for each pixel of length width * height.
        This will first render with width + 2, height + 2 to ensure that the edges are drawn correctly.
        """

        # First figure out what is 'above' and 'below' the curve. We render with 1 pixel extra on each edge which is cropped off later
        window_width = x2 - x1
        window_height = y2 - y1
        step_x = window_width / (width - 1)
        step_y = window_height / (height - 1)
        above_below_map = [[self.evaluate(x1 + step_x * (x - 1), y2 - step_y * (y - 1)) for y in range(height + 2)] for x in range(width + 2)]

        # Now where 'above' switches to 'below' is where we should draw the line. If we have [False, True, True], we will get [False, True, False]
        result = [[
            (above_below_map[x][y] and not (  # If we are true and any adjacent is not true
                get_if_in_array(x - 1, y, above_below_map) and
                get_if_in_array(x, y - 1, above_below_map) and
                get_if_in_array(x, y + 1, above_below_map) and
                get_if_in_array(x + 1, y, above_below_map)
            )) for y in range(height + 2)] for x in range(width + 2)]  # Still use extra padding

        # Crop off the padding on the edges we added and return
        return [
            list(result[x + 1][1:height+1]) for x in range(width)
        ]


def draw_equations(equations: list[Equation], x1: float, y1: float, x2: float, y2: float, width: int, height: int) -> str:
    """
    Render multiple equations and convert to a string.
    The result does not include newlines as those are implied by the size.
    :param x1: The left coordinate in the graph to draw.
    :param y1: The top coordinate in the graph to draw.
    :param x2: The right coordinate in the graph to draw.
    :param y2: The bottom coordinate in the graph to draw.
    :param width: The width of the string to draw.
    :param height: The height of the string to draw.
    """

    rendered = [e.render(x1, y1, x2, y2, width, height) for e in equations]
    result = ""
    for y in range(height):
        for x in range(width):
            result += "█" if any(map(lambda b: b[x][y], rendered)) else " "
    return result