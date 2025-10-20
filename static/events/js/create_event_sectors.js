(function(){
  const addBtn = document.getElementById('addSectorBtn');
  const tbody = document.getElementById('sectorsBody');
  const template = document.getElementById('sectorRowTemplate');
  const sectorError = document.getElementById('sectorError');

  function bindRemoveButtons(scope){
    (scope || document).querySelectorAll('.remove-sector').forEach(btn => {
      btn.addEventListener('click', () => {
        const tr = btn.closest('tr');
        if (tr && tbody.rows.length > 1) {
          tr.remove();
        }
      });
    });
  }

  function showError(){
    if (sectorError) {
      sectorError.classList.remove('d-none');
    }
  }

  function hideError(){
    if (sectorError) {
      sectorError.classList.add('d-none');
    }
  }

  // Prevent submitting without any sector rows (or with empty names)
  document.addEventListener('submit', function(e){
    const form = e.target;
    if (!form || !tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const validRows = rows.filter(tr => {
      const name = tr.querySelector('input[name="sector_name"]');
      return name && name.value.trim().length > 0;
    });
    if (validRows.length === 0) {
      e.preventDefault();
      showError();
    } else {
      hideError();
    }
  }, true);

  if(addBtn && tbody && template){
    addBtn.addEventListener('click', () => {
      const clone = document.importNode(template.content, true);
      tbody.appendChild(clone);
      bindRemoveButtons(tbody);
      hideError();
    });

    bindRemoveButtons();
  }
})();
