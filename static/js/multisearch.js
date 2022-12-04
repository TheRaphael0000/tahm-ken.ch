let text_area_multisearch = document.querySelector("#text_area_lobby")
let btn_multisearch = document.querySelector("#btn_multisearch")
let select_region = document.querySelector("#select_region")

// need all the languages here, PR if possible :) or send me a message on the discord server
let ignored_text = [
    /* en */ " joined the lobby",
    /* de */ " ist der Lobby beigetreten",
    /* es */ " se ha unido a la sala.",
    /* fr */ " a rejoint le salon",
    /* it */ " si è unito alla lobby",
]

text_area_multisearch.addEventListener("paste", e => {
    e.preventDefault()
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    let lines = paste.split("\n")

    let current_summoners = e.target.value.split("\n").filter(i => i != "")
    let summoners_names = new Set(current_summoners)

    for (let l of lines) {
        for (let j of ignored_text) {
            if (l.includes(j)) {
                let name = l.replace(j, "").replace("\r", "").replace("\n", "")
                summoners_names.add(name)
                break
            }
        }
    }

    e.target.value = Array(...summoners_names).join("\n")
})

btn_multisearch.addEventListener("click", function () {
    let url = "/multisearch/" + select_region.value + "/" + text_area_multisearch.value.split("\n").join(",")
    window.location.href = url
})