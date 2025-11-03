from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask backend running successfully!"

if __name__ == "__main__":
    app.run(debug=True, port=5003)

    # app.run(debug=True, port=5001)