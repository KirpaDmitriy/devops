from transformers import pipeline

generator = pipeline("text-generation", model="distilgpt2")

def generate_response(query: str, relevant_docs: list):
    context = "\n".join([doc[0] for doc in relevant_docs])
    prompt = f"Контекст: {context}\nВопрос: {query}\nОтвет:"
    response = generator(prompt, max_length=200, num_return_sequences=1)

    return response[0]["generated_text"]
  
