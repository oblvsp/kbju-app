import csv
import json

APP_VERSION = "1.5"
APP_BUILD = 4
DEFAULT_UPDATE_URL = "https://raw.githubusercontent.com/oblvsp/kbju-app/main/update.json"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Калькулятор КБЖУ — офлайн</title>
<style>
:root{
--primary:#6750a4;--on-primary:#fff;--primary-container:#eaddff;--on-primary-container:#21005d;
--secondary-container:#e8def8;--on-secondary-container:#1d192b;
--surface:#fef7ff;--surface-container-low:#f7f2fa;--surface-container:#f3edf7;--surface-container-high:#ece6f0;--surface-container-highest:#e6e0e9;
--on-surface:#1d1b20;--on-surface-variant:#49454f;--outline:#79747e;--outline-variant:#cac4d0;
--error:#b3261e;--error-container:#f9dedc;--on-error-container:#410e0b;
--inverse-surface:#322f35;--inverse-on-surface:#f5eff7
}
@media (prefers-color-scheme: dark){
:root{
--primary:#d0bcff;--on-primary:#381e72;--primary-container:#4f378b;--on-primary-container:#eaddff;
--secondary-container:#4a4458;--on-secondary-container:#e8def8;
--surface:#141218;--surface-container-low:#1d1b20;--surface-container:#211f26;--surface-container-high:#2b2930;--surface-container-highest:#36343b;
--on-surface:#e6e0e9;--on-surface-variant:#cac4d0;--outline:#938f99;--outline-variant:#49454f;
--error:#f2b8b5;--error-container:#8c1d18;--on-error-container:#f9dedc;
--inverse-surface:#e6e0e9;--inverse-on-surface:#322f35
}
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;font:15px/1.45 Roboto,system-ui,'Segoe UI',Arial,sans-serif;background:var(--surface);color:var(--on-surface);overflow:hidden;touch-action:manipulation}
.app{max-width:680px;margin:0 auto;height:100%;display:flex;flex-direction:column;background:var(--surface)}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:16px 20px 12px}
.topbar .title{font-size:22px;font-weight:500}
.badge{font-size:11px;color:var(--primary);border:1px solid var(--primary);border-radius:8px;padding:2px 8px;letter-spacing:.4px}
.pages{flex:1;position:relative;overflow:hidden}
.page{position:absolute;inset:0;overflow-y:auto;padding:12px 16px 28px;display:none}
.page.active{display:block}
.card{background:var(--surface-container-low);border-radius:16px;padding:16px;margin-bottom:12px}
h2{font-size:16px;font-weight:500;margin:0}
.kbju-stack{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
.kcard{border-radius:16px;padding:10px 14px}
.kcard.target{background:var(--primary-container);color:var(--on-primary-container)}
.kcard.remaining{background:var(--secondary-container);color:var(--on-secondary-container)}
.kcard.remaining.over{background:var(--error-container);color:var(--on-error-container)}
.kcard.eaten{background:var(--surface-container);color:var(--on-surface)}
.krow{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.klabel{font-size:13px;font-weight:500;letter-spacing:.2px}
.kval{font-size:24px;font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.kval .u{font-size:12px;font-weight:400;opacity:.8}
.kmac{display:flex;gap:16px;font-size:12.5px;margin-top:2px;opacity:.92}
.kmac b{font-weight:600;font-variant-numeric:tabular-nums}
#remNote{font-size:11.5px;margin-top:2px}
.grid{display:grid;gap:12px}
.profile-grid{grid-template-columns:1fr 1fr}
.editor-grid{grid-template-columns:1fr 1fr}
label.f{display:block;font-size:12px;color:var(--on-surface-variant);margin-bottom:4px}
input,select{width:100%;padding:9px 12px;border:none;border-radius:8px;font:inherit;background:var(--surface-container-highest);color:var(--on-surface)}
input:focus,select:focus{outline:2px solid var(--primary)}
.full{grid-column:1/-1}
.seg{display:flex;border:1px solid var(--outline-variant);border-radius:20px;overflow:hidden;background:transparent}
.seg label{flex:1;text-align:center;padding:8px 0;font-size:13.5px;cursor:pointer;color:var(--on-surface-variant)}
.seg input{display:none}
.seg label.sel{background:var(--secondary-container);color:var(--on-secondary-container);font-weight:500}
.search-wrap{position:relative;margin-bottom:14px}
.searchbar{display:flex;align-items:center;gap:10px;background:var(--surface-container-high);border-radius:28px;padding:0 18px;height:52px}
.searchbar svg{flex:none;color:var(--on-surface-variant)}
.searchbar input{background:transparent;padding:0;height:100%;border-radius:0}
.searchbar input:focus{outline:none}
.suggest{position:absolute;left:0;right:0;top:calc(100% + 6px);background:var(--surface-container-low);border-radius:16px;max-height:340px;overflow:auto;z-index:30;box-shadow:0 10px 28px rgba(29,27,32,.28);display:none}
.suggest.open{display:block}
.suggest .it{padding:11px 14px;cursor:pointer;display:flex;justify-content:space-between;gap:12px;align-items:baseline}
.suggest .it.active,.suggest .it:hover{background:var(--surface-container)}
.suggest .it .n{flex:1}
.suggest .it .m{color:var(--on-surface-variant);font-size:12px;white-space:nowrap}
.editor .grid{margin-top:12px}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.row.end{justify-content:space-between;width:100%}
.actions{margin-top:14px}
.btn{border:none;font:inherit;font-weight:500;height:40px;padding:0 22px;border-radius:20px;cursor:pointer;display:inline-flex;align-items:center;gap:8px;color:var(--on-surface)}
.btn.filled{background:var(--primary);color:var(--on-primary)}
.btn.filled:hover{filter:brightness(1.08)}
.btn.tonal{background:var(--secondary-container);color:var(--on-secondary-container)}
.btn.small{height:34px;padding:0 14px;font-size:13px}
.hint{margin-top:4px}
.stat{display:flex;justify-content:space-between;padding:8px 0;font-size:14px}
.stat b{font-variant-numeric:tabular-nums}
.switchline{display:flex;gap:12px;align-items:center;margin-top:14px;font-size:13.5px;color:var(--on-surface-variant);cursor:pointer}
.switchline input{display:none}
.track{width:52px;height:32px;border-radius:16px;background:var(--surface-container-highest);border:2px solid var(--outline);position:relative;flex:none;transition:.15s}
.thumb{position:absolute;top:4px;left:4px;width:16px;height:16px;border-radius:50%;background:var(--outline);transition:.15s}
.switchline input:checked + .track{background:var(--primary);border-color:var(--primary)}
.switchline input:checked + .track .thumb{left:24px;width:24px;height:24px;top:2px;background:var(--on-primary)}
ul.entries{list-style:none;margin:10px 0 0;padding:0;-webkit-user-select:none;user-select:none}
ul.entries li{position:relative;overflow:hidden;border-top:1px solid var(--outline-variant);border-radius:12px}
ul.entries li:first-child{border-top:none}
ul.entries .sw-bg{position:absolute;top:0;bottom:0;left:0;right:0;display:flex;align-items:center;font-size:13px;font-weight:500;opacity:0;transition:opacity .1s}
ul.entries .sw-bg.del{justify-content:flex-start;padding-left:18px;background:var(--error-container);color:var(--on-error-container)}
ul.entries .sw-bg.edit{justify-content:flex-end;padding-right:18px;background:var(--primary-container);color:var(--on-primary-container)}
ul.entries .sw-card{position:relative;display:flex;gap:6px;align-items:center;padding:10px 0;background:var(--surface-container-low);border-radius:12px;touch-action:pan-y;will-change:transform}
ul.entries .body{flex:1;min-width:0}
ul.entries .l1{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
ul.entries .l1 .w{font-size:12px;color:var(--on-surface-variant);white-space:nowrap}
ul.entries .l2{font-size:12.5px;color:var(--on-surface-variant);margin-top:3px;font-variant-numeric:tabular-nums}
.iconbtn{width:36px;height:36px;border-radius:50%;border:none;background:transparent;color:var(--on-surface-variant);font-size:20px;cursor:pointer;line-height:1;flex:none}
.iconbtn:hover{background:var(--surface-container)}
.chart{margin-top:10px}
.chart svg{display:block}
.navbar{display:flex;background:var(--surface-container);padding:8px 2px 12px}
.nav-item{flex:1;background:none;border:none;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;color:var(--on-surface-variant);padding:0;font:inherit;outline:none;-webkit-tap-highlight-color:transparent}
.nav-item:focus,.nav-item:focus-visible{outline:none}
.nav-item .nic{width:58px;height:30px;border-radius:15px;display:flex;align-items:center;justify-content:center}
.nav-item .nlabel{font-size:11px;font-weight:500;white-space:nowrap}
.nav-item.active{color:var(--on-surface)}
.nav-item.active .nic{background:var(--secondary-container);color:var(--on-secondary-container)}
#snackbar{position:fixed;left:50%;transform:translateX(-50%) translateY(20px);bottom:96px;background:var(--inverse-surface);color:var(--inverse-on-surface);padding:10px 18px;border-radius:10px;font-size:13.5px;opacity:0;pointer-events:none;transition:.2s;z-index:50;max-width:90vw}
#snackbar.show{opacity:1;transform:translateX(-50%) translateY(0)}
.small{font-size:12px;color:var(--on-surface-variant)}
#editOverlay{position:fixed;inset:0;z-index:60;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,.45);padding:20px}
#editOverlay.open{display:flex}
#editOverlay .sheet{width:100%;max-width:480px;margin:0}
</style>
</head>
<body data-app="kbju-calculator">
<div class="app">
<header class="topbar"><span class="title">Калькулятор КБЖУ</span><span class="badge">офлайн</span></header>

<div class="pages">
<section class="page" id="page-myday">
 <div class="kbju-stack">
  <section class="kcard target">
   <div class="krow"><span class="klabel">Целевое КБЖУ</span><span class="kval"><span id="t_k">—</span> <span class="u">ккал</span></span></div>
   <div class="kmac"><span>Б <b id="t_p">—</b></span><span>Ж <b id="t_f">—</b></span><span>У <b id="t_c">—</b></span></div>
  </section>
  <section class="kcard remaining" id="remCard">
   <div class="krow"><span class="klabel">Осталось</span><span class="kval"><span id="r_k">—</span> <span class="u">ккал</span></span></div>
   <div class="kmac"><span>Б <b id="r_p">—</b></span><span>Ж <b id="r_f">—</b></span><span>У <b id="r_c">—</b></span></div>
   <div id="remNote"></div>
  </section>
  <section class="kcard eaten">
   <div class="krow"><span class="klabel">Съедено за день</span><span class="kval"><span id="e_k">0</span> <span class="u">ккал</span></span></div>
   <div class="kmac"><span>Б <b id="e_p">0</b></span><span>Ж <b id="e_f">0</b></span><span>У <b id="e_c">0</b></span></div>
  </section>
 </div>
 <div class="card">
  <h2>Калории по дням недели</h2>
  <div class="chart" id="chart"></div>
  <div class="small" id="chartAvg" style="margin-top:6px"></div>
 </div>
</section>

<section class="page" id="page-search">
 <div class="search-wrap">
  <div class="searchbar">
   <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
   <input id="search" placeholder="Продукт или блюдо…" autocomplete="off">
  </div>
  <div class="suggest" id="suggest"></div>
 </div>
 <div class="card editor" id="editor" style="display:none">
  <div class="row end"><b id="selName"></b><span class="small" id="selBase"></span></div>
  <div class="grid editor-grid">
   <div><label class="f">Порция, г</label><input id="p_grams" type="number" min="1" step="1" value="100"></div>
   <div><label class="f">Ккал</label><input id="p_k" type="number" step="1"></div>
   <div><label class="f">Белки, г</label><input id="p_prot" type="number" step="0.1"></div>
   <div><label class="f">Жиры, г</label><input id="p_fat" type="number" step="0.1"></div>
   <div><label class="f">Углеводы, г</label><input id="p_carb" type="number" step="0.1"></div>
  </div>
  <div class="row actions">
   <button class="btn filled" id="addSel" type="button">Внести в дневник</button>
   <button class="btn tonal" id="cancelSel" type="button">Отмена</button>
  </div>
  <div class="small hint">Значения можно править вручную; изменение порции пересчитывает их из базы</div>
 </div>
 <div class="small hint">Найдите продукт, при необходимости измените порцию и значения, затем внесите в дневник</div>
</section>

<section class="page" id="page-manual">
 <div class="card" id="manualCard">
   <div class="grid editor-grid">
    <div class="full"><label class="f">Название</label><input id="m_name" placeholder="Например: домашний пирог"></div>
    <div><label class="f">Порция, г</label><input id="m_grams" type="number" min="1" step="1" value="100"></div>
    <div><label class="f">Белки, г (на 100 г)</label><input id="m_prot" type="number" step="0.1"></div>
    <div><label class="f">Жиры, г (на 100 г)</label><input id="m_fat" type="number" step="0.1"></div>
    <div><label class="f">Углеводы, г (на 100 г)</label><input id="m_carb" type="number" step="0.1"></div>
    <div><label class="f">Ккал (на 100 г)</label><input id="m_k" type="number" step="1"></div>
   </div>
   <label class="switchline"><input type="checkbox" id="m_save" checked><span class="track"><span class="thumb"></span></span><span>сохранить в базу для поиска</span></label>
   <div class="small" id="m_preview" style="margin-top:10px;font-variant-numeric:tabular-nums"></div>
   <div class="row actions"><button class="btn filled" id="addManual" type="button">Внести в дневник</button></div>
  </div>
  <div class="small hint">КБЖУ указываются на 100 г; в дневник попадает указанная порция целиком, в базу для поиска — значения на 100 г</div>
</section>

<section class="page" id="page-diary">
 <div class="card">
  <div class="row end"><h2>Дневник</h2><button class="btn tonal small" id="clearDay" type="button">Очистить всё</button></div>
  <div class="small" id="diaryCount" style="margin-top:4px"></div>
  <div id="emptyDiary" class="small" style="margin-top:8px">Пока ничего не добавлено</div>
  <ul class="entries" id="entryList"></ul>
 </div>
</section>

<section class="page" id="page-profile">
 <div class="card" id="profileCard">
  <div class="grid profile-grid">
   <div><label class="f">Рост, см</label><input id="height" type="number" min="80" max="250" step="1"></div>
   <div><label class="f">Вес, кг</label><input id="weight" type="number" min="30" max="300" step="0.1"></div>
   <div><label class="f">Дата рождения</label><input id="birth" type="date"></div>
   <div><label class="f">Пол</label>
    <div class="seg">
     <label class="sel"><input type="radio" name="sex" value="m" checked><span>Муж.</span></label>
     <label><input type="radio" name="sex" value="f"><span>Жен.</span></label>
    </div>
   </div>
   <div class="full"><label class="f">Активность (коэффициент TDEE)</label>
    <select id="activity">
     <option value="1.2">1.2 — минимальная (сидячий образ)</option>
     <option value="1.375">1.375 — лёгкая (1–3 тренировки/нед)</option>
     <option value="1.55" selected>1.55 — средняя (3–5 тренировок/нед)</option>
     <option value="1.725">1.725 — высокая (6–7 тренировок/нед)</option>
     <option value="1.9">1.9 — очень высокая (физ. труд, спорт)</option>
    </select>
   </div>
   <div><label class="f">Дефицит калорий, %</label><input id="deficit" type="number" min="-50" max="90" step="1" value="15"></div>
  </div>
 </div>
 <div class="card">
  <div class="stat"><span>BMR (Миффлин–Сан Жеор)</span><b><span id="bmrOut">—</span> ккал</b></div>
  <div class="stat"><span>TDEE</span><b><span id="tdeeOut">—</span> ккал</b></div>
  <div class="small">Целевые Б/Ж/У = 30/30/40% от целевой калорийности</div>
 </div>
 <div class="card">
  <div class="stat"><span>Версия приложения</span><b id="appVersion">—</b></div>
  <label class="f" style="margin-top:10px">Адрес обновления (update.json)</label>
  <input id="upd_url" placeholder="https://…/update.json или http://192.168.x.x:8000/update.json">
  <div class="row actions">
   <button class="btn filled" id="upd_btn" type="button">Обновить приложение</button>
   <button class="btn tonal small" id="upd_rollback" type="button" style="display:none">Откатить к встроенной</button>
  </div>
  <div class="small" id="upd_status" style="margin-top:8px">Скачивает новую версию интерфейса и базы продуктов по адресу выше и применяет её без переустановки APK.</div>
 </div>
</section>
</div>

<nav class="navbar">
 <button class="nav-item" data-page="search" type="button">
  <span class="nic"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg></span>
  <span class="nlabel">Поиск</span>
 </button>
 <button class="nav-item" data-page="manual" type="button">
  <span class="nic"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.9959.9959 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg></span>
  <span class="nlabel">Ввод</span>
 </button>
 <button class="nav-item active" data-page="myday" type="button">
  <span class="nic"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13zM8 10h2v2H8v-2zm4 0h2v2h-2v-2zm-4 4h2v2H8v-2z"/></svg></span>
  <span class="nlabel">Мой день</span>
 </button>
 <button class="nav-item" data-page="diary" type="button">
  <span class="nic"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg></span>
  <span class="nlabel">Дневник</span>
 </button>
 <button class="nav-item" data-page="profile" type="button">
  <span class="nic"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></span>
  <span class="nlabel">Профиль</span>
 </button>
</nav>
<div id="editOverlay">
 <div class="sheet card">
  <div class="row end"><b>Изменить запись</b><button class="iconbtn" id="editClose" type="button">×</button></div>
  <div class="grid editor-grid" style="margin-top:10px">
   <div class="full"><label class="f">Название</label><input id="em_name"></div>
   <div><label class="f">Порция, г</label><input id="em_grams" type="number" min="1" step="1"></div>
   <div><label class="f">Ккал</label><input id="em_k" type="number" step="1"></div>
   <div><label class="f">Белки, г</label><input id="em_p" type="number" step="0.1"></div>
   <div><label class="f">Жиры, г</label><input id="em_f" type="number" step="0.1"></div>
   <div class="full"><label class="f">Углеводы, г</label><input id="em_c" type="number" step="0.1"></div>
  </div>
  <div class="hint" id="em_preview"></div>
  <div class="row actions"><button class="btn filled" id="editSave" type="button">Сохранить</button><button class="btn tonal" id="editCancel" type="button">Отмена</button></div>
 </div>
</div>
<div id="snackbar"></div>
</div>

<script>
'use strict';
var DATA = __DATA__;
var APP_VERSION = '__APP_VERSION__';
var APP_BUILD = __APP_BUILD__;
var UPDATE_URL_DEFAULT = '__UPDATE_URL__';
function $(id) { return document.getElementById(id); }
function norm(s) { return s.toLowerCase().replace(/ё/g, 'е'); }
function r1(v) { return Math.round(v * 10) / 10; }
function num(v) { var n = parseFloat(String(v).replace(',', '.')); return isFinite(n) && n >= 0 ? n : 0; }
function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
function load(k, d) { try { var v = JSON.parse(localStorage.getItem(k)); return v === null || v === undefined ? d : v; } catch (e) { return d; } }
function todayISO() { var d = new Date(); return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
if (!Element.prototype.closest) {
  Element.prototype.closest = function (s) {
    var el = this;
    while (el && el.nodeType === 1) {
      if (el.matches(s)) return el;
      el = el.parentElement;
    }
    return null;
  };
}

var entries = load('cc_entries', []);
var custom = load('cc_custom', []);
var sel = null;
var sugList = [];
var sugActive = -1;

var INDEX = [];
(function buildIndex() {
  for (var i = 0; i < DATA.length; i++) {
    INDEX.push({ name: DATA[i][0], k: DATA[i][1], p: DATA[i][2], f: DATA[i][3], c: DATA[i][4], nn: norm(DATA[i][0]), custom: false });
  }
})();
function customIndex() {
  var out = [];
  for (var j = 0; j < custom.length; j++) {
    out.push({ name: custom[j][0], k: custom[j][1], p: custom[j][2], f: custom[j][3], c: custom[j][4], nn: norm(custom[j][0]), custom: true });
  }
  return out;
}

function switchPage(id) {
  var pages = document.querySelectorAll('.page');
  for (var i = 0; i < pages.length; i++) pages[i].classList.toggle('active', pages[i].id === 'page-' + id);
  var items = document.querySelectorAll('.nav-item');
  for (var j = 0; j < items.length; j++) items[j].classList.toggle('active', items[j].getAttribute('data-page') === id);
  closeSuggest();
}
(function bindNav() {
  var items = document.querySelectorAll('.nav-item');
  for (var i = 0; i < items.length; i++) {
    items[i].addEventListener('click', function () { switchPage(this.getAttribute('data-page')); });
  }
})();

var snackTimer = null;
function snackbar(msg) {
  var el = $('snackbar');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(snackTimer);
  snackTimer = setTimeout(function () { el.classList.remove('show'); }, 2200);
}

function syncSex() {
  var labels = document.querySelectorAll('.seg label');
  for (var i = 0; i < labels.length; i++) {
    labels[i].classList.toggle('sel', labels[i].querySelector('input').checked);
  }
}

function readProfile() {
  var sexEl = document.querySelector('input[name="sex"]:checked');
  var prof = {
    height: $('height').value,
    weight: $('weight').value,
    birth: $('birth').value,
    sex: sexEl ? sexEl.value : null,
    activity: $('activity').value,
    deficit: $('deficit').value
  };
  save('cc_profile', prof);
  return prof;
}

function calcTargets() {
  var pr = readProfile();
  var w = parseFloat(pr.weight), h = parseFloat(pr.height);
  var bd = pr.birth ? new Date(pr.birth) : null;
  if (!w || !h || !bd || isNaN(bd.getTime()) || !pr.sex) return null;
  var now = new Date();
  var age = now.getFullYear() - bd.getFullYear();
  var m = now.getMonth() - bd.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < bd.getDate())) age--;
  if (age <= 0 || age > 120) return null;
  var bmr = 10 * w + 6.25 * h - 5 * age + (pr.sex === 'm' ? 5 : -161);
  var tdee = bmr * (parseFloat(pr.activity) || 1.2);
  var deficit = parseFloat(pr.deficit);
  if (!isFinite(deficit)) deficit = 0;
  var kcal = tdee * (1 - deficit / 100);
  return { bmr: bmr, tdee: tdee, kcal: kcal, p: kcal * 0.3 / 4, f: kcal * 0.3 / 9, c: kcal * 0.4 / 4 };
}

function sums() {
  var t = todayISO();
  var out = { k: 0, p: 0, f: 0, c: 0 };
  for (var i = 0; i < entries.length; i++) {
    if (entries[i].d !== t) continue;
    out.k += entries[i].k;
    out.p += entries[i].p;
    out.f += entries[i].f;
    out.c += entries[i].c;
  }
  return out;
}

function renderAll() {
  syncSex();
  var t = calcTargets();
  $('bmrOut').textContent = t ? Math.round(t.bmr) : '—';
  $('tdeeOut').textContent = t ? Math.round(t.tdee) : '—';
  if (t) {
    $('t_k').textContent = Math.round(t.kcal);
    $('t_p').textContent = r1(t.p);
    $('t_f').textContent = r1(t.f);
    $('t_c').textContent = r1(t.c);
  } else {
    $('t_k').textContent = '—'; $('t_p').textContent = '—'; $('t_f').textContent = '—'; $('t_c').textContent = '—';
  }
  var s = sums();
  $('e_k').textContent = Math.round(s.k);
  $('e_p').textContent = r1(s.p);
  $('e_f').textContent = r1(s.f);
  $('e_c').textContent = r1(s.c);
  if (t) {
    $('r_k').textContent = Math.round(t.kcal - s.k);
    $('r_p').textContent = r1(t.p - s.p);
    $('r_f').textContent = r1(t.f - s.f);
    $('r_c').textContent = r1(t.c - s.c);
    $('remCard').classList.toggle('over', t.kcal - s.k < 0);
    $('remNote').textContent = t.kcal - s.k < 0 ? 'дневной лимит превышен' : '';
  } else {
    $('r_k').textContent = '—'; $('r_p').textContent = '—'; $('r_f').textContent = '—'; $('r_c').textContent = '—';
    $('remCard').classList.remove('over');
    $('remNote').textContent = '';
  }
  renderDiary();
  chartH = 172;
  renderChart();
  fitChart();
}

function renderDiary() {
  var ul = $('entryList');
  ul.innerHTML = '';
  var order = [];
  for (var i = 0; i < entries.length; i++) order.push(i);
  order.sort(function (a, b) {
    var da = entries[a].d || '', db = entries[b].d || '';
    if (da === db) return 0;
    return da < db ? 1 : -1;
  });
  var today = todayISO();
  for (var j = 0; j < order.length; j++) {
    var e = entries[order[j]];
    var li = document.createElement('li');
    var dateTag = (e.d && e.d !== today) ? ' · ' + e.d.slice(8, 10) + '.' + e.d.slice(5, 7) : '';
    li.innerHTML = '<div class="sw-bg edit">Изменить</div><div class="sw-bg del">Удалить</div>' +
      '<div class="sw-card"><div class="body">' +
      '<div class="l1"><span class="n">' + esc(e.name) + '</span><span class="w">' + e.g + ' г' + dateTag + '</span></div>' +
      '<div class="l2">' + Math.round(e.k) + ' ккал · Б ' + r1(e.p) + ' · Ж ' + r1(e.f) + ' · У ' + r1(e.c) + '</div>' +
      '</div><button class="x iconbtn" data-i="' + order[j] + '" title="Удалить">×</button></div>';
    ul.appendChild(li);
  }
  $('emptyDiary').style.display = entries.length ? 'none' : 'block';
  $('diaryCount').textContent = entries.length ? 'Записей: ' + entries.length : '';
  save('cc_entries', entries);
}

function mondayOf(d) {
  var day = (d.getDay() + 6) % 7;
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() - day);
}

var chartH = 172;
function renderChart() {
  var H = chartH;
  var t = calcTargets();
  var mon = mondayOf(new Date());
  var labels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  var days = [];
  var total = 0;
  for (var i = 0; i < 7; i++) {
    var d = new Date(mon.getFullYear(), mon.getMonth(), mon.getDate() + i);
    var iso = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    var k = 0;
    for (var j = 0; j < entries.length; j++) {
      if (entries[j].d === iso) k += entries[j].k;
    }
    days.push({ k: k, lbl: labels[i], today: iso === todayISO() });
    total += k;
  }
  var target = t ? Math.round(t.kcal) : 0;
  var maxV = Math.max(target, 1);
  for (var q = 0; q < 7; q++) if (days[q].k > maxV) maxV = days[q].k;
  var baseline = H - 40;
  var plotH = baseline - 16;
  var labelY = H - 22;
  var s = '<svg viewBox="0 0 357 ' + H + '" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">';
  if (target > 0) {
    var ty = baseline - Math.round(target / maxV * plotH);
    s += '<line x1="6" x2="351" y1="' + ty + '" y2="' + ty + '" style="stroke:var(--outline)" stroke-dasharray="4 4" stroke-width="1"/>';
    s += '<text x="351" y="' + (ty - 4) + '" text-anchor="end" font-size="10" style="fill:var(--on-surface-variant)">цель ' + target + '</text>';
  }
  for (var n = 0; n < 7; n++) {
    var x = 9 + n * 50;
    var h = days[n].k > 0 ? Math.max(3, Math.round(days[n].k / maxV * plotH)) : 2;
    var y = baseline - h;
    s += '<rect x="' + x + '" y="' + y + '" width="36" height="' + h + '" rx="4" style="fill:var(--primary)" fill-opacity="' + (days[n].today ? '1' : '0.35') + '"/>';
    s += '<text x="' + (x + 18) + '" y="' + (y - 5) + '" text-anchor="middle" font-size="10.5" font-weight="' + (days[n].today ? '600' : '400') + '" style="fill:var(--on-surface)">' + Math.round(days[n].k) + '</text>';
    s += '<text x="' + (x + 18) + '" y="' + labelY + '" text-anchor="middle" font-size="11" font-weight="' + (days[n].today ? '600' : '400') + '" style="fill:' + (days[n].today ? 'var(--primary)' : 'var(--on-surface-variant)') + '">' + days[n].lbl + '</text>';
  }
  s += '</svg>';
  $('chart').innerHTML = s;
  $('chartAvg').textContent = 'Среднее за неделю: ' + Math.round(total / 7) + ' ккал/день' + (target > 0 ? ' · цель ' + target + ' ккал/день' : '');
}

function fitChart() {
  var page = $('page-myday');
  if (!page.children.length || page.scrollTop > 0) return;
  var last = page.children[page.children.length - 1];
  var free = page.getBoundingClientRect().bottom - last.getBoundingClientRect().bottom - 28;
  if (free <= 12) return;
  var w = $('chart').clientWidth || 357;
  var H = Math.min(500, Math.round(172 + free / 2 * 357 / w));
  if (H > chartH + 2) { chartH = H; renderChart(); }
}

function collectHits(pool, toks) {
  var hits = [];
  for (var j = 0; j < pool.length; j++) {
    var it = pool[j];
    var sc = 2, ok = true;
    for (var i = 0; i < toks.length; i++) {
      var idx = it.nn.indexOf(toks[i]);
      if (idx < 0) { ok = false; break; }
      if (i === 0) sc = idx === 0 ? 0 : (it.nn.charAt(idx - 1) === ' ' ? 1 : 2);
    }
    if (ok) hits.push([sc, it.nn.length, it]);
  }
  return hits;
}

function suggest(q) {
  var toks = norm(q).split(/\s+/).filter(Boolean);
  if (!toks.length) return [];
  var pool = INDEX.concat(customIndex());
  var hits = collectHits(pool, toks);
  if (!hits.length && toks.length > 1) hits = collectHits(pool, [toks[0]]);
  hits.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1] || (a[2].custom ? 1 : 0) - (b[2].custom ? 1 : 0); });
  var out = [];
  for (var i = 0; i < hits.length && i < 30; i++) out.push(hits[i][2]);
  return out;
}

