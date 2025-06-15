from flask import Flask, request, jsonify
from deeppavlov import build_model

app = Flask(__name__)
model = build_model('squad_ru_bert', download=True, install=True)

with open('./context.txt', 'r', encoding='utf-8') as f:
    context = f.read()

@app.route('/answer', methods=['POST'])
def get_answer():
    data = request.json
    question = data.get('question')

    try:
        result = model([context], [question])
        answer = result[0][0]
        confidence = result[2][0]

        response = {
            'answer': answer,
            'confidence': confidence
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001) 