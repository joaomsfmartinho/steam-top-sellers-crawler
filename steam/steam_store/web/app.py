from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    resp = requests.get(
        url='http://localhost:8080/crawl.json?start_requests=true&spider_name=best_sellers',
    ).json()

    return render_template('index.html', games=resp.get('items'))


if __name__ == "__main__":
    app.run(debug=True)
