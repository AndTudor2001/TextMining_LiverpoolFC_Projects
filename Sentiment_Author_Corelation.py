import openai
import sqlite3


openai.api_key = ""


conn = sqlite3.connect('articoleLiverpool.db')
cursor = conn.cursor()

# Extragem autorii și sentimentele din baza de date
cursor.execute('''
    SELECT a.author, s.sentiment
    FROM articoleLiverpool AS a
    JOIN sentimente_articole AS s ON a.id = s.article_id
''')
data = cursor.fetchall()


conn.close()


author_sentiments = {}

for author, sentiment in data:
    if author not in author_sentiments:
        author_sentiments[author] = []
    author_sentiments[author].append(sentiment)

# Pregătim promptul pentru ChatGPT pentru a analiza corelația
analysis_text = "Analyze the correlation between article sentiment and authorship.\n\n"
for author, sentiments in author_sentiments.items():
    sentiments_text = ', '.join(sentiments)
    analysis_text += f"Author: {author}, Sentiments: {sentiments_text}\n"


prompt = f"""
The following data represents article sentiment scores for various authors. 
Please analyze if there are any patterns or correlations, such as certain authors having consistently positive, negative, or neutral sentiments.

{analysis_text}
"""

# Apelăm API-ul OpenAI pentru analiza corelării
try:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.3
    )
    # Extragem răspunsul generat
    analysis_result = response['choices'][0]['message']['content']
    print("ChatGPT Analysis on Author-Sentiment Correlation:")
    print(analysis_result)
except Exception as e:
    print(f"Error calling OpenAI API: {str(e)}")
