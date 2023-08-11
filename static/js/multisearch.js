let text_area_multisearch = document.querySelector("#text_area_lobby")
let btn_multisearch = document.querySelector("#btn_multisearch")
let select_region = document.querySelector("#select_region")

// thanks to DarkIntaqt: https://discord.com/channels/187652476080488449/379429593829867521/1139574848134332416
let ignored_text = [
    ",",
    "\n",
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
    " lobiye katıldı"
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