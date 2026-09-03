/* ===================================================
   AI MULTI-MODEL ANALYTICS HUB - CLIENT SCRIPT
   =================================================== */

let aspectChartInstance = null;
let metadataCache = null;

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    initLucide();
    initTheme();
    initTabs();
    initSqftConversion();
    initCharCounter();
    loadMetadata();

    // Form Event Listeners
    document.getElementById("diabetesForm").addEventListener("submit", handleDiabetesSubmit);
    document.getElementById("housePriceForm").addEventListener("submit", handleHousePriceSubmit);
    document.getElementById("ecommerceForm").addEventListener("submit", handleEcommerceSubmit);

    // House Zipcode change handler
    const zipSelect = document.getElementById("hp_zipcode");
    if (zipSelect) {
        zipSelect.addEventListener("change", handleZipcodeChange);
    }
});

function initLucide() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

/* ================= THEME TOGGLE ================= */
function initTheme() {
    const themeBtn = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const currentTheme = localStorage.getItem("theme") || "dark";

    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);

    themeBtn.addEventListener("click", () => {
        const activeTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = activeTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
        updateThemeIcon(newTheme);

        // Re-render radar chart with updated theme colors if it exists
        if (aspectChartInstance) {
            updateChartTheme(newTheme);
        }
    });
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById("themeIcon");
    if (!themeIcon) return;
    if (theme === "light") {
        themeIcon.setAttribute("data-lucide", "sun");
    } else {
        themeIcon.setAttribute("data-lucide", "moon");
    }
    initLucide();
}

/* ================= TAB NAVIGATION ================= */
function initTabs() {
    const tabs = document.querySelectorAll(".nav-tab");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

            tab.classList.add("active");
            const targetId = tab.getAttribute("data-tab");
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add("active");
            }
            initLucide();
        });
    });
}

/* ================= LOAD METADATA ================= */
async function loadMetadata() {
    try {
        const res = await fetch("/api/model-info");
        const json = await res.json();
        if (json.status === "success" && json.metadata) {
            metadataCache = json.metadata;
            populateLocations(json.metadata.us_states);
            populateZipcodes(json.metadata.zipcodes);
        }
    } catch (err) {
        console.warn("Could not load metadata from API:", err);
    }
}

function populateLocations(states) {
    const locSelect = document.getElementById("d_location");
    if (!locSelect || !states) return;
    locSelect.innerHTML = "";
    states.forEach(state => {
        const opt = document.createElement("option");
        opt.value = state;
        opt.textContent = state;
        if (state === "California") opt.selected = true;
        locSelect.appendChild(opt);
    });
}

function populateZipcodes(zipcodes) {
    const zipSelect = document.getElementById("hp_zipcode");
    if (!zipSelect || !zipcodes) return;
    zipSelect.innerHTML = "";
    zipcodes.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.zipcode;
        opt.textContent = `${item.zipcode} - ${item.city}`;
        opt.setAttribute("data-lat", item.lat);
        opt.setAttribute("data-long", item.long);
        opt.setAttribute("data-city", item.city);
        if (item.zipcode === "98004") opt.selected = true;
        zipSelect.appendChild(opt);
    });
    handleZipcodeChange();
}

function handleZipcodeChange() {
    const zipSelect = document.getElementById("hp_zipcode");
    const cityBadge = document.getElementById("hp_city_badge");
    const latInput = document.getElementById("hp_lat");
    const longInput = document.getElementById("hp_long");

    if (!zipSelect || !zipSelect.selectedOptions.length) return;
    const selected = zipSelect.selectedOptions[0];
    const city = selected.getAttribute("data-city") || "King County Area";
    const lat = selected.getAttribute("data-lat") || "47.56";
    const long = selected.getAttribute("data-long") || "-122.21";

    if (cityBadge) cityBadge.textContent = `Khu vực: ${city} (Tọa độ: ${lat}, ${long})`;
    if (latInput) latInput.value = lat;
    if (longInput) longInput.value = long;
}

