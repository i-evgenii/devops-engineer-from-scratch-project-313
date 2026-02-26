from flask import Flask

app = Flask(__name__)


@app.route("/ping")
def pong():
    return "pong"


def main():
    print("Hello from devops-engineer-from-scratch-project-313!")

    app.run(debug=True)


if __name__ == "__main__":
    main()
