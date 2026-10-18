// CalorieSnap client. All logs live in this browser's localStorage.

const STORE_KEY = "caloriesnap.v1";
const MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"];

const $ = (id) => document.getElementById(id);
const round = (n) => Math.round(Number(n) || 0);
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

// ---------- storage ----------
function loadState() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* fall through to defaults */ }
  return { settings: { goal: null, protein: null }, entries: [] };
}
function saveState() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  } catch {
    // Most likely quota exceeded: drop the oldest thumbnails and retry once.
    state.entries.slice(0, Math.ceil(state.entries.length / 2)).forEach((e) => delete e.thumb);
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch { toast("Storage is full — export and clear old data."); }
  }
}
const state = loadState();

// ---------- dates ----------
const dateKey = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const todayKey = () => dateKey(new Date());
let viewDate = todayKey();

function shiftDay(key, delta) {
  const [y, m, d] = key.split("-").map(Number);
  return dateKey(new Date(y, m - 1, d + delta));
}
function dayLabel(key) {
  if (key === todayKey()) return "Today";
  if (key === shiftDay(todayKey(), -1)) return "Yesterday";
  const [y, m, d] = key.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}
function defaultMealType() {
  const h = new Date().getHours();
  if (h < 10.5) return "Breakfast";
  if (h < 15) return "Lunch";
  if (h >= 17 && h < 22) return "Dinner";
  return "Snack";
}

// ---------- totals ----------
function entryTotals(entry) {
  return entry.items.filter((i) => i.included !== false).reduce(
    (t, i) => ({ cal: t.cal + i.calories, p: t.p + i.protein_g, c: t.c + i.carbs_g, f: t.f + i.fat_g }),
    { cal: 0, p: 0, c: 0, f: 0 },
  );
}
function dayTotals(key) {
  return state.entries.filter((e) => e.date === key).map(entryTotals).reduce(
    (t, x) => ({ cal: t.cal + x.cal, p: t.p + x.p, c: t.c + x.c, f: t.f + x.f }),
    { cal: 0, p: 0, c: 0, f: 0 },
  );
}

// ---------- render home ----------
const RING_LEN = 2 * Math.PI * 52;

function render() {
  const goal = state.settings.goal || 2000;
  const t = dayTotals(viewDate);
  const left = goal - round(t.cal);

  $("dayLabel").textContent = dayLabel(viewDate);
  $("nextDay").disabled = viewDate >= todayKey();
  $("goalNum").textContent = goal.toLocaleString();
  $("eatenNum").textContent = round(t.cal).toLocaleString();
  $("remaining").textContent = Math.abs(left).toLocaleString();
  $("remainingLabel").textContent = left >= 0 ? "calories left" : "calories over";

  const pct = Math.min(t.cal / goal, 1);
  const ring = $("ringFill");
  ring.style.strokeDasharray = RING_LEN;
  ring.style.strokeDashoffset = RING_LEN * (1 - pct);
  ring.classList.toggle("over", left < 0);
  ring.classList.toggle("near", left >= 0 && left < goal * 0.1);

  // Macro bars: protein vs. target if set, carbs/fat as share of calories.
  const proteinTarget = state.settings.protein || Math.round((goal * 0.25) / 4);
  const carbTarget = Math.round((goal * 0.45) / 4);
  const fatTarget = Math.round((goal * 0.3) / 9);
  $("macros").innerHTML = [
    ["Protein", t.p, proteinTarget, "p"],
    ["Carbs", t.c, carbTarget, "c"],
    ["Fat", t.f, fatTarget, "f"],
  ].map(([label, v, target, cls]) => `
    <div class="macro">
      <div class="macro-top"><span>${label}</span><span>${round(v)} / ${target}g</span></div>
      <div class="bar"><div class="bar-fill ${cls}" style="width:${Math.min(100, (v / target) * 100)}%"></div></div>
    </div>`).join("");

  renderMeals();
  renderRecents();
  renderWeek();
}

