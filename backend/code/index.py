from flask import Flask, render_template, flash, request, redirect, jsonify, Response
import os
import redis
import datetime
import random
# Google Cloud Profiler
import googlecloudprofiler

"""
#############################
# Google Cloud Debugger
try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass

# Google Cloud Trace
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer
#############################
"""

# Redis Env
redisHost = os.getenv('redishost')
redisPort = os.getenv('redisport')
gcp_projectid = os.getenv('gcp_project')

# Debug settings
print ("Node: {0}, Redis Host: {1} , Redis Port: {2}".format(os.uname()[1], redisHost, redisPort))
profiler=False

r = redis.StrictRedis(charset="utf-8", decode_responses=True, socket_timeout=2,
    host=redisHost,
    port=redisPort)

# App Config
app = Flask(__name__)
app.config.from_object(__name__)

##############
# Custom Functions
def GetCount():
    return len(r.keys())

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
            project_id=gcp_projectid,
        )
        print ("Profiler started for " + gcp_projectid)
        profiler=True
    except (ValueError, NotImplementedError) as exc:
        print(exc)  # Handle errors here
        print("failed")

##############
# API's
# Kubernetes health check
@app.route("/healthz", methods=['GET', 'POST'])
def health():
    try:
        r.ping()
        return Response("Happy", status=200, mimetype='text/html')
    except:
        return Response("Unhappy", status=500, mimetype='text/html')

# Kubernetes readiness check
@app.route("/ready", methods=['GET', 'POST'])
def ready():
    try:
        r.ping()
        # Check if profiler is running
        if profiler:
            return Response("Happy - Profiler Enabled", status=200, mimetype='text/html')
        else:
            return Response("Happy - No Profiler", status=200, mimetype='text/html')
    except:
        print ("Not able to connect to redis")

# Default, display help page
@app.route("/", methods=['GET'])
def default():
    return render_template('default.html')




########################## CORE APIs
# Add Joke
@app.route("/api/v1/add", methods=['POST'])
def addJoke(tags=[]):
    # Reqiured Fields:
    ## title: string
    ## body: string
    ## poster: user_id
    ## tags

    if (not 'setup' in request.args or not 'body' in request.args or not 'poster' in request.args):
        return Response("Error:missing required fields: setup body poster.", status=400, mimetype='text/html')
    else:
        setup = request.args['setup']
        body = request.args['body']
        poster = request.args['poster']
        if 'tags' in request.args:
            tags = request.args['tags'].split(';')

    # Create Hash of zinger to store in redis
    zinger_id = "zing:" + str(GetCount() + 1)
    print (zinger_id)
    zinger = {"setup":setup ,"body":body ,"time":datetime.datetime.now().timestamp(),"poster":poster ,"votes":1, "flags":"active", "tags":str(tags)}
    r.hmset(zinger_id, zinger)

    # Add to score zset
    r.zadd('score:', {zinger_id:1} )

    # Add recorded vote
    r.sadd("voted:" + zinger_id, poster)

    # Save Tags
    for aTag in tags:
        r.sadd("tag:"+aTag, zinger_id)

    #Generate return
    results = r.hgetall(zinger_id)
    results["zinger_id"] = zinger_id
    results["result"] = "success"
    return jsonify(results)


# Update Joke
@app.route("/api/v1/update", methods=['POST'])
def updateJoke():

    ## TODO: REMOVE FROM GROUPS!!!

    # Required Fields:
    ## title: string
    ## body: string
    ## zinger_id: string
    # Optional Fields:
    ## tags

    if (not 'setup' in request.args or not 'body' in request.args or not 'zinger_id' in request.args ):
        return Response("Error:missing required fiedls: setup body zinger_id.", status=400, mimetype='text/html')
    else:
        setup = request.args['setup']
        body = request.args['body']
        zinger_id = request.args['zinger_id']

    # Validate that zinger_id exists
    if not r.exists(zinger_id):
        return Response("Error: zinger_id provided does not exist", status=400, mimetype='text/html')

    # Update values in redis value
    r.hset(zinger_id,"setup", setup)
    r.hset(zinger_id,"body", body)
    if 'tags' in request.args:
        r.hset(zinger_id,"tags", request.args['tags'])

    # Save Tags
    if 'tags' in request.args:
        tags = request.args['tags'].split(';')
        # Itterate over
        for aTag in tags:
            r.sadd("tag:"+aTag, zinger_id)

    #Return values
    results = r.hgetall(zinger_id)
    results["zinger_id"] = zinger_id
    results["result"] = "success"
    return jsonify(results)




