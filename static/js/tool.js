let champion_img = document.querySelectorAll(".champion_img")
let challenge_cb = document.querySelectorAll(".challenge_cb")
let challenge_label = document.querySelectorAll(".challenge_label")
let challenge_qte = document.querySelectorAll(".challenge_qte")
let btn_reset = document.querySelector("#btn_reset")
let btn_copy = document.querySelector("#btn_copy")


function updateChampionsStyle() {
    for (let img of champion_img) {
        if (img.dataset.checked == "1") {
            img.style.opacity = "1.0"
        }
        else {
            img.style.opacity = "0.2"
        }

        if (img.dataset.selected == "1") {
            img.style.border = "3px solid yellow"
            img.style.padding = "0px"
        }
        else {
            img.style.padding = "3px"
            img.style.border = "none"
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
    for (let c of challenge_label) {
        c.style.opacity = "1.0"
    }
}

function resetSelection() {
    for (let c of challenge_label) {
        c.style.color = "white"
    }
    setChampionsSelected("0")
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
                let challenge_label = document.querySelector("#challenge_label_" + challenge)
                challenge_qte.innerHTML = qte
                if (qte < challenge_cb.dataset.qte)
                    challenge_label.style.opacity = "0.2"
                else
                    challenge_label.style.opacity = "1.0"
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
    console.log(selectedChampionName)
    if (selectedChampionName.length <= 0)
        return

    let champions = selectedChampionName.join(",")

    fetch("/champions_selected/" + champions)
        .then((response) => {
            return response.json()
        })
        .then((json) => {
            let array = Array.from(json.values())
            let i = 0
            for (const c of challenge_label) {
                if (array.includes(i))
                    c.style.color = "yellow"
                else
                    c.style.color = "white"
                i++
            }
        })
}


btn_reset.addEventListener("click", reset)
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
            e.target.style.padding = "0px"
            e.target.style.border = "3px solid yellow"
            // e.target.style.opacity = "1.0"
        }
    })
    c.addEventListener("mouseleave", function (e) {
        updateChampionsStyle()
    })
}