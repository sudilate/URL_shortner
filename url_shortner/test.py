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

    def test_shorten_url(self):
        long_url = "https://stockimg.ai/?code=4%2F0Adeu5BUTNhfgliocvF4zlARQE4EaOBPrj3VWMrvt0YraOTpO2XKE0cjDR4UMdYM4MMttSQ&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&authuser=0&prompt=consent#/dashboard"
        response = self.client.post('/shorten', json={'url': long_url})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('short_url', data)

        short_key = data['short_url'].replace(self.base_url, '')

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT long_url FROM urls WHERE short_key = ?', (short_key,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], long_url)

    def test_redirect_to_url(self):
        long_url = "https://stockimg.ai/?code=4%2F0Adeu5BUTNhfgliocvF4zlARQE4EaOBPrj3VWMrvt0YraOTpO2XKE0cjDR4UMdYM4MMttSQ&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&authuser=0&prompt=consent#/dashboard"
        short_url = self.url_shortener.shorten_url(long_url)
        short_key = short_url.replace(self.base_url, '')

        response = self.client.get(f'/{short_key}')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, long_url)

    def test_invalid_url_shorten(self):
        response = self.client.post('/shorten', json={'url': 'not_a_url'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_url_stats(self):
        long_url = "https://stockimg.ai/?code=4%2F0Adeu5BUTNhfgliocvF4zlARQE4EaOBPrj3VWMrvt0YraOTpO2XKE0cjDR4UMdYM4MMttSQ&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&authuser=0&prompt=consent#/dashboard"
        short_url = self.url_shortener.shorten_url(long_url)
        short_key = short_url.replace(self.base_url, '')

        response = self.client.get(f'/stats/{short_key}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['long_url'], long_url)
        self.assertEqual(data['visit_count'], 0)

        # Simulate a visit to update stats
        self.client.get(f'/{short_key}')
        response = self.client.get(f'/stats/{short_key}')
        data = json.loads(response.data)
        self.assertEqual(data['visit_count'], 1)

    def test_nonexistent_short_key(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
