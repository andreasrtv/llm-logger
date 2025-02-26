# LLM Logger
### Interface for conversing with an LLM
Created with the goal of logging LLM chats along with extra metadata. To be used in our bachelor thesis.

# Setup
```bash
pip install -r requirements.txt

flask db migrate
flask db upgrade
```

Create `.env` with relevant configging:
```ini
SECRET_KEY="sufficiently random string"
OPENAI_API_KEY="sk-"
USE_FAKE_LLM=True
```
If using fake LLM (debugging/testing/...), create a `fake_response.txt` file, and fill it with whatever you want.


# Development
```bash
flask --debug run
```


# Running
Use [run.py](./run.py) to run web server in production mode.

See the [infra](./infra/README.md) folder for notes regarding our setup.