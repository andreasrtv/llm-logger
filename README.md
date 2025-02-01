# LLM Logger
### Interface for conversing with an LLM
Created with the goal of logging LLM chats along with extra metadata to be used in research.

# Setup
```bash
pip install -r requirements.txt

flask db init
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

# Run in development
```bash
flask --debug run
```

# Run in production
TODO