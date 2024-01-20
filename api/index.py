import requests
import os 

from flask import Flask, request, render_template_string

HF_API_URL = os.environ.get('HF_API_URL')
HF_API_KEY = os.environ.get('HF_API_KEY')
ZZ_API_URL = os.environ.get('ZZ_API_URL')
ZZ_API_KEY = os.environ.get('ZZ_API_KEY')

def embed_query_hf(query):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    return requests.post(HF_API_URL, headers=headers, json={'inputs': query}).json()

def vector_query_zz(vector):
    headers = {"content-type": "application/json", "Authorization": f"Bearer {ZZ_API_KEY}"}
    payload = {
        "collectionName": "TranscriptChunks",
        "limit": 6,
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

def find_hivemind_clip_http(query):
    vector = embed_query_hf(query)
    results = vector_query_zz(vector)['data']
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
    .hl-blue {
    display: inline-block;
    text-align: center;
    width: 32px;
    margin-right: 2px;
    padding: -2px;
    box-sizing: border-box;
    line-height: 38px;
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
    line-height: 38px;
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
    line-height: 38px;  
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
    line-height: 38px;  
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
    line-height: 38px;
    background-color: #FE7F20;  /* Highlight color */
    color: white;                      /* White text color */
    text-shadow: -1px 1px 2px #000000;  /* Horizontal offset, Vertical offset, Blur radius, Shadow color */
    border: 0px white;
    }
  </style>
</head>
<body>
  <div class="container mt-4">
    <h2 class="mb-3"><span class="border"><span class="hl-blue">H</span><span class="hl-orange">I</span><span class="hl-yellow">V</span><span class="hl-green">E</span><span class="hl-orange">F</span><span class="hl-yellow">I</span><span class="hl-blue">N</span><span class="hl-green-last">D</span></span></h2>
    <form method="post" action="/" class="mb-3">
        <div class="form-group">
            <input type="text" name="text" class="form-control" placeholder="Search for your favorite Hivemind bits" />
        </div>
        <button type="submit" class="btn btn-primary">GO</button>
    </form>
    {% if results %}
      <h3>Results for: <small class="text-muted"> "{{ results[0].query }}" </small></h3>

      <div class="row">
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
    {% endif %}
  </div>
  <!-- Bootstrap JS and its dependencies (jQuery & Popper.js) -->
  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        user_input = request.form['text'].strip()

        if not user_input:
            # If the input is empty, do not proceed further
            return render_template_string(HTML_TEMPLATE, results=None)
        
        results = find_hivemind_clip_http(user_input)

    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(debug=True)
