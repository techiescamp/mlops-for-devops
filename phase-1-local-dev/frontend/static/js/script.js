document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = {};

    formData.forEach((val, key) => data[key] = Number(val));

    const yearsAtCompany = data['Years at Company'];
    const companyTenure = data['Company Tenure'];

    data["RoleStagnationRatio"] = Number((yearsAtCompany / (companyTenure + 1)).toFixed(3));
    data["TenureGap"] = Number((companyTenure - yearsAtCompany).toFixed(2));
    data["EarlyCompanyTenureRisk"] = yearsAtCompany <= 2 ? 1 : 0;
    data["LongTenureLowRoleRisk"] = (companyTenure > 5 && data["Job Level"] <= 2) ? 1 : 0;

    const showResult = document.getElementById("result");

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log(result);

        if (result.error) {
            showResult.style.display = 'block';
            showResult.innerHTML = `<p class="text-danger text-center">Error: ${result.error}</p>`;
            return;
        }

        showResult.style.display = 'block';
        showResult.innerHTML = `
            <h2 class="text-primary mb-3 text-center">Prediction Result</h2>

            <div class="text-center mb-3">
                <h4 class="fw-bold ${result.prediction === 1 ? "text-danger" : "text-success"}">
                    ${result.prediction === 1 ? "Likely to Leave" : "Likely to Stay"}
                </h4>

                <span class="badge fs-6 px-3 py-2 ${result.risk === "High" ? "bg-danger" : result.risk === "Medium" ? "bg-warning text-dark" : "bg-success"}">
                    ${result.risk} Risk
                </span>
            </div>
            <hr>
            <div class="row text-center mb-3">
                <div class="col-md-6">
                    <h6 class="text-muted">Leave Probability</h6>
                    <h4 class="text-danger fw-bold">${(result.p_leave * 100).toFixed(2)}%</h4>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted">Stay Probability</h6>
                    <h4 class="text-success fw-bold">${(result.p_stay * 100).toFixed(2)}%</h4>
                </div>
            </div>
            <div class="alert alert-light text-center mb-0">
                <small class="text-muted">
                    Decision threshold used: <strong>${result.threshold}</strong>
                </small>
            </div>
        `;
    } catch (error) {
        console.error("Prediction error:", error);
        showResult.style.display = 'block';
        showResult.innerHTML = `<p class="text-danger text-center">Prediction failed: ${error.message}</p>`;
    }
});
