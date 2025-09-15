from transformers import pipeline

# === Choose which analyzer you want ===
# 1) Sentiment Analysis
# analyzer = pipeline("sentiment-analysis")

# 2) Toxicity Detection
# analyzer = pipeline("text-classification", model="unitary/toxic-bert")

# 3) Emotion Detection
analyzer = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

print("💬 Message Analysis Tool (type 'exit' to quit)")
while True:
    msg = input("Enter your message: ")

    if msg.lower() == "exit":
        print("👋 Exiting program...")
        break

    result = analyzer(msg)[0]
    label = result['label']
    score = round(result['score'], 4)

    print(f"👉 Analysis: {label} (confidence: {score})\n")
