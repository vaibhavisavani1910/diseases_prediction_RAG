import pandas as pd
import random
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load the CSV file
file_path = "symptom_disease.csv"  # Replace with your file path
df = pd.read_csv(file_path)

# Use a free LLM model from Hugging Face
model_name = "EleutherAI/gpt-neo-1.3B"  # Replace with a free LLM
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Create a text generation pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

# Improved prompt to generate questions
def generate_questions(symptom, disease):
    prompt = (
        f"The following symptoms: {symptom}, are associated with the disease: {disease}. "
        f"Imagine you are helping someone who has been diagnosed with this disease. "
        f"Based on the symptoms and disease, generate thoughtful and relevant questions a person might ask their doctor or caregiver to better understand their condition, treatment options, and management strategies."
    )
    response = generator(prompt, max_length=200, num_return_sequences=1, temperature=0.7)
    return response[0]["generated_text"]

# Randomly select symptom-disease pairs
sampled_df = df.sample(n=46, random_state=42)  # Set random_state for reproducibility

# Generate and save questions
output_data = []
for index, row in sampled_df.iterrows():
    disease = row["disease"]
    symptoms = row["symptoms"]
    try:
        # Format the question and append to results
        question = generate_questions(symptoms, disease)
        output_data.append({"symptoms": question, "disease": disease})
    except Exception as e:
        print(f"Error processing {disease}: {e}")
        output_data.append({"symptoms": "Error generating question", "disease": disease})

# Convert results to a DataFrame and save
output_df = pd.DataFrame(output_data)
output_file = "symptom_diseases_test.csv"
output_df.to_csv(output_file, index=False)

print(f"Questions saved to {output_file}")