function renderMeals() {
  const entries = state.entries.filter((e) => e.date === viewDate);
  if (!entries.length) {
    $("mealList").innerHTML = `<p class="muted">Nothing logged yet. Snap your first meal!</p>`;
    return;
  }
  $("mealList").innerHTML = MEAL_TYPES.map((type) => {
    const group = entries.filter((e) => e.mealType === type).sort((a, b) => a.time.localeCompare(b.time));
    if (!group.length) return "";
    const sum = group.reduce((s, e) => s + entryTotals(e).cal, 0);
    return `<div class="meal-group">
      <div class="meal-group-head"><span>${type}</span><span>${round(sum)} cal</span></div>
      ${group.map((e) => {
        const tt = entryTotals(e);
        return `<button class="meal-row" data-id="${e.id}">
          ${e.thumb ? `<img src="${e.thumb}" alt="">` : `<div class="thumb-ph">🍽</div>`}
          <div class="meal-info"><div class="meal-name">${esc(e.name)}</div>
          <div class="muted small">P ${round(tt.p)}g · C ${round(tt.c)}g · F ${round(tt.f)}g</div></div>
          <div class="meal-cal">${round(tt.cal)}</div>
        </button>`;
      }).join("")}
    </div>`;
  }).join("");
  $("mealList").querySelectorAll(".meal-row").forEach((btn) =>
    btn.addEventListener("click", () => openReview(structuredClone(state.entries.find((e) => e.id === btn.dataset.id)), true)),
  );
}

function renderRecents() {
  const seen = new Set();
  const recents = [];
  for (const e of [...state.entries].reverse()) {
    const k = e.name.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k);
    recents.push(e);
    if (recents.length >= 8) break;
  }
  $("recentsCard").hidden = !recents.length;
  $("recents").innerHTML = recents.map((e) =>
    `<button class="chip" data-id="${e.id}">${esc(e.name)} <b>${round(entryTotals(e).cal)}</b></button>`).join("");
  $("recents").querySelectorAll(".chip").forEach((btn) => btn.addEventListener("click", () => {
    const src = state.entries.find((e) => e.id === btn.dataset.id);
    const copy = { ...structuredClone(src), id: uid(), date: viewDate, time: new Date().toISOString(), mealType: defaultMealType() };
    state.entries.push(copy);
    saveState();
    render();
    toast(`Logged ${copy.name} (${round(entryTotals(copy).cal)} cal)`);
  }));
}

function renderWeek() {
  const goal = state.settings.goal || 2000;
  const days = Array.from({ length: 7 }, (_, i) => shiftDay(todayKey(), i - 6));
  const vals = days.map((d) => dayTotals(d).cal);
  const max = Math.max(goal * 1.2, ...vals);
  const goalPct = (goal / max) * 100;
  $("weekChart").innerHTML = `<div class="goal-line" style="bottom:calc(22px + (100% - 26px) * ${goalPct / 100})"><span>${goal}</span></div>` +
    days.map((d, i) => {
      const [y, m, dd] = d.split("-").map(Number);
      const lbl = new Date(y, m - 1, dd).toLocaleDateString(undefined, { weekday: "narrow" });
      const v = vals[i];
      return `<button class="wk-col ${d === viewDate ? "sel" : ""}" data-day="${d}" title="${dayLabel(d)}: ${round(v)} cal">
        <div class="wk-bar-wrap"><div class="wk-bar ${v > goal ? "over" : ""}" style="height:${(v / max) * 100}%"></div></div>
        <div class="wk-lbl">${lbl}</div></button>`;
    }).join("");
  $("weekChart").querySelectorAll(".wk-col").forEach((b) => b.addEventListener("click", () => { viewDate = b.dataset.day; render(); }));
}

// ---------- image handling ----------
function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("Could not read that image.")); };
    img.src = url;
  });
}
function resize(img, maxSide, quality) {
  const scale = Math.min(1, maxSide / Math.max(img.width, img.height));
  const c = document.createElement("canvas");
  c.width = Math.round(img.width * scale);
  c.height = Math.round(img.height * scale);
  c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
  return c.toDataURL("image/jpeg", quality);
}

let pendingPhoto = null; // { full, thumb }

async function onPhotoPicked(e) {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file) return;
  try {
    const img = await loadImage(file);
    pendingPhoto = { full: resize(img, 1280, 0.85), thumb: resize(img, 160, 0.7) };
    openDescribe(true);
  } catch (err) {
    toast(err.message);
  }
}

