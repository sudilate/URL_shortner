# URL_shortner
An URL shortening tool which takes long url's and convert it to the short url with localhost as the base URL.

**Execution steps**:
1. Start the flask server: 
    python3 app.py
2. Run the curl command to shorten the URL (POST call):
    curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/some/long/url"}' http://localhost:5000/shorten

  Response will be Short URL: {"short_url": "http://localhost:5000/abc123"}

3. Access the Short URL(which redirect to the original URL) in the browser:
   http://localhost:5000/abc123

4. URL request to get the visit count:
   curl http://localhost:5000/stats/abc123

   Response will be:
   {
  "created_at": "2024-12-02 09:45:53",
  "long_url": "https://colab.research.google.com/drive/1OGzvsPn0uo68Nmw0oEDbdPWFfe1ksN6D",
  "visit_count": 3
}

