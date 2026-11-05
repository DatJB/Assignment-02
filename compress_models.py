"""
Script tối ưu hóa & nén dung lượng 3 mô hình Machine Learning (.joblib)
Giúp giảm kích thước từ ~320MB xuống dưới ~65MB để push trực tiếp lên GitHub và deploy Render.
"""
import os
import joblib
import models_service

def compress():
    model_dir = "model"
    files = [
        ("diabetes_model.joblib", "diabetes_model_compressed.joblib"),
        ("house_price_pipeline.joblib", "house_price_compressed.joblib")
    ]

    for orig_name, comp_name in files:
        orig_path = os.path.join(model_dir, orig_name)
        comp_path = os.path.join(model_dir, comp_name)
        if not os.path.exists(orig_path):
            continue

        orig_size_mb = os.path.getsize(orig_path) / (1024 * 1024)
        print(f"[*] Đang nén {orig_name} ({orig_size_mb:.2f} MB)...")
        obj = joblib.load(orig_path)
        joblib.dump(obj, comp_path, compress=3)
        comp_size_mb = os.path.getsize(comp_path) / (1024 * 1024)
        print(f"[OK] Đã nén thành công {comp_name}: {comp_size_mb:.2f} MB")

        # Thay thế file gốc bằng file đã nén
        os.replace(comp_path, orig_path)
        print(f"[REPLACED] {orig_name} hiện có dung lượng: {os.path.getsize(orig_path)/(1024*1024):.2f} MB (< 100MB Git limit)\n")

if __name__ == "__main__":
    compress()

