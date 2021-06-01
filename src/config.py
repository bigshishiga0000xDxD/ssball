from kivy.core.window import Window

window_width = Window.size[0]
window_height = Window.size[1]

def reload():
    global window_width
    global window_height

    window_width = Window.size[0]
    window_height = Window.size[1]

    print(window_width, window_height)

nodesize_coef = 1
ballsize_coef = 1
net_width_coef = 1
g_coeff = 1

nodesize = window_width * window_height / 19200 * nodesize_coef
ballsize = window_width * window_height / 19200 * ballsize_coef
net_width = window_width / 400 * net_width_coef

fps = 45
quantum = 1 / fps

g = 2 * window_height / 9 * g_coeff

spring_ability = 1

goals_count = 2

font_size = window_width * window_height / 16000

restart_waiting = 2
