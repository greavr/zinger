import unittest
import json

# ~/code/index.py
from index import app

# set our application to testing mode
app.testing = True

class BasicsTests(unittest.TestCase):

    #### setup and teardown ####

    # executed prior to each test
    def setUp(self):
        pass

    def tearDown(self):
        pass


    #### tests ####
    def test_health(self):
        with app.test_client() as client:
            response = client.get('/healthz')
            self.assertEqual(response.status_code, 200)
    
    def test_ready(self):
        with app.test_client() as client:
            response = client.get('/ready')
            self.assertEqual(response.status_code, 200)

    @app.route("/api/v1/add"

    @app.route("/api/v1/update"

    @app.route("/api/v1/remove

    @app.route("/api/v1/vote"

    @app.route("/api/v1/list"

    def get_zingers(conn, page, count, tag='score:'):

if __name__ == "__main__":
    unittest.main()