from pywebio import *

def pywebio_run():
    name = input.input("what's your name")
    output.put_text("hello", name)