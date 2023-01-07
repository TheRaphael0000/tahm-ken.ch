let table_challenges = document.querySelectorAll(".table_challenges")
let champions_pool = document.querySelector("#champions_pool")
let champion_img = document.querySelectorAll(".champion_img")
let challenge_cb = document.querySelectorAll(".challenge_cb")
let challenge_tr = document.querySelectorAll(".challenge_tr")
let challenge_no = document.querySelectorAll(".challenge_no")
let champion_role = document.querySelectorAll(".champion_role")
let challenges_select = document.querySelectorAll(".challenges_select")
let btn_reset = document.querySelector("#btn_reset")
let btn_share = document.querySelector("#btn_share")
let btn_toggle_completed_challenges = document.querySelector("#btn_toggle_completed_challenges")
let btn_optimize_selection = document.querySelector("#btn_optimize_selection")
let region = document.querySelector("#region")
let summoner = document.querySelector("#summoner")
let search = document.querySelector("#search")
let search_champion = document.querySelector("#search_champion")

let completed_challenges = true

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
    sort_champions()
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
    search_champion.value = "";
}

function getSelectedChallenges() {
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
    return ids
}

function challengeChanged(e) {
    let ids = getSelectedChallenges()

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
                let sub_id = parseInt(challenge_split[1])

                let select = document.getElementById("challenge_select_" + id)
                if (select) {
                    if (select.selectedIndex != sub_id) {
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
    let selectedChampionName = getSelectedChampionsName(true)
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

function toggle_completed_challenges() {
    completed_challenges ^= true

    //visual
    let hide = "fa-eye-slash"
    let show = "fa-eye"

    let el = btn_toggle_completed_challenges.children[0]
    if (completed_challenges) {
        el.classList.add(show)
        el.classList.remove(hide)
    }
    else {
        el.classList.add(hide)
        el.classList.remove(show)
    }

    update_challenges_visibility(completed_challenges)
}

function update_challenges_visibility(completed_challenges) {
    for (challenge_tr_ of challenge_tr) {
        let children = challenge_tr_.children
        let next_threshold = children[children.length - 1].dataset.next_threshold
        challenge_tr_.classList.remove("hide")

        if (!completed_challenges && next_threshold == "None")
            challenge_tr_.classList.add("hide")
    }
}

function reset() {
    resetChallenge()
    resetSelection()
    search_clear()
}

btn_reset.addEventListener("click", reset)
btn_toggle_completed_challenges.addEventListener("click", toggle_completed_challenges)

reset()

for (let cbc of challenge_cb) {
    cbc.addEventListener('change', challengeChanged)
}

for (let s of challenges_select) {
    s.addEventListener('change', challengeChanged)
}

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
        window.location.href = "/team_builder/" + region.value + "/" + summoner.value
    }
}

summoner.addEventListener("keydown", (event) => {
    if (event.key === 'Enter') {
        search_summoner()
    }
})

search.addEventListener("click", search_summoner)

function search_clear() {
    search_champion.value = ""

    for (let c of champion_img) {
        c.parentElement.style.display = "block"
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
        search_clear()
    }
})

search_champion.addEventListener("input", function (e) {
    if (e.target.value.length <= 0) {
        return search_clear()
    }

    for (let c of champion_img) {
        c.parentElement.style.display = "none"
    }
    for (let c of champion_img) {
        if (c.dataset.champion_display_name.toLowerCase().includes(e.target.value.toLowerCase()))
            c.parentElement.style.display = "block"
    }
})

search_champion.addEventListener("keypress", function (e) {
    if (e.key == "Enter") {
        let visible_champs = []
        for (let c of champion_img) {
            if (c.parentElement.style.display == "block") {
                visible_champs.push(c)
            }
        }
        if (visible_champs.length == 1) {
            selectChampion(visible_champs[0])
        }
        search_clear()
    }
})

btn_optimize_selection.addEventListener("click", (e) => {
    let champions = getSelectedChampionsName(true)
    let challenges = getSelectedChallenges()

    if (champions.length + challenges.length > 0) {
        let parameters = challenges.join(",") + "&" + champions.join(",")
        window.location.href = "/optimize/" + parameters;
    }
    else {
        alert("Select at least 1 champion or 1 challenge to optimize.")
    }
})

