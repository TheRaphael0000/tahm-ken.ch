let champion_img = document.querySelectorAll(".champion_img")
let challenge_cb = document.querySelectorAll(".challenge_cb")
let challenge_tr = document.querySelectorAll(".challenge_tr")
let challenge_qte = document.querySelectorAll(".challenge_qte")
let btn_reset_filters = document.querySelector("#btn_reset_filters")
let btn_reset_selection = document.querySelector("#btn_reset_selection")
let btn_copy = document.querySelector("#btn_copy")


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

function copyChallenges() {
    let selectedChampionName = getSelectedChampionsName()
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

function getSelectedChampionsName() {
    let selectedChampions = getSelectedChampions()
    let selectedChampionName = []
    for (let s of selectedChampions)
        selectedChampionName.push(s.dataset.champion_name)
    return selectedChampionName
}

function canSelectChampion() {
    selectedChampions = getSelectedChampions()
    return selectedChampions.length < 5
}

function selectChampion(e) {
    if (e.target.dataset.selected == "1") {
        e.target.dataset.selected = "0"
        updateChampionsSelection()
        updateChampionsStyle()
        return
    }

    if (canSelectChampion())
        e.target.dataset.selected = "1"

    updateChampionsSelection()
    updateChampionsStyle()
}

function updateChampionsSelection() {
    selectedChampionName = getSelectedChampionsName()
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
reset()

for (let cbc of challenge_cb) {
    cbc.addEventListener('change', challengeChanged)
}

btn_copy.addEventListener("click", copyChallenges)

for (let c of champion_img) {
    c.addEventListener("click", function (e) {
        selectChampion(e)
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
let region = document.getElementById("region")
let summoner = document.getElementById("summoner")
let search = document.getElementById("search")

function search_summoner() {
  window.location.href = "/tool/" + region.value + "/" + summoner.value
}

summoner.addEventListener("keydown", (ele) => {
  if(event.key === 'Enter') {
    search_summoner()
  }
})

search.addEventListener("click", (ele) => {
    search_summoner()
})