# AI Gmail email delete

This project is a simple Python script that uses AI to identify Unimportant emails and delete them from your Gmail account.

## Prerequisites

- Python 3.10 or later
- Google API Client Library for Python
- Gmail API enabled in Google Cloud Console
- Ollama
- OAuth 2.0 credentials (`credentials.json`)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yorubadeveloper/ai-email-deleter.git
cd ai-email-deleter
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Google Oauth 2.0
- Go to the Google Cloud Console.
- Navigate to APIs & Services > Credentials.
- Create an OAuth 2.0 Client ID and download the credentials.json file.
- Place the credentials.json file in the root directory of this project.

### 5. Install Ollama and pull llama3 model
Navigate to the [Ollama](https://ollama.com/download) follow the instructions to install
Ollama.
#### Run the following command to pull the llama3 model
```bash
ollama pull llama3
```

### 6. Run the script

```bash
python main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)