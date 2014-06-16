'''
Inject is a simple function that uses values from a dictionary as arguments for
a function.

>>> inject(lambda argument: argument, {'argument': 1})
1

>>> def positional(one, two): return one, two
>>> inject(positional, {'one': 1, 'two': 2})
(1, 2)

Extra arguments are ignored (the main difference from using
`function(**context)`)

>>> positional(**{'one': 1, 'two': 2, 'three': 3})
Traceback (most recent call last):
    ...
TypeError: positional() got an unexpected keyword argument 'three'

>>> inject(positional, {'one': 1, 'two': 2, 'three': 3})
(1, 2)

Inject can pass *args and **kwargs to the function:

>>> def varargs(*args): return args
>>> inject(varargs, {'args': [1, 3, 5], 'extra': None})
(1, 3, 5)

>>> def kwargs(**kwargs): return kwargs
>>> result = inject(kwargs, {'args': None, 'kwargs': {'a': [1,2], 'b': [5,7]}})
>>> result['a']
[1, 2]
>>> result['b']
[5, 7]
'''
import inspect
import sys
import unittest


__all__ = ('inject', )


def inject(function, context):
    ''' Use values from the dictionary `context` as arguments for `function` '''
    argspec = inspect.getargspec(function)

    positional = [context[name] for name in argspec.args if name in context]
    if argspec.varargs is not None and argspec.varargs in context:
        for value in context[argspec.varargs]:
            positional.append(value)

    if argspec.keywords is not None and argspec.keywords in context:
        return function(*positional, **context[argspec.keywords])

    return function(*positional)