/* ================= SQFT & CHAR COUNTER ================= */
function initSqftConversion() {
    const livingInput = document.getElementById("hp_sqft_living");
    const lotInput = document.getElementById("hp_sqft_lot");
    const livingM2 = document.getElementById("hp_m2_living");
    const lotM2 = document.getElementById("hp_m2_lot");

    if (livingInput && livingM2) {
        livingInput.addEventListener("input", () => {
            const sqft = parseFloat(livingInput.value) || 0;
            livingM2.textContent = `≈ ${(sqft * 0.092903).toFixed(1)} m²`;
        });
    }

    if (lotInput && lotM2) {
        lotInput.addEventListener("input", () => {
            const sqft = parseFloat(lotInput.value) || 0;
            lotM2.textContent = `≈ ${(sqft * 0.092903).toFixed(1)} m²`;
        });
    }
}

function initCharCounter() {
    const textarea = document.getElementById("ecom_review");
    const charCounter = document.getElementById("ecom_char_count");
    if (textarea && charCounter) {
        textarea.addEventListener("input", () => {
            charCounter.textContent = `${textarea.value.length} ký tự`;
        });
    }
}

function clearEcomReview() {
    const textarea = document.getElementById("ecom_review");
    const charCounter = document.getElementById("ecom_char_count");
    if (textarea) {
        textarea.value = "";
        if (charCounter) charCounter.textContent = "0 ký tự";
        textarea.focus();
    }
}

/* ================= DIABETES HANDLER ================= */
function loadDiabetesPreset(type) {
    if (type === "healthy") {
        document.getElementById("d_age").value = 28;
        document.getElementById("d_gender").value = "Male";
        document.getElementById("d_race").value = "Asian";
        document.getElementById("d_location").value = "California";
        document.getElementById("d_bmi").value = 21.8;
        document.getElementById("d_smoking").value = "never";
        document.getElementById("d_hypertension").value = "0";
        document.getElementById("d_heart_disease").value = "0";
        document.getElementById("d_hba1c").value = 4.8;
        document.getElementById("d_glucose").value = 88;
    } else if (type === "prediabetes") {
        document.getElementById("d_age").value = 48;
        document.getElementById("d_gender").value = "Female";
        document.getElementById("d_race").value = "Caucasian";
        document.getElementById("d_location").value = "Washington";
        document.getElementById("d_bmi").value = 27.5;
        document.getElementById("d_smoking").value = "former";
        document.getElementById("d_hypertension").value = "1";
        document.getElementById("d_heart_disease").value = "0";
        document.getElementById("d_hba1c").value = 5.9;
        document.getElementById("d_glucose").value = 118;
    } else if (type === "highrisk") {
        document.getElementById("d_age").value = 62;
        document.getElementById("d_gender").value = "Male";
        document.getElementById("d_race").value = "AfricanAmerican";
        document.getElementById("d_location").value = "Texas";
        document.getElementById("d_bmi").value = 34.2;
        document.getElementById("d_smoking").value = "current";
        document.getElementById("d_hypertension").value = "1";
        document.getElementById("d_heart_disease").value = "1";
        document.getElementById("d_hba1c").value = 7.4;
        document.getElementById("d_glucose").value = 195;
    }
    // Auto-submit preset
    document.getElementById("diabetesForm").requestSubmit();
}

