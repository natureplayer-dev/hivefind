import requests
import os 

from flask import Flask, request, render_template_string, jsonify

HF_API_URL = os.environ.get('HF_API_URL')
HF_API_KEY = os.environ.get('HF_API_KEY')
ZZ_API_URL = os.environ.get('ZZ_API_URL')
ZZ_API_KEY = os.environ.get('ZZ_API_KEY')

def embed_query_hf(query):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    return requests.post(HF_API_URL, headers=headers, json={'inputs': query}).json()

def vector_query_zz(vector, limit=6):
    headers = {"content-type": "application/json", "Authorization": f"Bearer {ZZ_API_KEY}"}
    payload = {
        "collectionName": "TranscriptChunks",
        "limit": int(limit),
        "outputFields": ["clip_text", "video_title", "start", "duration", "video_url"],
        "vector": vector
    }
    return requests.post(ZZ_API_URL, headers=headers, json=payload).json() 

def highlight(word):
    return f"<span class=\"highlight\">{word}</span>" #text.replace(word, f"\033[{color_code}m{word}\033[0m")

def highlight_matches(text, query):
    q_upper = [w.upper() for w in query.split()]
    text_arr = text.split()
    for i, w in enumerate(text_arr):
        if w.upper() in q_upper:
            text_arr[i] = highlight(w)
    return " ".join(text_arr)

def find_hivemind_clip_http(query, limit=6):
    lim_k = min(limit, 30)
    vector = embed_query_hf(query)
    results = vector_query_zz(vector, limit=lim_k)['data']
    for idx, r in enumerate(results):
        results[idx]['video_url'] = results[idx]['video_url'].replace("watch?v=", "embed/").replace("&t=", "?start=")
        results[idx]['mins'] = int((results[idx]['start'] % 3600)/ 60)
        results[idx]['hours'] = int(results[idx]['start'] / 3600)
        if results[idx]['hours'] == 0:
           results[idx]['hours'] = ""
        else:
            results[idx]['hours'] = str(results[idx]['hours'])+":"
            if results[idx]['mins']< 10: 
                results[idx]['mins'] = "0" + str(results[idx]['mins'])
        results[idx]['secs'] = int(results[idx]['start'] % 60)
        if results[idx]['secs'] < 10:
            results[idx]['secs'] = "0" + str(results[idx]['secs'])
        else:
            results[idx]['secs'] = str(results[idx]['secs'])
        results[idx]['query'] = query
        results[idx]['clip_text'] = highlight_matches(results[idx]['clip_text'], query)
    return results




app = Flask(__name__)

