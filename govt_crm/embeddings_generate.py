from sentence_transformers import SentenceTransformer
import json
import numpy as np

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the Q&A pairs from the JSON file
with open("static/json/qa.json", encoding="utf-8") as f:
    QA_PAIRS = json.load(f)

# Encode the questions to get their embeddings
embeddings = model.encode([qa["question"] for qa in QA_PAIRS], convert_to_tensor=True)

# Save the embeddings to a .npy file
np.save("static/json/qa1.npy", embeddings)
