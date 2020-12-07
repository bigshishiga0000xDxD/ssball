from random import randint
from enum import Enum
from time import time, sleep
from threading import Thread

from kivy.graphics import Ellipse, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from config import *
from half import Half
from geometry import Vector, distance, inf
import geometry

objects = Enum('objects', 'wall floor node plate')

class Object:
    def __init__(self, kind, point, node_id = None, inside = None):
        self.kind = kind
        self.point = point
        if node_id is not None:
            self.node_id = node_id
            self.inside = inside


class Ball:
    def __init__(self, v, circle, parent):
        self.v = v
        self.circle = circle
        self.parent = parent

    def update(self, t):
        time_left = t
        while time_left > 0:
            self.collisions = []

            # left wall
            self.add_collision(geometry.wall_collision(
                x = 0,
                y1 = 0, y2 = inf,
                ball = self.circle.pos,
                v = self.v * time_left
            ), objects.wall)

            # right wall
            self.add_collision(geometry.wall_collision(
                x = window_width - ballsize,
                y1 = 0, y2 = inf,
                ball = self.circle.pos,
                v = self.v * time_left
            ), objects.wall)

            # floor
            self.add_collision(geometry.floor_collision(
                y = 0,
                x1 = 0, x2 = window_width,
                ball = self.circle.pos,
                v = self.v * time_left
            ), objects.floor)

            # nodes
            for i in range(2):
                self.add_collision(geometry.node_collision(
                    list(self.parent.halves[i].node.pos),
                    list(self.circle.pos),
                    self.v * time_left
                ), objects.node, i)

            # net left wall
            self.add_collision(geometry.wall_collision(
                x = window_width / 2 - ballsize - net_width,
                y1 = 0, y2 = window_height / 2,
                ball = self.circle.pos,
                v = self.v * time_left
            ), objects.wall)

            # net right wall
            self.add_collision(geometry.wall_collision(
                x = window_width / 2 + net_width,
                y1 = 0, y2 = window_height / 2,
                ball = self.circle.pos,
                v = self.v * time_left
            ), objects.wall)

            # net top plate
            self.add_collision(geometry.floor_collision(
                y = window_height / 2,
                x1 = window_width / 2 - ballsize - net_width,
                x2 = window_width / 2 + net_width,
                ball = self.circle.pos,
                v = self.v * time_left
            ), objects.plate)

            if self.collisions == []:
                collides = False
            else:
                closest_collision = None

                for elem in self.collisions:
                    try:
                        if elem.inside:
                            closest_collision = elem
                            collides = True
                            break
                    except AttributeError:
                        continue

                if closest_collision is None:
                    closest_collision = min(
                        self.collisions,
                        key = lambda x : distance(
                            x.point, self.circle.pos
                        )
                    )

                    closest_collision_time = distance(
                        closest_collision.point,
                        self.circle.pos
                    ) / self.v.speed()
                    if closest_collision_time > time_left:
                        collides = False
                    else:
                        collides = True

            if not collides:
                self.circle.pos = [
                    self.circle.pos[0] + self.v.x * time_left,
                    self.circle.pos[1] + self.v.y * time_left
                ]
                self.v.y -= g * t
                time_left = 0
            else:
                stop_needed, restart_needed = \
                    self.handle_collision(closest_collision)

                if stop_needed:
                    return (stop_needed, restart_needed)

                closest_collision_time = distance(
                    closest_collision.point,
                    self.circle.pos
                ) / self.v.speed()

                time_left -= closest_collision_time
                self.v.y -= g * closest_collision_time
        return (False, False)

    def add_collision(self, *args):
        point = args[0]
        kind = args[1]
        if len(args) == 2:
            if point is not None:
                self.collisions.append(Object(
                    kind = kind,
                    point = point
                ))
        else:
            node_id = args[2]
            if point is not None:
                point, inside = point
                self.collisions.append(Object(
                    kind = kind,
                    point = point,
                    node_id = node_id,
                    inside = inside
                ))

    def handle_collision(self, collision):
        self.circle.pos = collision.point

        if collision.kind == objects.wall:
            self.v.x = -self.v.x

        elif collision.kind == objects.floor:
            if self.circle.pos[0] < window_width / 2:
                self.parent.add_goal(0)
            else:
                self.parent.add_goal(1)

            return (True, self.parent.stop())

        elif collision.kind == objects.plate:
            self.v.y = -self.v.y;

        elif collision.kind == objects.node:
            half = self.parent.halves[collision.node_id]
            node_pos = half.node.pos

            speed = self.v.speed()
            self.v = Vector(
                begin = node_pos,
                end = self.circle.pos
            )
            self.v.normalize()
            self.v *= speed
            self.v += half.vector

        self.v *= spring_ability
        return (False, False)


