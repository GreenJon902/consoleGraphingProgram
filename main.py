import curses

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
    """

    rendered = [e.render(x1, y1, x2, y2, width, height) for e in equations]
    result = ""
    for y in range(height):
        for x in range(width):
            result += "█" if any(map(lambda b: b[x][y], rendered)) else " "
        result += "\n"
    return result

def mainloop(stdscr):
    k = 0

    center_x = 0
    center_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses


    # Loop where k is the last character pressed
    while True:

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            center_y += 1
        elif k == curses.KEY_UP:
            center_y -= 1
        elif k == curses.KEY_RIGHT:
            center_x -= 1
        elif k == curses.KEY_LEFT:
            center_x += 1
        elif k == ord("q"):
            break


        string = draw_equations([
            Equation("y**2 + x**2", "1"),
            Equation("y", "x**3")
        ], center_x - 2, center_y - 2, center_x + 2, center_y + 2, width - 4, height - 4)
        for n, line in enumerate(string.split("\n")):
            stdscr.addstr(2 + n, 2, line)


        # Refresh the screen
        stdscr.refresh()
        k = stdscr.getch()



if __name__ == '__main__':
    curses.wrapper(mainloop)

