import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models_service import manager

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "diabetes_ready": manager.diabetes_pipeline is not None,
        "house_price_ready": manager.house_price_pipeline is not None,
        "ecommerce_ready": manager.ecommerce_pipeline is not None
    })

@app.route("/api/model-info", methods=["GET"])
def model_info():
    metadata = manager.get_metadata()
    return jsonify({
        "status": "success",
        "models": {
            "diabetes": {
                "name": manager.diabetes_bundle.get("model_name", "Random Forest Classifier") if manager.diabetes_bundle else "Random Forest",
                "type": "Classification (Binary)",
                "target": "diabetes (0 = Âm tính, 1 = Dương tính)",
                "features": manager.diabetes_bundle.get("input_features", []) if manager.diabetes_bundle else []
            },
            "house_price": {
                "name": "Random Forest Regressor (King County Pipeline)",
                "type": "Regression",
                "target": "price (USD)",
                "features_count": 21
            },
            "ecommerce": {
                "name": "SGD Text Classifier (TF-IDF + OneVsRest)",
                "type": "Multi-label Text Classification",
                "target": "8 Aspects (1 = Đề cập, 0 = Không đề cập)",
                "aspects": manager.ecommerce_aspects
            }
        },
        "metadata": metadata
    })

@app.route("/api/predict/diabetes", methods=["POST"])
def predict_diabetes():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Dữ liệu yêu cầu không hợp lệ hoặc rỗng."}), 400
        
        result = manager.predict_diabetes(data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predict/house-price", methods=["POST"])
def predict_house_price():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Dữ liệu yêu cầu không hợp lệ hoặc rỗng."}), 400
        
        result = manager.predict_house_price(data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predict/ecommerce", methods=["POST"])
def predict_ecommerce():
    try:
        data = request.get_json(force=True)
        if not data or "review_text" not in data:
            return jsonify({"error": "Thiếu trường 'review_text'."}), 400
        
        review_text = data.get("review_text", "")
        if not review_text.strip():
            return jsonify({"error": "Nội dung đánh giá không được để trống."}), 400

        result = manager.predict_ecommerce(review_text)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"==================================================")
    print(f"🚀 AI Multi-Model Dashboard Server running at:")
    print(f"👉 http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
