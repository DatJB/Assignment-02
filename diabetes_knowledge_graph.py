"""
Neo4j Diabetes Knowledge Graph & FPT Long Chau Medication Recommendation Engine
Tích hợp Knowledge Graph (Đồ thị tri thức) bệnh học Tiểu đường và gợi ý thuốc tham khảo FPT Long Châu.
Hỗ trợ kết nối Neo4j trực tiếp (Bolt) và fallback In-Memory Graph Engine tự động.
"""

import os
import json
from typing import Dict, List, Any, Optional

try:
    from neo4j import GraphDatabase, basic_auth
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


# ==============================================================================
# FPT LONG CHÂU DIABETES DRUG CATALOG
# Danh mục thuốc & sản phẩm kiểm soát đái tháo đường chính hãng tại FPT Long Châu
# ==============================================================================
FPT_LONG_CHAU_MEDICATIONS = [
    {
        "id": "med_glucophage_500",
        "name": "Glucophage 500mg (Merck)",
        "brand": "Glucophage",
        "manufacturer": "Merck Santé (Pháp)",
        "active_ingredient": "Metformin hydrochloride 500mg",
        "drug_class": "Biguanide",
        "drug_class_id": "class_biguanide",
        "price_vnd": 58000,
        "price_text": "58.000 đ / Hộp 50 viên",
        "packaging": "Hộp 5 vỉ x 10 viên nén",
        "prescription_required": True,
        "mechanism": "Ức chế tân tạo glucose tại gan, giảm hấp thu glucose ở ruột non, tăng nhạy cảm insulin ở tế bào cơ ngoại vi.",
        "target_organ": "Gan & Mô cơ",
        "target_organ_id": "organ_liver",
        "target_organ_text": "Gan & Mô cơ",
        "indications": "Lựa chọn đầu tay cho ĐTĐ Tuýp 2, đặc biệt thích hợp cho người thừa cân, béo phì (BMI ≥ 25).",
        "cautions": "Theo dõi độ lọc cầu thận (eGFR). Chống chỉ định khi suy thận nặng (eGFR < 30 mL/phút) hoặc nhiễm toan lactic.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Glucophage+500mg",
        "badge": "Lựa chọn đầu tay (First-line)",
        "badge_color": "emerald"
    },
    {
        "id": "med_glucophage_xr_750",
        "name": "Glucophage XR 750mg (Merck)",
        "brand": "Glucophage XR",
        "manufacturer": "Merck Santé (Pháp)",
        "active_ingredient": "Metformin hydrochloride 750mg (Phóng thích kéo dài)",
        "drug_class": "Biguanide (Giải phóng kéo dài)",
        "drug_class_id": "class_biguanide",
        "price_vnd": 135000,
        "price_text": "135.000 đ / Hộp 30 viên",
        "packaging": "Hộp 3 vỉ x 10 viên phóng thích kéo dài",
        "prescription_required": True,
        "mechanism": "Công nghệ Gel-matrix giúp Metformin phóng thích từ từ trong 24 giờ, giảm kích ứng dạ dày - ruột.",
        "target_organ": "Gan & Đường tiêu hóa",
        "target_organ_id": "organ_liver",
        "target_organ_text": "Gan & Hệ tiêu hóa",
        "indications": "Bệnh nhân ĐTĐ Tuýp 2 nhạy cảm với tác dụng phụ tiêu hóa của Metformin thông thường; uống 1 lần/ngày vào bữa tối.",
        "cautions": "Không được bẻ đôi hoặc nhai nát viên thuốc; uống nguyên viên với nước trong bữa ăn tối.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Glucophage+XR+750mg",
        "badge": "Êm dịu tiêu hóa",
        "badge_color": "blue"
    },
    {
        "id": "med_forxiga_10",
        "name": "Forxiga 10mg (AstraZeneca)",
        "brand": "Forxiga",
        "manufacturer": "AstraZeneca (Anh / Thụy Điển)",
        "active_ingredient": "Dapagliflozin 10mg",
        "drug_class": "Ức chế SGLT-2 (Thải trừ đường qua thận)",
        "drug_class_id": "class_sglt2",
        "price_vnd": 575000,
        "price_text": "575.000 đ / Hộp 28 viên",
        "packaging": "Hộp 2 vỉ x 14 viên nén bao phim",
        "prescription_required": True,
        "mechanism": "Ức chế kênh SGLT-2 tại ống lượn gần ở thận, ngăn tái hấp thu glucose và thải trừ khoảng 70g đường/ngày qua nước tiểu.",
        "target_organ": "Thận & Hệ tim mạch",
        "target_organ_id": "organ_kidney",
        "target_organ_text": "Thận & Tim mạch",
        "indications": "ĐTĐ Tuýp 2, ĐẶC BIỆT KHUYẾN CÁO cho bệnh nhân có kèm TĂNG HUYẾT ÁP, TIỀN SỬ TIM MẠCH, SUY TIM hoặc bệnh thận mạn.",
        "cautions": "Cần uống đủ nước trong ngày. Vệ sinh bộ phận sinh dục sạch sẽ để tránh nhiễm nấm đường niệu/sinh dục.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Forxiga+10mg",
        "badge": "Bảo vệ Tim Mạch & Thận (ADA 2024)",
        "badge_color": "rose"
    },
    {
        "id": "med_jardiance_10",
        "name": "Jardiance 10mg (Boehringer Ingelheim)",
        "brand": "Jardiance",
        "manufacturer": "Boehringer Ingelheim (Đức)",
        "active_ingredient": "Empagliflozin 10mg",
        "drug_class": "Ức chế SGLT-2",
        "drug_class_id": "class_sglt2",
        "price_vnd": 630000,
        "price_text": "630.000 đ / Hộp 30 viên",
        "packaging": "Hộp 3 vỉ x 10 viên nén bao phim",
        "prescription_required": True,
        "mechanism": "Tăng thải glucose và natri qua nước tiểu, hạ áp thẩm thấu nhẹ, bảo vệ mạch vành và làm chậm suy thận.",
        "target_organ": "Thận & Hệ tuần hoàn",
        "target_organ_id": "organ_kidney",
        "target_organ_text": "Thận & Tuần hoàn",
        "indications": "Bệnh nhân ĐTĐ Tuýp 2 có nguy cơ biến cố tim mạch cao, huyết áp khó kiểm soát, thừa cân.",
        "cautions": "Theo dõi huyết áp định kỳ vì thuốc có tác dụng lợi tiểu nhẹ; uống thuốc vào buổi sáng.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Jardiance+10mg",
        "badge": "Giảm biến cố tim mạch",
        "badge_color": "rose"
    },
    {
        "id": "med_januvia_100",
        "name": "Januvia 100mg (MSD)",
        "brand": "Januvia",
        "manufacturer": "Merck Sharp & Dohme (Mỹ)",
        "active_ingredient": "Sitagliptin phosphate 100mg",
        "drug_class": "Ức chế DPP-4 (Incretin enhancer)",
        "drug_class_id": "class_dpp4",
        "price_vnd": 520000,
        "price_text": "520.000 đ / Hộp 28 viên",
        "packaging": "Hộp 2 vỉ x 14 viên nén bao phim",
        "prescription_required": True,
        "mechanism": "Ức chế enzym DPP-4, kéo dài thời gian bán hủy của hormon incretin (GLP-1/GIP), kích thích tụy tiết insulin khi glucose tăng.",
        "target_organ": "Tuyến tụy",
        "target_organ_id": "organ_pancreas",
        "target_organ_text": "Tuyến tụy",
        "indications": "Đơn trị liệu hoặc phối hợp Metformin khi bệnh nhân cần hạ HbA1c mà không muốn nguy cơ hạ đường huyết quá mức hay tăng cân.",
        "cautions": "Thận trọng ở bệnh nhân có tiền sử viêm tụy cấp; điều chỉnh liều nếu suy thận trung bình - nặng.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Januvia+100mg",
        "badge": "An toàn - Không hạ đường quá mức",
        "badge_color": "purple"
    },
    {
        "id": "med_janumet_50_850",
        "name": "Janumet 50mg/850mg (MSD)",
        "brand": "Janumet",
        "manufacturer": "Merck Sharp & Dohme (Mỹ)",
        "active_ingredient": "Sitagliptin 50mg + Metformin HCl 850mg",
        "drug_class": "Thuốc phối hợp kép (DPP-4 + Biguanide)",
        "drug_class_id": "class_combination",
        "price_vnd": 590000,
        "price_text": "590.000 đ / Hộp 56 viên",
        "packaging": "Hộp 4 vỉ x 14 viên nén",
        "prescription_required": True,
        "mechanism": "Tác động kép đồng thời: Metformin giảm sản xuất glucose tại gan, Sitagliptin tăng tiết insulin tại tụy.",
        "target_organ": "Gan & Tuyến tụy",
        "target_organ_id": "organ_pancreas",
        "target_organ_text": "Gan & Tuyến tụy",
        "indications": "Bệnh nhân ĐTĐ Tuýp 2 có HbA1c cao (≥ 7.5% - 8.0%), đơn trị liệu không kiểm soát đạt đích.",
        "cautions": "Uống 2 lần/ngày cùng bữa ăn để giảm tác dụng không mong muốn trên dạ dày.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Janumet+50mg+850mg",
        "badge": "Hiệu quả phối hợp kép",
        "badge_color": "indigo"
    },
    {
        "id": "med_diamicron_mr_60",
        "name": "Diamicron MR 60mg (Servier)",
        "brand": "Diamicron MR",
        "manufacturer": "Les Laboratoires Servier (Pháp)",
        "active_ingredient": "Gliclazide 60mg (Giải phóng biến đổi)",
        "drug_class": "Sulfonylurea thế hệ mới",
        "drug_class_id": "class_sulfonylurea",
        "price_vnd": 165000,
        "price_text": "165.000 đ / Hộp 60 viên",
        "packaging": "Hộp 2 vỉ x 30 viên giải phóng biến đổi",
        "prescription_required": True,
        "mechanism": "Gắn đặc hiệu lên thụ thể SUR-1 trên màng tế bào beta đảo tụy, kích thích phục hồi pha 1 bài tiết insulin theo nhịp sinh học.",
        "target_organ": "Tế bào Beta Tuyến tụy",
        "target_organ_id": "organ_pancreas",
        "target_organ_text": "Tế bào Beta Tụy",
        "indications": "Hạ đường huyết nhanh khi chế độ ăn và Metformin đơn trị liệu không đủ kiểm soát; thích hợp khi HbA1c tăng cao.",
        "cautions": "Nguy cơ hạ đường huyết nếu bỏ bữa ăn sáng hoặc tập thể lực quá mức mà không bù năng lượng.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Diamicron+MR+60mg",
        "badge": "Hạ đường huyết hiệu quả",
        "badge_color": "amber"
    },
    {
        "id": "med_diabetna_namduoc",
        "name": "Viên Uống Tiểu Đường Diabetna (Nam Dược)",
        "brand": "Diabetna",
        "manufacturer": "Công ty CP Nam Dược (Việt Nam)",
        "active_ingredient": "Cao khô Dây Thìa Canh chuẩn hóa GACP-WHO 0.125g",
        "drug_class": "Thảo dược & Sản phẩm hỗ trợ",
        "drug_class_id": "class_herbal",
        "price_vnd": 115000,
        "price_text": "115.000 đ / Hộp 40 viên",
        "packaging": "Hộp 4 vỉ x 10 viên nang",
        "prescription_required": False,
        "mechanism": "Hoạt chất Gymnemic acid ức chế hấp thu đường ở ruột, phục hồi tế bào beta tụy, tăng tiết insulin tự nhiên.",
        "target_organ": "Hệ tiêu hóa & Đảo tụy",
        "target_organ_id": "organ_pancreas",
        "target_organ_text": "Đảo tụy & Đường ruột",
        "indications": "Dành cho người TIỀN TIỂU ĐƯỜNG, người có nguy cơ cao, hoặc hỗ trợ hạ & ổn định đường huyết cùng thuốc kê đơn.",
        "cautions": "Uống trước bữa ăn 30 phút. Không dùng thay thế hoàn toàn thuốc điều trị ĐTĐ đặc hiệu khi có chỉ định bác sĩ.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Diabetna",
        "badge": "Thảo dược hỗ trợ - Không kê đơn",
        "badge_color": "emerald"
    },
    {
        "id": "med_glucerna_850g",
        "name": "Sữa Bột Glucerna 850g (Abbott)",
        "brand": "Glucerna",
        "manufacturer": "Abbott Laboratories (Mỹ / Hà Lan)",
        "active_ingredient": "Hệ bột đường giải phóng chậm Fibersol, giàu MUFA & Chromium picolinate",
        "drug_class": "Dinh dưỡng Y học chuyên biệt",
        "drug_class_id": "class_herbal",
        "price_vnd": 845000,
        "price_text": "845.000 đ / Hộp 850g",
        "packaging": "Hộp thiếc 850g",
        "prescription_required": False,
        "mechanism": "Chỉ số đường huyết thấp (GI = 29), cung cấp dinh dưỡng cân đối 28 vitamin & khoáng chất, bình ổn đường sau ăn.",
        "target_organ": "Toàn thân & Chuyển hóa",
        "target_organ_id": "organ_metabolism",
        "target_organ_text": "Hệ chuyển hóa toàn thân",
        "indications": "Bổ sung hoặc thay thế bữa ăn phụ cho người đái tháo đường, tiền đái tháo đường nhằm tránh tụt đường huyết ban đêm.",
        "cautions": "Không dùng qua đường tĩnh mạch; không dùng cho trẻ em dưới 13 tuổi trừ khi có hướng dẫn y tế.",
        "long_chau_url": "https://nhathuoclongchau.com.vn/tim-kiem?q=Glucerna+850g",
        "badge": "Dinh dưỡng chuyên biệt GI thấp",
        "badge_color": "blue"
    }
]

