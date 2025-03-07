import curses

from equation import Equation
from ui import GraphPanel, LabelPanel, BoxLayoutPanel, EquationEditorPanel


def mainloop(stdscr):
    equations = [
        Equation("x**2 + y**2", "1"),
        Equation("y", "x**2 - 2 * x + 1"),
        Equation("y", "x**5 - 2*x**3 + 1*x**2 - x - 1")
    ]

    graph_panel = GraphPanel(None, None, None, None, equations)
    title_label = LabelPanel("Console Graphing Program")
    equation_holder = EquationEditorPanel(equations)
    horiz_panel = BoxLayoutPanel([
        (equation_holder, 1),
        (graph_panel, 10)
    ], True)
    root_panel = BoxLayoutPanel([
        (title_label, 1),
        (horiz_panel, 10)
    ], False)


    k = 0  # Key code

    center_x = 0  # Center of the graph
    center_y = 0

    stdscr.clear()
    stdscr.refresh()

    while True:
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
        graph_panel.update_positions(center_x - 2, center_y - 2, center_x + 2, center_y + 2)

        string = root_panel.draw(width, height)
        for y in range(height - 1):
            stdscr.addstr(y, 0, string[y * width:(y+1) * width])


        stdscr.refresh()
        k = stdscr.getch()



if __name__ == '__main__':
    curses.wrapper(mainloop)