function renderSuggest() {
  var box = $('suggest');
  if (!sugList.length) { box.classList.remove('open'); box.innerHTML = ''; return; }
  var html = '';
  for (var i = 0; i < sugList.length; i++) {
    var it = sugList[i];
    html += '<div class="it' + (i === sugActive ? ' active' : '') + '" data-i="' + i + '">' +
      '<span class="n">' + esc(it.name) + (it.custom ? ' <span class="small">(свой)</span>' : '') + '</span>' +
      '<span class="m">' + it.k + ' ккал · Б ' + it.p + ' · Ж ' + it.f + ' · У ' + it.c + '</span></div>';
  }
  box.innerHTML = html;
  box.classList.add('open');
}

function closeSuggest() { sugList = []; sugActive = -1; $('suggest').classList.remove('open'); }

function fillEditor() {
  var g = Math.max(1, num($('p_grams').value) || 100);
  sel.grams = g;
  var m = g / 100;
  $('p_prot').value = r1(sel.base.p * m);
  $('p_fat').value = r1(sel.base.f * m);
  $('p_carb').value = r1(sel.base.c * m);
  $('p_k').value = Math.round(sel.base.k * m);
}

function selectItem(it) {
  closeSuggest();
  sel = { name: it.name, base: { k: it.k, p: it.p, f: it.f, c: it.c }, grams: 100 };
  $('search').value = it.name;
  $('selName').textContent = it.name;
  $('selBase').textContent = 'в базе на 100 г: ' + it.k + ' ккал · Б ' + it.p + ' · Ж ' + it.f + ' · У ' + it.c;
  $('editor').style.display = 'block';
  $('p_grams').value = 100;
  fillEditor();
}

