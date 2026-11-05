# AI Multi-Model Analytics Hub

Ứng dụng web tích hợp 3 mô hình Machine Learning:
- Chẩn đoán nguy cơ Bệnh Tiểu Đường (Diabetes Classification)
- Dự đoán Giá Nhà King County (House Price Regression)
- Phân tích Mối Quan Tâm Khách Hàng E-commerce (Aspect-Based Sentiment & Interest NLP)

---

## 1. Tổng quan 3 Mô hình

### Chẩn đoán Bệnh Tiểu Đường (diabetes_model.joblib)
- Thuật toán: Random Forest Classifier (200 trees, class_weight='balanced').
- Đặc trưng phái sinh: `cardio_risk = hypertension + heart_disease`, `glucose_hba1c_interaction = blood_glucose_level * hbA1c_level`.
- Đầu vào: Tuổi, giới tính, chủng tộc, vị trí, BMI, hút thuốc, tiền sử tim mạch, huyết áp, mức HbA1c, mức đường huyết.
- Đầu ra: Kết luận nguy cơ (0: Âm tính, 1: Dương tính), xác suất (%) và đánh giá chỉ số sức khỏe.

### Dự đoán Giá Nhà King County (house_price_pipeline.joblib)
- Thuật toán: Random Forest Regressor Pipeline.
- Đặc trưng phái sinh: `house_age`, `renovated`, `years_since_renovation`, `sale_year`, `sale_month`.
- Mã hóa: One-Hot 70 mã bưu chính (Zipcode) vùng King County kèm tọa độ địa lý (lat, long).
- Đầu vào: Số phòng ngủ/tắm, diện tích nhà (sqft), diện tích đất, số tầng, view, condition, grade, waterfront, năm xây dựng, năm cải tạo.
- Đầu ra: Giá dự đoán theo USD và quy đổi VNĐ, đơn giá trên mỗi sqft và m².

### Phân tích Đánh giá E-commerce (ecommerce_interest_pipeline.joblib)
- Thuật toán: OneVsRestClassifier kết hợp SGDClassifier (log_loss, TF-IDF n-gram 1-2).
- Đầu vào: Nội dung đánh giá của khách hàng (tiếng Việt).
- Đầu ra: Nhận diện 8 khía cạnh quan tâm và điểm xác suất: Price, Shipping, Outlook, Quality, Size, Shop_Service, General, Others.

---

## 2. Cấu trúc Thư mục

```text
Assignment 02/
├── model/                                  # 3 tệp mô hình Machine Learning (.joblib)
├── templates/
│   └── index.html                         # Giao diện web Dashboard
├── static/
│   ├── css/style.css                      # Giao diện Glassmorphism (Dark/Light mode)
│   └── js/app.js                          # Xử lý tương tác, Chart.js & gọi API
├── models_service.py                      # Module nạp model, tiền xử lý và suy luận
├── app.py                                 # Server Flask cung cấp REST API & giao diện
├── run.py                                 # Script khởi chạy và tự động mở trình duyệt
├── test_api.py                            # Script kiểm thử tự động toàn bộ API
└── README.md                              # Tài liệu hướng dẫn
```

---

## 3. Cài đặt và Khởi chạy

### Cài đặt thư viện
```powershell
pip install flask flask-cors scikit-learn pandas numpy joblib
```

### Khởi chạy ứng dụng
Chạy script tự động mở trình duyệt:
```powershell
python run.py
```
Hoặc khởi chạy server Flask trực tiếp:
```powershell
python app.py
```
Truy cập ứng dụng tại: `http://127.0.0.1:5000`

### Chạy kiểm thử tự động
```powershell
python test_api.py
```

---

## 4. Tài liệu REST API

| Phương thức | Đường dẫn | Chức năng |
| :--- | :--- | :--- |
| POST | `/api/predict/diabetes` | Dự đoán nguy cơ đái tháo đường, gợi ý thuốc FPT Long Châu & Knowledge Graph |
| POST | `/api/predict/house-price` | Ước tính giá nhà King County theo USD và VNĐ |
| POST | `/api/predict/ecommerce` | Phân loại 8 khía cạnh quan tâm từ văn bản đánh giá |
| GET | `/api/diabetes/medications` | Danh mục 9 thuốc & dinh dưỡng đái tháo đường chính hãng FPT Long Châu |
| GET | `/api/diabetes/knowledge-graph/full` | Trích xuất toàn bộ Đồ thị Tri thức Bệnh học - Dược lý - Long Châu |
| POST | `/api/diabetes/neo4j-connect` | Cấu hình & thử kết nối trực tiếp đến Neo4j Database |
| GET | `/api/model-info` | Lấy siêu dữ liệu cấu hình (danh mục Zipcode, Aspects) |
| GET | `/api/health` | Kiểm tra trạng thái sẵn sàng của 3 mô hình |

### Ví dụ Request / Response

**Chẩn đoán Tiểu Đường:**
- POST `/api/predict/diabetes`
```json
{
  "age": 55,
  "gender": "Female",
  "race": "Caucasian",
  "location": "California",
  "bmi": 32.5,
  "smoking_history": "former",
  "hypertension": 1,
  "heart_disease": 0,
  "hbA1c_level": 6.8,
  "blood_glucose_level": 180.0,
  "year": 2023
}
```

**Dự đoán Giá Nhà:**
- POST `/api/predict/house-price`
```json
{
  "bedrooms": 3,
  "bathrooms": 2.0,
  "floors": 1.5,
  "sqft_living": 2000,
  "sqft_lot": 7500,
  "grade": 8,
  "condition": 4,
  "waterfront": 0,
  "view": 1,
  "zipcode": "98004",
  "yr_built": 2005,
  "yr_renovated": 0,
  "sqft_basement": 400
}
```

**Phân tích E-commerce:**
- POST `/api/predict/ecommerce`
```json
{
  "review_text": "Giao hàng rất nhanh, đóng gói cẩn thận, sản phẩm chất lượng tốt giá hợp lý"
}
```
