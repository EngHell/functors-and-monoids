from functools import reduce

def add5(a):
    return a + 5


def pow2(a):
    return a * a


# a monoid is associative
# closed
# and has a neutral element.
# for example function composition
def compose(f1, f2):
    return lambda arg: f1(f2(arg))


#another monoid
def concat(a, b):
    return a + b


def main():
    print('hi')
    pow2_after_adding5 = compose(pow2, add5)
    print(pow2_after_adding5(10))

    operands = ['hello', ' ', 'my ', 'bitch', '.']
    # we use a monoid with reduce so we can use
    # a function that takes two arguments and
    # make it take any number of arguments
    print(reduce(concat, operands))

    # then we can use chunks o:
    # chunks should improve our ability to do parallel jobs.
    big_list = [1,2,3,4,5,6,7,8,9,10]
    result1 = reduce(concat, big_list[:5])
    result2 = reduce(concat, big_list[5:])
    print(concat(result1, result2))



if __name__ == '__main__':
    main()
