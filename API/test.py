from flask import Flask, request

app = Flask(__name__)

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    # Process the received data
    processed_data = {"message": "Data processed successfully"}
    print(data)
    return processed_data

if __name__ == '__main__':
    app.run(debug=True, port=5000)






