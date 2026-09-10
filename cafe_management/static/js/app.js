document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 4s
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(a => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
                bsAlert.close();
            } catch(e) {}
        });
    }, 4000);
});
