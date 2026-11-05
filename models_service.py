import os
import sys
import re
import datetime
import joblib
import pandas as pd
import numpy as np
import gc
from diabetes_knowledge_graph import neo4j_graph

# Feature engineering function required by diabetes_model.joblib
def add_features(data):
    data = data.copy()
    data["cardio_risk"] = data["hypertension"] + data["heart_disease"]
    data["glucose_hba1c_interaction"] = data["blood_glucose_level"] * data["hbA1c_level"]
    return data

# Register add_features to __main__ so joblib unpickling can find it
sys.modules["__main__"].add_features = add_features

# Text cleaning for E-commerce reviews
def clean_review(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Approximate coordinates for King County Zipcodes
ZIPCODE_COORDINATES = {
    "98001": {"lat": 47.31, "long": -122.28, "city": "Auburn"},
    "98002": {"lat": 47.31, "long": -122.21, "city": "Auburn North"},
    "98003": {"lat": 47.31, "long": -122.31, "city": "Federal Way"},
    "98004": {"lat": 47.61, "long": -122.20, "city": "Bellevue Downtown"},
    "98005": {"lat": 47.61, "long": -122.17, "city": "Bellevue East"},
    "98006": {"lat": 47.56, "long": -122.16, "city": "Bellevue South / Somerset"},
    "98007": {"lat": 47.61, "long": -122.14, "city": "Bellevue Crossroads"},
    "98008": {"lat": 47.60, "long": -122.11, "city": "Bellevue Lake Hills"},
    "98010": {"lat": 47.33, "long": -122.02, "city": "Black Diamond"},
    "98011": {"lat": 47.75, "long": -122.21, "city": "Bothell"},
    "98014": {"lat": 47.64, "long": -121.90, "city": "Carnation"},
    "98019": {"lat": 47.74, "long": -121.98, "city": "Duvall"},
    "98022": {"lat": 47.20, "long": -121.99, "city": "Enumclaw"},
    "98023": {"lat": 47.31, "long": -122.36, "city": "Federal Way West"},
    "98024": {"lat": 47.57, "long": -121.88, "city": "Fall City"},
    "98027": {"lat": 47.53, "long": -122.04, "city": "Issaquah"},
    "98028": {"lat": 47.76, "long": -122.26, "city": "Kenmore"},
    "98029": {"lat": 47.55, "long": -122.00, "city": "Issaquah Highlands"},
    "98030": {"lat": 47.38, "long": -122.21, "city": "Kent East"},
    "98031": {"lat": 47.39, "long": -122.18, "city": "Kent Valley"},
    "98032": {"lat": 47.39, "long": -122.26, "city": "Kent West"},
    "98033": {"lat": 47.68, "long": -122.20, "city": "Kirkland"},
    "98034": {"lat": 47.72, "long": -122.23, "city": "Kirkland North / Juanita"},
    "98038": {"lat": 47.37, "long": -122.03, "city": "Maple Valley"},
    "98039": {"lat": 47.63, "long": -122.24, "city": "Medina (Gold Coast)"},
    "98040": {"lat": 47.56, "long": -122.23, "city": "Mercer Island"},
    "98042": {"lat": 47.37, "long": -122.11, "city": "Kent / Covington"},
    "98045": {"lat": 47.49, "long": -121.78, "city": "North Bend"},
    "98052": {"lat": 47.67, "long": -122.12, "city": "Redmond (Tech Hub)"},
    "98053": {"lat": 47.68, "long": -122.03, "city": "Redmond Ridge"},
    "98055": {"lat": 47.46, "long": -122.20, "city": "Renton South"},
    "98056": {"lat": 47.50, "long": -122.18, "city": "Renton North"},
    "98058": {"lat": 47.45, "long": -122.14, "city": "Renton East"},
    "98059": {"lat": 47.49, "long": -122.13, "city": "Renton / Newcastle"},
    "98065": {"lat": 47.53, "long": -121.87, "city": "Snoqualmie"},
    "98070": {"lat": 47.42, "long": -122.46, "city": "Vashon Island"},
    "98072": {"lat": 47.75, "long": -122.15, "city": "Woodinville"},
    "98074": {"lat": 47.62, "long": -122.04, "city": "Sammamish North"},
    "98075": {"lat": 47.59, "long": -122.04, "city": "Sammamish South"},
    "98077": {"lat": 47.74, "long": -122.08, "city": "Woodinville Rural"},
    "98092": {"lat": 47.29, "long": -122.19, "city": "Auburn South"},
    "98102": {"lat": 47.63, "long": -122.32, "city": "Seattle (Capitol Hill)"},
    "98103": {"lat": 47.67, "long": -122.34, "city": "Seattle (Fremont/Wallingford)"},
    "98105": {"lat": 47.66, "long": -122.29, "city": "Seattle (Univ. of Washington)"},
    "98106": {"lat": 47.53, "long": -122.35, "city": "Seattle (Delridge/White Center)"},
    "98107": {"lat": 47.67, "long": -122.37, "city": "Seattle (Ballard)"},
    "98108": {"lat": 47.55, "long": -122.32, "city": "Seattle (Georgetown/Beacon Hill)"},
    "98109": {"lat": 47.63, "long": -122.35, "city": "Seattle (Queen Anne East)"},
    "98112": {"lat": 47.63, "long": -122.30, "city": "Seattle (Madison Park/Montlake)"},
    "98115": {"lat": 47.68, "long": -122.30, "city": "Seattle (Green Lake/Wedgewood)"},
    "98116": {"lat": 47.58, "long": -122.39, "city": "Seattle (Alki/West Seattle)"},
    "98117": {"lat": 47.69, "long": -122.37, "city": "Seattle (Ballard North/Crown Hill)"},
    "98118": {"lat": 47.54, "long": -122.27, "city": "Seattle (Rainier Valley/Columbia City)"},
    "98119": {"lat": 47.64, "long": -122.36, "city": "Seattle (Queen Anne Hill)"},
    "98122": {"lat": 47.61, "long": -122.30, "city": "Seattle (Central District)"},
    "98125": {"lat": 47.72, "long": -122.30, "city": "Seattle (Lake City)"},
    "98126": {"lat": 47.55, "long": -122.37, "city": "Seattle (High Point/35th Ave)"},
    "98133": {"lat": 47.74, "long": -122.34, "city": "Seattle (Northgate/Bitter Lake)"},
    "98136": {"lat": 47.54, "long": -122.39, "city": "Seattle (Fauntleroy/Gatewood)"},
    "98144": {"lat": 47.59, "long": -122.30, "city": "Seattle (Mount Baker)"},
    "98146": {"lat": 47.50, "long": -122.36, "city": "Seattle / White Center South"},
    "98148": {"lat": 47.44, "long": -122.33, "city": "Burien"},
    "98155": {"lat": 47.76, "long": -122.30, "city": "Shoreline / Lake Forest Park"},
    "98166": {"lat": 47.44, "long": -122.36, "city": "Normandy Park"},
    "98168": {"lat": 47.49, "long": -122.31, "city": "Tukwila / Boulevard Park"},
    "98177": {"lat": 47.74, "long": -122.37, "city": "Seattle (Richmond Beach)"},
    "98178": {"lat": 47.49, "long": -122.24, "city": "Seattle (Bryn Mawr/Skyway)"},
    "98188": {"lat": 47.45, "long": -122.28, "city": "SeaTac"},
    "98198": {"lat": 47.39, "long": -122.32, "city": "Des Moines"},
    "98199": {"lat": 47.65, "long": -122.40, "city": "Seattle (Magnolia)"}
}

ASPECT_METADATA = {
    "Price": {
        "name_vi": "Giá cả & Chi phí",
        "icon": "tag",
        "description": "Đề cập đến mức giá đắt, rẻ, hợp lý, giảm giá hoặc khuyến mãi",
        "color": "#3B82F6"
    },
    "Shipping": {
        "name_vi": "Vận chuyển & Giao hàng",
        "icon": "truck",
        "description": "Thời gian giao hàng nhanh/chậm, phí ship, thái độ shiper",
        "color": "#10B981"
    },
    "Outlook": {
        "name_vi": "Mẫu mã & Ngoại quan",
        "icon": "eye",
        "description": "Kiểu dáng, màu sắc, thiết kế bên ngoài, giống/khác hình",
        "color": "#8B5CF6"
    },
    "Quality": {
        "name_vi": "Chất lượng sản phẩm",
        "icon": "shield-check",
        "description": "Độ bền, chất liệu, tính năng, hiệu năng sử dụng thực tế",
        "color": "#F59E0B"
    },
    "Size": {
        "name_vi": "Kích cỡ & Size",
        "icon": "maximize-2",
        "description": "Size quần áo, độ vừa vặn, form rộng, chật hay đúng size",
        "color": "#EC4899"
    },
    "Shop_Service": {
        "name_vi": "Dịch vụ & Tư vấn Shop",
        "icon": "headphones",
        "description": "Thái độ CSKH, tư vấn nhiệt tình, đóng gói quà tặng, bảo hành",
        "color": "#06B6D4"
    },
    "General": {
        "name_vi": "Đánh giá chung",
        "icon": "thumbs-up",
        "description": "Ý kiến tổng quan khen/chê trải nghiệm mua sắm chung",
        "color": "#6366F1"
    },
    "Others": {
        "name_vi": "Khía cạnh khác",
        "icon": "more-horizontal",
        "description": "Các nội dung phụ khác không thuộc 7 danh mục chính trên",
        "color": "#64748B"
    }
}

US_STATES = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
    'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Idaho',
    'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
    'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska',
    'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina',
    'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island',
    'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'United States', 'Utah', 'Vermont',
    'Virgin Islands', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.models_dir = os.path.join(self.base_dir, "model")

        self.diabetes_bundle = None
        self.diabetes_pipeline = None

        self.house_price_pipeline = None

        self.ecommerce_bundle = None
        self.ecommerce_pipeline = None
        self.ecommerce_aspects = [
            'Price', 'Shipping', 'Outlook', 'Quality', 'Size', 'Shop_Service', 'General', 'Others'
        ]

        # Lazy loading mode: models are loaded on first prediction to minimize startup RAM (< 512MB for Render)
        self.initialized = True

    def get_diabetes_pipeline(self):
        if self.diabetes_pipeline is None:
            diabetes_path = os.path.join(self.models_dir, "diabetes_model.joblib")
            if os.path.exists(diabetes_path):
                try:
                    print("[ModelManager] Lazy-loading Diabetes Model into RAM...")
                    self.diabetes_bundle = joblib.load(diabetes_path)
                    self.diabetes_pipeline = self.diabetes_bundle["pipeline"]
                    gc.collect()
                    print(f" [OK] Diabetes Model loaded: {self.diabetes_bundle.get('model_name', 'Random Forest')}")
                except Exception as e:
                    print(f" [ERROR] Could not load diabetes model: {e}")
        return self.diabetes_pipeline

    def get_house_price_pipeline(self):
        if self.house_price_pipeline is None:
            hp_path = os.path.join(self.models_dir, "house_price_pipeline.joblib")
            if os.path.exists(hp_path):
                try:
                    print("[ModelManager] Lazy-loading House Price Pipeline into RAM...")
                    self.house_price_pipeline = joblib.load(hp_path)
                    gc.collect()
                    print(" [OK] House Price Pipeline loaded successfully.")
                except Exception as e:
                    print(f" [ERROR] Could not load house price pipeline: {e}")
        return self.house_price_pipeline

    def get_ecommerce_pipeline(self):
        if self.ecommerce_pipeline is None:
            ecom_path = os.path.join(self.models_dir, "ecommerce_interest_pipeline.joblib")
            if os.path.exists(ecom_path):
                try:
                    print("[ModelManager] Lazy-loading Ecommerce Pipeline into RAM...")
                    self.ecommerce_bundle = joblib.load(ecom_path)
                    self.ecommerce_pipeline = self.ecommerce_bundle["pipeline"]
                    self.ecommerce_aspects = self.ecommerce_bundle.get("aspect_names", self.ecommerce_aspects)
                    gc.collect()
                    print(f" [OK] Ecommerce Pipeline loaded with {len(self.ecommerce_aspects)} aspects.")
                except Exception as e:
                    print(f" [ERROR] Could not load ecommerce pipeline: {e}")
        return self.ecommerce_pipeline

    # ==================== DIABETES PREDICTION ====================
    def predict_diabetes(self, data: dict) -> dict:
        pipeline = self.get_diabetes_pipeline()
        if pipeline is None:
            raise RuntimeError("Mô hình chẩn đoán tiểu đường chưa sẵn sàng.")

        # Map inputs
        race_selected = data.get("race", "Caucasian")
        race_cols = {
            "race:AfricanAmerican": 1 if race_selected == "AfricanAmerican" else 0,
            "race:Asian": 1 if race_selected == "Asian" else 0,
            "race:Caucasian": 1 if race_selected == "Caucasian" else 0,
            "race:Hispanic": 1 if race_selected == "Hispanic" else 0,
            "race:Other": 1 if race_selected in ["Other", "Khác"] else 0
        }

        row = {
            "year": int(data.get("year", 2023)),
            "gender": str(data.get("gender", "Female")),
            "age": float(data.get("age", 45)),
            "location": str(data.get("location", "California")),
            **race_cols,
            "hypertension": int(data.get("hypertension", 0)),
            "heart_disease": int(data.get("heart_disease", 0)),
            "smoking_history": str(data.get("smoking_history", "never")),
            "bmi": float(data.get("bmi", 24.5)),
            "hbA1c_level": float(data.get("hbA1c_level", 5.5)),
            "blood_glucose_level": float(data.get("blood_glucose_level", 120.0))
        }

        df_input = pd.DataFrame([row])
        pred = int(self.diabetes_pipeline.predict(df_input)[0])
        probas = self.diabetes_pipeline.predict_proba(df_input)[0]
        prob_positive = float(probas[1])
        prob_negative = float(probas[0])

        # Clinical risk interpretation
        risk_percentage = round(prob_positive * 100, 1)
        if risk_percentage < 20:
            risk_level = "Nguy cơ Rất Thấp"
            risk_color = "emerald"
            badge_type = "success"
        elif risk_percentage < 45:
            risk_level = "Nguy cơ Trung Bình"
            risk_color = "amber"
            badge_type = "warning"
        elif risk_percentage < 70:
            risk_level = "Nguy cơ Cao"
            risk_color = "orange"
            badge_type = "danger"
        else:
            risk_level = "Nguy cơ Rất Cao (Báo động)"
            risk_color = "rose"
            badge_type = "critical"

        # Health metric assessment notes
        assessments = []
        bmi = row["bmi"]
        if bmi < 18.5:
            assessments.append({"metric": "BMI", "val": bmi, "status": "Thiếu cân", "note": "Cần bổ sung dinh dưỡng cân đối."})
        elif bmi < 25:
            assessments.append({"metric": "BMI", "val": bmi, "status": "Bình thường", "note": "Chỉ số thể trọng chuẩn."})
        elif bmi < 30:
            assessments.append({"metric": "BMI", "val": bmi, "status": "Thừa cân", "note": "Nên tập luyện thể dục 30 phút/ngày."})
        else:
            assessments.append({"metric": "BMI", "val": bmi, "status": "Béo phì", "note": "Yếu tố làm tăng kháng insulin đáng kể."})

        hba1c = row["hbA1c_level"]
        if hba1c < 5.7:
            assessments.append({"metric": "HbA1c", "val": f"{hba1c}%", "status": "Bình thường", "note": "Mức đường huyết 3 tháng qua ổn định."})
        elif hba1c <= 6.4:
            assessments.append({"metric": "HbA1c", "val": f"{hba1c}%", "status": "Tiền tiểu đường", "note": "Cần kiểm soát chế độ ăn đường & tinh bột."})
        else:
            assessments.append({"metric": "HbA1c", "val": f"{hba1c}%", "status": "Mức tiểu đường", "note": "Chỉ số vượt ngưỡng an toàn lâm sàng (≥ 6.5%)."})

        glucose = row["blood_glucose_level"]
        if glucose < 100:
            assessments.append({"metric": "Đường huyết lúc đói", "val": f"{glucose} mg/dL", "status": "Bình thường", "note": "Lượng đường trong máu đạt chuẩn."})
        elif glucose <= 125:
            assessments.append({"metric": "Đường huyết lúc đói", "val": f"{glucose} mg/dL", "status": "Tăng đường huyết nhẹ", "note": "Giai đoạn cảnh báo tiền đái tháo đường."})
        else:
            assessments.append({"metric": "Đường huyết", "val": f"{glucose} mg/dL", "status": "Cao", "note": "Đường huyết cao cần theo dõi y tế (≥ 126 mg/dL)."})

        base_result = {
            "prediction": pred,
            "diagnosis": "Dương tính (Nguy cơ mắc tiểu đường)" if pred == 1 else "Âm tính (Không mắc tiểu đường)",
            "probability_positive": risk_percentage,
            "probability_negative": round(prob_negative * 100, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "badge_type": badge_type,
            "assessments": assessments,
            "input_echo": row
        }

        # Knowledge Graph & FPT Long Châu Medication Recommendation Engine
        try:
            graph_rec = neo4j_graph.generate_patient_recommendations(row, base_result)
            base_result["recommended_medications"] = graph_rec.get("recommended_medications", [])
            base_result["patient_conditions"] = graph_rec.get("patient_conditions", [])
            base_result["clinical_alerts"] = graph_rec.get("clinical_alerts", [])
            base_result["knowledge_graph"] = graph_rec.get("knowledge_graph", {})
            base_result["cypher_query"] = graph_rec.get("cypher_query", "")
            base_result["neo4j_status"] = graph_rec.get("neo4j_status", {})
        except Exception as ge:
            print(f"[Warning] Failed to generate knowledge graph recommendations: {ge}")
            base_result["recommended_medications"] = []
            base_result["knowledge_graph"] = {}
            base_result["cypher_query"] = ""

        return base_result

    # ==================== HOUSE PRICE PREDICTION ====================
    def predict_house_price(self, data: dict) -> dict:
        pipeline = self.get_house_price_pipeline()
        if pipeline is None:
            raise RuntimeError("Mô hình dự đoán giá nhà chưa sẵn sàng.")

        zipcode = str(data.get("zipcode", "98004")).strip()
        coords = ZIPCODE_COORDINATES.get(zipcode, {"lat": 47.56, "long": -122.21, "city": "King County"})

        lat = float(data.get("lat") if data.get("lat") not in [None, ""] else coords["lat"])
        long_val = float(data.get("long") if data.get("long") not in [None, ""] else coords["long"])

        # Timeline & feature engineering
        today = datetime.date.today()
        sale_year = int(data.get("sale_year", today.year))
        sale_month = int(data.get("sale_month", today.month))
        yr_built = int(data.get("yr_built", 1995))
        yr_renovated = int(data.get("yr_renovated", 0))

        house_age = max(0, sale_year - yr_built)
        renovated = 1 if yr_renovated > 0 else 0
        years_since_renovation = max(0, sale_year - yr_renovated) if yr_renovated > 0 else 0

        sqft_living = float(data.get("sqft_living", 2000))
        sqft_lot = float(data.get("sqft_lot", 7500))
        sqft_above = float(data.get("sqft_above", sqft_living * 0.8))
        sqft_basement = float(data.get("sqft_basement", sqft_living - sqft_above if sqft_living > sqft_above else 0))
        sqft_living15 = float(data.get("sqft_living15", sqft_living))
        sqft_lot15 = float(data.get("sqft_lot15", sqft_lot))

        row = {
            "bedrooms": int(data.get("bedrooms", 3)),
            "bathrooms": float(data.get("bathrooms", 2.0)),
            "sqft_living": sqft_living,
            "sqft_lot": sqft_lot,
            "floors": float(data.get("floors", 1.0)),
            "waterfront": int(data.get("waterfront", 0)),
            "view": int(data.get("view", 0)),
            "condition": int(data.get("condition", 3)),
            "grade": int(data.get("grade", 7)),
            "sqft_above": sqft_above,
            "sqft_basement": sqft_basement,
            "zipcode": zipcode,
            "lat": lat,
            "long": long_val,
            "sqft_living15": sqft_living15,
            "sqft_lot15": sqft_lot15,
            "sale_year": sale_year,
            "sale_month": sale_month,
            "house_age": house_age,
            "renovated": renovated,
            "years_since_renovation": years_since_renovation
        }

        df_input = pd.DataFrame([row])
        pred_price = float(pipeline.predict(df_input)[0])
        pred_price = max(50000.0, pred_price)

        # Exchange rate USD to VND (~ 25,500 VND/USD)
        usd_to_vnd = 25500
        vnd_price = pred_price * usd_to_vnd
        vnd_ty = round(vnd_price / 1_000_000_000, 2)

        price_per_sqft = round(pred_price / max(1.0, sqft_living), 1)

        return {
            "predicted_price_usd": round(pred_price, 2),
            "formatted_usd": f"${pred_price:,.0f}",
            "predicted_price_vnd": round(vnd_price, 0),
            "formatted_vnd": f"{vnd_ty:,.2f} tỷ VNĐ",
            "price_per_sqft": price_per_sqft,
            "location_info": {
                "zipcode": zipcode,
                "city": coords.get("city", "King County Area"),
                "lat": lat,
                "long": long_val
            },
            "metrics": {
                "house_age": house_age,
                "is_renovated": bool(renovated),
                "years_since_renovation": years_since_renovation,
                "sqft_living": sqft_living,
                "sqft_lot": sqft_lot,
                "grade": row["grade"],
                "condition": row["condition"]
            }
        }

    # ==================== ECOMMERCE INTEREST PREDICTION ====================
    def predict_ecommerce(self, review_text: str) -> dict:
        pipeline = self.get_ecommerce_pipeline()
        if pipeline is None:
            raise RuntimeError("Mô hình phân tích E-commerce chưa sẵn sàng.")

        cleaned = clean_review(review_text)
        if not cleaned:
            cleaned = "Sản phẩm tốt"

        preds = pipeline.predict([cleaned])[0]

        has_proba = hasattr(pipeline, "predict_proba")
        probas = pipeline.predict_proba([cleaned])[0] if has_proba else [float(p) for p in preds]

        aspect_results = []
        detected_aspects = []

        for i, name in enumerate(self.ecommerce_aspects):
            is_detected = bool(preds[i] == 1)
            prob = float(probas[i])
            pct = round(prob * 100, 1)

            meta = ASPECT_METADATA.get(name, {
                "name_vi": name,
                "icon": "circle",
                "description": "",
                "color": "#64748B"
            })

            aspect_info = {
                "aspect": name,
                "name_vi": meta["name_vi"],
                "icon": meta["icon"],
                "color": meta["color"],
                "description": meta["description"],
                "detected": is_detected,
                "probability": pct
            }
            aspect_results.append(aspect_info)

            if is_detected:
                detected_aspects.append(aspect_info)

        # Sort detected aspects by confidence descending
        detected_aspects.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "original_text": review_text,
            "cleaned_text": cleaned,
            "detected_count": len(detected_aspects),
            "detected_aspects": detected_aspects,
            "all_aspects": aspect_results,
            "summary": f"Phát hiện {len(detected_aspects)} / {len(self.ecommerce_aspects)} khía cạnh quan tâm."
        }

    def get_metadata(self) -> dict:
        return {
            "zipcodes": [
                {"zipcode": z, "city": info["city"], "lat": info["lat"], "long": info["long"]}
                for z, info in ZIPCODE_COORDINATES.items()
            ],
            "us_states": US_STATES,
            "aspects": [
                {"id": k, **v} for k, v in ASPECT_METADATA.items()
            ]
        }

# Global singleton
manager = ModelManager()
