import unittest
from mock import patch
import fakeredis
import json

# ~/code/index.py
import index

# set our application to testing mode
index.app.testing = True

class IndexTests(unittest.TestCase):


    #### setup and teardown ####
    # executed prior to each test
    def setUp(self):
        self.app = index.app.test_client()
        self.r = fakeredis.FakeServer()
        patch(index.r,  self.r) 


    def tearDown(self):
        pass

    #### tests ####
    def test_health(self):
        with index.app.test_client() as client:
            response = client.get('/healthz')
            self.assertEqual(response.status_code, 200)
    
    def test_ready(self):
        with index.app.test_client() as client:
            response = client.get('/ready')
            self.assertEqual(response.status_code, 200)
   
    # def test_ping(self):
    #     with index.app.test_client() as client:
    #         response = client.get('/ping')
    #         self.assertEqual(response.status_code, 200)

    # @app.route("/api/v1/add"
    # def test_add_good(self):
    #     with app.test_client() as client:
    #         #Sampe Test data
    #         TestData = {
    #             'setup' : 'TestData1',
    #             'body' : 'TestData1TestData1TestData1TestData1TestData1',
    #             'poster' : 'Test_User1',
    #             'tags' : 'test_tag;test_tag2'
    #         }
    #         response = client.post('/api/v1/add', query_string = TestData)

    #         print (response.json())
    #         self.assertEqual(response.status_code, 200)

    # def test_add_bad(self):
    #     pass

    # @app.route("/api/v1/update"

    # @app.route("/api/v1/remove

    # @app.route("/api/v1/vote"

    # @app.route("/api/v1/list"

    # def get_zingers(conn, page, count, tag='score:'):

    # def GetCount():
    def test_GetCount(self):     
        self.assertEqual(index.GetCount(), 1)

if __name__ == "__main__":
    unittest.main()