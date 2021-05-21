$(function() {
    $('[data-toggle="popover"]').popover();
})

window.addEventListener('mouseup', function(e) {
    target = e.target;

    while (target) {
        if (target.id === 'posts-info-button') {
            return
        }

        target = target.parentElement;
    }

    $('[data-toggle="popover"]').popover('hide');
})
