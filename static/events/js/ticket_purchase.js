document.addEventListener('DOMContentLoaded', function () {
  
    const form = document.getElementById('purchaseForm');
    if (!form) return;

    const qtyInput = document.getElementById('quantity');
    const maxPerUser = Number(form.dataset.maxPerUser || 1);
    const eventId = String(form.dataset.eventId || ''); // optional; not required for client checks
    const sectorSelect = document.getElementById('sector');
    const sectorPriceEl = document.getElementById('sectorPrice');
    const subtotalEl = document.getElementById('subtotal');
    const totalEl = document.getElementById('total');
    const decreaseBtn = document.getElementById('decreaseQty');
    const increaseBtn = document.getElementById('increaseQty');

    const getAvailable = () => {
        if (!sectorSelect) return Number.MAX_SAFE_INTEGER;
        let opt = sectorSelect.options[sectorSelect.selectedIndex];
        if (!opt) return Number.MAX_SAFE_INTEGER;
        const val = opt.getAttribute('data-available');
        const n = Number(val);
        if (!Number.isNaN(n) && n >= 0) return n;
        const m = (opt.textContent || '').match(/(\d+)\s+available/i);
        if (m) {
            const parsed = Number(m[1]);
            if (!Number.isNaN(parsed)) return parsed;
        }
        // If we cannot infer it, do not block on client-side
        return Number.MAX_SAFE_INTEGER;
    };

    const setAvailable = (newValue) => {
        if (!sectorSelect) return;
        const opt = sectorSelect.options[sectorSelect.selectedIndex];
        if (!opt) return;
        opt.setAttribute('data-available', String(newValue));
        // also update visible label
        opt.textContent = opt.textContent.replace(/\d+\s+available/i, `${newValue} available`);
    };

    const getCurrentPrice = () => {
        if (!sectorSelect) return 0;
        const opt = sectorSelect.options[sectorSelect.selectedIndex];
        if (!opt) return 0;
        const price = opt.getAttribute('data-price');
        return Number(price) || 0;
    };

    const updateTotals = () => {
        const qty = parseInt(qtyInput.value, 10) || 0;
        const price = getCurrentPrice();
        const total = qty * price;
        
        if (subtotalEl) subtotalEl.textContent = `$${total.toFixed(2)}`;
        if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
    };

    // Quantity buttons
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            const currentQty = parseInt(qtyInput.value, 10) || 1;
            if (currentQty > 1) {
                qtyInput.value = currentQty - 1;
                updateTotals();
            }
        });
    }

    if (increaseBtn) {
        increaseBtn.addEventListener('click', function() {
            const currentQty = parseInt(qtyInput.value, 10) || 1;
            const max = Math.min(maxPerUser, getAvailable());
            if (currentQty < max) {
                qtyInput.value = currentQty + 1;
                updateTotals();
            }
        });
    }

    // Update totals when quantity changes
    if (qtyInput) {
        qtyInput.addEventListener('input', updateTotals);
    }

    // Server is the source of truth; optionally the template can provide data-already-bought
    const getAlreadyBought = () => {
        const n = Number(form.dataset.alreadyBought || 0);
        return Number.isFinite(n) && n > 0 ? n : 0;
    };
    const redirectLogin = form.dataset.redirectLogin;

    // Bootstrap modal
    const modalEl = document.getElementById('confirmPurchaseModal');
    if (!modalEl) return;
    const bsModal = new bootstrap.Modal(modalEl, { keyboard: true });

    const confirmQuantitySpan = document.getElementById('confirmQuantity');
    const confirmText = document.getElementById('confirmText');
    const confirmWarning = document.getElementById('confirmWarning');
    const modalConfirmBtn = document.getElementById('modalConfirm');

    let submitting = false;

    // Helper to show feedback messages in a Bootstrap modal
    function showFeedback(message) {
        const modalEl = document.getElementById('feedbackModal');
        const bodyEl = document.getElementById('feedbackModalBody');
        if (!modalEl || !bodyEl) { window.alert(message); return; }
        bodyEl.textContent = message;
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl, { keyboard: true });
        modal.show();
    }

    form.addEventListener('submit', function (e) {
        // If already confirmed, allow the browser to submit normally to server
        if (form.dataset.confirmed === '1') {
            return;
        }
        e.preventDefault();
        if (submitting) return;

        if (redirectLogin) {
            const url = new URL(redirectLogin, window.location.origin);
            window.location.href = url.toString();
            return;
        }

        const qty = parseInt(qtyInput.value, 10) || 0;

        // Validaciones en cliente (suaves; el servidor valida en forma definitiva)
        if (qty < 1) {
            showFeedback('Please select at least 1 ticket.');
            return;
        }
        // Límite por compra + acumulado (simulado por navegador)
        const already = getAlreadyBought();
        const remaining = maxPerUser - already;
        if (remaining == 0) {
            showFeedback('You cannot buy more tickets for this event.')
            return;
        }

        if (qty > remaining) {
            showFeedback(`You have left only ${remaining} tickets to buy.`);
            return;
        }

        const avail = getAvailable();
        if (Number.isFinite(avail) && qty > avail) {
            showFeedback('Not enough tickets available.');
            return;
        }

        confirmQuantitySpan.textContent = qty;
        confirmText.textContent = `Are you sure you want to buy ${qty} ticket${qty > 1 ? 's' : ''}?`;
        confirmWarning.textContent = '';

        bsModal.show();
    });

    function refreshPriceHint(){
        if (!sectorSelect || !sectorPriceEl) return;
        const opt = sectorSelect.options[sectorSelect.selectedIndex];
        const price = opt ? opt.getAttribute('data-price') : null;
        sectorPriceEl.textContent = price ? `Price per ticket: $${price}` : '';
        updateTotals();
    }

    if (sectorSelect) {
        // Auto-seleccionar el primer sector válido si no hay selección
        if (sectorSelect.selectedIndex <= 0 && sectorSelect.options.length > 0) {
            for (let i = 0; i < sectorSelect.options.length; i++) {
                const o = sectorSelect.options[i];
                if (!o.disabled && o.value) { sectorSelect.selectedIndex = i; break; }
            }
        }
        sectorSelect.addEventListener('change', function(){
            qtyInput.value = '1';
            refreshPriceHint();
        });
        refreshPriceHint();
    }

        modalConfirmBtn.addEventListener('click', async function () {
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
            <p class="mt-3">Processing purchase...</p>
    </div>
  `;
        document.body.appendChild(overlay);
                // Submit via fetch to avoid full page reload and capture messages
                try {
                    const formData = new FormData(form);
                    const resp = await fetch(form.action, {
                        method: 'POST',
                        headers: { 'X-Requested-With': 'XMLHttpRequest' },
                        body: formData,
                        credentials: 'same-origin'
                    });
                    const data = await resp.json();
                    if (resp.ok && data && data.ok) {
                        // Update UI counts (defensive, server remains source of truth)
                        const qty = parseInt(qtyInput.value, 10) || 0;
                        const availBefore = getAvailable();
                        const availAfter = Math.max(availBefore - qty, 0);
                        setAvailable(availAfter);
                        const totalEl = document.getElementById('availableTickets');
                        if (totalEl) {
                            const totalVal = parseInt((totalEl.textContent || '0').replace(/[^0-9]/g, ''), 10) || 0;
                            const newTotal = Math.max(totalVal - qty, 0);
                            totalEl.textContent = String(newTotal);
                        }
                        window.location.href = data.redirect || '/purchase_success/';
                    } else {
                        const message = (data && data.error) ? data.error : 'Purchase failed. Please try again.';
                        showFeedback(message);
                    }
                } catch (err) {
                    showFeedback('Network error. Please try again.');
                } finally {
                    const overlayNow = document.getElementById('processingOverlay');
                    if (overlayNow) overlayNow.remove();
                    submitting = false;
                    modalConfirmBtn.disabled = false;
                    document.getElementById('buyBtn').disabled = false;
                }
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
