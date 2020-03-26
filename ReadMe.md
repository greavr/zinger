### Python
source env/bin/activate
pip3 install -r requirements.txt
export FLASK_APP=index.py
export FLASK_ENV=development
python3 -m flask run

deactivate


docker build -t back-end . && docker run --name backy -d -p 5000:5000 back-end
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
