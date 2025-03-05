import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data = {"Inputs": {"data": [{"instant": 3, "date": "2011-01-01T00:00:00.000", "season": 1, "yr": 0, "mnth": 1, "weekday": 6, "weathersit": 2, "temp": 0.344167, "atemp": 0.363625, "hum": 0.805833, "windspeed": 0.160446}]}, "GlobalParameters": {"quantiles": [0.025, 0.975]}}

body = str.encode(json.dumps(data))

url = 'http://f08e5954-9151-480e-bccf-cbbdef90a567.eastus2.azurecontainer.io/score'


headers = {'Content-Type':'application/json'}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))
