import sys
import base64
import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

# Load pre-trained model and tokenizer for generating embeddings
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
model = AutoModel.from_pretrained('distilbert-base-uncased')

def generate_embedding(input_bytes):
    # Decode the chunk from base64
    decoded_bytes = base64.b64decode(input_bytes)
    try:
        # Convert to string
        text = decoded_bytes.decode('utf-8', errors='ignore')
        # Tokenize the text
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        # Generate embedding using the model
        with torch.no_grad():
            outputs = model(**inputs)
        # Use the mean pooling of the token embeddings to get a single embedding vector per chunk
        embeddings = torch.mean(outputs.last_hidden_state, dim=1)
        return embeddings.detach().numpy().flatten().tolist()
    except UnicodeDecodeError:
        print("Could not decode bytes as UTF-8. Returning an empty embedding.")
        return []

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_embedding.py <base64_encoded_chunk>")
        sys.exit(1)

    input_data = sys.argv[1]
    embedding = generate_embedding(input_data)
    print(json.dumps(embedding))

if __name__ == "__main__":
    main()