// ---------- describe / note sheet ----------
function openDescribe(withPhoto) {
  if (!withPhoto) pendingPhoto = null;
  $("describeTitle").textContent = withPhoto ? "Anything to add?" : "Describe your meal";
  $("describeHint").textContent = withPhoto
    ? "Optional: amounts, hidden ingredients (oil, butter, sauce), or 'I only ate half'."
    : "Details like amounts, brands, or cooking oil make estimates more accurate.";
  $("describeSubmit").textContent = withPhoto ? "Analyze photo" : "Estimate";
  $("describePreview").hidden = !withPhoto;
  if (withPhoto) $("describePreview").src = pendingPhoto.thumb;
  $("describeText").value = "";
  $("describeText").required = !withPhoto;
  $("describeDialog").showModal();
}

$("describeDialog").addEventListener("close", () => {
  if ($("describeDialog").returnValue !== "ok") { pendingPhoto = null; return; }
  analyze({ photo: pendingPhoto, note: $("describeText").value });
});

// ---------- analysis ----------
async function requestAnalysis(photo, note) {
  const res = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: photo?.full ?? null, note }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function draftFromAnalysis(a, photo, note) {
  return {
    id: uid(),
    date: viewDate,
    time: new Date().toISOString(),
    mealType: defaultMealType(),
    name: a.meal_name || "Meal",
    items: a.items.map((i) => ({ ...i, included: true })),
    thumb: photo?.thumb ?? null,
    confidence: a.confidence,
    range: [a.calorie_range_low, a.calorie_range_high],
    question: a.clarifying_question || "",
    notes: a.notes || "",
    note: note || "",
    _photo: photo, // kept only while reviewing, for re-analysis
  };
}

async function analyze({ photo, note }, previousDraft) {
  showLoading(photo);
  try {
    const a = await requestAnalysis(photo, note);
    if (!a.is_food) {
      $("reviewDialog").close();
      toast("That doesn't look like food. Try another photo or describe it.");
      return;
    }
    const draft = draftFromAnalysis(a, photo, note);
    if (previousDraft) Object.assign(draft, { id: previousDraft.id, mealType: previousDraft.mealType, date: previousDraft.date, time: previousDraft.time });
    openReview(draft, false);
  } catch (err) {
    $("reviewDialog").close();
    toast(err.message);
  }
}

function showLoading(photo) {
  $("reviewBody").innerHTML = `<div class="loading">
    ${photo ? `<img class="preview" src="${photo.thumb}" alt="">` : ""}
    <div class="spinner"></div>
    <p>Identifying foods and estimating portions…</p></div>`;
  if (!$("reviewDialog").open) $("reviewDialog").showModal();
}

// ---------- review sheet ----------
let draft = null;
let editingExisting = false;

function openReview(entry, existing) {
  draft = entry;
  editingExisting = existing;
  // Remember the original portion of each item so grams edits rescale nutrition.
  draft.items.forEach((i) => { if (!i._base) i._base = { grams: i.grams, calories: i.calories, protein_g: i.protein_g, carbs_g: i.carbs_g, fat_g: i.fat_g }; });
  renderReview();
  if (!$("reviewDialog").open) $("reviewDialog").showModal();
}

function scaleItem(item, grams) {
  const b = item._base;
  const r = b.grams > 0 ? grams / b.grams : 1;
  item.grams = grams;
  item.calories = round(b.calories * r);
  item.protein_g = round(b.protein_g * r);
  item.carbs_g = round(b.carbs_g * r);
  item.fat_g = round(b.fat_g * r);
}

