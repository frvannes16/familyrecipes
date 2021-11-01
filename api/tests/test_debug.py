from api.settings import settings


def test_debug_is_true_in_test():
    assert settings.debug == True
