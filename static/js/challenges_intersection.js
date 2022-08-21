let champion_img = document.querySelectorAll(".champion_img")
let challenge_cb = document.querySelectorAll(".challenge_cb")
let challenge_tr = document.querySelectorAll(".challenge_tr")
let challenge_qte = document.querySelectorAll(".challenge_qte")
let btn_reset_filters = document.querySelector("#btn_reset_filters")
let btn_reset_selection = document.querySelector("#btn_reset_selection")
let btn_search_champion = document.querySelector("#btn_search_champion")
let btn_copy = document.querySelector("#btn_copy")
let region = document.querySelector("#region")
let summoner = document.querySelector("#summoner")
let search = document.querySelector("#search")
let search_champion = document.querySelector("#search_champion")


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
    setChampionsChecked("0")
    for (let c of challenge_cb) {
        c.checked = false
    }
    for (let c of challenge_qte) {
        c.innerHTML = c.dataset.maxqte
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
}

function reset() {
    resetChallenge()
    resetSelection()
}

function challengeChanged(e) {
    let checked_challenges = document.querySelectorAll(".challenge_cb:checked")
    let ids = []
    for (let cc of checked_challenges) {
        ids.push(cc.dataset.id)
    }

    if (ids.length <= 0) {
        resetChallenge()
        return
    }

    fetch("/challenge_intersection/" + ids)
        .then((response) => {
            return response.json()
        })
        .then((json) => {
            setChampionsChecked("0")
            if (json.intersection.length <= 0)
                return
            for (let c of json.intersection) {
                let img = document.getElementById("champion_" + c)
                img.dataset.checked = "1"
            }
            for (const [challenge, qte] of json.challenges_additional_intersection) {
                let challenge_cb = document.querySelector("#challenge_cb_" + challenge)
                let challenge_qte = document.querySelector("#challenge_qte_" + challenge)
                let challenge_tr = document.querySelector("#challenge_tr_" + challenge)
                challenge_qte.innerHTML = qte
                if (qte < challenge_cb.dataset.qte)
                    challenge_tr.classList.remove("checked")
                else
                    challenge_tr.classList.add("checked")
            }
            updateChampionsStyle()
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
        return
    }

    if (canSelectChampion())
        e.dataset.selected = "1"

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
                let qte = json[challenge]
                let challenge_tr = document.querySelector("#challenge_tr_" + challenge)
                let challenge_qte = document.querySelector("#challenge_current_selection_" + challenge)
                let challenge_requirement = parseInt(document.querySelector("#challenge_requirement_" + challenge).innerHTML)

                challenge_qte.innerHTML = qte

                if (qte >= challenge_requirement)
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

new Tablesort(document.getElementById('table_challenges'), { descending: true });

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