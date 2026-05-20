// Sidebar toggle
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    }
    // Auto-dismiss toasts
    document.querySelectorAll('.toast').forEach(t => {
        setTimeout(() => { t.classList.remove('show'); }, 4000);
    });
    // Dept → Program AJAX
    const deptSelect = document.getElementById('id_department');
    const programSelect = document.getElementById('id_program');
    if (deptSelect && programSelect) {
        deptSelect.addEventListener('change', function () {
            fetch('/accounts/ajax/programs/?department_id=' + this.value)
                .then(r => r.json())
                .then(data => {
                    programSelect.innerHTML = '<option value="">---------</option>';
                    data.programs.forEach(p => {
                        programSelect.innerHTML += `<option value="${p.id}">${p.name}</option>`;
                    });
                });
        });
    }
});
