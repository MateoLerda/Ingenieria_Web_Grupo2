document.addEventListener('DOMContentLoaded', function () {
  
    const form = document.getElementById('purchaseForm');
    if (!form) return;

    const qtyInput = document.getElementById('quantity');
    const maxPerUser = Number(form.dataset.maxPerUser || 1);
    const eventId = String(form.dataset.eventId || '');
    const sectorSelect = document.getElementById('sector');
    const sectorPriceEl = document.getElementById('sectorPrice');
    const getAvailable = () => {
        if (!sectorSelect) return Number.MAX_SAFE_INTEGER;
        let opt = sectorSelect.options[sectorSelect.selectedIndex];
        if (!opt) return Number.MAX_SAFE_INTEGER;
        const val = opt.getAttribute('data-available');
        const n = Number(val);
        if (!Number.isNaN(n) && n >= 0) return n;
        // Fallback: try to read from visible text "(disp: N)"
        const m = (opt.textContent || '').match(/disp:\s*(\d+)/i);
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
        // also update visible label "(disp: N)"
        opt.textContent = (opt.textContent || '').replace(/\(disp:[^)]+\)/i, `(disp: ${newValue})`);
    };

    const getAlreadyBought = () => {
        if (!eventId) return 0;
        const k = `pf_evt_${eventId}_bought`;
        const n = Number(window.localStorage.getItem(k));
        return Number.isFinite(n) && n > 0 ? n : 0;
    };
    const addBought = (delta) => {
        if (!eventId) return;
        const k = `pf_evt_${eventId}_bought`;
        const val = getAlreadyBought() + delta;
        window.localStorage.setItem(k, String(val));
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

    form.addEventListener('submit', function (e) {
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
            alert('Please select at least 1 ticket.');
            return;
        }
        // Límite por compra + acumulado (simulado por navegador)
        const already = getAlreadyBought();
        const remaining = Math.max(maxPerUser - already, 0);
        if (qty > remaining) {
            alert('You cannot buy more than ' + remaining + ' tickets for this event with your account.');
            return;
        }
        const avail = getAvailable();
        if (Number.isFinite(avail) && qty > avail) {
            alert('Not enough tickets available.');
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
        sectorPriceEl.textContent = price ? `Precio por entrada: $${price}` : '';
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

        // Simular compra: actualizar inventario del sector y total, almacenar tickets "comprados"
        const qty = parseInt(qtyInput.value, 10) || 0;
        const availBefore = getAvailable();
        const availAfter = Math.max(availBefore - qty, 0);
        setAvailable(availAfter);
        addBought(qty);

        // Actualizar total de entradas visibles
        const totalEl = document.getElementById('availableTickets');
        if (totalEl) {
            const totalVal = parseInt((totalEl.textContent || '0').replace(/[^0-9]/g, ''), 10) || 0;
            const newTotal = Math.max(totalVal - qty, 0);
            totalEl.textContent = String(newTotal);
        }

        // Redirigir a página de "éxito" simulada
        setTimeout(() => {
            window.location.href = '/purchase_success/';
        }, 1500);
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
