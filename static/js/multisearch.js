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

text_area_multisearch.addEventListener("input", function (e) {
    let lines = e.target.value.split("\n")
    let cleared_lines = []
    for (let l of lines) {
        let has = false
        for (let j of ignored_text) {
            if (l.includes(j)) {
                has = true
                cleared_lines.push(l.replace(j, ""))
                break
            }
        }
        // push the uncleard
        if (!has) {
            cleared_lines.push(l)
        }
    }
    e.target.value = cleared_lines.join("\n")
})

btn_multisearch.addEventListener("click", function () {
    let url = "/multisearch/" + select_region.value + "/" + text_area_multisearch.value.split("\n").join(",")
    window.location.href = url
})