# Drug class metadata
DRUG_CLASSES = {
    "class_biguanide": {
        "name": "Nhóm Biguanide (Metformin)",
        "desc": "Giảm sinh đường ở gan, tăng nhạy insulin, không gây tăng cân.",
        "color": "#10B981"
    },
    "class_sglt2": {
        "name": "Nhóm Ức chế SGLT-2",
        "desc": "Thải trừ đường qua nước tiểu, bảo vệ tim mạch, huyết áp và thận.",
        "color": "#F43F5E"
    },
    "class_dpp4": {
        "name": "Nhóm Ức chế DPP-4",
        "desc": "Tăng cường incretin nội sinh, kích thích insulin theo mức glucose, không gây hạ đường quá mức.",
        "color": "#8B5CF6"
    },
    "class_sulfonylurea": {
        "name": "Nhóm Sulfonylurea",
        "desc": "Kích thích tế bào beta tiết insulin, hạ đường huyết nhanh.",
        "color": "#F59E0B"
    },
    "class_combination": {
        "name": "Thuốc Phối Hợp Kép",
        "desc": "Tích hợp 2 cơ chế hiệp đồng tác dụng trong một viên uống.",
        "color": "#6366F1"
    },
    "class_herbal": {
        "name": "Thảo Dược & Dinh Dưỡng Hỗ Trợ",
        "desc": "Hỗ trợ ổn định đường huyết tự nhiên và cung cấp năng lượng chuẩn hóa.",
        "color": "#06B6D4"
    }
}

