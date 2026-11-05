// ==============================================================================
// KNOWLEDGE GRAPH BỆNH HỌC TIỂU ĐƯỜNG & DANH MỤC THUỐC FPT LONG CHÂU
// Neo4j Cypher Schema & Data Seeding Script
// ==============================================================================

// 1. TẠO RÀNG BUỘC DUY NHẤT (CONSTRAINTS)
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Pharmacy) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:DrugClass) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Medication) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (o:TargetOrgan) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (b:Biomarker) REQUIRE b.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Condition) REQUIRE c.id IS UNIQUE;

// 2. KHỞI TẠO NODE NHÀ THUỐC FPT LONG CHÂU
MERGE (ph:Pharmacy {id: 'pharmacy_long_chau'})
ON CREATE SET 
    ph.name = 'Nhà Thuốc FPT Long Châu',
    ph.chain = 'FPT Retail',
    ph.website = 'https://nhathuoclongchau.com.vn',
    ph.verified = true;

// 3. KHỞI TẠO NODE BỆNH LÝ
MERGE (dis1:Condition {id: 'disease_t2d', name: 'Đái Tháo Đường Tuýp 2', code: 'E11'})
MERGE (dis2:Condition {id: 'disease_prediabetes', name: 'Tiền Đái Tháo Đường', code: 'R73.03'})
MERGE (dis3:Condition {id: 'disease_cvd', name: 'Biến Chứng Tim Mạch', code: 'I25'})

// 4. KHỞI TẠO NODE CƠ QUAN ĐÍCH (TARGET ORGANS)
MERGE (o1:TargetOrgan {id: 'organ_liver', name: 'Gan (Liver)', role: 'Ức chế tân tạo đường & phóng thích glucose'})
MERGE (o2:TargetOrgan {id: 'organ_kidney', name: 'Thận (Kidneys)', role: 'Tăng thải trừ glucose và natri qua nước tiểu'})
MERGE (o3:TargetOrgan {id: 'organ_pancreas', name: 'Tuyến Tụy (Pancreas)', role: 'Kích thích tế bào Beta đảo tụy tiết Insulin'})
MERGE (o4:TargetOrgan {id: 'organ_heart', name: 'Hệ Tim Mạch (Cardiovascular)', role: 'Bảo vệ mạch vành và ngăn ngừa suy tim'})
MERGE (o5:TargetOrgan {id: 'organ_metabolism', name: 'Hệ Chuyển Hóa (Metabolism)', role: 'Điều hòa hấp thu đường và cân bằng lipid máu'})

// 5. KHỞI TẠO CÁC NHÓM DƯỢC LÝ (DRUG CLASSES)
MERGE (dc1:DrugClass {id: 'class_biguanide', name: 'Nhóm Biguanide (Metformin)', color: '#10B981'})
MERGE (dc2:DrugClass {id: 'class_sglt2', name: 'Nhóm Ức chế SGLT-2', color: '#F43F5E'})
MERGE (dc3:DrugClass {id: 'class_dpp4', name: 'Nhóm Ức chế DPP-4', color: '#8B5CF6'})
MERGE (dc4:DrugClass {id: 'class_sulfonylurea', name: 'Nhóm Sulfonylurea', color: '#F59E0B'})
MERGE (dc5:DrugClass {id: 'class_combination', name: 'Thuốc Phối Hợp Kép', color: '#6366F1'})
MERGE (dc6:DrugClass {id: 'class_herbal', name: 'Thảo Dược & Dinh Dưỡng Hỗ Trợ', color: '#06B6D4'})

