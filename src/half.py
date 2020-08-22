from kivy.uix.widget import Widget
from kivy.graphics import Ellipse

from config import nodesize, ballsize
from geometry import Vector, distance

class Node(Ellipse):
    def __init__(self, **kwargs):
        Ellipse.__init__(
            self,
            size = kwargs['size'],
            pos = kwargs['pos']
        )
        self.last_pos = kwargs['pos']

class Half(Widget):
    def __init__(self, node_x, node_y, **kwargs):
        super(Half, self).__init__(**kwargs)

        self.node = Node(
            size = [nodesize, nodesize],
            pos = [node_x, node_y]
        )

        self.vector = Vector(0, 0)

    def on_touch_down(self, touch):
        if self.parent is None:
            return

        if abs(self.node.pos[0] - touch.pos[0]) <= nodesize \
                and abs(self.node.pos[1] - touch.pos[1]) <= nodesize:
            touch.grab(self)
            return True

    def on_touch_up(self, touch):
        if self.parent is None:
            return

        if touch.grab_current is self:
            touch.ungrab(self)


    def on_touch_move(self, touch):
        if self.parent is None:
            return

        if touch.grab_current is self:
            next_node = [
                touch.pos[0] - nodesize / 2,
                touch.pos[1] - nodesize / 2
            ]

            if next_node[0] <= self.x:
                self.node.pos = [self.x, next_node[1]]
            elif next_node[0] >= self.right:
                self.node.pos = [self.right, next_node[1]]
            else:
                self.node.pos = next_node

            ball = self.parent.ball.circle.pos

            if distance(ball, self.node.pos) <= ballsize + nodesize:
                self.parent.update()
