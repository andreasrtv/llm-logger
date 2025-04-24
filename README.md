# LLM Logger
### Interface for conversing with an LLM
Created with the goal of logging LLM chats along with extra metadata. To be used in our bachelor thesis.

# Setup
## Create `./src/.env` with relevant configging:
- `SECRET_KEY`: Random secret string for Flask sessions, for example generated with `head -c32 /dev/random | xxd -p`.
- `MOCK_LLM_RESPONSES`: If set to `true`, all "AI" messages will be the contents of `fake_response.txt` instead of actually calling an API. Useful for debugging/testing/.

### With Azure OpenAI API:
- `AZURE_OPENAI_API_KEY`: Your API key
- `AZURE_ENDPOINT`: Your endpoint URL (e.g. `https://[xyz].openai.azure.com/`)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name (created in the Azure AI Foundry portal)

### With OpenAI API:
- `OPENAI_API_KEY`: Your API key
- `OPENAI_MODEL`: Your model of choice (e.g. `o3-mini`)

If both `AZURE_OPENAI_API_KEY` and `OPENAI_API_KEY` are defined, Azure will take precedence and be used.

### Example
```ini
SECRET_KEY="53b7b7ed21a9ec434af799e74799c4761c85cbbba032690dd903ee8753b6ce3da"

MOCK_LLM_RESPONSES=false

AZURE_OPENAI_API_KEY="..."
AZURE_ENDPOINT="https://[xyz].openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="o3-mini"

OPENAI_API_KEY="..."
OPENAI_MODEL="o3-mini"
```

# Running
## Docker
Use `docker compose up -d` to run, after creating `./src/.env` file.

**Should not be publicly exposed in any way**, as the application does not implement any form of authorization - all users are admins and anyone can register a user. For our use case we've hosted LLM Logger behind a WireGuard VPN. See the [infra](./infra/README.md) folder for notes regarding our setup.


## Development
Initial setup:
```bash
pip install -r requirements.txt

flask db migrate
flask db upgrade
```

Running
```bash
flask --debug run
```