from flask import Flask, render_template, flash, request, redirect, jsonify, Response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
import datetime
import random
import requests
import string

# Google Cloud Profiler
import googlecloudprofiler

#App config
app = Flask(__name__)
app.config.from_object(__name__)

#App Settings
gcp_projectid = os.getenv('gcp_project')
profiler=False
backend="http://0.0.0.0:5000/"

# Global Variables


##############
# Custom Functions
def start_debugger():
    try:
        import googleclouddebugger
        googleclouddebugger.enable()
    except ImportError:
        pass

def start_profiler():
    # Profiler initialization. It starts a daemon thread which continuously
    # collects and uploads profiles. Best done as early as possible.
    try:
        googlecloudprofiler.start(
            service='zinger-backend',
            service_version='1.0.1',
            # verbose is the logging level. 0-error, 1-warning, 2-info,
            # 3-debug. It defaults to 0 (error) if not set.
            verbose=3,
            # project_id must be set if not running on GCP.
            project_id=os.getenv('gcp_project'),
        )
        print ("Profiler started for " + os.getenv('gcp_project'))
        profiler=True
    except (ValueError, NotImplementedError) as exc:
        print(exc)  # Handle errors here
        print("failed")
        
# Function to test connection to back end
def testBackend():
    try:
        response = requests.get(backend+ "/healthz", timeout=1)
        return True
    except:
        print("Unable to get response from:" + backend+"/healthz")
        return False

# Used for testing
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


#Add Zinger To backend
def AddZinger(title, body, user, tags = []):
    url = backend + "api/v1/add"

    Zinger = {}
    Zinger["setup"] = title
    Zinger["body"] = body
    Zinger["poster"] = user
    Zinger["tags"] = tags

    AddRequest = requests.post(url, params = Zinger)
    return(AddRequest.json())

#Vote for Zinger
def VoteForZinger(id, user):
    url = backend + "api/v1/vote"

    Zinger = {}
    Zinger["zinger_id"] = id
    Zinger["voter"] = user

    AddVoteRequest = requests.post(url, params = Zinger)
    return(AddVoteRequest.json())

# Get Zinger Vote Count
def GetVoteCount(id):
    url = backend + "api/v1/vote"

    Zinger = {}
    Zinger["zinger_id"] = id
    GetVoteRequest = requests.get(url, params = Zinger)
    return(GetVoteRequest.json())

# Update Zinger
def UpdateZinger(id,title, body, tags = []):
    url = backend + "api/v1/update"

    Zinger = {}
    Zinger["zinger_id"] = id
    Zinger["setup"] = title
    Zinger["body"] = body
    Zinger["tags"] = tags

    UpdateRequest = requests.post(url, params = Zinger)
    return(UpdateRequest.json())

#Get Zingers List
def GetZingers(page = 1, count = None, tag = None):
    url = backend + "api/v1/list"

    Zingers = {}
    Zingers["page"] = page
    if count is not None:
        Zingers["count"] = count
    if tag is not None:
        Zingers["tag"] = tag

    ZingersList = requests.get(url, params = Zingers)
    #Check for null return
    try:
        result = ZingersList.json()
        return(result)
    except ValueError:
        return ([])

def RemoveZinger(id):
    url = backend + "api/v1/remove"

    Zinger = {}
    Zinger["zinger_id"] = id
    RemoveRequest = requests.post(url, params = Zinger)
    return(RemoveRequest.json())

#############
# API's
# Kubernetes health check

@app.route("/healthz", methods=['GET', 'POST'])
def health():
    if testBackend():
        return Response("Happy", status=200, mimetype='text/html')
    else:
        return Response("Unhappy", status=500, mimetype='text/html')

# Kubernetes readiness check
@app.route("/ready", methods=['GET', 'POST'])
def ready():
    if testBackend():
        # Check if profiler is running
        if profiler:
            return Response("Happy - Profiler Enabled", status=200, mimetype='text/html')
        else:
            return Response("Happy - No Profiler", status=200, mimetype='text/html')
    else:
        print ("Not able to connect to back-end")


## Default pages
@app.route("/", methods=['GET'])
def default():
    ## Populate latest list of Zingers
    ZingerList = GetZingers()
    if ZingerList != []:
        for aZinger in ZingerList:
            print (aZinger["body"])
        return render_template('index.html', Zingers=ZingerList)
    else:
        return render_template('index.html', Zingers={})

@app.route('/edit/<string:id>', methods=["POST"])
def task(id):

    return ("Coming Soon...")


if __name__ == "__main__":
     # Start Google Services if flagged
    if os.getenv('gcp_project') is not None and os.getenv('GOOGLE_APPLICATION_CREDENTIALS') is not None:
        print ("Starting Google Services")
        # Start Service
        start_profiler()
        start_debugger()
    else:
        print ("Missing env settings: [ {0} ],[ {1} ]", os.getenv('gcp_project'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))

    app.run(host='0.0.0.0', port=8080)