class GameLayout(FloatLayout):
    def __init__(self, parent_app, **kwargs):
        super(GameLayout, self).__init__(**kwargs)

        self.parent_app = parent_app
        self.new_game()

    def define_labels(self):
        self.labels = [
            Label(
                text = str(self.goals[0]),
                pos = (-window_width / 4, window_height / 4),
                font_size = font_size
            ),
            Label(
                text = str(self.goals[1]),
                pos = (window_width / 4, window_height / 4),
                font_size = font_size
            )
        ]

    def define_canvas(self):
        self.canvas.clear()
        self.canvas.add(self.halves[0].node)
        self.canvas.add(self.halves[1].node)
        self.canvas.add(self.net)
        self.canvas.add(self.ball.circle)

    def define_ball(self):
        player = randint(0, 1)
        self.ball = Ball(
            v = Vector(0, 0),
            circle = Ellipse(
                size = [ballsize, ballsize],
                pos = [
                    self.halves[player].node.pos[0],
                    window_height * 2 / 3
                ]
            ),
            parent = self
        )

    def define_halves(self):
        self.halves = [
            Half(
                window_width / 4,
                window_height / 4,
                pos = (0, 0),
                width = window_width / 2 - nodesize - net_width,
                size_hint = (None, 1)
            ),
            Half(
                3 * window_width / 4,
                window_height / 4,
                pos = (window_width / 2 + net_width, 0),
                width = window_width / 2 - nodesize - net_width,
                size_hint = (None, 1)
            ),
        ]

    def define_net(self):
        self.net = Line(
            points = [
                window_width / 2,
                0,
                window_width / 2,
                window_height / 2
            ],
            joint = 'none',
            cap = 'none',
            width = net_width
        )

    def add_goal(self, player):
        self.goals[player] += 1

    def stop(self):
        for i in range(2):
            if self.goals[i] == goals_count:
                self.win(i)
                return False

        self.canvas.remove(self.halves[0].node)
        self.canvas.remove(self.halves[1].node)
        self.canvas.remove(self.ball.circle)

        self.define_labels()
        for i in range(2):
            self.remove_widget(self.halves[i])
            self.add_widget(self.labels[i])
        return True

    def win(self, player):
        self.canvas.clear()
        self.clear_widgets()

        side = 'left' if player == 1 else 'right'
        self.winner = Label(
            text = '{0} player wins!'.format(side),
            pos = (0, window_height / 4),
            font_size = font_size
        )

        def set_color(button):
            button.background_color = [0.1, 0.1, 0.1, 1]

        self.restart_button = Button(
            text = 'restart',
            font_size = font_size,
            on_press = set_color,
            on_release = self.new_game,
            pos_hint = {'x': 0.25, 'y': 0.4},
            size_hint = (0.5, 0.25),
            background_color = [0, 0, 0, 1]
        )

        self.exit_button = Button(
            text = 'exit',
            font_size = font_size,
            on_press = set_color,
            on_release = self.exit,
            pos_hint = {'x': 0.25, 'y': 0.15},
            size_hint = (0.5, 0.25),
            background_color = [0, 0, 0, 1]
        )

        self.add_widget(self.winner)
        self.add_widget(self.restart_button)
        self.add_widget(self.exit_button)

    def update(self):
        cur_time = time()

        stop_needed, restart_needed = \
            self.ball.update(cur_time - self.last_updated)

        if stop_needed:
            return (stop_needed, restart_needed)

        for i in range(2):
            self.halves[i].vector = Vector (
                begin = self.halves[i].node.last_pos,
                end = self.halves[i].node.pos
            )
        self.last_updated = cur_time

        for i in range(2):
            self.halves[i].node.last_pos = self.halves[i].node.pos

        return (False, False)

    def restart(self):
        sleep(restart_waiting)
        self.define_halves()
        for i in range(2):
            self.add_widget(self.halves[i])
            self.remove_widget(self.labels[i])

        self.define_ball()
        self.define_canvas()
        self.start_thread()

    def new_game(self, button = None):
        try:
            self.remove_widget(self.restart_button)
            self.remove_widget(self.exit_button)
            self.remove_widget(self.winner)
        except AttributeError:
            pass
        except Exception as e:
            raise e

        self.define_net()
        self.define_halves()
        self.define_ball()
        self.goals = [0, 0]

        self.add_widget(self.halves[0])
        self.add_widget(self.halves[1])
        self.define_canvas()

        self.start_thread()

    def exit(self, button = None):
        self.parent_app.get_running_app().stop()

    def start_thread(self):
        self.last_updated = time()
        self.running = True
        self.game_thread = Thread(target = self.do_updates)
        self.game_thread.start()

    def do_updates(self):
        restart = False
        while self.running:
            sleep(quantum)

            stop_needed, restart_needed = self.update()
            if stop_needed:
                restart = restart_needed
                break

        if restart:
           self.restart()
