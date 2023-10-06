const { button, input, div, label, p, pre, table, tbody, td, textarea, th, thead, tr, h5, form, iframe } = van.tags

const userInput = input({ type: "text", class: "form-control", id: "username", name: "username", required: "" });
const passwordInput = input({ type: "password", class: "form-control", id: "password", name: "password", required: "" });
const serverInput = input({ type: "text", class: "form-control", id: "server", name: "server", required: "" });
const portInput = input({ type: "text", class: "form-control", id: "port", name: "port", required: "" });
const loginModal = div({ class: "modal fade", id: "loginModal", tabindex: "-1", "aria-labelledby": "loginModalLabel", "aria-hidden": "true" },
    div({ class: "modal-dialog" },
        div({ class: "modal-content" },
            div({ class: "modal-header" },
                h5({ class: "modal-title", id: "loginModalLabel" },
                    "Login",
                ),
                button({ type: "button", class: "btn-close", "data-bs-dismiss": "modal", "aria-label": "Close" }),
            ),
            div({ class: "modal-body" },
                form(
                    div({ class: "mb-3" },
                        label({ for: "username", class: "form-label" },
                            "Username",
                        ),
                        userInput
                    ),
                    div({ class: "mb-3" },
                        label({ for: "password", class: "form-label" },
                            "Password",
                        ),
                        passwordInput
                    ),
                    div({ class: "mb-3" },
                        label({ for: "server", class: "form-label" },
                            "Server",
                        ),
                        serverInput
                    ),
                    div({ class: "mb-3" },
                        label({ for: "port", class: "form-label" },
                            "port",
                        ),
                        portInput
                    )
                )
            ),
            div({ class: "modal-footer" },
                button({ type: "button", class: "btn btn-secondary", "data-bs-dismiss": "modal" },
                    "Close"
                ),
                button({
                    type: "button", class: "btn btn-primary", onclick: async () => {
                        const response = await fetch('/authenticate', {
                            method: 'post',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                email: userInput.value,
                                password: passwordInput.value,
                                server: serverInput.value,
                                port: Number(portInput.value)
                            })
                        });
                        if (response.ok) {
                            await response.text()
                            window.location.reload();
                        }
                    }
                },
                    "Login"
                )
            )
        )
    )
)

function timeSince(date) {

    var seconds = Math.floor((new Date() - date) / 1000);

    var interval = seconds / 31536000;

    if (interval > 1) {
        return Math.floor(interval) + " years";
    }
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + " months";
    }
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + " days";
    }
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + " hours";
    }
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + " minutes";
    }
    return Math.floor(seconds) + " seconds";
}
const envelopsPayload = van.state(null)
const messagePayload = van.state(null)
async function init(search = null) {
    const url = new URL(window.location.protocol + "//" + window.location.host);
    if (search != null && search != "") {
        url.searchParams.append('q', search);
    }
    url.pathname = '/api/mail/inbox';
    const response = await fetch(url);
    if (response.status == 404) {
        document.getElementById('loginNavItemButton').click();
        return false;
    }
    document.getElementById('loginNavItem').hidden = true;
    const json = await response.json();
    envelopsPayload.val = json;
    return true;
}
(async () => { await init(); })();
document.getElementById('searchBtn').addEventListener('click', async () => {
    await init(document.getElementById('searchInput').value);
});


function messageView() {
    if (!messagePayload.val) return div()
    return iframe({ src: messagePayload.val });
}

// const h = window.innerHeight - document.getElementsByClassName('navbar')[0].clientHeight;
// height:${window.innerHeight}px;
const editorCol = div({ class: "col-sm", hidden: true, id: 'editorCol' }, div({ id: 'editor' }));
const viewEmalCol = div({ class: "col-sm", id: 'viewEmailCol' },
    () => {
        if (!messagePayload.val) return div()
        return div({ class: 'ratio ratio-16x9', style: 'height: 100%;' }, iframe({ src: messagePayload.val }));
    }
);
document.getElementById('newMailBtn').addEventListener('click', async () => {
    editorCol.hidden = !editorCol.hidden;
    viewEmalCol.hidden = !viewEmalCol.hidden;
});

const view = div({ class: "container-fluid" },
    div({ class: "row" },
        div({ class: "col-sm", id: 'listEmailsCol', style: `overflow-y: scroll;` }, () => {
            if (!envelopsPayload.val) return div()
            const envelops = envelopsPayload.val;
            let rows = [];
            for (let index = 0; index < envelops.length; index++) {
                const envelop = envelops[index];
                rows.push(tr({
                    onclick: async (ele) => {
                        Array.from(ele.srcElement.parentNode.parentNode.children).forEach(child => {
                            child.classList.remove('table-active');
                        });
                        ele.srcElement.parentNode.classList.add('table-active');
                        messagePayload.val = `/api/mail/inbox/${envelop.uid}`;
                    }
                }, td(envelop.subject), td(timeSince(new Date(envelop.date))))
                );
            }
            // table-dark 
            return table({ class: "table table-striped table-hover table-sm" },
                thead(tr(th('Subject'), th('Date'))
                ), tbody(rows));
        }),
        viewEmalCol,
        editorCol
    ),
)


van.add(document.body, view)
van.add(document.body, loginModal)

var options = {
    placeholder: 'Compose...',
    theme: 'snow'
};

const editor = new Quill(document.getElementById('editor'), options);