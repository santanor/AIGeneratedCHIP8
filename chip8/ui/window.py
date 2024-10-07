import imgui

class Window:
    def __init__(self, title):
        self.title = title

    def render(self):
        if imgui.begin(self.title):
            self.draw_contents()
        imgui.end()

    def draw_contents(self):
        raise NotImplementedError("Subclasses must implement draw_contents method")