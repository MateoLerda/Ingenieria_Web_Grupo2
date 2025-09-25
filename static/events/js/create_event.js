document.addEventListener('DOMContentLoaded', function(){
    countries = document.getElementById('country-options')

    const flyerInput = document.getElementById('flyerInput');
    const flyerPreview = document.getElementById('flyerPreview');
    if (flyerInput && flyerPreview) {
        flyerInput.addEventListener('change', (e) => {
            const [file] = e.target.files || [];
            if (file) {
                const url = URL.createObjectURL(file);
                flyerPreview.onload = () => {
                    try { URL.revokeObjectURL(url); } catch (_) {}
                };
                flyerPreview.src = url;
            }
        });
    }

    const dateEl = document.getElementById('eventDateInput');
    if (dateEl) {
        const MAX_DATE = '2100-12-31';
        function clamp(){
            if(!dateEl.value) return;
            const v = dateEl.value;
            if(!/^\d{4}-\d{2}-\d{2}$/.test(v)) return;
            const year = parseInt(v.slice(0,4),10);
            if(year > 2100){ dateEl.value = MAX_DATE; }
        }
        dateEl.addEventListener('change', clamp);
        dateEl.addEventListener('blur', clamp);
        dateEl.addEventListener('input', function(){
            const v = dateEl.value;
            if(/^\d{4}$/.test(v)){
                if(parseInt(v,10) > 2100){ dateEl.value = '2100'; }
            }
        });
    }
});