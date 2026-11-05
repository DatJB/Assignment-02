import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models_service import manager
from diabetes_knowledge_graph import neo4j_graph, FPT_LONG_CHAU_MEDICATIONS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "diabetes_ready": manager.diabetes_pipeline is not None or os.path.exists(os.path.join(manager.models_dir, "diabetes_model.joblib")),
        "house_price_ready": manager.house_price_pipeline is not None or os.path.exists(os.path.join(manager.models_dir, "house_price_pipeline.joblib")),
        "ecommerce_ready": manager.ecommerce_pipeline is not None or os.path.exists(os.path.join(manager.models_dir, "ecommerce_interest_pipeline.joblib"))
    })

@app.route("/api/model-info", methods=["GET"])
def model_info():
    metadata = manager.get_metadata()
    return jsonify({
        "status": "success",
        "models": {
            "diabetes": {
                "name": "Random Forest Classifier (60 Trees Optimized)",
                "type": "Classification (Binary)",
                "target": "diabetes (0 = Âm tính, 1 = Dương tính)",
                "features": ["year", "age", "bmi", "hbA1c_level", "blood_glucose_level", "gender", "location", "smoking_history", "hypertension", "heart_disease"]
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

@app.route("/api/diabetes/knowledge-graph/full", methods=["GET"])
def diabetes_full_knowledge_graph():
    try:
        graph = neo4j_graph.get_full_graph()
        return jsonify({
            "status": "success",
            "data": graph,
            "neo4j_status": {
                "connected": neo4j_graph.is_connected,
                "uri": neo4j_graph.uri,
                "mode": "Live Neo4j Bolt Instance" if neo4j_graph.is_connected else "In-Memory Knowledge Graph Engine",
                "error": neo4j_graph.connection_error
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/diabetes/medications", methods=["GET"])
def diabetes_medications():
    return jsonify({
        "status": "success",
        "data": FPT_LONG_CHAU_MEDICATIONS,
        "pharmacy": {
            "name": "Nhà Thuốc FPT Long Châu",
            "website": "https://nhathuoclongchau.com.vn",
            "disclaimer": "Thuốc kê đơn (Rx). Chỉ sử dụng khi có chỉ định và hướng dẫn của bác sĩ chuyên khoa."
        }
    })

@app.route("/api/diabetes/neo4j-connect", methods=["POST"])
def diabetes_neo4j_connect():
    try:
        data = request.get_json(force=True) or {}
        uri = data.get("uri", neo4j_graph.uri)
        user = data.get("user", neo4j_graph.user)
        password = data.get("password", neo4j_graph.password)

        neo4j_graph.uri = uri
        neo4j_graph.user = user
        neo4j_graph.password = password
        neo4j_graph.init_neo4j_driver()

        return jsonify({
            "status": "success" if neo4j_graph.is_connected else "info",
            "connected": neo4j_graph.is_connected,
            "mode": "Live Neo4j Bolt Instance" if neo4j_graph.is_connected else "In-Memory Knowledge Graph Engine",
            "error": neo4j_graph.connection_error,
            "message": "Kết nối Neo4j thành công!" if neo4j_graph.is_connected else f"Không kết nối được Neo4j ({neo4j_graph.connection_error}). Đang dùng chế độ In-Memory Knowledge Graph."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
