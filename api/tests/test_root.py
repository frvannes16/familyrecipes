from .testcase import DBTestCase


class RootTestCase(DBTestCase):
    def test_get_hello(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_get_index_html(self):
        response = self.client.get("/index.html")
        assert response.status_code == 200
        assert "<title>Family Recipes</title>" in response.text
