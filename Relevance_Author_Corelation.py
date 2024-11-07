import openai
import sqlite3
import re


openai.api_key = ""


conn = sqlite3.connect('articoleLiverpool.db')
cursor = conn.cursor()

# Extragem autorii și scorurile de relevanță din baza de date
cursor.execute('''
    SELECT a.author, r.relevance_score
    FROM articoleLiverpool AS a
    JOIN relevanta_articole AS r ON a.id = r.article_id
''')
data = cursor.fetchall()

# Închidem conexiunea la baza de date
conn.close()


author_scores = {}

for author, relevance_score_text in data:
    # Extragem primul număr din relevanță (scorul) folosind regex
    match = re.search(r'\d+(\.\d+)?', relevance_score_text)
    if match:
        relevance_score = float(match.group(0))
        if author not in author_scores:
            author_scores[author] = []
        author_scores[author].append(relevance_score)

# Calculăm media scorurilor pentru fiecare autor și limităm la primii 10 autori pentru prompt
analysis_text = "Analyze the correlation between average relevance scores and authorship.\n\n"
for author, scores in list(author_scores.items())[:10]:  # Limitează la primii 10 autori
    avg_score = sum(scores) / len(scores)
    analysis_text += f"Author: {author}, Average Relevance Score: {avg_score:.2f}\n"

# Construim promptul pentru ChatGPT
prompt = f"""
The following data represents average article relevance scores for various authors. 
Please analyze if there are any patterns or correlations, such as certain authors having consistently high or low average relevance scores.

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
        max_tokens=1000,
        temperature=0.3
    )

    analysis_result = response['choices'][0]['message']['content']
    print("ChatGPT Analysis on Author-Average Relevance Correlation:")
    print(analysis_result)
except Exception as e:
    print(f"Error calling OpenAI API: {str(e)}")
