import hashlib
import sqlite3
import logging
from flask import Flask, request, redirect, jsonify
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class URLShortener:
    def __init__(self, base_url='http://localhost:5000/', db_path='urls.db'):
        self.base_url = base_url
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS urls (
                        short_key TEXT PRIMARY KEY,
                        long_url TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        visit_count INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _generate_short_key(self, long_url, length=6):
        
        hash_object = hashlib.sha256(long_url.encode())
        short_key = hash_object.hexdigest()[:length]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for i in range(3):  
                    cursor.execute('SELECT 1 FROM urls WHERE short_key = ?', (short_key,))
                    if not cursor.fetchone():
                        return short_key  
                    
                    short_key = hash_object.hexdigest()[:length + i + 1]

        except Exception as e:
            logger.error(f"Error checking short key uniqueness: {e}")
            raise
        
        raise ValueError("Unable to generate a unique short key")
    
    def shorten_url(self, long_url):
        logger.info(f"Attempting to shorten URL: {long_url}")
        
        result = urlparse(long_url)
        if not all([result.scheme, result.netloc]):
            logger.error(f"Invalid URL format: {long_url}")
            raise ValueError("Invalid URL format")
        
        try:
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT short_key FROM urls WHERE long_url = ?', (long_url,))
                result = cursor.fetchone()
                if result:
                    short_key = result[0]
                    short_url = f"{self.base_url}{short_key}"
                    logger.info(f"Existing short URL found: {short_url}")
                    return short_url
        
        
            short_key = self._generate_short_key(long_url)
            cursor.execute(
                'INSERT INTO urls (short_key, long_url) VALUES (?, ?)',
                (short_key, long_url)
            )
            conn.commit()
        
            short_url = f"{self.base_url}{short_key}"
            logger.info(f"URL shortened: {long_url} -> {short_url}")
            return short_url
        except Exception as e:
            logger.error(f"Error storing or retrieving URL in database: {e}")
            raise

    
    def get_original_url(self, short_key):
        logger.info(f"Looking up short key: {short_key}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE urls 
                    SET visit_count = visit_count + 1 
                    WHERE short_key = ?
                    RETURNING long_url, visit_count
                ''', (short_key,))
                
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"Short URL not found: {short_key}")
                    raise ValueError("Short URL not found")
                
                logger.info(f"Retrieved URL for {short_key}: {result[0]}")
                return result[0], result[1]
        
        except Exception as e:
            logger.error(f"Error retrieving URL: {e}")
            raise

app = Flask(__name__)
url_shortener = URLShortener()

@app.route('/shorten', methods=['POST'])
def shorten():
    logger.info("Received shorten request")
    data = request.get_json()
    
    if not data or 'url' not in data:
        logger.error("No URL provided in request")
        return jsonify({"error": "URL is required"}), 400
    
    try:
        short_url = url_shortener.shorten_url(data['url'])
        return jsonify({"short_url": short_url}), 201
    except ValueError as e:
        logger.error(f"URL shortening error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/<short_key>', methods=['GET'])
def redirect_to_url(short_key):
    logger.info(f"Redirect request for short key: {short_key}")
    try:
        original_url, visit_count = url_shortener.get_original_url(short_key)
        logger.info(f"Redirecting to: {original_url}")
        
        response = redirect(original_url, code=301)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response
    except ValueError:
        logger.warning(f"Short key not found: {short_key}")
        return jsonify({"error": "URL not found"}), 404

@app.route('/stats/<short_key>', methods=['GET'])
def get_url_stats(short_key):
    logger.info(f"Stats request for short key: {short_key}")
    try:
        with sqlite3.connect(url_shortener.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT long_url, visit_count, created_at FROM urls WHERE short_key = ?',
                (short_key,)
            )
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"No stats found for short key: {short_key}")
                return jsonify({"error": "URL not found"}), 404
            
            return jsonify({
                "long_url": result[0],
                "visit_count": result[1],
                "created_at": result[2]
            })
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
