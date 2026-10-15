from openai import OpenAI

# Ne conectăm la instanța locală Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def chat_loop():
    # 1. & 2. Inițializăm istoricul cu "system prompt-ul"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    print("Chat pornit. Scrie 'exit' sau 'quit' pentru a ieși.\n")

    while True:
        # 3. Citim inputul de la tastatură
        user_input = input("User: ")

        # 8. Comanda de ieșire
        if user_input.strip().lower() in ['exit', 'quit']:
            print("Conversație încheiată.")
            break

        # 4. Adăugăm mesajul utilizatorului în istoric
        messages.append({"role": "user", "content": user_input})

        # 5. Trimitem TOT istoricul către model
        response = client.chat.completions.create(
            model="qwen2.5:1.5b",
            temperature=0.7,
            messages=messages
        )

        # Extragem răspunsul generat
        assistant_reply = response.choices[0].message.content

        # 6. Afișăm răspunsul pe ecran
        print(f"Assistant: {assistant_reply}\n")

        # 7. CRUCIAL: Adăugăm răspunsul modelului înapoi în istoric,
        # pentru a-l trimite data viitoare
        messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == "__main__":
    chat_loop()