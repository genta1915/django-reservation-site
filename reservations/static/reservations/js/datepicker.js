document.addEventListener("DOMContentLoaded", async function () {
  const input = document.getElementById("date-picker");
  if (!input) return;

  const form = document.getElementById("filterForm");
  const showBtn = document.getElementById("showBtn");


  if (form) {
      form.addEventListener("submit", function (e) {
          e.preventDefault();
      });
  }

  async function showLoadingAndLoadSlots() {
    if (!input.value) return;

    const loading = document.getElementById("page-loading");

    if (loading) {
      loading.style.display = "flex";
    }

    await new Promise(resolve => setTimeout(resolve, 50));
    await loadSlots(input.value);

    if (loading) {
      loading.style.display = "none";
    }
  }

  input.addEventListener("change", async function () {
    await showLoadingAndLoadSlots();
  });

  if (showBtn) {
    showBtn.addEventListener("click", async function () {
      await showLoadingAndLoadSlots();

      if (input.value) {
        const loading = document.getElementById("page-loading");
        console.log("loading:", loading);

        if (loading) {
          loading.style.display = "flex";
        }

        await new Promise(resolve => setTimeout(resolve, 50));
        await loadSlots(input.value);

        if (loading) {
          loading.style.display = "none";
        }
      }
    });
  }

  // Django json_script から dateStatus を取得
  let dateStatus = {};
  const el = document.getElementById("date-status-date");
  if (el) {
    try {
      dateStatus = JSON.parse(el.textContent);
    } catch (e) {
      console.warn("dateStatus JSON parse failed:", e);
    }
  }

  // 今年の祝日データ（holidays-jp）
  const year = new Date().getFullYear();
  let holidayData = {};
  try {
    const res = await fetch(`https://holidays-jp.github.io/api/v1/${year}/date.json`);
    holidayData = await res.json(); // {"2026-01-01":"元日", ...}
  } catch (e) {
    console.warn("祝日データ取得に失敗:", e);
    holidayData = {};
  }

  // ===== AJAXで枠一覧だけ更新する関数 =====
  async function loadSlots(dateStr) {
    const slotBox = document.getElementById("slotBox");
    if (!slotBox) return;

    slotBox.classList.add("loading");

    try {
      const res = await fetch(`/slots/partial/?date=${encodeURIComponent(dateStr)}`, {
        headers: { "X-Requested-With": "fetch" }
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const html = await res.text();
      slotBox.innerHTML = html;
    } catch (e) {
      console.error("loadSlots failed:", e);
      // 失敗したら、保険で普通にページ遷移させてもOK（任意）
      // window.location.href = `/?date=${encodeURIComponent(dateStr)}`;
    } finally {
      slotBox.classList.remove("loading");
    }
  }

  flatpickr(input, {
    locale: "ja",
    dateFormat: "Y-m-d",

    onChange: function(selectedDates, dateStr) {
      if (dateStr) {
        loadSlots(dateStr);
      }
    },

    onDayCreate: function (dObj, dStr, fp, dayElem) {
      const date = dayElem.dateObj;

      // yyyy-mm-dd に変換
      const yyyy = date.getFullYear();
      const mm = String(date.getMonth() + 1).padStart(2, "0");
      const dd = String(date.getDate()).padStart(2, "0");
      const dateStr = `${yyyy}-${mm}-${dd}`;

      // 土日
      const dow = date.getDay();
      if (dow === 0) dayElem.classList.add("is-sun");
      if (dow === 6) dayElem.classList.add("is-sat");

      // 祝日
      if (holidayData && holidayData[dateStr]) {
        dayElem.classList.add("is-holiday");
      }

      // 空き/満席/混在 を付与（views.py が返す status を使う）
      const status = dateStatus[dateStr]; // "available" / "full" / "mixed"
      if (status === "available") dayElem.classList.add("is-available");
      if (status === "full") dayElem.classList.add("is-full");
      if (status === "mixed") dayElem.classList.add("is-mixed");
    },
  });
});