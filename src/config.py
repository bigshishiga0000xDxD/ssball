from kivy.core.window import Window

window_width = Window.size[0]
window_height = Window.size[1]

nodesize_coef = 1.5
ballsize_coef = 1
net_width_coef = 1

nodesize = window_width * window_height / 19200 * nodesize_coef
ballsize = window_width * window_height / 19200 * ballsize_coef
net_width = window_width / 400 * net_width_coef

fps = 30
quantum = 1 / fps

g = window_height / 10
spring_ability = 1

node_weight = 1
ball_weight = 1

goals_count = 1

font_size = window_width * window_height / 16000

restart_waiting = 2
