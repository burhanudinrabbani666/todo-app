import pytest


def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 2


def test_is_instance():
    assert isinstance("This is string", str)
    assert not isinstance("10", int)


def test_boolean():
    validated = True
    assert validated is True
    assert ("hello" == "world") is False


def test_type():
    assert type("Hello" is str)
    assert type("World" is not int)


def test_greater_and_less_then():
    assert 7 > 3
    assert 4 < 9


def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]

    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)


class Student:
    first_name: str
    last_name: str
    major: str
    year: int

    def __init__(
        self,
        first_name: str,
        last_name: str,
        major: str,
        year: int,
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = year


@pytest.fixture
def default_employe():
    return Student("burhanudin", "rabbani", "art", 2021)


def test_student_init(default_employe: Student):
    assert default_employe.first_name == "burhanudin"
    assert default_employe.last_name == "rabbani"
    assert default_employe.major == "art"
    assert default_employe.year == 2021
