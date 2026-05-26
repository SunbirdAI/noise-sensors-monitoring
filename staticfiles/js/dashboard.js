/**
 * Column selector for device health tables.
 *
 * initColumnSelector(wrapperId, tableId, storageKey, defaultCols)
 *   wrapperId   – id of the .col-selector-wrap element
 *   tableId     – id of the <table> element
 *   storageKey  – localStorage key for persisting choices
 *   defaultCols – array of data-col values that should be visible by default
 */
function initColumnSelector(wrapperId, tableId, storageKey, defaultCols) {
  var wrap = document.getElementById(wrapperId);
  var table = document.getElementById(tableId);
  if (!wrap || !table) return;

  var toggleBtn = wrap.querySelector('.col-selector-toggle');
  var menu = wrap.querySelector('.col-selector-menu');
  var checkboxes = wrap.querySelectorAll('input[data-col]');

  // Load persisted state or fall back to defaults
  var saved = null;
  try {
    var raw = localStorage.getItem(storageKey);
    if (raw) saved = JSON.parse(raw);
  } catch (e) {}

  var active = saved || defaultCols.slice();

  // Apply checked state to checkboxes
  checkboxes.forEach(function (cb) {
    cb.checked = active.indexOf(cb.dataset.col) !== -1;
  });

  // Apply column visibility to the table
  applyVisibility();

  // Toggle menu open / closed
  toggleBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    var isOpen = !menu.hidden;
    menu.hidden = isOpen;
    toggleBtn.setAttribute('aria-expanded', String(!isOpen));
  });

  // Close menu when clicking outside
  document.addEventListener('click', function (e) {
    if (!wrap.contains(e.target)) {
      menu.hidden = true;
      toggleBtn.setAttribute('aria-expanded', 'false');
    }
  });

  // React to checkbox changes
  checkboxes.forEach(function (cb) {
    cb.addEventListener('change', function () {
      var col = cb.dataset.col;
      if (cb.checked) {
        if (active.indexOf(col) === -1) active.push(col);
      } else {
        active = active.filter(function (c) { return c !== col; });
      }
      applyVisibility();
      try {
        localStorage.setItem(storageKey, JSON.stringify(active));
      } catch (e) {}
    });
  });

  function applyVisibility() {
    // Gather all data-col th/td pairs
    var allCols = table.querySelectorAll('th[data-col], td[data-col]');
    allCols.forEach(function (cell) {
      var col = cell.dataset.col;
      cell.style.display = active.indexOf(col) !== -1 ? '' : 'none';
    });
  }
}
