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
let completed = document.querySelector("#completed")
let completed_img = document.querySelector("#completed_img")
let selection = document.querySelector("#selection")

let completed_challenges = true

let role_mapping = {
    "top": "top",
    "jungle": "jungle",
    "mid": "middle",
    "bottom": "bottom",
    "support": "utility",
}

let completed_possible_icons = [
    "fiora_happy_cheers_inventory.png",
    "leesin_happy_cheers_inventory.png",
    "lulu_happy_cheerful_inventory.png",
    "lux_happy_cheerful_inventory.png",
    "poro_happy_cheers_inventory.png",
    "teemo_happy_cheers_inventory.png",
    "thumb_happy_up_inventory.png",
    "ziggs_happy_cheers_inventory.png",
]

// selection order for the URL selection bitfield
// APPEND NEW CHALLEGNES ID AT THE END OF THIS LIST TO KEEP URL CONSISTENCY 
let selection_order = [
    303401, 303402, 303403, 303404, 303405, 303406, 303407, 3034080, 3034081, 3034082, 3034083, 3034084, 3034085, 303409, 303410, 303411, 303412, 303501, 303502, 303503, 303504, 303505, 303506, 303507, 303508, 303509, 303510, 303511, 303512, 303513
]

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

    let selectedChampions = getSelectedChampions()
    let champion_placeholder_large = document.querySelector(".champion_placeholder_large")
    selection.innerHTML = ""
    for (let i = 0; i < 5; i++) {
        if (i < selectedChampions.length) {
            let champion = selectedChampions[i]
            let img = document.createElement("img")
            img.src = champion.src
            img.classList.add("selection_champion")
            img.addEventListener("click", () => selectChampion(champion))
            selection.appendChild(img)
        } else {
            let svg = champion_placeholder_large.cloneNode(true)
            svg.style.display = "inline-block"
            selection.appendChild(svg)
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

            if (json.intersection.length <= 0 && ids == "none") {
                for (let c of champion_img)
                    c.dataset.checked = "1"
            }

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
    resetRoles()

    if (e.dataset.selected == "1") {
        e.dataset.selected = "0"
    }
    else if (canSelectChampion()) {
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
                        img.src = "/static/cache_datadragon/champions_img/" + champion + ".png"
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
    let visible_challenges = 0
    for (challenge_tr_ of challenge_tr) {
        let children = challenge_tr_.children
        let next_threshold = children[children.length - 1].dataset.next_threshold
        challenge_tr_.classList.remove("hide")
        visible_challenges++

        if (!completed_challenges && next_threshold == "None") {
            challenge_tr_.classList.add("hide")
            visible_challenges--
        }
    }

    let icon = completed_possible_icons[Math.floor(Math.random() * completed_possible_icons.length)]
    let url = `/static/img/happy_cheerful/${icon}`
    completed_img.src = url

    completed.classList.add("hide")
    if (visible_challenges <= 2)
        completed.classList.remove("hide")
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
        window.location.href = "/team_builder/" + region.value + "/" + summoner.value.replaceAll("#", "-")
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

        /**
         * Make a champion searchable by name or internal id
         * By using the internal id, it is easier to search champions 
         * like Vel'Koz, as you don't have to add the apostrophe or space
         */
        let query = e.target.value.toLowerCase()
        let targets = [
            c.dataset.champion_display_name,
            c.dataset.champion_name,
        ]

        if (targets.some((e) => e.toLowerCase().includes(query))) {
            c.parentElement.style.display = "block"
        }
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
        let name_a = name(a)
        let name_b = name(b)
        let name_compare = name_a.localeCompare(name_b)

        return name_compare
    })

    els.sort((a, b) => {
        let level = (x) => x.children[0].dataset.champion_level
        let level_a = level(a)
        let level_b = level(b)
        let level_compare = level_b - level_a

        let points = (x) => x.children[0].dataset.champion_points
        let points_a = points(a)
        let points_b = points(b)
        let points_compare = points_b - points_a

        return level_compare || points_compare
    })

    els.sort((a, b) => {
        let checked = (x) => x.children[0].dataset.checked
        let checked_a = checked(a)
        let checked_b = checked(b)
        let checked_compare = checked_b - checked_a

        return checked_compare
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

    let champions = document.querySelectorAll(".champion")

    // reset the width to reset the pool size
    for (let champion of champions) {
        champion.style.width = "0px"
        champion.style.height = "0px"
    }

    let pool = document.querySelector("#champions_pool")
    let w = pool.offsetWidth
    let h = pool.offsetHeight

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

    optimal_s += 1

    for (let champion of champions) {
        champion.style.width = optimal_s + "px"
        champion.style.height = optimal_s + "px"
    }
}


window.addEventListener("resize", set_champion_size)
set_champion_size()

// SHARE API
btn_share.addEventListener("click", share)

function encodeSelection() {
    let bitField = ""

    // challenge selection order
    for (let s of selection_order) {
        let isSelected
        if (typeof s == "number") {
            s = s.toString()
            isSelected = document.querySelector("#challenge_cb_" + s.substring(0, 6)).checked
            if (s.length == 7) {
                isSelected &= challenges_select[0].selectedIndex == s.substring(6, 7)
            }
        }
        bitField += isSelected ? "1" : "0"
    }
    // pad with the start with a 1 for the encoding
    let challengesCode = encodeURL("1" + bitField)

    let selectedChampions = document.querySelectorAll(".champion_img.selected")
    let championsCode = Array.from(selectedChampions).map((e) => {
        return e.dataset.champion_name
    }).toString();

    let code = challengesCode + "-" + championsCode
    return code
}


function decodeSelection(code) {
    code = code.replace("#", "").split("-")

    let challengesCode = code[0]

    // ignore the first padded 1 used for the encoding
    let bitField = decodeURL(challengesCode).substring(1)

    for (let i = 0; i < selection_order.length; i++) {
        let bit = bitField[i]

        if (bit != "1")
            continue

        let s = selection_order[i]
        let node

        if (typeof s == "number") {
            s = s.toString()
            if (s.length == 7) {
                challenges_select[0].selectedIndex = s.substring(6, 7)
            }
            node = document.querySelector("#challenge_cb_" + s.substring(0, 6))
        }
        else if (typeof s == "string") {
            node = document.querySelector("#champion_" + s)
        }

        node.click()
    }

    let selectedChampions = code[1]
    selectedChampions = selectedChampions.split(",")

    for (let i = 0; i < champion_img.length; i++) {
        let node = champion_img[i]
        if (selectedChampions.includes(node.dataset.champion_name))
            node.click()
    }
}

function createShareURL() {
    let code = encodeSelection()
    let shareURL = `${window.location.protocol}//${window.location.host}${window.location.pathname}${window.location.search}?#${code}`
    return shareURL
}

function share() {
    let shareURL = createShareURL()

    // SECURITY RISK MINIMATION: Instead of using outdated functions (execCommand(copy)), just throw the url as an alert to users who have old browser
    if (!navigator.clipboard) {
        alert(shareURL)
        return
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
        }, 750);
    }, (e) => {
        console.warn(e)
        // failed to copy url, show alert() as an fallback instead
        alert(shareURL)
    })
}

// check for the hash
let hash = document.location.hash
if (hash.length > 0) {
    decodeSelection(hash)
    history.pushState("", document.title, window.location.pathname + window.location.search)
}