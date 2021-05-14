function activateCurrentNavitem() {
    var items = document.getElementsByClassName('nav-item');

    for (var i = 0; i < items.length; i++) {
        if (window.location.href.startsWith(items[i].querySelector('.nav-link').href)) {
            items[i].classList.add('active-nav-item');
            break;
        }
    }
}

activateCurrentNavitem()

function toggleSortableHeader() {
    const urlParams = new URLSearchParams(window.location.search);
    var sort = urlParams.get('sort');

    if (!sort) {
        return;
    }

    desc = sort.startsWith('-');

    if (desc) {
        sort = sort.substring(1);
    }

    header = document.querySelector(`[data-sort=${sort}]`);

    if (!header) {
        return;
    }

    if (desc) {
        header.classList.add('th-sort-desc');
    }
    else {
        header.classList.add('th-sort-asc');
    }
}

toggleSortableHeader();

document.querySelectorAll('.th-sortable').forEach(header => {
    header.addEventListener('click', () => {
        const url = new URL(window.location.href);
        url.search = new URLSearchParams();
        const urlParams = new URLSearchParams(window.location.search);
        const page = urlParams.get('page');

        if (page) {
            url.searchParams.append('page', page);
        }

        if (header.classList.contains('th-sort-asc')) {
            url.searchParams.append('sort', `-${header.dataset.sort}`);
        } else {
            url.searchParams.append('sort', header.dataset.sort);
        }

        window.location.href = url.href;
    });
});