function resetEditor() {
  sel = null;
  $('editor').style.display = 'none';
  $('search').value = '';
  closeSuggest();
}

function addSelected() {
  if (!sel) return;
  entries.push({
    name: sel.name,
    d: todayISO(),
    g: Math.round(sel.grams),
    p: r1(num($('p_prot').value)),
    f: r1(num($('p_fat').value)),
    c: r1(num($('p_carb').value)),
    k: num($('p_k').value)
  });
  save('cc_entries', entries);
  renderAll();
  resetEditor();
}

function updateManualPreview() {
  var has = num($('m_prot').value) || num($('m_fat').value) || num($('m_carb').value) || num($('m_k').value);
  if (!has) { $('m_preview').textContent = ''; return; }
  var g = Math.max(1, Math.round(num($('m_grams').value)) || 100);
  var m = g / 100;
  $('m_preview').textContent = 'В порции ' + g + ' г: ' + Math.round(num($('m_k').value) * m) + ' ккал · Б ' + r1(num($('m_prot').value) * m) + ' · Ж ' + r1(num($('m_fat').value) * m) + ' · У ' + r1(num($('m_carb').value) * m);
}

function addManual() {
  var name = $('m_name').value.trim();
  if (!name) { $('m_name').focus(); return; }
  var g = Math.max(1, Math.round(num($('m_grams').value)) || 100);
  var m = g / 100;
  var p = r1(num($('m_prot').value)), f = r1(num($('m_fat').value)), c = r1(num($('m_carb').value)), k = num($('m_k').value);
  entries.push({ name: name, d: todayISO(), g: g, p: r1(p * m), f: r1(f * m), c: r1(c * m), k: Math.round(k * m) });
  if ($('m_save').checked && !custom.some(function (r) { return r[0] === name; })) {
    custom.push([name, k, p, f, c]);
    save('cc_custom', custom);
  }
  save('cc_entries', entries);
  $('m_name').value = ''; $('m_prot').value = ''; $('m_fat').value = ''; $('m_carb').value = ''; $('m_k').value = ''; $('m_grams').value = '100';
  updateManualPreview();
  renderAll();
  snackbar('Порция ' + g + ' г внесена в дневник');
}