// 6. KHỞI TẠO QUAN HỆ CHỈ ĐỊNH ĐIỀU TRỊ GIỮA BỆNH LÝ & NHÓM THUỐC
MERGE (dis1)-[:INDICATED_TREATMENT {guideline: 'ADA 2024 / Bộ Y Tế'}]->(dc1)
MERGE (dis1)-[:INDICATED_TREATMENT {guideline: 'ADA 2024 / Bộ Y Tế'}]->(dc2)
MERGE (dis1)-[:INDICATED_TREATMENT {guideline: 'ADA 2024 / Bộ Y Tế'}]->(dc3)
MERGE (dis1)-[:INDICATED_TREATMENT {guideline: 'ADA 2024 / Bộ Y Tế'}]->(dc4)
MERGE (dis1)-[:INDICATED_TREATMENT {guideline: 'ADA 2024 / Bộ Y Tế'}]->(dc5)
MERGE (dis2)-[:SUPPORT_TREATMENT]->(dc6)
MERGE (dis2)-[:LIFESTYLE_INTERVENTION]->(o5)

// 7. KHỞI TẠO DANH MỤC THUỐC FPT LONG CHÂU & QUAN HỆ
// --- Glucophage 500mg ---
MERGE (m1:Medication {id: 'med_glucophage_500'})
ON CREATE SET 
    m1.name = 'Glucophage 500mg (Merck)',
    m1.brand = 'Glucophage',
    m1.active_ingredient = 'Metformin hydrochloride 500mg',
    m1.price_vnd = 58000,
    m1.price_text = '58.000 đ / Hộp 50 viên',
    m1.prescription = true,
    m1.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Glucophage+500mg'
MERGE (dc1)-[:CONTAINS_MEDICATION]->(m1)
MERGE (m1)-[:AVAILABLE_AT]->(ph)
MERGE (m1)-[:ACTS_ON]->(o1)

// --- Glucophage XR 750mg ---
MERGE (m2:Medication {id: 'med_glucophage_xr_750'})
ON CREATE SET 
    m2.name = 'Glucophage XR 750mg (Merck)',
    m2.brand = 'Glucophage XR',
    m2.active_ingredient = 'Metformin hydrochloride 750mg (Phóng thích kéo dài)',
    m2.price_vnd = 135000,
    m2.price_text = '135.000 đ / Hộp 30 viên',
    m2.prescription = true,
    m2.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Glucophage+XR+750mg'
MERGE (dc1)-[:CONTAINS_MEDICATION]->(m2)
MERGE (m2)-[:AVAILABLE_AT]->(ph)
MERGE (m2)-[:ACTS_ON]->(o1)

// --- Forxiga 10mg ---
MERGE (m3:Medication {id: 'med_forxiga_10'})
ON CREATE SET 
    m3.name = 'Forxiga 10mg (AstraZeneca)',
    m3.brand = 'Forxiga',
    m3.active_ingredient = 'Dapagliflozin 10mg',
    m3.price_vnd = 575000,
    m3.price_text = '575.000 đ / Hộp 28 viên',
    m3.prescription = true,
    m3.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Forxiga+10mg'
MERGE (dc2)-[:CONTAINS_MEDICATION]->(m3)
MERGE (m3)-[:AVAILABLE_AT]->(ph)
MERGE (m3)-[:ACTS_ON]->(o2)
MERGE (m3)-[:CARDIOPROTECTIVE_FOR]->(dis3)
MERGE (m3)-[:PROTECTS]->(o4)

// --- Jardiance 10mg ---
MERGE (m4:Medication {id: 'med_jardiance_10'})
ON CREATE SET 
    m4.name = 'Jardiance 10mg (Boehringer Ingelheim)',
    m4.brand = 'Jardiance',
    m4.active_ingredient = 'Empagliflozin 10mg',
    m4.price_vnd = 630000,
    m4.price_text = '630.000 đ / Hộp 30 viên',
    m4.prescription = true,
    m4.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Jardiance+10mg'
MERGE (dc2)-[:CONTAINS_MEDICATION]->(m4)
MERGE (m4)-[:AVAILABLE_AT]->(ph)
MERGE (m4)-[:ACTS_ON]->(o2)
MERGE (m4)-[:PROTECTS]->(o4)

