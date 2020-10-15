# Order managment

### Running api (development):
Install Redis:
```bash
sudo apt-get install redis
```
Start Redis server:
```bash
redis-server
```
Virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Export flask environmental variables:
```bash
export FLASK_APP=application
export FLASK_ENV=development
```
Initializing DB tables:
```bash
flask db init
flask db migrate
flask db upgrade
```
Populate "products" and "users" tables:
```bash
python fixtures.py 
```
Running flask server:
```bash
flask run
```