function migrateEntries() {
  var t = todayISO();
  var changed = false;
  for (var i = 0; i < entries.length; i++) {
    if (!entries[i].d) { entries[i].d = t; changed = true; }
  }
  if (changed) save('cc_entries', entries);
}

function hasBridge() {
  return typeof AppBridge !== 'undefined' && AppBridge && AppBridge.httpGet;
}

function updStatus(msg) { $('upd_status').textContent = msg; }

function syncUpdateUi() {
  var has = false;
  if (hasBridge()) {
    try { has = AppBridge.updateExists(); } catch (e) { has = false; }
  }
  $('upd_rollback').style.display = has ? 'inline-flex' : 'none';
}

function doUpdate() {
  if (!hasBridge()) { updStatus('Обновление работает только в Android-приложении'); return; }
  var url = $('upd_url').value.trim();
  if (!url) { updStatus('Укажите адрес файла update.json'); return; }
  save('cc_update_url', url);
  updStatus('Проверяю обновление…');
  setTimeout(function () {
    var resp;
    try { resp = JSON.parse(AppBridge.httpGet(url)); } catch (e) { updStatus('Ошибка ответа: ' + e.message); return; }
    if (!resp || !resp.ok) { updStatus('Не удалось скачать update.json: ' + (resp && resp.error ? resp.error : '?')); return; }
    var man;
    try { man = JSON.parse(resp.body); } catch (e2) { updStatus('Файл update.json не разбирается'); return; }
    if (!man || !man.build || !man.url) { updStatus('В update.json нет полей build или url'); return; }
    if (man.build <= APP_BUILD) { updStatus('Установлена актуальная версия (сборка ' + APP_BUILD + ')'); return; }
    updStatus('Скачиваю версию ' + (man.version || man.build) + '…');
    var resp2;
    try { resp2 = JSON.parse(AppBridge.httpGet(man.url)); } catch (e3) { updStatus('Ошибка скачивания: ' + e3.message); return; }
    if (!resp2 || !resp2.ok) { updStatus('Не удалось скачать файл: ' + (resp2 && resp2.error ? resp2.error : '?')); return; }
    var html = resp2.body;
    if (!html || html.length < 100000 || html.indexOf('kbju-calculator') < 0) { updStatus('Файл не похож на обновление этого приложения'); return; }
    var sr;
    try { sr = JSON.parse(AppBridge.saveUpdate(html)); } catch (e4) { updStatus('Ошибка сохранения: ' + e4.message); return; }
    if (!sr || !sr.ok) { updStatus('Ошибка сохранения: ' + (sr && sr.error ? sr.error : '?')); return; }
    save('cc_app_build', man.build);
    updStatus('Установлено. Перезагружаю…');
    snackbar('Приложение обновлено до сборки ' + man.build);
    setTimeout(function () { AppBridge.restart(); }, 900);
  }, 30);
}

