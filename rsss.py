import feedparser
from openai import OpenAI
import os
import requests
import logging
import datetime
import pprint

def get_new_articles(feed_url):
    feed = feedparser.parse(feed_url)
    threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)

    new_articles = []
    for article in feed.entries:
        published_time = article.published_parsed if "published_parsed" in article else article.updated_parsed
        published_datetime = datetime.datetime(*published_time[:6], tzinfo=datetime.timezone.utc)
        if published_datetime > threshold:
            new_articles.append(article)

    return new_articles

def summarize_article(article):
    prompt = f"""
下記のフォーマットで与えられた情報を、以下の制約条件をもとに要約を出力してください。

入力のフォーマット:
・一行目はタイトル
・二行目は、要約したい記事のURL

制約条件:
・文章は簡潔にわかりやすく。
・箇条書きで3行で出力。
・要約した文章は日本語へ翻訳。
・最終的な結論を含めること。

期待する出力フォーマット:
1.
2.
3.

"""
    body = f"""
{article.title}
{article.link}
"""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": body,
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # pprint.pprint(response)
    return f"""
{article.title}
{article.link}

{response.choices[0].message.content.strip()}
"""

def send_message(message):
    line_notify_token = os.environ["LINE_NOTIFY_ACCESS_TOKEN"]
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{message}'}
    result = requests.post(line_notify_api, headers = headers, data = data)
    if result.status_code != 200:
        logging.error(f"request failed ({result}")

def main():
    rsss=[
          'https://hnrss.org/newest?points=100',
          'https://www.phoronix.com/rss.php',
          'http://lwn.net/headlines/newrss']
    for rss in rsss:
        logging.info(f"rss = {rss}")
        articles = get_new_articles(rss)
        for article in articles:
            summary = summarize_article(article)
            send_message(summary)

def lambda_handler(event, context):
    main()
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": ""
    }

if __name__ == "__main__":
    main()
