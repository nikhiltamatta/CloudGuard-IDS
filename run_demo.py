# opens Flask demo on port 8000 (same UI as Elastic Beanstalk)

from application import app

if __name__ == "__main__":
    print("demo -> http://localhost:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
