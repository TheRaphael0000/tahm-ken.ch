let champion_cb = document.querySelectorAll(".champion_cb")
let challenge_cb = document.querySelectorAll(".challenge_cb")
let challenge_label = document.querySelectorAll(".challenge_label")
let challenge_qte = document.querySelectorAll(".challenge_qte")
let btn_reset = document.querySelector("#btn_reset")
let btn_copy = document.querySelector("#btn_copy")


function updateAll() {
    for (let cbc of champion_cb) {
        cbc.dispatchEvent(new Event('change'))
    }
}

function setAllChampion(value) {
    for (let cbc of champion_cb) {
        cbc.checked = value
    }
    updateAll()
}

function resetChallenge() {
    setAllChampion(false)
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
            return response.json();
        })
        .then((json) => {
            setAllChampion(false)
            if (json.intersection.length <= 0)
                return
            for (let c of json.intersection) {
                let el = document.getElementById("champion_" + c)
                el.checked = true
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
            updateAll();
        })
}

function copyChallenges() {
    let champions = []
    for (let cbc of champion_cb) {
        if(cbc.checked) {
            champions.push(cbc.dataset.champion_name)
        }
    }
    let s = champions.join(", ")
    navigator.clipboard.writeText(s);
}

for (let cbc of champion_cb) {
    cbc.addEventListener('change', function (e) {
        let label = e.target.nextSibling.nextSibling
        if (e.target.checked) {
            label.style.opacity = "1"
        } else {
            label.style.opacity = "0.2"
        }
    })
}

btn_reset.addEventListener("click", resetChallenge);
updateAll();

for (let cbc of challenge_cb) {
    cbc.addEventListener('change', challengeChanged)
}


btn_copy.addEventListener("click", copyChallenges);