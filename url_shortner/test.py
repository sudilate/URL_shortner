import unittest
import sqlite3
import os
from flask import json
from app import app, URLShortener

class URLShortenerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "urls.db"
        cls.base_url = 'http://localhost:5000/'
        cls.url_shortener = URLShortener(base_url=cls.base_url, db_path=cls.test_db_path)

    def setUp(self):
        # Setup a clean test database before each test
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS urls')
            conn.commit()
        self.url_shortener._init_database()
        self.client = app.test_client()

    def tearDown(self):
        # Remove test database after each test
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def log_test_output(self, response):
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data.decode('utf-8')}")

    def test_shorten_url(self):
        long_url = "https://github.com/sudilate/URL_shortner"
        response = self.client.post('/shorten', json={'url': long_url})
        self.log_test_output(response)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('short_url', data)
        print("Test shorten url: ",data)

        short_key = data['short_url'].replace(self.base_url, '')

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT long_url FROM urls WHERE short_key = ?', (short_key,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], long_url)

    def test_redirect_to_url(self):
        long_url = "https://github.com/sudilate/URL_shortner"
        short_url = self.url_shortener.shorten_url(long_url)
        short_key = short_url.replace(self.base_url, '')

        response = self.client.get(f'/{short_key}')
        self.log_test_output(response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, long_url)
        print("Test redirecting url: ",response.location)

    def test_invalid_url_shorten(self):
        response = self.client.post('/shorten', json={'url': 'not_a_url'})
        self.log_test_output(response)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("Test invalid url shorten: ",data) 

    def test_get_url_stats(self):
        long_url = "https://github.com/sudilate/URL_shortner"
        short_url = self.url_shortener.shorten_url(long_url)
        short_key = short_url.replace(self.base_url, '')

        response = self.client.get(f'/stats/{short_key}')
        self.log_test_output(response)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['long_url'], long_url)
        self.assertEqual(data['visit_count'], 0)

        # Simulate a visit to update stats
        self.client.get(f'/{short_key}')
        response = self.client.get(f'/stats/{short_key}')
        self.log_test_output(response)
        data = json.loads(response.data)
        self.assertEqual(data['visit_count'], 1)
        print("URL Stats: ",data['visit_count'])

    def test_nonexistent_short_key(self):
        response = self.client.get('/nonexistent')
        self.log_test_output(response)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("Non existing Short Key: ",data)

    # Additional Negative Test Cases

    def test_empty_url_shorten(self):
        response = self.client.post('/shorten', json={'url': ''})
        self.log_test_output(response)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("testing empty url: ",data)

    def test_missing_url_field(self):
        response = self.client.post('/shorten', json={})
        self.log_test_output(response)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("Testing missing url field: ",data)

    # def test_database_error(self):
    #     # Simulate database error by removing the database file
    #     if os.path.exists(self.test_db_path):
    #         os.remove(self.test_db_path)

    #     response = self.client.post('/shorten', json={'url': 'https://github.com/sudilate/URL_shortner'})
    #     self.log_test_output(response)
    #     self.assertEqual(response.status_code, 500)
    #     data = json.loads(response.data)
    #     self.assertIn('error', data)

    def test_invalid_short_key_redirect(self):
        response = self.client.get('/invalidkey')
        self.log_test_output(response)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("testing invalid short key: ",data)

if __name__ == '__main__':
    unittest.main()
