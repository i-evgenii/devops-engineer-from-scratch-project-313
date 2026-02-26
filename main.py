from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/ping")
def pong():
    return jsonify({"result": "pong"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


def main():
    print("Hello from devops-engineer-from-scratch-project-313!")

    app.run(debug=True)


if __name__ == "__main__":
    main()
