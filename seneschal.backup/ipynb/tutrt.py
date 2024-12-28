from turtle import Turtle, colormode, Screen
import random


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


def draw_spirograph(size_of_gap):
    for _ in range(int(360/size_of_gap)):
        T.color(random_color())
        T.circle(140)
        T.setheading(T.heading() + size_of_gap)


if __name__ == '__main__':
    colormode(255)
    T = Turtle()
    T.speed(1)

    draw_spirograph(1)
    S = Screen()
    S.exitonclick()
