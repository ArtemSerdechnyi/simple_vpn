
function submitClosestForm(element) {
    var form = element.closest('form');
    if (form) {
        form.submit();
    }
}