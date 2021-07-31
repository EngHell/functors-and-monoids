# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    print_hi('holis')
    print(add(5)(2))
    holis = greet('holis')
    print(holis('perro'))


#this is a called an unit function, takes a single parameter, and its a pure function.
def add(a):
    return lambda b: a + b


#another example of unit curred function.
def greet(greet):
    return lambda name: f'{greet}, {name}'


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
