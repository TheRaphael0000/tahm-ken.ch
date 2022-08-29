let table_challenges = document.querySelectorAll(".table_challenges")
let champion_img = document.querySelectorAll(".champion_img")
let challenge_cb = document.querySelectorAll(".challenge_cb")
let challenge_tr = document.querySelectorAll(".challenge_tr")
let challenge_no = document.querySelectorAll(".challenge_no")
let champion_role = document.querySelectorAll(".champion_role")
let challenges_select = document.querySelectorAll(".challenges_select")
let btn_reset_filters = document.querySelector("#btn_reset_filters")
let btn_reset_selection = document.querySelector("#btn_reset_selection")
let btn_search_champion = document.querySelector("#btn_search_champion")
let btn_copy = document.querySelector("#btn_copy")
let region = document.querySelector("#region")
let summoner = document.querySelector("#summoner")
let search = document.querySelector("#search")
let search_champion = document.querySelector("#search_champion")

let role_mapping = {
    "top": "top",
    "jungle": "jungle",
    "mid": "middle",
    "bottom": "bottom",
    "support": "utility",
}

let table = new Tablesort(table_challenges[0], {
    descending: true
})

function updateChampionsStyle() {
    for (let img of champion_img) {
        if (img.dataset.checked == "1") {
            img.classList.add("checked");
        }
        else {
            img.classList.remove("checked");
        }

        if (img.dataset.selected == "1") {
            img.classList.add("selected");
        }
        else {

            img.classList.remove("selected");
        }
    }
}

function setChampionsChecked(value) {
    for (let img of champion_img) {
        img.dataset.checked = value
    }
    updateChampionsStyle()
}

function setChampionsSelected(value) {
    for (let img of champion_img) {
        img.dataset.selected = value
    }
    updateChampionsStyle()
}

function resetChallenge() {
    fetch_intersection("none")
    for (let c of challenge_cb) {
        c.checked = false
    }
    for (let c of challenge_tr) {
        c.classList.add("checked")
    }
}

function resetSelection() {
    for (let c of challenge_tr) {
        c.classList.remove("selected")
    }
    setChampionsSelected("0")
    updateChampionsSelection()
    resetRoles()
}

function resetRoles() {
    for (let c of champion_role) {
        c.src = ""
    }
}

function reset() {
    resetChallenge()
    resetSelection()
}

function challengeChanged(e) {
    let checked_challenges = document.querySelectorAll(".challenge_cb:checked")
    let ids = []
    for (let cc of checked_challenges) {
        let id_ = cc.dataset.id
        let select = document.getElementById("challenge_select_" + id_)
        if (select) {
            id_ = id_ + ":" + select.selectedIndex
        }

        ids.push(id_)
    }

    if (ids.length <= 0) {
        resetChallenge()
        return
    }

    fetch_intersection(ids)
}

function fetch_intersection(ids) {
    fetch("/intersection/" + ids)
        .then((response) => {
            return response.json()
        })
        .then((json) => {
            setChampionsChecked("0")
            for (let c of json.intersection) {
                let img = document.getElementById("champion_" + c)
                img.dataset.checked = "1"
            }

            for (const [challenge, no] of json.challenges_additional_intersection) {
                let challenge_split = challenge.split(":")
                let id = challenge_split[0]
                let subid = parseInt(challenge_split[1])

                let select = document.getElementById("challenge_select_" + id)
                if (select) {
                    if (select.selectedIndex != subid) {
                        continue
                    }
                }
                let challenge_no = document.getElementById("challenge_no_" + id)

                challenge_no.innerHTML = no
            }

            updateChampionsStyle()

            if (table.current == document.querySelector("#column_qte")) {
                table.refresh()
            }
        })
}


function copyCurrentComp() {
    let selectedChampionName = getSelectedChampionsName(false)
    navigator.clipboard.writeText(selectedChampionName.join(", "))
}

function getSelectedChampions() {
    let selectedChampions = [];
    for (let img of champion_img) {
        if (img.dataset.selected == "1") {
            selectedChampions.push(img)
        }
    }
    return selectedChampions
}

function getSelectedChampionsName(id) {
    let selectedChampions = getSelectedChampions()
    let selectedChampionName = []
    for (let s of selectedChampions)
        if (id == true)
            selectedChampionName.push(s.dataset.champion_name)
        else
            selectedChampionName.push(s.dataset.champion_display_name)
    return selectedChampionName
}

function canSelectChampion() {
    selectedChampions = getSelectedChampions()
    return selectedChampions.length < 5
}

function selectChampion(e) {
    if (e.dataset.selected == "1") {
        e.dataset.selected = "0"
        updateChampionsSelection()
        updateChampionsStyle()
        resetRoles()
        return
    }

    if (canSelectChampion()) {
        e.dataset.selected = "1"
        if (getSelectedChampions().length >= 5)
            best_fit_roles()
    }

    updateChampionsSelection()
    updateChampionsStyle()


}

function updateChampionsSelection() {
    selectedChampionName = getSelectedChampionsName(true)
    fetch_challenges(selectedChampionName)
}


