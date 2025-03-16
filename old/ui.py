from equation import Equation


class Panel:
    """
    The base class for widgets, all sub-panels should inherit from this.
    """

    def draw(self, width: int, height: int) -> str:
        """
        Draws the contents of this panel as a string.
        The length of this string should be width * height.
        This should not have newlines as those are implied by the size.
        The given sizes are in number of characters.
        """
        raise NotImplemented


class BoxLayoutPanel(Panel):
    """
    A panel that draws other panels.
    """

    children = [(Panel, int)]  # (Panel, relative width)
    horizontal: bool  # True for draw horizontally, else vertically

    def __init__(self, children, horizontal):
        self.children = children
        self.horizontal = horizontal

    def draw(self, width: int, height: int) -> str:
        # Render all panels at their allocated sizes
        rendered = []
        total_rsize = sum([x[1] for x in self.children])
        for panel, rsize in self.children:
            if self.horizontal:
                panel_width = round(width * rsize / total_rsize)
                panel_height = height
            else:
                panel_width = width
                panel_height = round(height * rsize / total_rsize)

            rendered.append(panel.draw(panel_width, panel_height))

        # Now add the panels together
        if self.horizontal:
            result = ""
            for y in range(height):
                for render in rendered:
                    panel_width = int(len(render) / height)
                    result += render[y * panel_width:(y+1) * panel_width]
        else:
            result = ""
            for render in rendered:
                result += render

        return result

    def update_children(self, children):
        self.children = children


class GraphPanel(Panel):
    """
    A panel that draws a set of equations.
    """

    x1: float  # The left coordinate in the graph to draw.
    y1: float  # The top coordinate in the graph to draw.
    x2: float  # The right coordinate in the graph to draw.
    y2: float  # The bottom coordinate in the graph to draw.
    equations: [Equation]

    def __init__(self, x1, y1, x2, y2, equations):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.equations = equations

    def update_positions(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, width: int, height: int) -> str:
        rendered = [e.render(self.x1, self.y1, self.x2, self.y2, width, height) for e in self.equations]
        result = ""
        for y in range(height):
            for x in range(width):
                result += "█" if any(map(lambda b: b[x][y], rendered)) else " "
        return result


class LabelPanel(Panel):
    """
    A panel that draws a piece of text.
    """

    text: str

    def __init__(self, text):
        self.text = text

    def draw(self, width: int, height: int) -> str:
        start_x = round(width / 2 - len(self.text) / 2)
        start_y = round(height / 2) - 1
        empty_line = "█" * width
        text_line = ("█" * start_x) + self.text + ("█" * (width - start_x - len(self.text)))
        return (empty_line * (start_y)) + text_line + (empty_line * (height - start_y - 1))


class EquationEditorPanel(Panel):
    """
    A panel that stores multiple equations and allows the user to edit them.
    """
    box_panel: BoxLayoutPanel
    equations: [Equation]

    def __init__(self, equations):
        self.equations = equations
        self.box_panel = BoxLayoutPanel([(LabelPanel("Text"), 1)], False)

    def draw(self, width: int, height: int) -> str:
        # Ensure box_panel is up to date
        self.box_panel.update_children([(LabelPanel(equation.lhs + "=" + equation.rhs), 1) for equation in self.equations])
        return self.box_panel.draw(width, height)


if __name__ == '__main__':
    label_panel = LabelPanel("Ho")
    graph_panel = GraphPanel(-2, -2, 2, 2, [Equation("x**2 + y**2", "1")])
    box_panel = BoxLayoutPanel([(label_panel, 3), (graph_panel, 7)], True)
    to_draw = box_panel


    width = 10
    height = 10
    drawn = to_draw.draw(width, height)
    print(" " + "".join(map(str, range(width))) + " ")
    for y in range(height):
        print(str(y) + drawn[y * width:(y+1) * width] +  str(y))
    print(" " + "".join(map(str, range(width))) + " ")