# Target organs metadata
TARGET_ORGANS = {
    "organ_liver": {"name": "Gan (Liver)", "role": "Ức chế tân tạo đường & phóng thích glucose vào máu"},
    "organ_kidney": {"name": "Thận (Kidneys)", "role": "Tăng thải trừ glucose và natri qua nước tiểu"},
    "organ_pancreas": {"name": "Tuyến Tụy (Pancreas)", "role": "Kích thích tế bào Beta đảo tụy tiết Insulin"},
    "organ_heart": {"name": "Hệ Tim Mạch (Cardiovascular)", "role": "Giảm tiền gánh, hậu gánh, ngăn ngừa biến cố mạch vành"},
    "organ_metabolism": {"name": "Hệ Chuyển Hóa (Metabolism)", "role": "Điều hòa hấp thu đường và cân bằng lipid máu"}
}


# ==============================================================================
# NEO4J KNOWLEDGE GRAPH ENGINE CLASS
# ==============================================================================
class Neo4jDiabetesKnowledgeGraph:
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.environ.get("NEO4J_USER", "neo4j")
        self.password = os.environ.get("NEO4J_PASSWORD", "password")
        self.driver = None
        self.is_connected = False
        self.connection_error = None
        
        self.init_neo4j_driver()

    def init_neo4j_driver(self):
        """Khởi tạo kết nối tới Neo4j database nếu có"""
        if not NEO4J_AVAILABLE:
            self.is_connected = False
            self.connection_error = "Thư viện python neo4j chưa khả dụng"
            return

        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=basic_auth(self.user, self.password),
                connection_timeout=2.0
            )
            # Thử verify connectivity
            self.driver.verify_connectivity()
            self.is_connected = True
            self.connection_error = None
            print(f"[Neo4j] ✅ Kết nối thành công tới Neo4j Server tại {self.uri}")
            self.seed_neo4j_schema()
        except Exception as e:
            self.is_connected = False
            self.connection_error = str(e)
            print(f"[Neo4j] ℹ️ Không phát hiện Neo4j Server đang chạy ({e}). Kích hoạt In-Memory Knowledge Graph Engine.")

    def close(self):
        if self.driver:
            try:
                self.driver.close()
            except Exception:
                pass

    def seed_neo4j_schema(self):
        """Khởi tạo node và relationship vào Neo4j nếu đang kết nối"""
        if not self.is_connected or not self.driver:
            return

        cypher_init = """
        // Tạo Pharmacy FPT Long Châu
        MERGE (ph:Pharmacy {id: 'pharmacy_long_chau'})
        ON CREATE SET ph.name = 'Nhà Thuốc FPT Long Châu', ph.type = 'Chuỗi nhà thuốc bán lẻ y tế', ph.verified = true;

        // Tạo Organs
        MERGE (o1:TargetOrgan {id: 'organ_liver', name: 'Gan', role: 'Ức chế tân tạo glucose'})
        MERGE (o2:TargetOrgan {id: 'organ_kidney', name: 'Thận', role: 'Thải glucose qua nước tiểu'})
        MERGE (o3:TargetOrgan {id: 'organ_pancreas', name: 'Tuyến Tụy', role: 'Kích thích tiết insulin'})
        MERGE (o4:TargetOrgan {id: 'organ_heart', name: 'Hệ Tim Mạch', role: 'Bảo vệ mạch vành & suy tim'})
        MERGE (o5:TargetOrgan {id: 'organ_metabolism', name: 'Hệ Chuyển Hóa', role: 'Ổn định đường huyết'});
        """
        try:
            with self.driver.session() as session:
                session.run(cypher_init)
                # Seed Drug classes & Medications
                for med in FPT_LONG_CHAU_MEDICATIONS:
                    cypher_med = """
                    MERGE (m:Medication {id: $id})
                    ON CREATE SET 
                        m.name = $name,
                        m.brand = $brand,
                        m.manufacturer = $manufacturer,
                        m.active_ingredient = $active_ingredient,
                        m.price_vnd = $price_vnd,
                        m.price_text = $price_text,
                        m.prescription = $prescription_required,
                        m.mechanism = $mechanism,
                        m.url = $long_chau_url
                    WITH m
                    MATCH (ph:Pharmacy {id: 'pharmacy_long_chau'})
                    MERGE (m)-[:AVAILABLE_AT]->(ph)
                    MERGE (dc:DrugClass {id: $drug_class_id})
                    ON CREATE SET dc.name = $drug_class
                    MERGE (dc)-[:CONTAINS_MEDICATION]->(m)
                    WITH m, $target_organ_id AS oid
                    MATCH (o:TargetOrgan {id: oid})
                    MERGE (m)-[:ACTS_ON]->(o);
                    """
                    session.run(cypher_med, **med)
            print("[Neo4j] ✅ Đã nạp thành công Danh mục Thuốc FPT Long Châu vào Neo4j Knowledge Graph!")
        except Exception as err:
            print(f"[Neo4j] Lỗi khi seed dữ liệu: {err}")

    # ==============================================================================
    # RECOMMENDATION & GRAPH TRAVERSAL ALGORITHM
    # ==============================================================================
    def generate_patient_recommendations(self, patient_data: dict, diagnosis_result: dict) -> dict:
        """
        Duyệt cây tri thức (Knowledge Graph Traversal) để tìm phác đồ thuốc phù hợp
        với hồ sơ bệnh nhân từ danh mục FPT Long Châu.
        """
        age = float(patient_data.get("age", 45))
        bmi = float(patient_data.get("bmi", 24.5))
        hypertension = int(patient_data.get("hypertension", 0))
        heart_disease = int(patient_data.get("heart_disease", 0))
        hba1c = float(patient_data.get("hbA1c_level", 5.5))
        glucose = float(patient_data.get("blood_glucose_level", 120))
        risk_pct = float(diagnosis_result.get("probability_positive", 0))
        prediction = int(diagnosis_result.get("prediction", 0))

        recommended_meds = []
        patient_conditions = []
        clinical_alerts = []

        # 1. Nhận diện các yếu tố bệnh học của bệnh nhân
        if bmi >= 30:
            patient_conditions.append({"type": "Béo phì độ I-II (BMI ≥ 30)", "severity": "danger", "target": "organ_liver"})
        elif bmi >= 25:
            patient_conditions.append({"type": "Thừa cân (BMI ≥ 25)", "severity": "warning", "target": "organ_liver"})

        if hypertension == 1:
            patient_conditions.append({"type": "Kèm Tăng Huyết Áp (Hypertension)", "severity": "danger", "target": "organ_kidney"})
        if heart_disease == 1:
            patient_conditions.append({"type": "Kèm Bệnh Lý Tim Mạch (Heart Disease)", "severity": "danger", "target": "organ_heart"})

        if hba1c >= 8.0:
            patient_conditions.append({"type": f"HbA1c rất cao ({hba1c}%)", "severity": "critical", "target": "organ_pancreas"})
        elif hba1c >= 6.5:
            patient_conditions.append({"type": f"HbA1c mức đái tháo đường ({hba1c}%)", "severity": "danger", "target": "organ_pancreas"})
        elif hba1c >= 5.7:
            patient_conditions.append({"type": f"HbA1c tiền tiểu đường ({hba1c}%)", "severity": "warning", "target": "organ_metabolism"})

        if glucose >= 180:
            patient_conditions.append({"type": f"Đường huyết lúc đói báo động ({glucose} mg/dL)", "severity": "critical", "target": "organ_kidney"})
        elif glucose >= 126:
            patient_conditions.append({"type": f"Đường huyết vượt ngưỡng lâm sàng ({glucose} mg/dL)", "severity": "danger", "target": "organ_liver"})
        elif glucose >= 100:
            patient_conditions.append({"type": f"Rối loạn dung nạp đường đói ({glucose} mg/dL)", "severity": "warning", "target": "organ_metabolism"})

        # 2. MATCH RULES THEO PHÁC ĐỒ ADA / BỘ Y TẾ TỪ DANH MỤC FPT LONG CHÂU
        if prediction == 1 or risk_pct >= 45:
            # Ca bệnh nguy cơ cao hoặc đã mắc ĐTĐ
            
            # ƯU TIÊN 1: Nếu có TĂNG HUYẾT ÁP hoặc BỆNH TIM MẠCH -> Bắt buộc gợi ý Nhóm SGLT-2 (Forxiga 10mg / Jardiance 10mg)
            if hypertension == 1 or heart_disease == 1:
                forxiga = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_forxiga_10")
                recommended_meds.append({
                    **forxiga,
                    "match_reason": "⭐ ƯU TIÊN ĐẶC BIỆT: Khuyến cáo vàng (ADA 2024) cho bệnh nhân ĐTĐ kèm Tăng Huyết Áp / Bệnh Tim. Giúp thải đường qua thận và bảo vệ tim mạch, giảm nguy cơ suy tim.",
                    "match_score": 98,
                    "priority_tag": "Bảo vệ Tim Mạch & Huyết Áp"
                })
                clinical_alerts.append("Theo khuyến cáo ADA/KDIGO: Bệnh nhân có yếu tố tim mạch hoặc tăng huyết áp được chỉ định ưu tiên nhóm ức chế SGLT-2 (như Forxiga) để giảm tỷ lệ tử vong và biến chứng thận.")

            # ƯU TIÊN 2: Thuốc nền tảng đầu tay (Metformin: Glucophage XR hoặc 500mg)
            if bmi >= 25 or hba1c >= 6.5:
                # Nếu người lớn tuổi hoặc sợ đau bụng -> Glucophage XR
                glucophage_choice = "med_glucophage_xr_750" if age >= 50 or bmi >= 27 else "med_glucophage_500"
                med_meta = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_glucophage_xr_750")
                recommended_meds.append({
                    **med_meta,
                    "match_reason": f"Thuốc đầu tay (First-line) thiết yếu cho bệnh nhân thể trọng BMI = {bmi} nhằm giảm kháng insulin tại gan, không gây tăng cân.",
                    "match_score": 95,
                    "priority_tag": "Điều Trị Nền Tảng (First-line)"
                })

            # ƯU TIÊN 3: Nếu HbA1c >= 7.5% hoặc cần hạ đường huyết nhanh -> Nhóm DPP-4 (Januvia) hoặc phối hợp kép (Janumet)
            if hba1c >= 7.5:
                janumet = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_janumet_50_850")
                recommended_meds.append({
                    **janumet,
                    "match_reason": f"Chỉ số HbA1c ({hba1c}%) tăng cao. Cần phối hợp Sitagliptin + Metformin để kiểm soát kép cả 2 nguồn sinh đường (Gan & Tụy).",
                    "match_score": 90,
                    "priority_tag": "Phối Hợp Kép Hạ HbA1c Sâu"
                })
            elif hba1c >= 6.8:
                januvia = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_januvia_100")
                recommended_meds.append({
                    **januvia,
                    "match_reason": "Bảo tồn chức năng tế bào beta tụy, kích thích tiết insulin an toàn theo nồng độ glucose trong máu, tránh tụt đường huyết.",
                    "match_score": 88,
                    "priority_tag": "An Toàn Cho Tụy"
                })

            # Gợi ý bổ trợ dinh dưỡng FPT Long Châu
            glucerna = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_glucerna_850g")
            recommended_meds.append({
                **glucerna,
                "match_reason": "Dinh dưỡng y học bổ sung năng lượng chuẩn hóa GI=29, giúp bệnh nhân ăn kiêng không bị thiếu chất hoặc hạ đường huyết ban đêm.",
                "match_score": 80,
                "priority_tag": "Dinh Dưỡng Bổ Trợ"
            })

        else:
            # Ca bệnh Nguy cơ thấp hoặc Tiền Đái Tháo Đường (Pre-diabetes)
            diabetna = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_diabetna_namduoc")
            recommended_meds.append({
                **diabetna,
                "match_reason": f"Chỉ số ở ngưỡng nguy cơ nhẹ ({risk_pct}%). Ưu tiên thảo dược Dây Thìa Canh tự nhiên giúp kích thích tụy và giảm hấp thu đường sau ăn mà không cần dùng thuốc kê đơn liều cao.",
                "match_score": 95,
                "priority_tag": "Hỗ Trợ Tiền Đái Tháo Đường"
            })

            glucerna = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_glucerna_850g")
            recommended_meds.append({
                **glucerna,
                "match_reason": "Sản phẩm kiểm soát chế độ ăn lành mạnh, thay thế các bữa ăn phụ nhiều tinh bột nhanh.",
                "match_score": 85,
                "priority_tag": "Dinh Dưỡng Dự Phòng"
            })

            # Nếu BMI cao dù chưa tiểu đường
            if bmi >= 25:
                glucophage = next(m for m in FPT_LONG_CHAU_MEDICATIONS if m["id"] == "med_glucophage_500")
                recommended_meds.append({
                    **glucophage,
                    "match_reason": f"Tham khảo y khoa: ADA khuyến cáo cân nhắc liều Metformin dự phòng ở người có BMI={bmi} kèm tiền đái tháo đường nếu không giảm cân bằng lối sống.",
                    "match_score": 75,
                    "priority_tag": "Dự Phòng Kháng Insulin"
                })

        # 3. XÂY DỰNG KNOWLEDGE GRAPH CHO FRONTEND (NODES & EDGES)
        graph_data = self.build_patient_knowledge_graph(
            patient_data, diagnosis_result, recommended_meds, patient_conditions
        )

        # 4. TẠO CÂU LỆNH CYPHER TƯƠNG ỨNG CHO NEO4J BROWSER
        cypher_code = self.generate_cypher_query(patient_data, recommended_meds)

        return {
            "recommended_medications": recommended_meds,
            "patient_conditions": patient_conditions,
            "clinical_alerts": clinical_alerts,
            "knowledge_graph": graph_data,
            "cypher_query": cypher_code,
            "neo4j_status": {
                "connected": self.is_connected,
                "uri": self.uri,
                "mode": "Live Neo4j Bolt Instance" if self.is_connected else "In-Memory Knowledge Graph Engine",
                "error": self.connection_error
            }
        }

    def build_patient_knowledge_graph(self, patient_data: dict, diagnosis_result: dict, 
                                     recommended_meds: list, conditions: list) -> dict:
        """Tạo cấu trúc Đồ thị Tri thức (Vis.js compatible)"""
        nodes = []
        edges = []
        node_ids = set()

        def add_node(nid, label, group, title, shape="dot", size=25, color=None, icon=None):
            if nid not in node_ids:
                node_ids.add(nid)
                node_obj = {
                    "id": nid,
                    "label": label,
                    "group": group,
                    "title": title,
                    "shape": shape,
                    "size": size
                }
                if color:
                    node_obj["color"] = color
                nodes.append(node_obj)

        def add_edge(source, target, label, color="#94A3B8", dashes=False, arrows="to"):
            edges.append({
                "from": source,
                "to": target,
                "label": label,
                "color": {"color": color, "highlight": "#6366F1"},
                "dashes": dashes,
                "arrows": arrows,
                "font": {"size": 11, "align": "middle", "color": "#CBD5E1", "background": "rgba(15, 23, 42, 0.7)"}
            })

        # 1. Root Patient Node
        patient_label = f"Bệnh Nhân\n(Nguy cơ: {diagnosis_result.get('probability_positive', 0)}%)"
        patient_color = "#EF4444" if diagnosis_result.get("prediction") == 1 else "#10B981"
        add_node("patient_root", patient_label, "patient", 
                 f"Hồ sơ bệnh nhân: Tuổi {patient_data.get('age')}, BMI {patient_data.get('bmi')}, Huyết áp: {patient_data.get('hypertension')}, Tim: {patient_data.get('heart_disease')}",
                 shape="diamond", size=36, color=patient_color)

        # 2. Pharmacy Node: FPT Long Châu
        add_node("pharmacy_long_chau", "Nhà Thuốc\nFPT Long Châu", "pharmacy",
                 "Hệ thống nhà thuốc FPT Long Châu - Chuỗi dược phẩm uy tín toàn quốc cung cấp thuốc điều trị ĐTĐ chính hãng.",
                 shape="hexagon", size=34, color="#0052CC")

        # 3. Biomarker Nodes
        biomarkers = [
            ("bio_hba1c", f"HbA1c\n{patient_data.get('hbA1c_level')}%", "#F59E0B", "Chỉ số xét nghiệm HbA1c 3 tháng"),
            ("bio_glucose", f"Glucose\n{patient_data.get('blood_glucose_level')} mg/dL", "#F59E0B", "Đường huyết mao mạch lúc đói"),
            ("bio_bmi", f"BMI\n{patient_data.get('bmi')}", "#3B82F6", "Chỉ số khối cơ thể thể trọng"),
        ]
        if int(patient_data.get("hypertension", 0)) == 1:
            biomarkers.append(("bio_htn", "Tăng Huyết Áp\n(Hypertension)", "#EF4444", "Tiền sử chẩn đoán cao huyết áp"))
        if int(patient_data.get("heart_disease", 0)) == 1:
            biomarkers.append(("bio_heart", "Bệnh Tim Mạch\n(Heart Disease)", "#EF4444", "Tiền sử biến cố tim mạch"))

        for b_id, b_label, b_col, b_title in biomarkers:
            add_node(b_id, b_label, "biomarker", b_title, size=22, color=b_col)
            add_edge("patient_root", b_id, "CHỈ SỐ", color=b_col)

        # 4. Disease / Diagnosis Node
        diag_id = "disease_t2d" if diagnosis_result.get("prediction") == 1 else "disease_prediabetes"
        diag_label = "Đái Tháo Đường\nTuýp 2" if diagnosis_result.get("prediction") == 1 else "Nguy Cơ\nTiền Tiểu Đường"
        add_node(diag_id, diag_label, "disease", 
                 "Chẩn đoán lâm sàng từ mô hình Machine Learning Random Forest",
                 shape="box", size=30, color="#EC4899")
        add_edge("patient_root", diag_id, "KẾT LUẬN", color="#EC4899")

        # 5. Organs & Drug Classes & Medication Nodes
        seen_classes = set()
        seen_organs = set()

        for med in recommended_meds:
            med_id = med["id"]
            add_node(med_id, f"{med['brand']}\n({med['price_vnd']:,}đ)", "medication",
                     f"<strong>{med['name']}</strong><br>Hoạt chất: {med['active_ingredient']}<br>Giá FPT Long Châu: {med['price_text']}<br><em>{med['match_reason']}</em>",
                     shape="dot", size=26, color="#06B6D4")
            
            # Edge from Patient -> Recommended Medication
            add_edge("patient_root", med_id, "GỢI Ý", color="#10B981")
            # Edge Medication -> FPT Long Chau
            add_edge(med_id, "pharmacy_long_chau", "PHÂN PHỐI", color="#0052CC", dashes=True)

            # Class Node
            class_id = med["drug_class_id"]
            if class_id not in seen_classes:
                seen_classes.add(class_id)
                c_meta = DRUG_CLASSES.get(class_id, {"name": med["drug_class"], "color": "#8B5CF6", "desc": ""})
                add_node(class_id, c_meta["name"], "drug_class", c_meta["desc"], shape="ellipse", size=24, color=c_meta["color"])
                add_edge(diag_id, class_id, "PHÁC ĐỒ", color="#8B5CF6")
            add_edge(class_id, med_id, "HOẠT CHẤT", color="#8B5CF6")

            # Target Organ Node
            organ_id = med["target_organ_id"]
            if organ_id not in seen_organs:
                seen_organs.add(organ_id)
                o_meta = TARGET_ORGANS.get(organ_id, {"name": med["target_organ_text"], "role": ""})
                add_node(organ_id, o_meta["name"], "organ", o_meta["role"], shape="database", size=22, color="#6366F1")
            add_edge(med_id, organ_id, "TÁC ĐỘNG", color="#6366F1")

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "nodes_count": len(nodes),
                "edges_count": len(edges),
                "medications_count": len(recommended_meds)
            }
        }

    def generate_cypher_query(self, patient_data: dict, recommended_meds: list) -> str:
        """Tạo mã Cypher trực quan để người dùng sao chép vào Neo4j Browser"""
        med_ids_str = ", ".join([f"'{m['id']}'" for m in recommended_meds])
        cypher = f"""// ==============================================================
// NEO4J CYPHER QUERY: TRUY VẤN TRI THỨC ĐÁI THÁO ĐƯỜNG & FPT LONG CHÂU
// Hồ sơ: Tuổi {patient_data.get('age')}, BMI {patient_data.get('bmi')}, Huyết áp: {patient_data.get('hypertension')}, Tim: {patient_data.get('heart_disease')}
// ==============================================================

// 1. Tạo Node Bệnh nhân và Chỉ số lâm sàng
MERGE (p:PatientProfile {{
    id: "patient_active", 
    age: {patient_data.get('age', 45)}, 
    bmi: {patient_data.get('bmi', 24.5)},
    hba1c: {patient_data.get('hbA1c_level', 5.5)},
    glucose: {patient_data.get('blood_glucose_level', 120)},
    hypertension: {patient_data.get('hypertension', 0)},
    heart_disease: {patient_data.get('heart_disease', 0)}
}})

// 2. Tìm kiếm Thuốc tại Nhà thuốc FPT Long Châu phù hợp với phác đồ
MATCH (m:Medication)-[:AVAILABLE_AT]->(ph:Pharmacy {{id: 'pharmacy_long_chau'}})
WHERE m.id IN [{med_ids_str}]
MATCH (dc:DrugClass)-[:CONTAINS_MEDICATION]->(m)
MATCH (m)-[:ACTS_ON]->(o:TargetOrgan)

// 3. Kết nối quan hệ Gợi Ý (RECOMMENDS) từ Bệnh nhân đến Thuốc
MERGE (p)-[r:RECOMMENDED_TREATMENT]->(m)
ON CREATE SET r.evaluated_at = datetime(), r.source = "AI ADA Algorithm"

// 4. Trả về đồ thị để hiển thị trên Neo4j Bloom hoặc Neo4j Browser
RETURN p, dc, m, ph, o;
"""
        return cypher

    def get_full_graph(self) -> dict:
        """Lấy toàn bộ Đồ thị Tri thức nền tảng của hệ thống"""
        nodes = []
        edges = []
        node_ids = set()

        def add_n(nid, label, group, title, color="#3B82F6", shape="dot", size=24):
            if nid not in node_ids:
                node_ids.add(nid)
                nodes.append({"id": nid, "label": label, "group": group, "title": title, "color": color, "shape": shape, "size": size})

        def add_e(src, dst, lbl, col="#94A3B8"):
            edges.append({"from": src, "to": dst, "label": lbl, "color": {"color": col}})

        add_n("pharmacy_long_chau", "Nhà Thuốc\nFPT Long Châu", "pharmacy", "Chuỗi nhà thuốc FPT Long Châu", color="#0052CC", shape="hexagon", size=36)
        add_n("disease_t2d", "Đái Tháo Đường\nTuýp 2", "disease", "Bệnh lý nội tiết mạn tính", color="#EC4899", shape="box", size=30)
        add_n("disease_prediabetes", "Tiền Đái Tháo Đường\n(Pre-diabetes)", "disease", "Giai đoạn dung nạp glucose suy giảm", color="#F59E0B", shape="box", size=28)

        for cid, cm in DRUG_CLASSES.items():
            add_n(cid, cm["name"], "drug_class", cm["desc"], color=cm["color"], shape="ellipse", size=24)
            add_e("disease_t2d", cid, "CHỈ ĐỊNH", cm["color"])

        for oid, om in TARGET_ORGANS.items():
            add_n(oid, om["name"], "organ", om["role"], color="#6366F1", shape="database", size=22)

        for med in FPT_LONG_CHAU_MEDICATIONS:
            add_n(med["id"], f"{med['brand']}\n{med['price_vnd']:,}đ", "medication", 
                  f"<strong>{med['name']}</strong><br>Hoạt chất: {med['active_ingredient']}<br>Giá FPT Long Châu: {med['price_text']}", 
                  color="#06B6D4", shape="dot", size=25)
            add_e(med["drug_class_id"], med["id"], "THUỐC", "#8B5CF6")
            add_e(med["id"], "pharmacy_long_chau", "BÁN TẠI", "#0052CC")
            add_e(med["id"], med["target_organ_id"], "TÁC ĐỘNG", "#6366F1")

        return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes), "total_edges": len(edges)}


# Singleton instance
neo4j_graph = Neo4jDiabetesKnowledgeGraph()

