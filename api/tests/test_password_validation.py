import pytest
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError

from api.schemas import PasswordStr


class TestUser(BaseModel):
    password: PasswordStr


def test_good_passwords():
    TestUser(password="passwordPASSWORD12@!")
    TestUser(password="eXperiMent@!")
    TestUser(password="UPPERCASElowercase@!")
    TestUser(password="ab123091823079123AB@!")
    TestUser(password="12charsLong@")


def test_short_password_fails():
    with pytest.raises(ValueError, match="12"):
        TestUser(password="pW2!")


def test_empty_password_fails():
    with pytest.raises(ValueError):
        TestUser(password="")


def test_none_password_fails():
    with pytest.raises(ValidationError):
        TestUser(password=None)


def test_missing_special_char_fails():
    with pytest.raises(ValueError, match="special"):
        TestUser(password="passwordMIXTURE123")


def test_missing_case_mixture_fails():
    with pytest.raises(ValueError, match="case"):
        TestUser(password="passwordmixture123!@#")


def test_is_not_string():
    with pytest.raises(ValidationError):
        TestUser(password=12)


def test_all_bad_cases_in_one():
    with pytest.raises(ValidationError):
        TestUser(password="abc123")
