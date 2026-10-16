# Setup & run instructions
## Fill environment variables
1. ```cp .env.example .env```
2. ```nano .env```
3. Replace the changeme for the API key

## Option A (venv):
### Create virtual environment
1. ```python3 -m venv env```

### Install dependencies
1. ```source env/bin/activate```
2. ```pip install -r requirements.txt```
3. ```deactivate```

### Run
1. ```source env/bin/activate```
2. ```fastapi dev src/main.py``` (local) or ```fastapi run src/main.py``` (network)
3. ```deactivate```

## Option B (Docker):
### Compose
```sudo docker compose -f compose.yaml up --build -d```
## Restart
```sudo docker restart yv-take-home```
### Remove
```sudo docker rm -f yv-take-home```

# Decisions & Assumptions
* Deciding to do api backend as that is what I'm more interested in, though I'm used to usually doing full-stack for my personal projects
* Using python as that is what is standard for the company, though notably I've heard there is some work Golang and I am more familiar with the language
* Went with FastAPI as I know it's simple and easy to use
* I initally assumed versions and days would be correct but later realized there may be edge cases

# What I'd do next
* Have the caching of valid versions be more robust
