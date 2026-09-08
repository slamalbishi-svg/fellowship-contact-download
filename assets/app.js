// iOS Safari needs a touch listener for :active on taps.
document.querySelectorAll('.btn, .btn-row').forEach(function (b) {
  b.addEventListener('touchstart', function () {}, { passive: true });
});

// Simple RTL contact table (# | name | إضافة) from window.FELLOWSHIP_CONTACTS.
(function () {
  var list = document.getElementById('contactList');
  var empty = document.getElementById('contactEmpty');
  var search = document.getElementById('contactSearch');
  var contacts = window.FELLOWSHIP_CONTACTS || [];
  if (!list || !contacts.length) return;

  function arabicNum(n) {
    var d = '٠١٢٣٤٥٦٧٨٩';
    return String(n).replace(/[0-9]/g, function (x) { return d[+x]; });
  }
  // normalize for tolerant Arabic search (hamza/alef/taa marbuta/spaces)
  function norm(s) {
    return (s || '')
      .replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
      .replace(/[\u064B-\u0652]/g, '').replace(/\s+/g, ' ').trim();
  }

  var rows = contacts.map(function (c, i) {
    var li = document.createElement('li');
    li.className = 'contact-row';

    var num = document.createElement('span');
    num.className = 'row-num';
    num.textContent = arabicNum(i + 1);

    var name = document.createElement('span');
    name.className = 'contact-name';
    name.textContent = c.name;
    name.title = c.name;

    var link = document.createElement('a');
    link.className = 'btn-row';
    link.href = c.file;
    link.setAttribute('download', c.name + '.vcf');
    link.setAttribute('aria-label', 'إضافة ' + c.name + ' إلى جهات الاتصال');
    link.innerHTML = '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      '<path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>' +
      '</svg><span>إضافة</span>';
    link.addEventListener('touchstart', function () {}, { passive: true });

    li.appendChild(num);
    li.appendChild(name);
    li.appendChild(link);
    list.appendChild(li);
    return { el: li, key: norm(c.name) };
  });

  if (!search) return;
  search.addEventListener('input', function () {
    var q = norm(search.value);
    var visible = 0;
    rows.forEach(function (row) {
      var match = q === '' || row.key.indexOf(q) !== -1;
      row.el.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    empty.hidden = visible !== 0;
  });
})();
