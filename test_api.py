import json
from app import app

def run_tests():
    client = app.test_client()
    print("==================== STARTING AUTOMATED API TESTS ====================")

    # 1. Test Health
    res = client.get("/api/health")
    print(f"[1] /api/health -> Status: {res.status_code}")
    assert res.status_code == 200, f"Health check failed: {res.data}"
    health_data = res.get_json()
    print(f"    Data: {health_data}")
    assert health_data["diabetes_ready"] == True
    assert health_data["house_price_ready"] == True
    assert health_data["ecommerce_ready"] == True

    # 2. Test Model Info
    res = client.get("/api/model-info")
    print(f"[2] /api/model-info -> Status: {res.status_code}")
    assert res.status_code == 200
    info = res.get_json()
    assert "models" in info
    assert "metadata" in info
    assert len(info["metadata"]["zipcodes"]) == 70
    print(f"    Zipcodes count: {len(info['metadata']['zipcodes'])}, Aspects count: {len(info['metadata']['aspects'])}")

    # 3. Test Diabetes Prediction - Positive Case
    diabetes_payload = {
        "age": 60,
        "gender": "Male",
        "race": "Caucasian",
        "location": "California",
        "bmi": 32.5,
        "smoking_history": "former",
        "hypertension": 1,
        "heart_disease": 1,
        "hbA1c_level": 7.5,
        "blood_glucose_level": 190.0,
        "year": 2023
    }
    res = client.post("/api/predict/diabetes", json=diabetes_payload)
    print(f"[3] /api/predict/diabetes -> Status: {res.status_code}")
    assert res.status_code == 200
    d_res = res.get_json()
    assert d_res["status"] == "success"
    print(f"    Diagnosis: {d_res['data']['diagnosis']}")
    print(f"    Risk level: {d_res['data']['risk_level']} ({d_res['data']['probability_positive']}%)")
    assert d_res['data']['prediction'] in [0, 1]

    # 4. Test House Price Prediction
    house_payload = {
        "bedrooms": 3,
        "bathrooms": 2.5,
        "floors": 2.0,
        "sqft_living": 2500,
        "sqft_lot": 8000,
        "grade": 8,
        "condition": 4,
        "waterfront": 0,
        "view": 1,
        "zipcode": "98004",
        "yr_built": 2005,
        "yr_renovated": 0,
        "sqft_basement": 500,
        "lat": 47.61,
        "long": -122.20
    }
    res = client.post("/api/predict/house-price", json=house_payload)
    print(f"[4] /api/predict/house-price -> Status: {res.status_code}")
    assert res.status_code == 200
    hp_res = res.get_json()
    assert hp_res["status"] == "success"
    print(f"    Predicted USD: {hp_res['data']['formatted_usd']}")
    print(f"    Predicted VNĐ: {hp_res['data']['formatted_vnd']}")
    assert hp_res['data']['predicted_price_usd'] > 0

    # 5. Test Ecommerce Review Aspect Prediction
    review_payload = {
        "review_text": "Giao hàng rất nhanh chóng, đóng gói cẩn thận. Áo chất vải tốt nhưng giá hơi đắt."
    }
    res = client.post("/api/predict/ecommerce", json=review_payload)
    print(f"[5] /api/predict/ecommerce -> Status: {res.status_code}")
    assert res.status_code == 200
    ecom_res = res.get_json()
    assert ecom_res["status"] == "success"
    detected = [a["name_vi"] for a in ecom_res["data"]["detected_aspects"]]
    print(f"    Detected Aspects ({ecom_res['data']['detected_count']}): {detected}")
    assert len(ecom_res["data"]["all_aspects"]) == 8

    print("==================== ALL API TESTS PASSED SUCCESSFULLY! ====================")

if __name__ == "__main__":
    run_tests()
