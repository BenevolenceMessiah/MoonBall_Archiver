import sys
import base64
import json
import numpy as np
from transformers import pipeline

# Load pre-trained model for generating embeddings
embedding_pipeline = pipeline('feature-extraction', model='distilbert-base-uncased')

def generate_embedding(input_bytes):
    # Decode the chunk from base64
    decoded_bytes = base64.b64decode(input_bytes)
    # Convert to a list of integers
    data = list(decoded_bytes)
    # Generate embedding using the model
    embedding = embedding_pipeline(data)
    # Flatten the embedding to a 1D array
    flattened_embedding = np.array(embedding).flatten().tolist()
    return flattened_embedding

def main():
    # Get the input data from the command line arguments
    if len(sys.argv) != 2:
        print("Usage: python generate_embedding.py <base64_encoded_chunk>")
        sys.exit(1)

    input_data = sys.argv[1]
    # Generate the embedding
    embedding = generate_embedding(input_data)
    # Print the embedding as JSON
    print(json.dumps(embedding))

if __name__ == "__main__":
    main()
