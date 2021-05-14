const sentinel_template = document.querySelector('#sentinel-template').content.cloneNode(true);
document.body.appendChild(sentinel_template);

const postsContainer = document.querySelector('#posts-container');
const postTemplate = document.querySelector('#post-template');
const noPostTemplate = document.querySelector('#no-post-template');
const tagTemplate = document.querySelector('#tag-template');
var sentinel = document.querySelector('#sentinel');
var page = 1;
var fetching = false;
var filter = '';

function loadPosts() {
    fetch(`${window.location.pathname}?page=${page}&search=${filter}`).then((response) => {
        response.json().then((data) => {
            fetching = false;

            if (page === 1 && !data.posts.length) {
                const template = noPostTemplate.content.cloneNode(true);
                postsContainer.appendChild(template);
                intersectionObserver.disconnect();
                sentinel.remove();
                return;
            }

            for (var i = 0; i < data.posts.length; i++) {
                const templatePost = postTemplate.content.cloneNode(true);
                templatePost.querySelector('.author-img').src = data.posts[i].profile_pic_url;
                templatePost.querySelector('.author-username').innerText = data.posts[i].author;
                templatePost.querySelector('.meme-preview').src = data.posts[i].meme_url;
                templatePost.querySelector('.post-link').href = data.posts[i].post_link;
                const tagsContainer = templatePost.querySelector('.tags-container');

                for (var j = 0; j < data.posts[i].tags.length; j++) {
                    const templateTag = tagTemplate.content.cloneNode(true);
                    templateTag.querySelector('.post-tag').innerText = data.posts[i].tags[j];
                    tagsContainer.appendChild(templateTag);
                }

                postsContainer.appendChild(templatePost);
                const last = postsContainer.children.length - 1;
                author_links = postsContainer.children[last].getElementsByClassName('author-link');

                for (var j = 0; j < author_links.length; j++) {
                    author_links[j].href = data.posts[i].author_link;
                }
            }

            page += 1;

            if (!data.has_next) {
                sentinel.innerHTML = 'No more memes';
            }
        });
    });
}

const intersectionObserver = new IntersectionObserver(entries => {
    if (fetching || entries[0].intersectionRation <= 0) {
        return;
    }

    fetching = true;
    loadPosts();
});

intersectionObserver.observe(sentinel);

$('.search-form').on('submit', function(event) {
    event.preventDefault();
    intersectionObserver.disconnect();

    if (sentinel) {
        sentinel.remove();
    }

    var noPost = document.querySelector('.container-msg');

    if (noPost) {
        noPost.remove();
    }

    var postContainer = document.querySelector('.post-container');

    while (postContainer) {
        postContainer.remove();
        postContainer = document.querySelector('.post-container');
    }

    sentinelTemplate = document.querySelector('#sentinel-template').content.cloneNode(true);
    document.body.appendChild(sentinelTemplate);
    sentinel = document.querySelector('#sentinel');
    page = 1;
    fetching = false;
    filter = document.querySelector('#search-input').value;
    intersectionObserver.observe(sentinel);
});

$(function() {
    $('[data-toggle="popover"]').popover();
})

window.addEventListener('mouseup', function(e) {
    target = e.target;

    while (target) {
        if (target.id === 'search-info-button') {
            return
        }

        target = target.parentElement;
    }

    $('[data-toggle="popover"]').popover('hide');
})
