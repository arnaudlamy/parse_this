from parse_this import parse_this, create_parser, parse_class
from parse_this.core import Self, Class, ParseThisError
import unittest


def parse_me(one, two, three=12):
    """Could use some parsing.

    Args:
        one: some stuff shouldn't be written down
        two: I can turn 2 syllables words into 6 syllables words
        three: I don't like the number three

    Returns:
        the first string argument concatenated with itself 'two' times and the
        last parameters multiplied by itself
    """
    return one * two, three * three


class TestParseThis(unittest.TestCase):

    def test_parse_this_return_value(self):
        self.assertEqual(parse_this(parse_me, [str, int], "yes 2".split()),
                          ("yesyes", 144))
        self.assertEqual(parse_this(parse_me, [str, int],
                                     "no 3 --three 2".split()),
                          ("nonono", 4))


@create_parser(str, int)
def iam_parseable(one, two, three=12):
    """I too want to be parseable.

    Args:
      one: the one and only
      two: for the money
      three: don't like the number three
    """
    return one * two, three * three


@parse_class(description="Hello World", parse_private=True)
class NeedParsing(object):
    """This will be used as the parser description."""

    @create_parser(Self, int)
    def __init__(self, four):
        """
        Args:
            four: an int that will be used to multiply stuff
        """
        self._four = four

    @create_parser(Self, int)
    def multiply_self_arg(self, num):
        return self._four * num

    @create_parser(Self, int)
    def _private_method(self, num):
        return self._four * num

    @create_parser(Self)
    def __str__(self):
        return str(self._four)

    @create_parser(Self, str, int)
    def could_you_parse_me(self, one, two, three=12):
        """I would like some arg parsing please.

        Args:
          one: and only one
          two: will never be first
          three: I don't like the number three
        """
        return one * two, three * three

    @classmethod
    @create_parser(Class, str, int)
    def parse_me_if_you_can(cls, one, two, three=12):
        return one * two, three * three


@parse_class()
class ShowMyDocstring(object):
    """This should be the parser description"""

    @create_parser(Self, int)
    def _will_not_appear(self, num):
        return num * num

    @create_parser(Self)
    def __str__(self):
        return self.__class__.__name__


@parse_class()
class NeedInitDecorator(object):

    def __init__(self, val):
        self._val = val

    @create_parser(Self, int)
    def do_stuff(self, num, div=2):
        return self._val * num / div


class TestParseable(unittest.TestCase):

    def test_class_decorator_description(self):
        self.assertEqual(NeedParsing.parser.description, "Hello World")
        self.assertEqual(ShowMyDocstring.parser.description,
                         "This should be the parser description")

    def test_class_is_decorated(self):
        self.assertTrue(hasattr(NeedParsing, "parser"))
        self.assertTrue(hasattr(NeedParsing(12), "parser"))
        self.assertTrue(hasattr(ShowMyDocstring, "parser"))

    def test_subparsers(self):
        parser = NeedParsing.parser
        self.assertEqual(parser.call("12 multiply-self-arg 2".split()), 24)
        self.assertEqual(parser.call("12 could-you-parse-me yes 2 --three 4".split()),
                         ("yesyes", 16))

    def test_private_method_are_exposed(self):
        parser = NeedParsing.parser
        self.assertEqual(parser.call("12 private-method 2".split()), 24)

    def test_special_method_is_exposed(self):
        parser = NeedParsing.parser
        self.assertEqual(parser.call("12 str".split()), "12")

    def test_private_method_are_not_exposed(self):
        with self.assertRaises(SystemExit):
            ShowMyDocstring.parser.parse_args("will-not-appear 12".split())
        with self.assertRaises(SystemExit):
            ShowMyDocstring.parser.parse_args("str".split())

    def test_parseable(self):
        parser = iam_parseable.parser
        namespace = parser.parse_args("yes 2 --three 3".split())
        self.assertEqual(namespace.one, "yes")
        self.assertEqual(namespace.two, 2)
        self.assertEqual(namespace.three, 3)
        self.assertEqual(iam_parseable("yes", 2, 3), ("yesyes", 9))

    def test_parseable_method(self):
        need_parsing = NeedParsing(12)
        parser = need_parsing.could_you_parse_me.parser
        namespace = parser.parse_args("yes 2 --three 3".split())
        self.assertEqual(namespace.one, "yes")
        self.assertEqual(namespace.two, 2)
        self.assertEqual(namespace.three, 3)
        self.assertEqual(need_parsing.could_you_parse_me(2, "yes", 3),
                         ("yesyes", 9))

    def test_parseable_class(self):
        parser = NeedParsing.parse_me_if_you_can.parser
        namespace = parser.parse_args("yes 2 --three 3".split())
        self.assertEqual(namespace.one, "yes")
        self.assertEqual(namespace.two, 2)
        self.assertEqual(namespace.three, 3)
        self.assertEqual(NeedParsing.parse_me_if_you_can(2, "yes", 3),
                         ("yesyes", 9))

    def test_init_need_decoration(self):
        with self.assertRaises(ParseThisError):
            NeedInitDecorator.parser.call("do-stuff 12".split())

    def test_need_init_decorator_with_instance(self):
        instance = NeedInitDecorator(2)
        self.assertEqual(NeedInitDecorator.parser.call("do-stuff 12".split(),
                                                       instance), 12)
        self.assertEqual(NeedInitDecorator.parser.call("do-stuff 12 --div 3".split(),
                                                       instance), 8)

if __name__ == "__main__":
    unittest.main()
