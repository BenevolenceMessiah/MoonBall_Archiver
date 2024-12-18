import os
import requests
import logging

MODEL_DOWNLOAD_PATH = "./models"
logging.basicConfig(level=logging.INFO)

def download_model(model_name):
    model_path = os.path.join(MODEL_DOWNLOAD_PATH, model_name)
    if os.path.exists(model_path):
        logging.info(f"Model '{model_name}' already exists.")
        return

    # Create the models directory if it doesn't exist
    os.makedirs(MODEL_DOWNLOAD_PATH, exist_ok=True)

    # URL to download the model (using Hugging Face model hub as an example)
    url = f"https://huggingface.co/{model_name}/resolve/main/pytorch_model.bin"

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(model_path, 'wb') as model_file:
            for chunk in response.iter_content(chunk_size=8192):
                model_file.write(chunk)
        logging.info(f"Model '{model_name}' downloaded successfully.")
    else:
        logging.error(f"Failed to download model: {response.status_code} - {response.text}")

def list_models():
    if not os.path.exists(MODEL_DOWNLOAD_PATH):
        logging.info("No models directory found.")
        return

    models = os.listdir(MODEL_DOWNLOAD_PATH)
    if models:
        logging.info("Available models:")
        for model in models:
            logging.info(f" - {model}")
    else:
        logging.info("No models available.")

def delete_model(model_name):
    model_path = os.path.join(MODEL_DOWNLOAD_PATH, model_name)
    if os.path.exists(model_path):
        os.remove(model_path)
        logging.info(f"Model '{model_name}' deleted successfully.")
    else:
        logging.info(f"Model '{model_name}' not found.")

def model_exists(model_name):
    model_path = os.path.join(MODEL_DOWNLOAD_PATH, model_name)
    return os.path.exists(model_path)

if __name__ == "__main__":
    # Example usage
    download_model("distilbert-base-uncased")
    list_models()
    delete_model("distilbert-base-uncased")
    list_models()