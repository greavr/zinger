### Python
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
export FLASK_APP=index.py
export FLASK_ENV=development
python3 -m flask run

deactivate


### Run without GCP APM
docker rm -f backy && docker build -t back-end . && docker run --name backy -d -p 5000:5000 back-end
docker rm -f backy

### Run with GCP APM
docker rm -f backy && docker build -t back-end . && docker run --name backy -d -p 5000:5000 -e "gcp_project=ricks-sandbox" -e "GOOGLE_APPLICATION_CREDENTIALS=/home/rgreaves/key.json" -v /home/rgreaves:/home/rgreaves back-end
docker rm -f backy

#### REDIS
docker run --name some-redis -d -p 7001:6379 redis
docker rm -f some-redis

export redishost=127.0.0.1
export redisport=7001
export redisdb="zingers"
export gcp_project="ricks-sandbox"

export redishost="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' some-redis)"

#### Docker compose
docker-compose build
docker-compose -d up


#### GCP Profiler Service account
gcloud iam service-accounts create zinger-stackdriver-sa --display-name "Stackdriver Profiler Service Account"

gcloud projects add-iam-policy-binding ricks-sandbox \
    --member serviceAccount:zinger-stackdriver-sa@ricks-sandbox.iam.gserviceaccount.com \
    --role roles/cloudprofiler.agent 

gcloud projects add-iam-policy-binding ricks-sandbox \
    --member serviceAccount:zinger-stackdriver-sa@ricks-sandbox.iam.gserviceaccount.com \
    --role roles/clouddebugger.agent

gcloud projects add-iam-policy-binding ricks-sandbox \
    --member serviceAccount:zinger-stackdriver-sa@ricks-sandbox.iam.gserviceaccount.com \
    --role roles/cloudtrace.agent
    
gcloud iam service-accounts keys create \
     ~/key.json \
     --iam-account zinger-stackdriver-sa@ricks-sandbox.iam.gserviceaccount.com