function doRollback() {
  if (!hasBridge()) return;
  var r;
  try { r = JSON.parse(AppBridge.removeUpdate()); } catch (e) { updStatus('Ошибка отката: ' + e.message); return; }
  if (r && r.ok) {
    save('cc_app_build', APP_BUILD);
    snackbar('Возврат к встроенной версии');
    updStatus('Возвращаю встроенную версию…');
    setTimeout(function () { AppBridge.restart(); }, 700);
  } else {
    updStatus('Ошибка отката: ' + (r && r.error ? r.error : '?'));
  }
}

function hexToRgb(h) {
  h = String(h).replace('#', '');
  if (h.length === 3) h = h.charAt(0) + h.charAt(0) + h.charAt(1) + h.charAt(1) + h.charAt(2) + h.charAt(2);
  var n = parseInt(h, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function rgbToHsl(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  var mx = Math.max(r, g, b), mn = Math.min(r, g, b), h = 0, s = 0, l = (mx + mn) / 2;
  if (mx !== mn) {
    var d = mx - mn;
    s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
    if (mx === r) h = (g - b) / d + (g < b ? 6 : 0);
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60;
  }
  return [h, s * 100, l * 100];
}

function hsl(h, s, l) {
  s = Math.max(0, Math.min(100, s));
  l = Math.max(0, Math.min(100, l));
  var c = (1 - Math.abs(2 * l / 100 - 1)) * s / 100;
  var hp = ((h % 360) + 360) % 360 / 60;
  var x = c * (1 - Math.abs(hp % 2 - 1));
  var r = 0, g = 0, b = 0;
  if (hp < 1) { r = c; g = x; }
  else if (hp < 2) { r = x; g = c; }
  else if (hp < 3) { g = c; b = x; }
  else if (hp < 4) { g = x; b = c; }
  else if (hp < 5) { r = x; b = c; }
  else { r = c; b = x; }
  var m = l / 100 - c / 2;
  function f(v) { return ('0' + Math.max(0, Math.min(255, Math.round((v + m) * 255))).toString(16)).slice(-2); }
  return '#' + f(r) + f(g) + f(b);
}

function applyAppTheme(t) {
  t = t || {};
  var dark = !!t.dark;
  var h = 262, s = 34;
  if (t.color) {
    var rgb = hexToRgb(t.color);
    var hs = rgbToHsl(rgb[0], rgb[1], rgb[2]);
    h = hs[0];
    s = Math.max(25, Math.min(85, hs[1]));
  }
  var v;
  if (dark) {
    v = {
      'primary': hsl(h, s, 80), 'on-primary': hsl(h, s, 22),
      'primary-container': hsl(h, s * 0.9, 32), 'on-primary-container': hsl(h, s, 90),
      'secondary-container': hsl(h, s * 0.45, 30), 'on-secondary-container': hsl(h, s * 0.6, 90),
      'surface': hsl(h, s * 0.25, 7.5), 'surface-container-low': hsl(h, s * 0.25, 11.5),
      'surface-container': hsl(h, s * 0.25, 14), 'surface-container-high': hsl(h, s * 0.25, 17.5),
      'surface-container-highest': hsl(h, s * 0.25, 21.5),
      'on-surface': hsl(h, s * 0.2, 89), 'on-surface-variant': hsl(h, s * 0.15, 79),
      'outline': hsl(h, s * 0.12, 59), 'outline-variant': hsl(h, s * 0.18, 30),
      'inverse-surface': hsl(h, s * 0.15, 90), 'inverse-on-surface': hsl(h, s * 0.2, 20)
    };
  } else {
    v = {
      'primary': hsl(h, s, 48), 'on-primary': '#ffffff',
      'primary-container': hsl(h, s * 0.85, 91), 'on-primary-container': hsl(h, s, 20),
      'secondary-container': hsl(h, s * 0.5, 89.5), 'on-secondary-container': hsl(h, s * 0.6, 18),
      'surface': hsl(h, s * 0.3, 98.6), 'surface-container-low': hsl(h, s * 0.3, 96.6),
      'surface-container': hsl(h, s * 0.3, 94.6), 'surface-container-high': hsl(h, s * 0.3, 92.6),
      'surface-container-highest': hsl(h, s * 0.3, 90.4),
      'on-surface': hsl(h, s * 0.15, 12), 'on-surface-variant': hsl(h, s * 0.12, 30),
      'outline': hsl(h, s * 0.1, 48), 'outline-variant': hsl(h, s * 0.15, 81),
      'inverse-surface': hsl(h, s * 0.15, 20), 'inverse-on-surface': hsl(h, s * 0.15, 95)
    };
  }
  var root = document.documentElement;
  for (var k in v) root.style.setProperty('--' + k, v[k]);
  if (hasBridge() && AppBridge.setStatusBar) {
    try { AppBridge.setStatusBar(JSON.stringify({ color: v['surface'], iconsLight: !dark })); } catch (e) {}
  }
}

$('upd_btn').addEventListener('click', doUpdate);
$('upd_rollback').addEventListener('click', doRollback);

$('profileCard').addEventListener('input', renderAll);
$('search').addEventListener('input', function () {
  sugList = suggest($('search').value);
  sugActive = -1;
  renderSuggest();
});
$('search').addEventListener('keydown', function (e) {
  if (e.key === 'Enter') { e.preventDefault(); if (sugList.length) selectItem(sugList[Math.max(0, sugActive)]); return; }
  if (!sugList.length) return;
  if (e.key === 'ArrowDown') { sugActive = (sugActive + 1) % sugList.length; renderSuggest(); e.preventDefault(); }
  else if (e.key === 'ArrowUp') { sugActive = (sugActive - 1 + sugList.length) % sugList.length; renderSuggest(); e.preventDefault(); }
  else if (e.key === 'Escape') closeSuggest();
});
$('suggest').addEventListener('click', function (e) {
  var el = e.target.closest ? e.target.closest('.it') : null;
  if (el) { e.stopPropagation(); selectItem(sugList[+el.getAttribute('data-i')]); }
});
document.addEventListener('click', function (e) {
  if (!e.target.closest('.search-wrap')) closeSuggest();
});
$('p_grams').addEventListener('input', function () { if (sel) fillEditor(); });
$('addSel').addEventListener('click', addSelected);
$('cancelSel').addEventListener('click', resetEditor);
$('addManual').addEventListener('click', addManual);
$('manualCard').addEventListener('input', updateManualPreview);
$('entryList').addEventListener('click', function (e) {
  var b = e.target.closest ? e.target.closest('button.x') : null;
  if (b) { entries.splice(+b.getAttribute('data-i'), 1); save('cc_entries', entries); renderAll(); }
});
$('clearDay').addEventListener('click', function () { entries = []; save('cc_entries', entries); renderAll(); });

var editIdx = -1;
var em = { k100: 0, p100: 0, f100: 0, c100: 0 };
function emSnap() {
  var g = num($('em_grams').value);
  if (!(g > 0)) return;
  em.k100 = num($('em_k').value) / g;
  em.p100 = num($('em_p').value) / g;
  em.f100 = num($('em_f').value) / g;
  em.c100 = num($('em_c').value) / g;
}
function emApply() {
  var g = num($('em_grams').value);
  if (g > 0) {
    $('em_k').value = Math.round(em.k100 * g);
    $('em_p').value = r1(em.p100 * g);
    $('em_f').value = r1(em.f100 * g);
    $('em_c').value = r1(em.c100 * g);
  }
  emPreview();
}
function emPreview() {
  var g = num($('em_grams').value);
  var k = num($('em_k').value), p = num($('em_p').value), f = num($('em_f').value), c = num($('em_c').value);
  var base = (g > 0 && k > 0) ? Math.round(k * 100 / g) : 0;
  $('em_preview').textContent = 'Итог: ' + Math.round(k) + ' ккал · Б ' + r1(p) + ' · Ж ' + r1(f) + ' · У ' + r1(c) + (base ? ' · на 100 г: ' + base + ' ккал' : '');
}
function openEdit(i) {
  editIdx = i;
  var e = entries[i];
  if (!e) return;
  $('em_name').value = e.name;
  $('em_grams').value = e.g;
  $('em_k').value = Math.round(e.k);
  $('em_p').value = e.p;
  $('em_f').value = e.f;
  $('em_c').value = e.c;
  emSnap();
  emPreview();
  $('editOverlay').classList.add('open');
}
function closeEdit() { $('editOverlay').classList.remove('open'); editIdx = -1; }
$('editClose').addEventListener('click', closeEdit);
$('editCancel').addEventListener('click', closeEdit);
$('editOverlay').addEventListener('click', function (e) { if (e.target === this) closeEdit(); });
$('em_grams').addEventListener('input', emApply);
$('em_k').addEventListener('input', emSnap);
$('em_p').addEventListener('input', emSnap);
$('em_f').addEventListener('input', emSnap);
$('em_c').addEventListener('input', emSnap);
$('editSave').addEventListener('click', function () {
  if (editIdx < 0 || !entries[editIdx]) { closeEdit(); return; }
  var name = $('em_name').value.trim();
  if (!name) { $('em_name').focus(); return; }
  var e = entries[editIdx];
  e.name = name;
  e.g = Math.max(1, Math.round(num($('em_grams').value)) || 100);
  e.k = num($('em_k').value);
  e.p = r1(num($('em_p').value));
  e.f = r1(num($('em_f').value));
  e.c = r1(num($('em_c').value));
  save('cc_entries', entries);
  renderAll();
  closeEdit();
  snackbar('Запись обновлена');
});

(function bindSwipe() {
  var ul = $('entryList');
  var st = null;
  function resetBgs(li) {
    li.querySelector('.sw-bg.edit').style.opacity = '0';
    li.querySelector('.sw-bg.del').style.opacity = '0';
  }
  ul.addEventListener('touchstart', function (e) {
    if (st || e.touches.length !== 1) return;
    var card = e.target.closest ? e.target.closest('.sw-card') : null;
    if (!card) return;
    st = { card: card, x0: e.touches[0].clientX, y0: e.touches[0].clientY, dx: 0, lock: '' };
  }, { passive: true });
  ul.addEventListener('touchmove', function (e) {
    if (!st) return;
    var dx = e.touches[0].clientX - st.x0, dy = e.touches[0].clientY - st.y0;
    if (!st.lock) {
      if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return;
      st.lock = Math.abs(dx) > Math.abs(dy) ? 'h' : 'v';
      if (st.lock === 'v') { st = null; return; }
    }
    if (st.lock !== 'h') return;
    e.preventDefault();
    var maxDx = st.card.parentElement.clientWidth;
    st.dx = Math.max(-maxDx, Math.min(maxDx, dx));
    st.card.style.transition = 'none';
    st.card.style.transform = 'translateX(' + st.dx + 'px)';
    var li = st.card.parentElement;
    li.querySelector('.sw-bg.edit').style.opacity = String(Math.max(0, Math.min(1, st.dx / 84)));
    li.querySelector('.sw-bg.del').style.opacity = String(Math.max(0, Math.min(1, -st.dx / 84)));
  }, { passive: false });
  ul.addEventListener('touchend', function () {
    if (!st) return;
    var card = st.card, dx = st.dx;
    var li = card.parentElement;
    var i = +card.querySelector('button.x').getAttribute('data-i');
    st = null;
    card.style.transition = '.18s';
    var th = Math.max(72, li.clientWidth * 0.28);
    if (dx > th) {
      card.style.transform = 'translateX(' + li.clientWidth + 'px)';
      setTimeout(function () { card.style.transform = ''; card.style.transition = 'none'; resetBgs(li); openEdit(i); }, 170);
    } else if (dx < -th) {
      card.style.transform = 'translateX(-' + li.clientWidth + 'px)';
      setTimeout(function () { entries.splice(i, 1); save('cc_entries', entries); renderAll(); snackbar('Запись удалена'); }, 170);
    } else {
      card.style.transform = 'translateX(0)';
      resetBgs(li);
    }
  });
  ul.addEventListener('touchcancel', function () {
    if (!st) return;
    st.card.style.transform = 'translateX(0)';
    resetBgs(st.card.parentElement);
    st = null;
  });
})();

(function init() {
  migrateEntries();
  var pr = load('cc_profile', {});
  if (pr.height) $('height').value = pr.height;
  if (pr.weight) $('weight').value = pr.weight;
  if (pr.birth) $('birth').value = pr.birth;
  if (pr.activity) $('activity').value = pr.activity;
  if (pr.deficit !== undefined && pr.deficit !== '') $('deficit').value = pr.deficit;
  if (pr.sex) {
    var el = document.querySelector('input[name="sex"][value="' + pr.sex + '"]');
    if (el) el.checked = true;
  }
  syncSex();
  renderAll();
  switchPage('myday');
  $('appVersion').textContent = APP_VERSION + ' · сборка ' + APP_BUILD;
  if (UPDATE_URL_DEFAULT && !load('cc_update_url', '')) $('upd_url').value = UPDATE_URL_DEFAULT;
  else if (load('cc_update_url', '')) $('upd_url').value = load('cc_update_url', '');
  syncUpdateUi();
  if (hasBridge()) {
    try { applyAppTheme(JSON.parse(AppBridge.getTheme())); } catch (e) {}
  }
})();
</script>
</body>
</html>
"""


def main(build=None, version=None):
    ver = version or APP_VERSION
    bl = build if build is not None else APP_BUILD
    rows = []
    with open("products.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            rows.append([
                r["name"],
                round(float(r["kcal"]), 1),
                round(float(r["protein"]), 1),
                round(float(r["fat"]), 1),
                round(float(r["carbs"]), 1),
            ])
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", payload)
    html = html.replace("__APP_VERSION__", ver)
    html = html.replace("__APP_BUILD__", str(bl))
    html = html.replace("__UPDATE_URL__", DEFAULT_UPDATE_URL)
    with open("calorie_app.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"calorie_app.html: {len(rows)} продуктов, {len(html.encode('utf-8')) / 1024:.0f} КБ, версия {ver} (сборка {bl})")


if __name__ == "__main__":
    main()
