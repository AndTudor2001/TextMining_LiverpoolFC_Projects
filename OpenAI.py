import openai
import sqlite3
from docx import Document

openai.api_key = ""

# Funcție care ne va ajuta în analiza relevanței unui articol față de subiectul "Liverpool FC"
def evaluate_relevance_with_chatgpt(article_body):
    prompt = f"Please evaluate how relevant this article is to the topic 'Liverpool FC' on a scale from 1 to 10, where 1 is 'not relevant at all' and 10 is 'very relevant': {article_body}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a relevance evaluation assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )
        relevance_score = response['choices'][0]['message']['content'].strip()
        return relevance_score
    except Exception as e:
        print(f"Error evaluating relevance: {str(e)}")
        return None

# Funcție care ne arată sentimentul articolului
def analyze_sentiment_with_chatgpt(article_body):
    prompt = f"Please analyze the sentiment of the following article. Is it positive, negative, or neutral? {article_body}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a sentiment analysis assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        sentiment = response['choices'][0]['message']['content'].strip()
        return sentiment
    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        return None

# Funcție pentru a analiza dacă un articol conține informații controversate sau polarizante
def detect_controversial_content(article_body):
    prompt = f"Analyze the following article and detect if it contains any controversial or polarizing content: {article_body}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a controversy detection assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        analysis_result = response['choices'][0]['message']['content'].strip()
        return analysis_result
    except Exception as e:
        print(f"Error detecting controversial content: {str(e)}")
        return None


conn = sqlite3.connect('articoleLiverpool.db')
cursor = conn.cursor()

# Crearea de tabele pentru relevanță, sentiment și conținut controversat, dacă nu există deja
cursor.execute('''
    CREATE TABLE IF NOT EXISTS relevanta_articole (
        article_id INTEGER PRIMARY KEY,
        relevance_score TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sentimente_articole (
        article_id INTEGER PRIMARY KEY,
        sentiment TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS controversial_content (
        article_id INTEGER PRIMARY KEY,
        analysis TEXT
    )
''')


cursor.execute("SELECT id, body_text FROM articoleLiverpool")
articles = cursor.fetchall()

# Analizăm fiecare articol pentru relevanță, sentiment și conținut controversat
for article in articles:
    article_id, body_text = article

    if body_text:

        relevance_score = evaluate_relevance_with_chatgpt(body_text)
        if relevance_score:
            cursor.execute("INSERT OR REPLACE INTO relevanta_articole (article_id, relevance_score) VALUES (?, ?)", (article_id, relevance_score))
            print(f"Article ID: {article_id}, Relevance to 'Liverpool FC': {relevance_score}/10")
        else:
            print(f"Could not evaluate relevance for article ID: {article_id}")


        sentiment = analyze_sentiment_with_chatgpt(body_text)
        if sentiment:
            cursor.execute("INSERT OR REPLACE INTO sentimente_articole (article_id, sentiment) VALUES (?, ?)", (article_id, sentiment))
            print(f"Article ID: {article_id}, Sentiment: {sentiment}")
        else:
            print(f"Could not analyze sentiment for article ID: {article_id}")


        analysis = detect_controversial_content(body_text)
        if analysis:
            cursor.execute("INSERT OR REPLACE INTO controversial_content (article_id, analysis) VALUES (?, ?)", (article_id, analysis))
            print(f"Article ID: {article_id}, Controversial Content: {analysis}")
        else:
            print(f"Could not analyze controversial content for article ID: {article_id}")

        # Salvăm schimbările în baza de date după fiecare articol
        conn.commit()
    else:
        print(f"Article ID {article_id} has no content.")