function renderReview() {
  const t = entryTotals(draft);
  const conf = draft.confidence ? `<span class="badge ${draft.confidence}">${draft.confidence} confidence</span>` : "";
  const range = draft.range ? `<span class="muted small">likely ${round(draft.range[0])}–${round(draft.range[1])} cal</span>` : "";
  $("reviewBody").innerHTML = `
    <div class="review-head">
      ${draft.thumb ? `<img class="review-thumb" src="${draft.thumb}" alt="">` : ""}
      <div class="grow">
        <input class="title-input" id="rvName" value="${esc(draft.name)}" aria-label="Meal name">
        <div class="review-total"><b>${round(t.cal)}</b> cal · P ${round(t.p)}g · C ${round(t.c)}g · F ${round(t.f)}g</div>
        <div>${conf} ${range}</div>
      </div>
    </div>

    ${draft.question && !editingExisting ? `<div class="question">
      <div>🤔 ${esc(draft.question)}</div>
      <div class="inline"><input id="rvAnswer" placeholder="Your answer"><button class="btn small-btn" id="rvRefine">Update</button></div>
    </div>` : ""}

    <div class="portion-row">
      <span class="muted small">I ate</span>
      ${[0.5, 0.75, 1, 1.5, 2].map((m) => `<button class="pill" data-mult="${m}">${m === 0.5 ? "½" : m === 0.75 ? "¾" : m + "×"}</button>`).join("")}
    </div>

    <div class="items">
      ${draft.items.map((i, idx) => `
        <div class="item ${i.included === false ? "off" : ""} ${i.hidden ? "hidden-item" : ""}">
          <label class="item-check"><input type="checkbox" data-idx="${idx}" class="rvInc" ${i.included === false ? "" : "checked"}></label>
          <div class="grow">
            <div class="item-name">${esc(i.name)} ${i.hidden ? `<span class="tag">hidden extra</span>` : ""}</div>
            <div class="muted small">${esc(i.portion)} · P ${round(i.protein_g)} C ${round(i.carbs_g)} F ${round(i.fat_g)}</div>
          </div>
          <label class="num-field"><input type="number" inputmode="numeric" min="0" class="rvGrams" data-idx="${idx}" value="${round(i.grams)}"><span>g</span></label>
          <label class="num-field"><input type="number" inputmode="numeric" min="0" class="rvCal" data-idx="${idx}" value="${round(i.calories)}"><span>cal</span></label>
        </div>`).join("")}
    </div>
    <button class="btn link" id="rvAddItem">+ Add an item</button>

    ${draft.notes ? `<p class="muted small">ℹ️ ${esc(draft.notes)}</p>` : ""}

    <label class="field">Meal
      <select id="rvType">${MEAL_TYPES.map((m) => `<option ${m === draft.mealType ? "selected" : ""}>${m}</option>`).join("")}</select>
    </label>

    <div class="sheet-actions">
      ${editingExisting ? `<button class="btn danger-text" id="rvDelete">Delete</button>` : `<button class="btn" id="rvCancel">Cancel</button>`}
      <button class="btn primary" id="rvSave">${editingExisting ? "Save" : `Log ${round(t.cal)} cal`}</button>
    </div>`;

  $("rvName").addEventListener("input", (e) => { draft.name = e.target.value; });
  $("rvType").addEventListener("change", (e) => { draft.mealType = e.target.value; });
  document.querySelectorAll(".rvInc").forEach((el) => el.addEventListener("change", () => { draft.items[el.dataset.idx].included = el.checked; renderReview(); }));
  document.querySelectorAll(".rvGrams").forEach((el) => el.addEventListener("change", () => { scaleItem(draft.items[el.dataset.idx], Math.max(0, Number(el.value) || 0)); renderReview(); }));
  document.querySelectorAll(".rvCal").forEach((el) => el.addEventListener("change", () => {
    // A manual calorie override becomes the new base so later gram edits scale from it.
    const item = draft.items[el.dataset.idx];
    const cal = Math.max(0, Number(el.value) || 0);
    const r = item.calories > 0 ? cal / item.calories : 0;
    item.calories = cal;
    if (r) { item.protein_g *= r; item.carbs_g *= r; item.fat_g *= r; }
    item._base = { grams: item.grams, calories: item.calories, protein_g: item.protein_g, carbs_g: item.carbs_g, fat_g: item.fat_g };
    renderReview();
  }));
  document.querySelectorAll(".pill").forEach((el) => el.addEventListener("click", () => {
    const m = Number(el.dataset.mult);
    draft.items.forEach((i) => scaleItem(i, round(i._base.grams * m)));
    renderReview();
  }));
  $("rvAddItem").addEventListener("click", () => {
    const name = prompt("Item name (e.g. 'Diet Coke' or '1 tbsp olive oil')");
    if (!name) return;
    const cal = Number(prompt(`Calories in ${name}?`, "100"));
    if (!Number.isFinite(cal)) return;
    const item = { name, portion: "1 serving", grams: 0, calories: cal, protein_g: 0, carbs_g: 0, fat_g: 0, hidden: false, included: true };
    item._base = { ...item };
    draft.items.push(item);
    renderReview();
  });
  $("rvRefine")?.addEventListener("click", () => {
    const answer = $("rvAnswer").value.trim();
    if (!answer) return;
    const note = [draft.note, `Q: ${draft.question} A: ${answer}`].filter(Boolean).join("\n");
    analyze({ photo: draft._photo, note }, draft);
  });
  $("rvCancel")?.addEventListener("click", () => $("reviewDialog").close());
  $("rvDelete")?.addEventListener("click", () => {
    if (!confirm("Delete this meal?")) return;
    state.entries = state.entries.filter((e) => e.id !== draft.id);
    saveState();
    $("reviewDialog").close();
    render();
  });
  $("rvSave").addEventListener("click", saveDraft);
}

