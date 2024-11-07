import requests
import sqlite3

api_key = ""

url="https://content.guardianapis.com/search"

params={
    'api-key': api_key,
    'q':'"Liverpool FC"',
    'from-date':'2009-03-20',
    'to-date':'2024-10-23',
    'section':'football',
    'page-size':200,
    'order-by':'newest',
    'show-fields':'headline,trailText,byline,bodyText,webPublicationDate,webUrl'
}

conn=sqlite3.connect('articoleLiverpool.db')
c=conn.cursor()

c.execute('''
        CREATE TABLE IF NOT EXISTS articoleLiverpool(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            author TEXT,
            published_date TEXT,
            body_text TEXT
        )
        ''')

response=requests.get(url,params=params)
if response.status_code==200:
    data=response.json()

    articles=data['response']['results']
    for article in articles:
        title=article['fields']['headline']
        summary=article['fields']['trailText']
        author=article['fields'].get('byline','No author listed')
        published_date=article['webPublicationDate']
        body_text=article['fields']['bodyText']

        c.execute(''' INSERT INTO articoleLiverpool (title, summary, author, published_date, body_text)
            VALUES (?, ?, ?, ?, ?)''',(title,summary,author,published_date,body_text))


    conn.commit()
    print(f"{len(articles)} articole salvate in baza de date")
else:
    print(f"Error:{response.status_code}")

def display_articles():
    c.execute('SELECT * FROM articoleLiverpool')
    rows=c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Title: {row[1]}")
        print(f"Summary: {row[2]}")
        print(f"Author: {row[3]}")
        print(f"Published Date: {row[4]}")
        print(f"Body Text: {row[5]}...")
        print("-" * 80)

display_articles()

conn.close()





