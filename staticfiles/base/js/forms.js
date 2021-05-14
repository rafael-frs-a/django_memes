function focusInput(className) {
    const inputs = document.getElementsByClassName(className)

    if (inputs.length > 0) {
        inputs[0].focus();
        return true;
    }

    return false;
}

if (!focusInput('form-control is-invalid')) {
    focusInput('form-control');
}
