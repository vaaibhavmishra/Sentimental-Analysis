// ─── Sentiment Colors ───
const SENTIMENT_COLORS = {
  "Very Positive": "#22c55e",
  Positive: "#86efac",
  Neutral: "#facc15",
  Negative: "#fb923c",
  "Very Negative": "#ef4444",
  Error: "#6b7280",
};

const SENTIMENT_CLASS = {
  "Very Positive": "very-positive",
  Positive: "positive",
  Neutral: "neutral",
  Negative: "negative",
  "Very Negative": "very-negative",
  Error: "error",
};

// ─── DOM References ───
const moodInput = document.getElementById("mood-input");
const charCount = document.getElementById("char-count");
const loadingEl = document.getElementById("loading");
const loadingText = document.getElementById("loading-text");
const singleResult = document.getElementById("single-result");
const csvResults = document.getElementById("csv-results");
const realtimeResult = document.getElementById("realtime-result");
const csvFileInput = document.getElementById("csv-file");
const fileNameEl = document.getElementById("file-name");

let chartInstance = null;
let currentCsvData = null;
let debounceTimer = null;

// ─── Character Count ───
moodInput.addEventListener("input", () => {
  charCount.textContent = moodInput.value.length;

  // Debounced real-time detection
  clearTimeout(debounceTimer);
  const text = moodInput.value.trim();
  if (text.length > 3) {
    debounceTimer = setTimeout(() => realtimeDetect(text), 600);
  } else {
    realtimeResult.classList.add("hidden");
  }
});

// ─── Enter Key Support ───
moodInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    detectMood();
  }
});

// ─── File Name Display ───
csvFileInput.addEventListener("change", () => {
  const file = csvFileInput.files[0];
  if (file) {
    fileNameEl.textContent = `📄 ${file.name}`;
    fileNameEl.classList.remove("hidden");
  } else {
    fileNameEl.classList.add("hidden");
  }
});

// ─── Show/Hide Helpers ───
function showLoading(message = "Analyzing...") {
  loadingText.textContent = message;
  loadingEl.classList.remove("hidden");
  singleResult.classList.add("hidden");
  csvResults.classList.add("hidden");
}

function hideLoading() {
  loadingEl.classList.add("hidden");
}

function getSentimentColor(label) {
  return SENTIMENT_COLORS[label] || SENTIMENT_COLORS.Error;
}

// ─── Real-time Detection ───
async function realtimeDetect(text) {
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const result = await response.json();

    if (result.error) {
      realtimeResult.classList.add("hidden");
      return;
    }

    document.getElementById("realtime-emoji").textContent = result.emoji;
    document.getElementById("realtime-label").textContent = result.label;
    document.getElementById("realtime-label").style.color =
      getSentimentColor(result.label);

    const fill = document.getElementById("realtime-bar-fill");
    fill.style.width = `${result.confidence * 100}%`;
    fill.style.backgroundColor = getSentimentColor(result.label);

    realtimeResult.classList.remove("hidden");
  } catch {
    realtimeResult.classList.add("hidden");
  }
}

// ─── Single Text Detection ───
async function detectMood() {
  const text = moodInput.value.trim();

  if (!text) {
    alert("Please enter text to detect sentiment.");
    return;
  }

  showLoading("Detecting sentiment...");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const result = await response.json();
    hideLoading();

    if (result.error) {
      alert(`Error: ${result.error}`);
      return;
    }

    // Display result
    document.getElementById("result-emoji").textContent = result.emoji;
    const labelEl = document.getElementById("result-label");
    labelEl.textContent = result.label;
    labelEl.style.color = getSentimentColor(result.label);

    // Animate confidence bar
    const fill = document.getElementById("confidence-fill");
    fill.style.backgroundColor = getSentimentColor(result.label);
    setTimeout(() => {
      fill.style.width = `${result.confidence * 100}%`;
    }, 100);
    document.getElementById("confidence-value").textContent = `${Math.round(
      result.confidence * 100
    )}%`;

    singleResult.classList.remove("hidden");
    csvResults.classList.add("hidden");
  } catch (error) {
    hideLoading();
    alert("Error: Unable to detect sentiment. Please try again.");
    console.error(error);
  }
}

// ─── CSV Analysis ───
async function analyzeCSV() {
  const file = csvFileInput.files[0];

  if (!file) {
    alert("Please upload a CSV file.");
    return;
  }

  showLoading("Processing CSV file...");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/upload_csv", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    hideLoading();

    if (result.error) {
      alert(`Error: ${result.error}`);
      return;
    }

    currentCsvData = result;
    renderCSVResults(result);

    singleResult.classList.add("hidden");
    csvResults.classList.remove("hidden");
  } catch (error) {
    hideLoading();
    alert("Error: Unable to analyze the CSV file.");
    console.error(error);
  }
}

// ─── Render CSV Results ───
function renderCSVResults(data) {
  const { sentiment_counts, per_row, total, errors } = data;

  // Update summary stats
  document.querySelector("#stat-total .stat-number").textContent = total;
  document.querySelector("#stat-positive .stat-number").textContent =
    sentiment_counts["Very Positive"] + sentiment_counts["Positive"];
  document.querySelector("#stat-negative .stat-number").textContent =
    sentiment_counts["Very Negative"] + sentiment_counts["Negative"];
  document.querySelector("#stat-errors .stat-number").textContent = errors;

  // Build chart
  renderChart(sentiment_counts);

  // Build table
  const tbody = document.getElementById("results-body");
  tbody.innerHTML = "";

  per_row.forEach((row) => {
    const tr = document.createElement("tr");
    const chipClass = SENTIMENT_CLASS[row.label] || "error";
    tr.innerHTML = `
      <td>${row.row}</td>
      <td>${escapeHtml(row.text)}</td>
      <td><span class="sentiment-chip ${chipClass}">${row.emoji} ${row.label}</span></td>
      <td>${row.label === "Error" ? "—" : Math.round(row.confidence * 100) + "%"}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ─── Chart.js Donut ───
function renderChart(counts) {
  const ctx = document.getElementById("sentiment-chart").getContext("2d");

  if (chartInstance) {
    chartInstance.destroy();
  }

  const labels = Object.keys(counts);
  const values = Object.values(counts);
  const colors = labels.map((l) => getSentimentColor(l));

  chartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: colors,
          borderColor: "#161616",
          borderWidth: 3,
          hoverBorderColor: "#fff",
          hoverBorderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "65%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#a3a3a3",
            font: { family: "'Inter', sans-serif", size: 11 },
            padding: 12,
            usePointStyle: true,
            pointStyleWidth: 8,
          },
        },
        tooltip: {
          backgroundColor: "#1a1a1a",
          titleColor: "#fff",
          bodyColor: "#a3a3a3",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          cornerRadius: 8,
          padding: 10,
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : 0;
              return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
            },
          },
        },
      },
      animation: {
        animateRotate: true,
        duration: 1000,
      },
    },
  });
}

// ─── Export CSV ───
function exportCSV() {
  if (!currentCsvData || !currentCsvData.per_row) return;

  const headers = ["Row", "Review", "Sentiment", "Confidence"];
  const rows = currentCsvData.per_row.map((r) => [
    r.row,
    `"${r.text.replace(/"/g, '""')}"`,
    r.label,
    r.label === "Error" ? "" : r.confidence,
  ]);

  const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "sentiment_analysis_results.csv";
  link.click();

  URL.revokeObjectURL(url);
}

// ─── Utility ───
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
