import functools
import re


# here we go into functors, i guess a class should do it
class NumberBox:
    value = None

    def __init__(self, value):
        self.value = value

    def map(self, fn):
        if not isinstance(self.value, (int, float)):
            return NumberBox(float('NaN'))
        return NumberBox(fn(self.value))


# we can use the functor pattern to typecheck too.
# i plan to use this on a parser later
# just realized i can do this o:
# nvm this makes the values coupled.
def type_box(predicate, default):
    def map_decorator(func):
        @functools.wraps(func)
        def wrapper(value):
            # print('something happens before')
            func.map = lambda fn: type_predicate(fn(value)) if predicate(value) else type_predicate(default)
            func.value = value
            # print('something happens after')
            return func

        return wrapper

    @map_decorator
    def type_predicate():
        pass

    return type_predicate


# i researched and a functor is a callable object
def is_nothing(value):
    return value is None


def is_dict(value):
    return type(value) is dict


def maybe_to_either(maybe):
    return Left('NO VALUE') if maybe.is_nothing() else Right(maybe.flatten())

class Left:
    def __init__(self, value):
        self.value = value

    def map(self, fn):
        return self

    def flatten(self):
        return self.value

    def chain(self, fn):
        return self.map(fn).flatten()

    def catch(self, fn):
        return Right(fn(self.value))


class Right:
    def __init__(self, value):
        self.value = value

    def map(self, fn):
        return Right(fn(self.value))

    def flatten(self):
        return self.value

    def chain(self, fn):
        return self.map(fn).flatten()

    def catch(self, fn):
        return self


class Maybe:
    class Nothing:
        def __init__(self, value, error=None):
            self.value = None
            self.error = error

        def __repr__(self):
            if not is_nothing(self.error):
                return 'Nothing: ' + repr(self.value)

            return 'Nothing: ' + repr(self.error)

        def is_nothing(self):
            return True

        def map(self, fn):
            return self

        def flatten(self):
            return self

        def chain(self, fn):
            return self

        def get_or_else(self, default):
            return default

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'MAYBE ' + repr(self.value)

    def is_nothing(self):
        return is_nothing(self.value)

    def map(self, fn):
        if self.is_nothing():
            return Maybe.Nothing()
        try:
            return Maybe(fn(self.value))
        except Exception as e:
            return Maybe.Nothing(None, e)

    def flatten(self):
        return self.value

    def chain(self, fn):
        return self.map(fn).flatten()

    def get_or_else(self, default):
        return default if is_nothing(self.value) else self.value

def get(key):
    return lambda value: value[key]


def get_street(user):
    return Maybe(user) \
        .map(get('address')) \
        .map(get('street')) \
        .get_or_else('uknown street')


def try_catch(fn):
    def wrap(value):
        try:
            return Right(fn(value))
        except Exception as e:
            return Left(e)

    return wrap


def validate_email(value):
    def wrap(value):
        if not re.search("\S+@\S+\.\S+", value):
            raise ValueError('The given email is invalid.')

        return value

    fn_body = try_catch(wrap)
    return fn_body(value)


def either_to_maybe(either):
    return Maybe(either.catch(lambda e: None).flatten())



# now we test this.
def main():
    a = NumberBox(5).map(lambda v: v * 2).map(lambda v: v + 1).value
    print(a)
    b = NumberBox('hi').map(lambda v: v * 2).value
    print(b)

    number_box = type_box(lambda val: isinstance(val, (int, float)), float('NaN'))
    # c = number_box(1).map(lambda v:v*2).map(lambda v:v+20).map(lambda v:v+1)
    # d = number_box(2)

    a = number_box(5).map(lambda v: v)
    b = number_box(5)

    print(a)
    print(b)

    # identity test
    if a == b:
        print('identity o:')

    # now we test maybe.
    user = {
        'name': 'holmes'
    }

    a = Maybe(user).map(lambda u: u['address'])
    print(a)

    # map has not side ffects.
    a = Maybe(user).map(lambda v: v)
    b = Maybe(user)

    print(a.value == b.value)

    user2 = {
        'name': 'angel',
        'address': {
            'street': 'besto streeto waifu'
        }
    }

    print(get_street(user))
    print(get_street(user2))

    print(validate_email('a@a.com').map(lambda v: 'Email: ' + v).value)
    print(validate_email('a@b').map(lambda v: 'Email: ' + v).value)

    # someone said
    print(Right(5).catch(lambda e: e.__repr__()).value)
    print(Left(Exception('this is an exception')).catch(lambda e: e.__repr__()).value)

    print(validate_email('test1@test.com').map(lambda v: 'E: ' + v).catch(lambda e: e.__repr__()).value)

    print(validate_email('test1@testaaarosacom').map(lambda v: 'E: ' + v).catch(lambda e: e.__repr__()).value)

    # we combine a functor
    def validate_user(user):
        return Maybe(user) \
            .map(get('email')) \
            .map(lambda v: validate_email(v).catch(lambda e: e.__repr__()))

    print(validate_user({'email': 'hi@hi.com'}).value.value)
    print(validate_user({'email': 'foo@foo'}).value.value)
    print(validate_user({}).value)

    # now with flatten
    def validate_user_with_flatten(user):
        return Maybe(user) \
            .map(get('email')) \
            .map(lambda v: validate_email(v).catch(lambda e: e.__repr__())) \
            .flatten() \
            .get_or_else('The user has no mail.')

    # these 3 now trigger an error.
    #print(validate_user_with_flatten({'email':'email@email.com'}))
    #print(validate_user_with_flatten({'email':'notmail'}))
    #print(validate_user_with_flatten({'name':'juan'}))
    

    #now with chain
    def validate_user_chain(user):
        return Maybe(user) \
            .map(get('email')) \
            .chain(lambda v: validate_email(v).catch(lambda e: e.__repr__())) \
            .get_or_else('The User Has No EMAILLLL')

    # these return error now, cause flatten on maybe just returns the value does not wrap
    # it on anything else.
    # print(validate_user_chain({'email': 'email@email.com'}))
    # print(validate_user_chain({'email': 'notmail'}))
    # print(validate_user_chain({'name': 'juan'}))


    print('testing')
    # now maybe to either
    a = Maybe({'name': 'gallo', 'mail': 'test1@exampl.ecom'})\
        .map(get('mail'))\
        .map(validate_email)\
        .chain(either_to_maybe)
    print(a)

    b = Maybe({'name': 'foo', 'mail': 'not an email o:'})\
        .map(get("mail"))\
        .map(validate_email)\
        .chain(either_to_maybe)

    print(b)

    print(a)

    print(maybe_to_either(Maybe.Nothing('hahasdf')))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
