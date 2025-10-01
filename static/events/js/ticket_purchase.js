document.addEventListener('DOMContentLoaded', function () {
  
    const form = document.getElementById('purchaseForm');
    if (!form) return;

    const qtyInput = document.getElementById('quantity');
    const maxPerUser = Number(form.dataset.maxPerUser || 1);
    const available = Number(form.dataset.availableTickets || 0);

    // Bootstrap modal
    const modalEl = document.getElementById('confirmPurchaseModal');
    if (!modalEl) return;
    const bsModal = new bootstrap.Modal(modalEl, { keyboard: true });

    const confirmQuantitySpan = document.getElementById('confirmQuantity');
    const confirmText = document.getElementById('confirmText');
    const confirmWarning = document.getElementById('confirmWarning');
    const modalConfirmBtn = document.getElementById('modalConfirm');

    let submitting = false;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (submitting) return;

        const qty = parseInt(qtyInput.value, 10) || 0;

        // Validaciones en cliente
        if (qty < 1) {
            alert('Please select at least 1 ticket.');
            return;
        }
        if (qty > maxPerUser) {
            alert('You cannot buy more than ' + maxPerUser + ' tickets.');
            return;
        }
        if (qty > available) {
            alert('Not enough tickets available.');
            return;
        }

        confirmQuantitySpan.textContent = qty;
        confirmText.textContent = `Are you sure you want to buy ${qty} ticket${qty > 1 ? 's' : ''}?`;
        confirmWarning.textContent = '';

        bsModal.show();
    });

    modalConfirmBtn.addEventListener('click', function () {
        if (submitting) return;
        submitting = true;
        modalConfirmBtn.disabled = true;
        document.getElementById('buyBtn').disabled = true;

        bsModal.hide();

        const overlay = document.createElement('div');
        overlay.id = 'processingOverlay';
        overlay.innerHTML = `
    <div class="processing-container">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3">Procesando compra...</p>
    </div>
  `;
        document.body.appendChild(overlay);

        // Esperar 3 segundos y enviar form
        setTimeout(() => {
            form.submit();
        }, 3000);
    });

    modalEl.addEventListener('hidden.bs.modal', function () {
        if (!submitting) {
            modalConfirmBtn.disabled = false;
            document.getElementById('buyBtn').disabled = false;
        }
    });
});

window.addEventListener('pageshow', function () {
  const overlay = document.getElementById('processingOverlay');
  if (overlay) overlay.remove();

  const buyBtn = document.getElementById('buyBtn');
  if (buyBtn) buyBtn.disabled = false;

  const modalConfirmBtn = document.getElementById('modalConfirm');
  if (modalConfirmBtn) modalConfirmBtn.disabled = false;
});