function sort_champions() {
    let els = Array.prototype.slice.call(champions_pool.children, 0)

    els.sort((a, b) => {
        let name = (x) => x.children[0].dataset.champion_display_name
        let checked = (x) => x.children[0].dataset.checked

        let a_name = name(a)
        let b_name = name(b)
        let az_compare = a_name.localeCompare(b_name)

        let a_checked = checked(a)
        let b_checked = checked(b)
        return 2 * (b_checked - a_checked) + az_compare
    })

    champions_pool.innerHTML = ""
    for (let el of els) {
        champions_pool.appendChild(el)
    }
}

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
    let maxImageSize = 200
    let minImageSize = 65

    let pool = document.querySelector("#champions_pool")
    let w = pool.offsetWidth
    let h = pool.offsetHeight
    let champions = document.querySelectorAll(".champion")

    let n = champions.length

    let optimal_s = minImageSize

    for (let s = maxImageSize; s > minImageSize; s--) {
        let c = Math.floor(w / s)
        let r = Math.ceil(n / c)
        // +1 since we want to stop before it overflows
        rs = (r + 1) * s
        if (rs < h) {
            break
        }
        optimal_s = s
    }

    for (let champion of champions) {
        champion.style.width = optimal_s + "px";
        champion.style.height = optimal_s + "px";
    }
}

window.addEventListener("resize", set_champion_size)
set_champion_size()



// SHARE API
btn_share.addEventListener("click", share)

function share() {
    // get selected champions with a query selector
    let selectedChampions = document.querySelectorAll(".champion_img.selected");

    // map the champions to a string with their ids
    let championString = Array.from(selectedChampions).map((e) => {
        return parseInt(e.getAttribute("data-champion_id")).toString(16);
    }).toString();


    // get selected challenges with a query selected => search for all :checked checkboxes
    let selectedChallenges = document.querySelectorAll("td > input.challenge_cb:checked");

    // map the challenges to a string with their ids
    let challengeString = Array.from(selectedChallenges).map((e) => {
        return parseInt(e.getAttribute("data-id")).toString(16);
    }).toString();

    console.log(window.location);

    let shareURL = `${window.location.protocol}//${window.location.host}${window.location.pathname}${window.location.search}#${challengeString};${championString}`


    // SECURITY RISK MINIMATION: Instead of using outdated functions (execCommand(copy)), just throw the url as an alert to users who have old browser
    if (!navigator.clipboard) {
        alert(shareURL);
        return;
    }

    navigator.clipboard.writeText(shareURL).then(() => {
        // copied url successfully
        let oldHTML = btn_share.innerHTML;
        btn_share.classList.add("btn-success");
        btn_share.classList.remove("btn-outline-light");
        btn_share.innerHTML = "<i class='fa-solid fa-check'></i>";

        setTimeout(() => {
            btn_share.classList.remove("btn-success");
            btn_share.classList.add("btn-outline-light");
            btn_share.innerHTML = oldHTML;
        }, 1500);
    }, (e) => {
        console.warn(e);
        // failed to copy url, show alert() as an fallback instead
        alert(shareURL);
    })
}


function decodeShareURL(hash) {
    hash = hash.replace("#", "");

    let hashes = hash.split(";");

    if (hashes.length < 2) {
        return;
        // that should not happen, the url was most likely modified by hand
    }

    let challengesEncoded = hashes[0];
    let championsEncoded = hashes[1];

    let challenges = challengesEncoded.split(",").map((c) => {
        return parseInt(c, 16);
    })
    let champions = championsEncoded.split(",").map((c) => {
        return parseInt(c, 16);
    })


    for (let i = 0; i < challenge_cb.length; i++) {
        const node = challenge_cb[i];
        if (challenges.includes(parseInt(node.getAttribute("data-id")))) {
            node.click();
        }
    }


    for (let i = 0; i < champion_img.length; i++) {
        const node = champion_img[i];
        if (champions.includes(parseInt(node.getAttribute("data-champion_id")))) {
            node.click();
        }
    }


}

// check for the hash
let hash = document.location.hash;
if (hash.length > 0) {
    decodeShareURL(hash)
    history.pushState("", document.title, window.location.pathname + window.location.search);
}