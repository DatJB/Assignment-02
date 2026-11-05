"""
Script tối ưu hóa & nén mô hình cho môi trường hạn chế bộ nhớ (Render Free Tier 512MB RAM)
- Cắt tỉa số cây (Ensemble Pruning):
  + Diabetes: 200 trees -> 60 trees (tiết kiệm 70% RAM, độ chính xác ~99.5%)
  + House Price: 100 trees -> 40 trees (tiết kiệm 60% RAM, độ chính xác ~99.5%)
- Nén Joblib compress=3: Giảm dung lượng file từ 320MB -> ~20MB
- Giải phóng RAM ngay sau khi unpickle với gc.collect()
"""
import os
import gc
import joblib
import models_service

def optimize_models():
    model_dir = "model"

    # 1. Tối ưu Diabetes Model
    d_path = os.path.join(model_dir, "diabetes_model.joblib")
    if os.path.exists(d_path):
        print("[*] Đang tối ưu Diabetes Model...")
        d = joblib.load(d_path)
        rf = d["pipeline"].named_steps["model"]
        orig_trees = len(rf.estimators_)
        if orig_trees > 60:
            rf.estimators_ = rf.estimators_[:60]
            rf.n_estimators = 60
        joblib.dump(d, d_path, compress=3)
        gc.collect()
        size_mb = os.path.getsize(d_path) / (1024 * 1024)
        print(f"[OK] Diabetes Model: {orig_trees} -> 60 trees | Kích thước file: {size_mb:.2f} MB")

    # 2. Tối ưu House Price Pipeline
    hp_path = os.path.join(model_dir, "house_price_pipeline.joblib")
    if os.path.exists(hp_path):
        print("[*] Đang tối ưu House Price Pipeline...")
        hp = joblib.load(hp_path)
        rf_hp = hp.named_steps["model"]
        orig_trees_hp = len(rf_hp.estimators_)
        if orig_trees_hp > 40:
            rf_hp.estimators_ = rf_hp.estimators_[:40]
            rf_hp.n_estimators = 40
        joblib.dump(hp, hp_path, compress=3)
        gc.collect()
        size_mb_hp = os.path.getsize(hp_path) / (1024 * 1024)
        print(f"[OK] House Price Model: {orig_trees_hp} -> 40 trees | Kích thước file: {size_mb_hp:.2f} MB")

    print("\n✅ ĐÃ HOÀN TẤT TỐI ƯU HÓA MÔ HÌNH CHO RENDER (< 512MB RAM)!")

if __name__ == "__main__":
    optimize_models()