function fetch_challenges(selectedChampionName) {
    let champions = "null"

    if (selectedChampionName.length > 0)
        champions = selectedChampionName.join(",")

    fetch("/champions_selected/" + champions)
        .then((response) => {
            return response.json()
        })
        .then((json) => {
            for (const challenge in json) {
                let champions = json[challenge]
                let challenge_tr = document.querySelector("#challenge_tr_" + challenge)
                let champion_selected = document.querySelector("#champion_selected_" + challenge)
                let champion_placeholder = document.querySelector(".champion_placeholder")

                champion_selected.innerHTML = ""
                let requirements = parseInt(challenge_tr.dataset.requirements)

                for (let i = 0; i < 5; i++) {
                    if (i < champions.length) {
                        let champion = champions[i]
                        let img = document.createElement("img")
                        img.src = "/static/datadragon_cache/champions_img/" + champion + ".png"
                        img.classList.add("challenge_selection_img")
                        champion_selected.appendChild(img)
                    } else {
                        if (i >= requirements)
                            break
                        let svg = champion_placeholder.cloneNode(true)
                        svg.style.display = "inline-block"
                        champion_selected.appendChild(svg)
                    }
                }

                if (champions.length >= requirements)
                    challenge_tr.classList.add("selected")
                else
                    challenge_tr.classList.remove("selected")
            }
        })
}


btn_reset_filters.addEventListener("click", resetChallenge)
btn_reset_selection.addEventListener("click", resetSelection)
btn_search_champion.addEventListener("click", e => search_champion.focus())

reset()

for (let cbc of challenge_cb) {
    cbc.addEventListener('change', challengeChanged)
}

for (let s of challenges_select) {
    s.addEventListener('change', challengeChanged)
}

btn_copy.addEventListener("click", copyCurrentComp)

for (let c of champion_img) {
    c.addEventListener("click", function (e) {
        selectChampion(e.target)
    })

    c.addEventListener("mouseenter", function (e) {
        if (canSelectChampion()) {
            e.target.classList.add("selected");
        }
    })
    c.addEventListener("mouseleave", function (e) {
        updateChampionsStyle()
    })
}

// search summmoner logic
function search_summoner() {
    if (summoner.value.length > 0) {
        window.location.href = "/challenges_intersection/" + region.value + "/" + summoner.value
    }
}

summoner.addEventListener("keydown", (event) => {
    if (event.key === 'Enter') {
        search_summoner()
    }
})

search.addEventListener("click", search_summoner)

function clear_out() {
    search_champion.value = ""
    search_champion.blur()

    for (let c of champion_img) {
        c.style.display = "block"
    }
    return false
}

document.addEventListener("keydown", function (e) {
    if (document.activeElement.id == "summoner") {
        return
    }
    if (e.key.length <= 1) {
        search_champion.focus()
    }
    if (["Escape"].includes(e.key)) {
        clear_out()
    }
})

search_champion.addEventListener("input", function (e) {
    if (e.target.value.length <= 0) {
        return clear_out()
    }

    for (let c of champion_img) {
        c.style.display = "none"
    }
    for (let c of champion_img) {
        if (c.dataset.champion_display_name.toLowerCase().includes(e.target.value.toLowerCase()))
            c.style.display = "block"
    }
})

search_champion.addEventListener("keypress", function (e) {
    if (e.key == "Enter") {
        let visible_champs = []
        for (let c of champion_img) {
            if (c.style.display == "block") {
                visible_champs.push(c)
            }
        }
        if (visible_champs.length == 1) {
            selectChampion(visible_champs[0])
        }
        clear_out()
    }
})

function best_fit_roles() {
    let selected_champions = getSelectedChampionsName(true)

    selected_champions = selected_champions.join(",")

    fetch("/best_fit_roles/" + selected_champions)
        .then((response) => {
            return response.json()
        })
        .then((json) => {
            let roles = json[0]
            let off_role = json[2]
            for (const [role, champion] of Object.entries(roles)) {
                let champion_role = document.getElementById("champion_role_" + champion)
                let role_ = role_mapping[role]
                let color = ""
                if (off_role.includes(champion))
                    color = "-red"

                champion_role.src = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/svg/position-" + role_ + color + ".svg"
            }
        })
}

function set_champion_size() {
    let minPoolHeight = 770
    let maxImageSize = 200
    let minImageSize = 60

    let pool = document.querySelector("#champions_pool")
    let w = pool.offsetWidth
    let h = Math.min(pool.offsetHeight, minPoolHeight)
    let champions = document.querySelectorAll(".champion")

    let n = champions.length

    let optimal_s = minImageSize

    for (let s = maxImageSize; s > minImageSize; s--) {
        let c = w / s
        let r = Math.ceil(n / c) + 1

        rs = r * s
        if (rs < h) {
            optimal_s = s
            break
        }
    }

    for (let champion of champions) {
        champion.style.width = optimal_s + "px";
        champion.style.height = optimal_s + "px";
    }
}

window.addEventListener("resize", set_champion_size)
set_champion_size()