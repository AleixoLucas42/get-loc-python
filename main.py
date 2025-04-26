from flask import Flask, request, jsonify, render_template_string
import os
import requests

global last_loc_received
last_loc_received = ""

app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head>
  <title>Get your localization</title>
</head>
<body>
  <h1>Localização</h1>
  <p id="status">Getting loc...</p>

  <script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const acc = position.coords.accuracy;

                fetch('/loc', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        latitude: lat,
                        longitude: lon,
                        accuracy: acc
                    })
                }).then(response => response.json())
                  .then(data => {
                    document.getElementById('status').innerHTML =
                      `localizacao sent!<br>
                      Latitude: ${lat}<br>
                      Longitude: ${lon}<br>
                      Precisão: ±${acc.toFixed(1)} meters<br>
                      <a href="${data.google_maps}" target="_blank">See on Google Maps</a>`;
                  });
            },
            function(error) {
                document.getElementById('status').textContent =
                    'Error: ' + error.message;
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        document.getElementById('status').textContent =
            'Cant get geolocalization on this device';
    }
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/loc', methods=['POST'])
def localizacao():
    global last_loc_received
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')
    acc = data.get('accuracy')
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    last_loc_received = maps_url
    print(f"User on: {lat},{lon} (±{acc}m) -> {maps_url}")
    headers = {
        "Authorization": f"Basic {os.environ['BASIC_AUTH']}"
    }
    print(headers)
    response = requests.request("GET", os.environ["PIPELINE_URL"], headers=headers, data={}, verify=False)
    if response.status_code == 201:
        print("Pipeline called")
    else:
        print(f"Error: {response.status_code} {response.text}")
    return jsonify({
        "status": "recebido",
        "google_maps": maps_url
    })

@app.route('/last', methods=['GET'])
def last_loc_received():
    global last_loc_received
    return last_loc_received
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

