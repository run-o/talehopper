# talehopper

TaleHopper is a Choose-Your-Own-Adventure story generator for kids, leveraging LLMs to generate fun, engaging and compelling stories that kids love to read.
TaleHopper gives the reader control over the storyline, both on the initial setup and by letting them choose how the story progresses step-by-step.

The backend is using FastAPI with Python and the frontend is using React with Typescript.


## Docker Setup (Recommended)

First make sure to create a `.env` file containing the config settings (LLM API key/URL, etc.) in the `/backend` folder of the project.
You can use the provided [`.env.example`](backend/.env.example) file as a template.

The easiest way to run TaleHopper is using Docker: `docker compose up -d`
And then open a browser to: `http://localhost:3000/index.html`

For more details on Docker setup, including development mode with hot-reloading, see [DOCKER.md](DOCKER.md).

See the [`Makefile`](Makefile) for available commands.

## API Documentation

Docs provided via FastAPI: run the server and go to http://localhost:8000/docs

## Manual Setup

If you prefer to run the application without Docker, follow the instructions below.

### Backend setup

Make sure to create a `.env` file containing the config settings (LLM API key/URL, etc.) in the `/backend` folder of the project.
You can use the provided [`.env.example`](backend/.env.example) file as a template.

First install the required version of python as defined in the project (3.12.7) with pyenv:
- install pyenv if necessary: `brew install pyenv` 
- install 3.12.7: `pyenv install 3.12.7`
- set the pyenv version: `pyenv local 3.12.7`

- create python virtual env: `python3 -m venv .venv`
- activate virtual env: `source .venv/bin/activate`
- upgrade pip: `pip install --upgrade pip`
- install requirements: `pip install -r requirements.txt -r requirements-dev.txt`

Run the server with: `./run-server.sh`

### Frontend setup

To set up the frontend, ensure you have the correct Node.js and npm versions installed, as these are required for compatibility with the project's dependencies:
- `nvm install 24.1.0`
- `nvm use 24.1.0`
- upgrade npm if necessary: `npm install -g npm@11.4.1`
- install dependencies: `npm install`
- run the frontend with: `npm start`

## Testing

If running manually, run backend tests in the `/backend` folder: `python -m pytest`

If running in Docker: 
`docker compose -f docker-compose.dev.yml exec backend python -m pytest`


## LLM Configuration

### Hosted LLM setup

- create an account with OpenAI API compatible LLM (eg Groq)
- retrieve the base URL and API key and add them under `LLM_OPENAI_API_URL` and `LLM_OPENAI_API_KEY` in `.env` file

### Ollama LLM setup

- install Ollama: `brew install ollama`
- start the server: `ollama serve`
- pull desired model: `ollama pull mistral`

### Huggingface LLM Setup

- install transformers (this includes huggingface-hub): `pip install transformers`
- download the desired model locally: `huggingface-cli download OpenLLM-France/Claire-Mistral-7B-0.1`
