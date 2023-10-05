const { button, input, div, label, p, pre, table, tbody, td, textarea, th, thead, tr } = van.tags

const TableViewer = () => {
    const autoGrow = e => {
        e.style.height = "5px"
        e.style.height = (e.scrollHeight + 5) + "px"
    }

    const textareaDom = textarea({ oninput: e => autoGrow(e.target) }, '')
    setTimeout(() => autoGrow(textareaDom), 10)
    fetch('/inbox/').then(response => response.text()).then(data => {
        textareaDom.value = data
        console.log(data)
    }).catch(error => console.error(error));

    const text = van.state("")

    const tableFromJson = text => {
        const json = JSON.parse(text), head = Object.keys(json[0])
        return {
            head,
            data: json.map(row => head.map(h => row[h]))
        }
    }

    return div(
        div(textareaDom),
        div(button({ onclick: () => text.val = textareaDom.value }, "Show Table")),
        p(() => {
            if (!text.val) return div()
            try {
                const { head, data } = tableFromJson(text.val)
                return table(
                    thead(tr(head.map(h => th(h)))),
                    tbody(data.map(row => tr(row.map(col => td(col))))),
                )
            } catch (e) {
                return pre({ class: "err" }, e.toString())
            }
        }),
    )
}

van.add(document.body, TableViewer())