function saveDraft() {
  const entry = structuredClone({ ...draft, _photo: undefined });
  delete entry._photo;
  delete entry.question;
  entry.items.forEach((i) => { i.protein_g = round(i.protein_g); i.carbs_g = round(i.carbs_g); i.fat_g = round(i.fat_g); });
  const idx = state.entries.findIndex((e) => e.id === entry.id);
  if (idx >= 0) state.entries[idx] = entry; else state.entries.push(entry);
  saveState();
  $("reviewDialog").close();
  viewDate = entry.date;
  render();
  const left = (state.settings.goal || 2000) - round(dayTotals(entry.date).cal);
  toast(left >= 0 ? `Logged! ${left.toLocaleString()} cal left today.` : `Logged. You're ${Math.abs(left).toLocaleString()} cal over today.`);
}

// ---------- settings ----------
function openSettings() {
  $("goalInput").value = state.settings.goal || "";
  $("proteinInput").value = state.settings.protein || "";
  $("calcResult").textContent = "";
  $("settingsDialog").showModal();
}

$("settingsDialog").addEventListener("close", () => {
  if ($("settingsDialog").returnValue !== "ok") return;
  const goal = round($("goalInput").value);
  if (goal >= 800) state.settings.goal = goal;
  state.settings.protein = round($("proteinInput").value) || null;
  saveState();
  render();
});

// Mifflin-St Jeor resting energy x activity factor, plus the chosen surplus/deficit.
$("calcBtn").addEventListener("click", () => {
  const sex = $("calcSex").value;
  const age = Number($("calcAge").value);
  let cm = Number($("calcHeight").value);
  if ($("calcHeightUnit").value === "in") cm *= 2.54;
  let kg = Number($("calcWeight").value);
  if ($("calcWeightUnit").value === "lb") kg *= 0.4536;
  const bmr = 10 * kg + 6.25 * cm - 5 * age + (sex === "male" ? 5 : -161);
  const tdee = bmr * Number($("calcActivity").value);
  const floor = sex === "male" ? 1500 : 1200;
  const target = Math.max(floor, Math.round((tdee + Number($("calcGoal").value)) / 10) * 10);
  $("goalInput").value = target;
  if (!$("proteinInput").value) $("proteinInput").value = Math.round(kg * 1.6);
  $("calcResult").textContent = `Maintenance ≈ ${Math.round(tdee)} cal/day. Suggested goal: ${target} cal, protein ${Math.round(kg * 1.6)} g. Tap Save to use it.`;
});

$("exportBtn").addEventListener("click", () => {
  const rows = [["date", "meal", "name", "item", "grams", "calories", "protein_g", "carbs_g", "fat_g"]];
  for (const e of state.entries) for (const i of e.items.filter((x) => x.included !== false)) {
    rows.push([e.date, e.mealType, e.name, i.name, round(i.grams), round(i.calories), round(i.protein_g), round(i.carbs_g), round(i.fat_g)]);
  }
  const csv = rows.map((r) => r.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = `caloriesnap-${todayKey()}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
});

// ---------- misc ----------
let toastTimer;
function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 3200);
}

$("cameraInput").addEventListener("change", onPhotoPicked);
$("galleryInput").addEventListener("change", onPhotoPicked);
$("describeBtn").addEventListener("click", () => openDescribe(false));
$("openSettings").addEventListener("click", openSettings);
$("prevDay").addEventListener("click", () => { viewDate = shiftDay(viewDate, -1); render(); });
$("nextDay").addEventListener("click", () => { if (viewDate < todayKey()) { viewDate = shiftDay(viewDate, 1); render(); } });
// Roll over to the new day if the app was left open past midnight.
document.addEventListener("visibilitychange", () => { if (!document.hidden) render(); });

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});

render();
if (!state.settings.goal) openSettings();