class InjectTestCase(unittest.TestCase):
    def test_positional(self):
        def function(a, b, c):
            return (a, b, c)

        with self.assertRaises(TypeError):
            inject(function, {})

        self.assertEquals(inject(function, {'a': 1, 'b': 2, 'c': 3}), (1, 2, 3))
        self.assertEquals(inject(function, {'a': 1, 'b': 2, 'c': 3, 'extra': 5}), (1, 2, 3))

    def test_defaults(self):
        def function(extra=[1,2]):
            return extra

        self.assertEquals(inject(function, {}), [1, 2])
        self.assertEquals(inject(function, {'extra': [3, 5]}), [3, 5])

    def test_varargs(self):
        def function(*args):
            return args

        self.assertEquals(inject(function, {}), ())
        self.assertEquals(inject(function, {'a': [3, 5]}), ())
        self.assertEquals(inject(function, {'args': [3, 5]}), (3, 5))
        self.assertEquals(inject(function, {'args': [3, 5], 'c': None}), (3, 5))

        with self.assertRaises(TypeError):
            # None is not iterable
            inject(function, {'args': None})

    def test_keywords(self):
        def function(**extra):
            return extra

        self.assertEquals(inject(function, {}), {})
        self.assertEquals(inject(function, {'extra': {}}), {})
        self.assertEquals(inject(function, {'extra': {'a': 1}}), {'a': 1})
        self.assertEquals(inject(function, {'extra': {'a': 1}, 'a': 1}), {'a': 1})

        with self.assertRaises(TypeError):
            # must be a mapping not list
            self.assertEquals(inject(function, {'extra': [], 'a': 1}), {'a': 1})

        with self.assertRaises(TypeError):
            # must be a mapping not NoneType
            self.assertEquals(inject(function, {'extra': None}), {})

    def test_positional_defaults(self):
        def function(a, b=1):
            return (a, b)

        with self.assertRaises(TypeError):
            inject(function, {})

        self.assertEquals(inject(function, {'a': 3}), (3, 1))
        self.assertEquals(inject(function, {'a': 3, 'c': 4}), (3, 1))
        self.assertEquals(inject(function, {'a': 3, 'b': 4}), (3, 4))

    def test_positional_keywords(self):
        def function(a, b, **extra):
            return (a, b, extra)

        with self.assertRaises(TypeError):
            inject(function, {})

        with self.assertRaises(TypeError):
            inject(function, {'a': 3})

        self.assertEquals(inject(function, {'a': 3, 'b': 4}), (3, 4, {}))
        self.assertEquals(inject(function, {'a': 3, 'b': 4, 'extra': {}}), (3, 4, {}))
        self.assertEquals(inject(function, {'a': 3, 'b': 4, 'extra': {'c': 1}}), (3, 4, {'c': 1}))
        self.assertEquals(inject(function, {'a': 3, 'b': 4, 'extra': {'c': 1}, 'd': None}), (3, 4, {'c': 1}))

    def test_positional_varargs(self):
        def function(a, *varargs):
            return (a, varargs)

        with self.assertRaises(TypeError):
            inject(function, {})

        self.assertEquals(inject(function, {'a': 3}), (3, ()))
        self.assertEquals(inject(function, {'a': 3, 'c': 4}), (3, ()))
        self.assertEquals(inject(function, {'a': 3, 'varargs': (4,)}), (3, (4,)))

    def test_missing_positional(self):
        def function(first, second):
            return second

        if sys.version_info.major == 2:
            with self.assertRaisesRegexp(TypeError, '^function\(\) takes exactly 2 arguments \(0 given\)$'):
                inject(function, {})

            with self.assertRaisesRegexp(TypeError, '^function\(\) takes exactly 2 arguments \(1 given\)$'):
                inject(function, {'first': 1})
        else:
            with self.assertRaisesRegexp(TypeError, "^function\(\) missing 2 required positional arguments: 'first' and 'second'$"):
                inject(function, {})

            with self.assertRaisesRegexp(TypeError, "^function\(\) missing 1 required positional argument: 'second'"):
                inject(function, {'first': 1})

    def test_missing_positional_vararg(self):
        def function(first, second, *third):
            return second

        if sys.version_info.major == 2:
            with self.assertRaisesRegexp(TypeError, '^function\(\) takes at least 2 arguments \(0 given\)$'):
                inject(function, {})

            with self.assertRaisesRegexp(TypeError, '^function\(\) takes at least 2 arguments \(1 given\)$'):
                inject(function, {'first': 1})
        else:
            with self.assertRaisesRegexp(TypeError, "^function\(\) missing 2 required positional arguments: 'first' and 'second'$"):
                inject(function, {})

            with self.assertRaisesRegexp(TypeError, "^function\(\) missing 1 required positional argument: 'second'"):
                inject(function, {'first': 1})

    def test_missing_positional_keywords(self):
        def function(first, second, **third):
            return second

        if sys.version_info.major == 2:
            with self.assertRaisesRegexp(TypeError, '^function\(\) takes exactly 2 arguments \(0 given\)$'):
                inject(function, {})

            with self.assertRaisesRegexp(TypeError, '^function\(\) takes exactly 2 arguments \(1 given\)$'):
                inject(function, {'first': 1})
        else:
            with self.assertRaisesRegexp(TypeError, "^function\(\) missing 2 required positional arguments: 'first' and 'second'$"):
                inject(function, {})

            with self.assertRaisesRegexp(TypeError, "^function\(\) missing 1 required positional argument: 'second'"):
                inject(function, {'first': 1})


    def test_multiple_pisitional_keywords(self):
        def function(a, **b):
            return a, b

        if sys.version_info.major == 2:
            with self.assertRaisesRegexp(TypeError, "^function\(\) got multiple values for keyword argument 'a'"):
                inject(function, {'a': 1, 'b': {'a': 2}})
        else:
            with self.assertRaisesRegexp(TypeError, "^function\(\) got multiple values for argument 'a'"):
                inject(function, {'a': 1, 'b': {'a': 2}})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', default=False, help='flag to run the tests')
    parser.add_argument('--failfast', action='store_true', default=False, help='unittest failfast')
    args = parser.parse_args()

    if args.test:
        import doctest
        (failures, total) = doctest.testmod()

        if failures:
            sys.exit(failures)

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(InjectTestCase)
        result = unittest.TextTestRunner(failfast=args.failfast).run(suite)

        if result.errors or result.failures:
            sys.exit(len(result.errors) + len(result.failures))