async function handleDiabetesSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById("btnSubmitDiabetes");
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="pulse-dot"></span> Đang phân tích mô hình...`;
    btn.classList.add("loading");

    const payload = {
        age: parseFloat(document.getElementById("d_age").value),
        gender: document.getElementById("d_gender").value,
        race: document.getElementById("d_race").value,
        location: document.getElementById("d_location").value,
        bmi: parseFloat(document.getElementById("d_bmi").value),
        smoking_history: document.getElementById("d_smoking").value,
        hypertension: parseInt(document.getElementById("d_hypertension").value),
        heart_disease: parseInt(document.getElementById("d_heart_disease").value),
        hbA1c_level: parseFloat(document.getElementById("d_hba1c").value),
        blood_glucose_level: parseFloat(document.getElementById("d_glucose").value),
        year: 2023
    };

    try {
        const res = await fetch("/api/predict/diabetes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (result.status === "success") {
            renderDiabetesResult(result.data);
        } else {
            alert("Lỗi: " + (result.message || "Không thể dự đoán"));
        }
    } catch (err) {
        alert("Lỗi kết nối máy chủ: " + err.message);
    } finally {
        btn.innerHTML = originalText;
        btn.classList.remove("loading");
        initLucide();
    }
}

function renderDiabetesResult(data) {
    document.getElementById("diabetesPlaceholder").classList.add("hidden");
    const content = document.getElementById("diabetesResultContent");
    content.classList.remove("hidden");

    // Badge and Diagnosis
    const badge = document.getElementById("d_badge");
    badge.className = `badge ${data.badge_type}`;
    badge.textContent = data.risk_level;

    const title = document.getElementById("d_diagnosis_title");
    title.textContent = data.diagnosis;
    title.style.color = data.prediction === 1 ? "var(--accent-rose)" : "var(--accent-emerald)";

    // Probability & Meter
    const probVal = document.getElementById("d_prob_val");
    probVal.textContent = `${data.probability_positive}%`;

    const meterFill = document.getElementById("d_meter_fill");
    meterFill.style.width = `${Math.min(100, Math.max(5, data.probability_positive))}%`;
    if (data.probability_positive < 20) {
        meterFill.style.background = "linear-gradient(90deg, #10B981, #34D399)";
        probVal.style.color = "#34D399";
    } else if (data.probability_positive < 45) {
        meterFill.style.background = "linear-gradient(90deg, #F59E0B, #FBBF24)";
        probVal.style.color = "#FBBF24";
    } else if (data.probability_positive < 70) {
        meterFill.style.background = "linear-gradient(90deg, #F97316, #FB923C)";
        probVal.style.color = "#FB923C";
    } else {
        meterFill.style.background = "linear-gradient(90deg, #EF4444, #F43F5E)";
        probVal.style.color = "#F87171";
    }

    // Assessments
    const evalList = document.getElementById("d_metric_list");
    evalList.innerHTML = "";
    data.assessments.forEach(item => {
        const div = document.createElement("div");
        div.className = "eval-item";
        div.innerHTML = `
            <div class="eval-left">
                <span class="eval-title">${item.metric}</span>
                <span class="eval-note">${item.note}</span>
            </div>
            <div class="eval-right">
                <span class="eval-val">${item.val}</span>
                <span class="badge ${item.status.includes('Bình thường') ? 'success' : 'warning'} eval-tag">${item.status}</span>
            </div>
        `;
        evalList.appendChild(div);
    });

    // Advice text
    const adviceText = document.getElementById("d_advice_text");
    if (data.prediction === 1) {
        adviceText.innerHTML = `<strong>Khuyến nghị khẩn cấp:</strong> Chỉ số đường huyết và HbA1c cho thấy nguy cơ cao. Bạn nên đến gặp bác sĩ chuyên khoa nội tiết để làm xét nghiệm dung nạp glucose và được tư vấn phác đồ điều trị kịp thời.`;
    } else if (data.probability_positive > 25) {
        adviceText.innerHTML = `<strong>Cảnh báo tiền đái tháo đường:</strong> Chỉ số ở ngưỡng cần chú ý. Nên giảm tinh bột nhanh, hạn chế nước ngọt, tăng cường rau xanh và tập thể dục đều đặn 150 phút/tuần.`;
    } else {
        adviceText.innerHTML = `<strong>Trạng thái tốt:</strong> Các chỉ số xét nghiệm và thể trạng hiện tại nằm trong giới hạn an toàn. Tiếp tục duy trì chế độ dinh dưỡng cân bằng và kiểm tra sức khỏe định kỳ.`;
    }
}

/* ================= HOUSE PRICE HANDLER ================= */
function loadHousePreset(type) {
    if (type === "condo") {
        document.getElementById("hp_bedrooms").value = 2;
        document.getElementById("hp_bathrooms").value = 1.5;
        document.getElementById("hp_floors").value = 1;
        document.getElementById("hp_sqft_living").value = 1100;
        document.getElementById("hp_sqft_lot").value = 2000;
        document.getElementById("hp_grade").value = "7";
        document.getElementById("hp_condition").value = "3";
        document.getElementById("hp_waterfront").value = "0";
        document.getElementById("hp_view").value = "0";
        document.getElementById("hp_zipcode").value = "98103";
        document.getElementById("hp_yr_built").value = 1985;
        document.getElementById("hp_yr_renovated").value = 0;
        document.getElementById("hp_sqft_basement").value = 0;
    } else if (type === "suburb") {
        document.getElementById("hp_bedrooms").value = 4;
        document.getElementById("hp_bathrooms").value = 2.5;
        document.getElementById("hp_floors").value = 2;
        document.getElementById("hp_sqft_living").value = 2650;
        document.getElementById("hp_sqft_lot").value = 8500;
        document.getElementById("hp_grade").value = "8";
        document.getElementById("hp_condition").value = "4";
        document.getElementById("hp_waterfront").value = "0";
        document.getElementById("hp_view").value = "1";
        document.getElementById("hp_zipcode").value = "98033";
        document.getElementById("hp_yr_built").value = 2005;
        document.getElementById("hp_yr_renovated").value = 0;
        document.getElementById("hp_sqft_basement").value = 450;
    } else if (type === "luxury") {
        document.getElementById("hp_bedrooms").value = 5;
        document.getElementById("hp_bathrooms").value = 4.5;
        document.getElementById("hp_floors").value = 2;
        document.getElementById("hp_sqft_living").value = 4800;
        document.getElementById("hp_sqft_lot").value = 18000;
        document.getElementById("hp_grade").value = "11";
        document.getElementById("hp_condition").value = "5";
        document.getElementById("hp_waterfront").value = "1";
        document.getElementById("hp_view").value = "4";
        document.getElementById("hp_zipcode").value = "98039";
        document.getElementById("hp_yr_built").value = 2012;
        document.getElementById("hp_yr_renovated").value = 2020;
        document.getElementById("hp_sqft_basement").value = 1200;
    }

    handleZipcodeChange();
    initSqftConversion();
    document.getElementById("housePriceForm").requestSubmit();
}

async function handleHousePriceSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById("btnSubmitHouse");
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="pulse-dot"></span> Đang tính toán định giá...`;
    btn.classList.add("loading");

    const payload = {
        bedrooms: parseInt(document.getElementById("hp_bedrooms").value),
        bathrooms: parseFloat(document.getElementById("hp_bathrooms").value),
        floors: parseFloat(document.getElementById("hp_floors").value),
        sqft_living: parseFloat(document.getElementById("hp_sqft_living").value),
        sqft_lot: parseFloat(document.getElementById("hp_sqft_lot").value),
        grade: parseInt(document.getElementById("hp_grade").value),
        condition: parseInt(document.getElementById("hp_condition").value),
        waterfront: parseInt(document.getElementById("hp_waterfront").value),
        view: parseInt(document.getElementById("hp_view").value),
        zipcode: document.getElementById("hp_zipcode").value,
        yr_built: parseInt(document.getElementById("hp_yr_built").value),
        yr_renovated: parseInt(document.getElementById("hp_yr_renovated").value || 0),
        sqft_basement: parseFloat(document.getElementById("hp_sqft_basement").value || 0),
        lat: parseFloat(document.getElementById("hp_lat").value),
        long: parseFloat(document.getElementById("hp_long").value)
    };

    try {
        const res = await fetch("/api/predict/house-price", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (result.status === "success") {
            renderHouseResult(result.data);
        } else {
            alert("Lỗi: " + (result.message || "Không thể tính định giá"));
        }
    } catch (err) {
        alert("Lỗi kết nối máy chủ: " + err.message);
    } finally {
        btn.innerHTML = originalText;
        btn.classList.remove("loading");
        initLucide();
    }
}

