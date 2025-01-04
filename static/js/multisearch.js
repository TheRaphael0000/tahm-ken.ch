let text_area_multisearch = document.querySelector("#text_area_lobby")
let btn_multisearch = document.querySelector("#btn_multisearch")
let select_region = document.querySelector("#select_region")

// thanks to DarkIntaqt: https://discord.com/channels/187652476080488449/379429593829867521/1139574848134332416
let ignored_text = [
    "⁦⁦",
    "⁩ ",
    "⁦",
    "⁩⁩",
    ",",
    "\n",
    "\r",
    ":",
    " 님이 방에 참가했습니다.",
    " 님이 그룹에 참여했습니다.",
    " 님이 로비에 참가하셨습니다.",
    " 進入組隊房間",
    " 加入了队伍聊天",
    " が入室しました。",
    " がロビーに参加しました",
    " joined the room",
    " joined the lobby",
    " joined the group",
    " a rejoint la salle",
    " a rejoint le salon",
    " hat den Chatraum betreten",
    " ist der Lobby beigetreten",
    " dołączył do pokoju",
    " dołącza do pokoju",
    " vstoupil do lobby",
    " μπήκε στο δωμάτιο",
    " μπήκε στο λόμπι",
    " присоединился к лобби",
    " \xe8 entrato nella stanza",
    " a intrat \xeen sală",
    " entr\xf3 en la sala",
    " entr\xf3 a la sala",
    " entrou no sagu\xe3o",
    " entrou na sala",
    " entrou no sagu\xe3o",
    " se ha unido a la sala",
    " se uni\xf3 a la sala",
    " odaya katıldı",
    " lobiye katıldı",
]

let search_summoners = (summoners_names) => {
    btn_multisearch.classList.add("disabled")
    let summoners_args = summoners_names.join(",").replaceAll("#", "-")
    let url = `/multisearch/${select_region.value}/${summoners_args}`
    window.location.href = url
}

text_area_multisearch.addEventListener("paste", (event) => {
    event.preventDefault()

    // load the current paste
    let paste = (event.clipboardData || window.clipboardData).getData("text")

    //change the current paste with summoner's name if present
    let lines = paste.split("\n")
    let summoners_names = new Set()
    for (let l of lines) {
        let prefix = " : "
        let substr = l.substring(0, prefix.length)
        if (substr === prefix) {
            continue
        }

        for (let j of ignored_text) {
            if (l.includes(j)) {
                l = l.replace(j, "")
            }
        }

        if (l) {
            summoners_names.add(l)
        }
    }
    if (summoners_names.size > 0) {
        paste = Array(...summoners_names).join("\n")
    }

    // handle selection
    const selectionStart = text_area_multisearch.selectionStart
    const selectionEnd = text_area_multisearch.selectionEnd
    const currentValue = text_area_multisearch.value
    const modifiedValue = currentValue.substring(0, selectionStart) + paste + currentValue.substring(selectionEnd)
    text_area_multisearch.value = modifiedValue
    const newPosition = selectionStart + paste.length
    text_area_multisearch.setSelectionRange(newPosition, newPosition)

    // If someone pasted a complete set of 5 names, no reason for them to click the button, we start the search
    if (summoners_names.size === 5) {
        search_summoners(Array.from(summoners_names))
    }
})

btn_multisearch.addEventListener("click", function () {
    let summoners_names = text_area_multisearch.value
        .split("\n")
        // filter out empty lines
        .filter((str) => str)
    search_summoners(summoners_names)
})
