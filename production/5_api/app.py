from flask import Flask, request, redirect, url_for, flash, jsonify
import pickle


app = Flask(__name__)


@app.route('/api/', methods=['POST'])
def calculate_discount():
    data = request.get_json()
    brand_name = data['brand']
    discount = model[brand_name]

    return jsonify({'discount_pct': discount})

if __name__ == '__main__':
    modelfile = '../models/heuristic_model.p'
    model = pickle.load(open(modelfile, 'rb'))
    app.run(host='0.0.0.0')