function renderHouseResult(data) {
    document.getElementById("housePlaceholder").classList.add("hidden");
    const content = document.getElementById("houseResultContent");
    content.classList.remove("hidden");

    document.getElementById("hp_result_usd").textContent = data.formatted_usd;
    document.getElementById("hp_result_vnd").textContent = data.formatted_vnd;

    document.getElementById("hp_stat_sqft").textContent = `$${data.price_per_sqft} / sqft`;
    const pricePerM2 = Math.round(data.price_per_sqft / 0.092903);
    document.getElementById("hp_stat_m2").textContent = `$${pricePerM2.toLocaleString()} / m²`;
    document.getElementById("hp_stat_age").textContent = `${data.metrics.house_age} năm tuổi`;
    document.getElementById("hp_stat_location").textContent = `${data.location_info.zipcode} (${data.location_info.city})`;

    // Property specs
    const specsUl = document.getElementById("hp_property_specs");
    specsUl.innerHTML = `
        <li><span>Khu vực bưu chính:</span> <strong>${data.location_info.zipcode} - ${data.location_info.city}</strong></li>
        <li><span>Tọa độ địa lý:</span> <strong>Lat: ${data.location_info.lat} | Long: ${data.location_info.long}</strong></li>
        <li><span>Cấp độ xây dựng Grade:</span> <strong>Cấp ${data.metrics.grade} / 13</strong></li>
        <li><span>Tình trạng bảo quản:</span> <strong>Mức ${data.metrics.condition} / 5</strong></li>
        <li><span>Diện tích sinh hoạt:</span> <strong>${data.metrics.sqft_living.toLocaleString()} sqft (≈ ${(data.metrics.sqft_living * 0.092903).toFixed(1)} m²)</strong></li>
        <li><span>Diện tích khuôn viên:</span> <strong>${data.metrics.sqft_lot.toLocaleString()} sqft (≈ ${(data.metrics.sqft_lot * 0.092903).toFixed(1)} m²)</strong></li>
        <li><span>Tình trạng cải tạo:</span> <strong>${data.metrics.is_renovated ? `Đã cải tạo (cách đây ${data.metrics.years_since_renovation} năm)` : 'Nguyên bản (Chưa cải tạo)'}</strong></li>
    `;
}

