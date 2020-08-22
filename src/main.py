from kivy.app import App

from game import GameLayout

class MainApp(App):
    def build(self):
        self.root = GameLayout(self)

        return self.root

    def on_stop(self):
        if self.root.running:
            self.root.running = False
            self.root.game_thread.join()


if __name__ == '__main__':
    MainApp().run()

