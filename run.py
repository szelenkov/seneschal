#!python -u
# -*- coding: utf-8 -*-
# pylama: ignore:E265
"""
[summary].

.
"""
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class LoginScreen(GridLayout):
    """Login screen."""

    def __init__(self, **kwargs):
        """Initialize."""
        super(LoginScreen, self).__init__(**kwargs)

        self.cols = 2
        self.rows = 2
        self.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)


class MyApp(App):
    """Awesome app class."""

    def build(self):
        self.title = 'Awesome app!!!'
        # return LoginScreen()
        return Button(text='ggg')


if __name__ == '__main__':
    MyApp().run()