/* ================= E-COMMERCE HANDLER ================= */
const ECOM_PRESETS = [
    "Giao hàng siêu nhanh luôn shop ơi, đóng gói 3 lớp bóng khí rất cẩn thận, sản phẩm chất lượng tốt đáng tiền!",
    "Chất vải áo thun cotton 100% dày dặn mát mẻ, form áo rộng rãi đúng size bảng hướng dẫn. Shop tư vấn size cực kỳ nhiệt tình, 5 sao!",
    "Áo giao về mặc bị chật hơn form chuẩn, chất vải sờ hơi thô ráp. Thời gian giao hàng mất cả tuần lễ mới tới nơi.",
    "Giá săn sale 1k rẻ như cho, chất lượng ở mức tạm ổn dùng được, màu sắc ở ngoài giống hình quảng cáo."
];

function loadEcomPreset(idx) {
    const text = ECOM_PRESETS[idx] || "";
    const textarea = document.getElementById("ecom_review");
    textarea.value = text;
    const charCounter = document.getElementById("ecom_char_count");
    if (charCounter) charCounter.textContent = `${text.length} ký tự`;
    document.getElementById("ecommerceForm").requestSubmit();
}

async function handleEcommerceSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById("btnSubmitEcom");
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="pulse-dot"></span> Đang trích xuất khía cạnh...`;
    btn.classList.add("loading");

    const reviewText = document.getElementById("ecom_review").value.trim();

    try {
        const res = await fetch("/api/predict/ecommerce", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review_text: reviewText })
        });
        const result = await res.json();
        if (result.status === "success") {
            renderEcommerceResult(result.data);
        } else {
            alert("Lỗi: " + (result.message || "Không thể phân tích"));
        }
    } catch (err) {
        alert("Lỗi kết nối máy chủ: " + err.message);
    } finally {
        btn.innerHTML = originalText;
        btn.classList.remove("loading");
        initLucide();
    }
}

function renderEcommerceResult(data) {
    document.getElementById("ecomPlaceholder").classList.add("hidden");
    const content = document.getElementById("ecomResultContent");
    content.classList.remove("hidden");

    // Count badge
    const countBadge = document.getElementById("ecom_count_badge");
    countBadge.textContent = `${data.detected_count} Khía Cạnh Được Nhận Diện`;

    // Detected Badges List
    const badgesContainer = document.getElementById("ecom_detected_badges");
    badgesContainer.innerHTML = "";
    if (data.detected_aspects.length === 0) {
        badgesContainer.innerHTML = `<span style="font-size: 0.8125rem; color: var(--text-muted);">Không phát hiện khía cạnh nổi bật vượt ngưỡng phân loại.</span>`;
    } else {
        data.detected_aspects.forEach(asp => {
            const span = document.createElement("span");
            span.className = "aspect-tag-detected";
            span.style.background = asp.color;
            span.innerHTML = `<i data-lucide="${asp.icon}"></i> ${asp.name_vi} (${asp.probability}%)`;
            badgesContainer.appendChild(span);
        });
    }

    // Render Radar Chart
    renderAspectRadarChart(data.all_aspects);

    // Render All Aspects Progress Bars
    const barsContainer = document.getElementById("ecom_aspects_bars");
    barsContainer.innerHTML = "";
    data.all_aspects.forEach(asp => {
        const row = document.createElement("div");
        row.className = "aspect-bar-row";
        row.innerHTML = `
            <div class="aspect-bar-info">
                <span class="aspect-bar-name" style="color: ${asp.detected ? asp.color : 'var(--text-secondary)'}">
                    ${asp.detected ? '✓ ' : ''}${asp.name_vi} (${asp.aspect})
                </span>
                <span class="aspect-bar-pct" style="color: ${asp.detected ? asp.color : 'var(--text-muted)'}">
                    ${asp.probability}%
                </span>
            </div>
            <div class="aspect-bar-track">
                <div class="aspect-bar-fill" style="width: ${Math.max(3, asp.probability)}%; background: ${asp.color}"></div>
            </div>
        `;
        barsContainer.appendChild(row);
    });

    initLucide();
}

function renderAspectRadarChart(aspects) {
    const canvas = document.getElementById("aspectRadarChart");
    if (!canvas) return;

    const labels = aspects.map(a => a.name_vi);
    const dataVals = aspects.map(a => a.probability);
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";

    const gridColor = isDark ? "rgba(255, 255, 255, 0.12)" : "rgba(0, 0, 0, 0.1)";
    const textColor = isDark ? "#CBD5E1" : "#475569";

    if (aspectChartInstance) {
        aspectChartInstance.destroy();
    }

    aspectChartInstance = new Chart(canvas, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                label: "Độ tự tin (%)",
                data: dataVals,
                backgroundColor: "rgba(99, 102, 241, 0.28)",
                borderColor: "#6366F1",
                borderWidth: 2,
                pointBackgroundColor: "#38BDF8",
                pointBorderColor: "#FFFFFF",
                pointHoverRadius: 6,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: gridColor },
                    grid: { color: gridColor },
                    pointLabels: {
                        color: textColor,
                        font: { size: 11, family: "'Plus Jakarta Sans', sans-serif", weight: 600 }
                    },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: {
                        stepSize: 25,
                        display: false
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function updateChartTheme(theme) {
    if (!aspectChartInstance) return;
    const isDark = theme === "dark";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.12)" : "rgba(0, 0, 0, 0.1)";
    const textColor = isDark ? "#CBD5E1" : "#475569";

    aspectChartInstance.options.scales.r.angleLines.color = gridColor;
    aspectChartInstance.options.scales.r.grid.color = gridColor;
    aspectChartInstance.options.scales.r.pointLabels.color = textColor;
    aspectChartInstance.update();
}
