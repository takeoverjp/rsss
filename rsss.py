import feedparser
import openai
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

openai.api_key = os.environ["OPENAI_API_KEY"]

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

{article.title}
{article.link}
"""
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return f"""
{article.title}
{article.link}

{response.choices[0].text.strip()}
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
