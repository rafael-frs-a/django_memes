const sentinel_template = document.querySelector('#sentinel-template').content.cloneNode(true);
document.body.appendChild(sentinel_template);

const postsContainer = document.querySelector('#posts-container');
const postTemplate = document.querySelector('#post-template');
const noPostTemplate = document.querySelector('#no-post-template');
const templateWaitingModeration = document.querySelector('#waiting-moderation-info');
const templateModerating = document.querySelector('#moderating-info');
const templateDenied = document.querySelector('#denied-info');
const templateApproved = document.querySelector('#approved-info');
const sentinel = document.querySelector('#sentinel');
var page = 1;
const date = new Date();
const timezone = date.getTimezoneOffset();
var fetching = false;

function loadPosts() {
    fetch(`${window.location.pathname}?page=${page}&timezone=${timezone}`).then((response) => {
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
                templatePost.querySelector('.meme-preview').src = data.posts[i].meme_url;
                templatePost.querySelector('.post-created-at').innerText = data.posts[i].post_created_at;

                if (data.posts[i].is_waiting_moderation) {
                    templateStatus = templateWaitingModeration.content.cloneNode(true);
                } else if (data.posts[i].is_moderating) {
                    templateStatus = templateModerating.content.cloneNode(true);
                    templateStatus.querySelector('.status-create-at').innerText = data.posts[i].status_created_at;
                } else if (data.posts[i].is_denied) {
                    templateStatus = templateDenied.content.cloneNode(true);
                    templateStatus.querySelector('.status-created-at').innerText = data.posts[i].status_created_at;
                    templateStatus.querySelector('.denial-reason').innerText = data.posts[i].denial_reason;
                    templateStatus.querySelector('.denial-details').innerText = data.posts[i].denial_details;
                } else {
                    templateStatus = templateApproved.content.cloneNode(true);
                    templateStatus.querySelector('.status-created-at').innerText = data.posts[i].status_created_at;
                }

                postContainer = templatePost.querySelector('.post-container');
                postContainer.appendChild(templateStatus);
                postsContainer.appendChild(templatePost);
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
