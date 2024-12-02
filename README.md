# URL_shortner
An URL shortening tool which takes long url's and convert it to the short url with localhost as the base URL.

**Execution steps**:
1. Start the flask server: 
    python3 app.py
   
2. Run the curl command to shorten the URL (POST call):
   
    curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/some/long/url"}' http://localhost:5000/shorten

  Response will be Short URL: 
  
  {"short_url": "http://localhost:5000/abc123"}


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

**Alternative Tool to test:**

**Postman(GUI)- **

i. Create a new request:
ii. Set the method to POST.
iii. Enter the URL: http://localhost:5000/shorten.
iv. Go to the Body tab, select raw, and choose JSON format.
v. Paste your JSON payload:

{"url": "https://example.com/some/long/url"}

vi. Click Send. You’ll see the response in the Postman interface.


**Sample execution:**

1.<img width="1253" alt="Screenshot 2024-12-02 at 7 05 43 PM" src="https://github.com/user-attachments/assets/01fb239b-c725-4263-98a1-4cd96663ea9e">


2.<img width="701" alt="Screenshot 2024-12-02 at 7 06 18 PM" src="https://github.com/user-attachments/assets/7585f656-cba4-47bc-a409-e2628e612570">


3.<img width="1262" alt="Screenshot 2024-12-02 at 7 06 45 PM" src="https://github.com/user-attachments/assets/07d8a6f4-d75a-4b62-a431-04fbc515a978">

4.<img width="685" alt="Screenshot 2024-12-02 at 7 07 08 PM" src="https://github.com/user-attachments/assets/9ae25648-63a3-418b-8f29-39fcfa454dea">