# HTML template for the main page
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HIVEFIND</title>
  <!-- Bootstrap CSS -->
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <style>
    /* Custom CSS for uniform card height */
    body {
        background-color: #FDC308;
        height: 100%;
        margin: 0;
    }
    html {
        height: 100%;
        margin: 0;
    }
    footer {
        height: 36px;
        text-align: center;
        padding: 8px;
        background-color: #333;
        color: white;
        bottom: 0;
        width: 100%;
        font-size: 12px;
    }
    .home-button-container {
        cursor: pointer;
    }
    .load-button-container {
        display: flex;
        justify-content: center;
        margin-top: 8px;
        margin-bottom: 24px;
    }
    .page-container { 
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    .content-wrap {
        flex: 1;
    }
    .border {
        background-color: white;
        padding: 2px;
    }
    .card-deck .card {
      height: 100%;  /* Make cards take full height of card-deck */
    }
    .card-body {
      display: flex;
      flex-direction: column;
    }
    .card-body > * {
      margin-bottom: auto;  /* Pushes everything up */
    }
    .embed-responsive {
      margin-top: auto;  /* Pushes video to bottom */
    }
    .highlight {
    background-color: #FFFACD;  /* Highlight color */
    }
    .footer-link {
        color: #77CCFF;
    }
    .query-styling {
        display: inline-block;
        color: #495057;
        background-color: #FFFACD;
        border-radius: 4px;
        padding: 4px;
        border: 1px solid #495057;
        box-shadow: 0 0 1px #495057;
        font-size: 12pt;
    }
    .hl-blue {
    display: inline-block;
    text-align: center;
    width: 32px;
    margin-right: 2px;
    padding: -2px;
    box-sizing: border-box;
    line-height: 39px;
    background-color: #3286F6;  /* Highlight color */
    color: white;                      /* White text color */
    text-shadow: -1px 1px 2px #000000;  /* Horizontal offset, Vertical offset, Blur radius, Shadow color */
    border: 0px white;
    }
    .hl-yellow {
    display: inline-block;
    text-align: center;
    width: 32px;
    margin-right: 2px;
    padding: -2px;
    box-sizing: border-box;
    line-height: 39px;
    background-color: #FDC308;  /* Highlight color */
    color: white;                      /* White text color */
    text-shadow: -1px 1px 2px #000000;  /* Horizontal offset, Vertical offset, Blur radius, Shadow color */
    border: 0px white;
    }
    .hl-green {
    display: inline-block;
    text-align: center;
    width: 32px;
    margin-right: 2px;
    padding: -2px;
    box-sizing: border-box;
    line-height: 39px;  
    background-color: #62D023;  /* Highlight color */
    color: white;                      /* White text color */
    text-shadow: -1px 1px 2px #000000;  /* Horizontal offset, Vertical offset, Blur radius, Shadow color */
    border: 0px white;
    }
    .hl-green-last {
    display: inline-block;
    text-align: center;
    width: 32px;
    margin-right: 0px;
    padding: -2px;
    box-sizing: border-box;
    line-height: 39px;  
    background-color: #62D023;  /* Highlight color */
    color: white;                      /* White text color */
    text-shadow: -1px 1px 2px #000000;  /* Horizontal offset, Vertical offset, Blur radius, Shadow color */
    border: 0px white;
    }
    .hl-orange {
    display: inline-block;
    text-align: center;
    width: 32px;
    margin-right: 2px;
    padding: -2px;
    box-sizing: border-box;
    line-height: 39px;
    background-color: #FE7F20;  /* Highlight color */
    color: white;                      /* White text color */
    text-shadow: -1px 1px 2px #000000;  /* Horizontal offset, Vertical offset, Blur radius, Shadow color */
    border: 0px white;
    }
  </style>
</head>
<body>
<div class="page-container">
<div class="content-wrap">
  <div class="container mt-4">
    <h2 class="mb-3"><span id="homeButton" class="home-button-container"><span class="border"><span class="hl-blue">H</span><span class="hl-orange">I</span><span class="hl-yellow">V</span><span class="hl-green">E</span><span class="hl-orange">F</span><span class="hl-yellow">I</span><span class="hl-blue">N</span><span class="hl-green-last">D</span></span></span></h2>
    <form method="post" action="/" class="mb-3" id="search-form">
        <div class="form-group">
            <input id="user-input" type="text" name="text" class="form-control" placeholder="Search for your favorite Hivemind bits" value="{{ user_input|default('') }}"/>
            <input type="hidden" id="limit-input" name="limit" value="{{ limit }}">
        </div>
        <button type="submit" onclick="loadQuery()" class="btn btn-primary">Go</button>
    </form>
    {% if results %}
      <h3><small>Results for: &shy;<span class="query-styling">"{{ results[0].query }}"</span></small></h3>

      <div class="row" id="results-container">
      {% for result in results %}
        <div class="col-md-6 col-lg-4 mb-3">
          <div class="card h-100">
            <div class="card-body">
            <h5 class="card-title">{{ result.video_title }}<small class="text-muted"> (@ {{result.hours}}{{result.mins}}:{{result.secs}})</small></h5>
            <p class="card-text"><strong>Caption text:</strong> {{ result.clip_text|safe }}</p>
            <div class="embed-responsive embed-responsive-16by9">
                <iframe class="embed-responsive-item" src="{{ result.video_url }}" allowfullscreen></iframe>
            </div>
            </div>
          </div>
        </div>
      {% endfor %}
      </div>
      {% if limit < 30 %}
        <div class="load-button-container">
        <button onclick="loadMore()" class="btn btn-primary">Show more</button>
        </div>
      {% endif %}
    {% endif %}
  </div>
</div>
<footer>
    Made with love by <spa><a href="https://twitter.com/natureplayer_" class="footer-link">natureplayer</a>.
</footer> 
</div>  
  <!-- Bootstrap JS and its dependencies (jQuery & Popper.js) -->
  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
<script>
    function loadMore() {
        let currentLimit = parseInt(document.getElementById('limit-input').value);
        const newLimit = currentLimit + 6;
        document.getElementById('limit-input').value = newLimit;

        // Trigger form submission
        document.getElementById('search-form').submit();
    }
    function loadQuery() {
        let currentLimit = parseInt(document.getElementById('limit-input').value);
        const newLimit = 6;
        document.getElementById('limit-input').value = newLimit;

        // Trigger form submission
        document.getElementById('search-form').submit();
    }
</script>
<script>
    document.getElementById('homeButton').addEventListener('click', function() {
        let currentLimit = parseInt(document.getElementById('limit-input').value);
        document.getElementById('limit-input').value = 6;
        document.getElementById('user-input').value = "";

        document.getElementById('search-form').submit();
    });
</script>
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
</html>
"""

from flask import request, render_template_string, jsonify

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = ""
    limit = 6
    max_results = 30
    if request.method == 'POST':
        user_input = request.form['text'].strip()

        if 'limit' in request.form:
            limit = int(request.form['limit'])
        
    results = find_hivemind_clip_http(user_input, min(max_results, limit)) if user_input else None

    return render_template_string(HTML_TEMPLATE, results=results, user_input=user_input, limit=limit)

if __name__ == '__main__':
    app.run(debug=True)
