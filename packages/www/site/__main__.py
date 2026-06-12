from flask import Flask, jsonify, render_template_string

# 1. Initialize a standard Flask app instance
app = Flask(__name__)

# 2. Write your standard Flask routes normally
@app.route("/")
def home():
    return "<h1>Welcome to my Serverless Flask Home Page</h1>"

@app.route("/api/data")
def get_data():
    return jsonify({"status": "success", "framework": "Flask on DO Functions"})

@app.route("/user/<name>")
def hello_user(name):
    return render_template_string("<h1>Hello, {{ name }}!</h1>", name=name)


# 3. The DigitalOcean Entry Bridge
def main(args):
    """
    DigitalOcean invokes this function on every web hit.
    We capture their cloud payload and route it through Flask in-memory.
    """
    # Extract path and method safely from DO's system wrapper
    # Defaulting to root if no path parameters are passed
    path = args.get("__ow_path", "/")
    method = args.get("__ow_method", "GET")

    # Create an in-memory execution context mirroring an actual web request
    with app.test_request_context(path=path, method=method):
        try:
            # Let Flask dispatch the URL matching internally
            rv = app.preprocess_request()
            if rv is None:
                rv = app.dispatch_request()
            response = app.make_response(rv)
            response = app.process_response(response)

            # Format response back to DigitalOcean's structural layout
            return {
                "headers": dict(response.headers),
                "statusCode": response.status_code,
                "body": response.get_data(as_text=True)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": f"Internal Serverless Flask Error: {str(e)}"
            }