// --- Januvia 100mg ---
MERGE (m5:Medication {id: 'med_januvia_100'})
ON CREATE SET 
    m5.name = 'Januvia 100mg (MSD)',
    m5.brand = 'Januvia',
    m5.active_ingredient = 'Sitagliptin phosphate 100mg',
    m5.price_vnd = 520000,
    m5.price_text = '520.000 đ / Hộp 28 viên',
    m5.prescription = true,
    m5.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Januvia+100mg'
MERGE (dc3)-[:CONTAINS_MEDICATION]->(m5)
MERGE (m5)-[:AVAILABLE_AT]->(ph)
MERGE (m5)-[:ACTS_ON]->(o3)

// --- Janumet 50mg/850mg ---
MERGE (m6:Medication {id: 'med_janumet_50_850'})
ON CREATE SET 
    m6.name = 'Janumet 50mg/850mg (MSD)',
    m6.brand = 'Janumet',
    m6.active_ingredient = 'Sitagliptin 50mg + Metformin HCl 850mg',
    m6.price_vnd = 590000,
    m6.price_text = '590.000 đ / Hộp 56 viên',
    m6.prescription = true,
    m6.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Janumet+50mg+850mg'
MERGE (dc5)-[:CONTAINS_MEDICATION]->(m6)
MERGE (m6)-[:AVAILABLE_AT]->(ph)
MERGE (m6)-[:ACTS_ON]->(o1)
MERGE (m6)-[:ACTS_ON]->(o3)

// --- Diamicron MR 60mg ---
MERGE (m7:Medication {id: 'med_diamicron_mr_60'})
ON CREATE SET 
    m7.name = 'Diamicron MR 60mg (Servier)',
    m7.brand = 'Diamicron MR',
    m7.active_ingredient = 'Gliclazide 60mg (Phóng thích biến đổi)',
    m7.price_vnd = 165000,
    m7.price_text = '165.000 đ / Hộp 60 viên',
    m7.prescription = true,
    m7.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Diamicron+MR+60mg'
MERGE (dc4)-[:CONTAINS_MEDICATION]->(m7)
MERGE (m7)-[:AVAILABLE_AT]->(ph)
MERGE (m7)-[:ACTS_ON]->(o3)

// --- Viên uống Diabetna ---
MERGE (m8:Medication {id: 'med_diabetna_namduoc'})
ON CREATE SET 
    m8.name = 'Viên Uống Tiểu Đường Diabetna (Nam Dược)',
    m8.brand = 'Diabetna',
    m8.active_ingredient = 'Cao khô Dây Thìa Canh GACP-WHO 0.125g',
    m8.price_vnd = 115000,
    m8.price_text = '115.000 đ / Hộp 40 viên',
    m8.prescription = false,
    m8.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Diabetna'
MERGE (dc6)-[:CONTAINS_MEDICATION]->(m8)
MERGE (m8)-[:AVAILABLE_AT]->(ph)
MERGE (m8)-[:ACTS_ON]->(o3)
MERGE (m8)-[:ACTS_ON]->(o5)

// --- Sữa Glucerna 850g Abbott ---
MERGE (m9:Medication {id: 'med_glucerna_850g'})
ON CREATE SET 
    m9.name = 'Sữa Bột Glucerna 850g (Abbott)',
    m9.brand = 'Glucerna',
    m9.active_ingredient = 'Hệ bột đường giải phóng chậm Fibersol GI=29 & MUFA',
    m9.price_vnd = 845000,
    m9.price_text = '845.000 đ / Hộp 850g',
    m9.prescription = false,
    m9.url = 'https://nhathuoclongchau.com.vn/tim-kiem?q=Glucerna+850g'
MERGE (dc6)-[:CONTAINS_MEDICATION]->(m9)
MERGE (m9)-[:AVAILABLE_AT]->(ph)
MERGE (m9)-[:ACTS_ON]->(o5)

// 8. TRUY VẤN XEM TOÀN BỘ ĐỒ THỊ
MATCH (n) RETURN n LIMIT 100;

