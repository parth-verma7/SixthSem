## Setup
1. Copy example env file
```sh
cp .env.example .env
```
2. Generate a secret key and set the value of `SECRET_KEY` to this value
```sh
openssl rand -hex 32
```
3. Make a virtual environment. Install the dependencies
```sh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```
4. Source the .env file
```sh
export $(grep -v '^#' .env | xargs)
```