# Remove Joke
@app.route("/api/v1/remove", methods=['POST'])
def removeJoke():
    # Mark Zinger as inactive
    if 'zinger_id' in request.args:
        zinger_id = request.args['zinger_id']
    else:
        return Response("Error: No zinger_id field provided. Please specify an zinger_id.", status=400, mimetype='text/html')

    # Validate that zinger_id exists
    if not r.exists(zinger_id):
        return Response("Error: zinger_id provided does not exist", status=400, mimetype='text/html')

    # Mark zinger as inactive
    r.hset(zinger_id,"flags", "inactive")

    # Remove from score zset
    r.zrem('score:',zinger_id)

    # Generate Results
    results = {}
    results["zinger_id"] = zinger_id
    results["result"] = "success"
    return jsonify(results)



# Vote For Joke
@app.route("/api/v1/vote", methods=['GET', 'POST'])
def voteJoke():
    # Reqiured Fields:
    ## zinger_id
    ## voter
    # POST Increases vote count
    # Get Returns current vote

    if 'zinger_id' in request.args :
        zinger_id = request.args['zinger_id']
    else:
        return Response("Error: No zinger_id field provided. Please specify an zinger_id.", status=400, mimetype='text/html')

    # Validate that zinger_id exists
    if not r.exists(zinger_id):
        return Response("Error: zinger_id provided does not exist", status=400, mimetype='text/html')


    # Used for response
    results = {}

    #GET
    if request.method == 'GET':
        results["votes"] = r.hget(zinger_id, "votes")
        results["zinger_id"] = zinger_id
        results["result"] = "success"
        return jsonify(results)

    #POST
    if request.method == 'POST':
        if not 'voter' in request.args:
            return Response("Error: No voter field provided. Please specify an voter.", status=400, mimetype='text/html')
        else:
            voter = request.args['voter']

        # Check for vote before:
        if r.sadd("voted:" + zinger_id, voter):
            # Increment vote in article
            r.hincrby(zinger_id, "votes", 1)

            # Increment vote in score zset
            r.zincrby("score:", 1, zinger_id)

            # Generate Results
            results["votes"] = r.hget(zinger_id, "votes")
            results["zinger_id"] = zinger_id
            results["user"] = voter
            results["result"] = "success"
            return jsonify(results)
        else:
            return Response("Error: user already voted for post", status=400, mimetype='text/html')

# Return top N Jokes
@app.route("/api/v1/list", methods=['GET'])
def listJoke(count=10,page=1,tag="" ):
    # Set via optional parameters else default to 10
    if 'count' in request.args:
        count = int(request.args['count'])

    # Get page
    if 'page' in request.args:
        page = int(request.args['page'])

    # Get tag
    key = 'score:'
    if 'tag' in request.args:
        tag = request.args['tag']
        key += tag

    if not r.exists(key):
        r.zinterstore(key, ['tag:'+tag,'score:'],aggregate='max')

    return jsonify(get_zingers(r,page,count,key))

def get_zingers(conn, page, count, tag='score:'):
    #Set up the start and end indexes for fetching the articles.
    start = (page-1) * count
    end = start + count - 1

    #Fetch the article ids.
    ids = conn.zrevrange(tag, start, end)

    articles = []
    for id in ids:
        article_data = conn.hgetall(id)
        article_data['zinger_id'] = id
        articles.append(article_data)

    #Get the article information from the list of article ids.
    return articles



if __name__ == "__main__":
    #start_profiler()
    app.run(host='0.0.0.0')
