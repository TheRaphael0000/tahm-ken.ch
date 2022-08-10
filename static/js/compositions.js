let select = document.querySelector("#filter_select")
let compositions = document.querySelectorAll(".composition")
let filters = document.querySelector("#filters")
let filters_ = new Map()

function filterChanged(e) {
    let option = e.target.selectedOptions[0]
    filters_.set(option.value, option.innerHTML)
    updateFilterElements()
    filterCompositions()
    updateFilters()

    e.target.selectedIndex = 0
}

function filterCompositions() {
    for (let composition of compositions) {
        let imgs = composition.getElementsByTagName("img")
        let comp_champs = []
        for (let img of imgs) {
            comp_champs.push(img.dataset.champion)
        }

        let champions = Array.from(filters_.keys())
        let intersection = champions.filter(value => comp_champs.includes(value))

        if (intersection.length >= champions.length)
            composition.style.display = "block"
        else
            composition.style.display = "none"
    }
}

function updateFilterElements() {
    filters.innerHTML = ""

    for (let [champion_id, champion_name] of filters_) {

        function removeFilter(id_) {
            filters_.delete(id_)
            updateFilterElements()
            filterCompositions()
            updateFilters()
        }

        let badge = document.createElement("span")
        badge.classList.add("badge")
        badge.classList.add("text-bg-primary")
        badge.innerText = new DOMParser().parseFromString(champion_name, "text/html").documentElement.textContent + " "
        badge.addEventListener("click", (e) => removeFilter(champion_id))


        let button = document.createElement("button")
        button.type = "button"
        button.classList.add("btn-close")
        button.addEventListener("click", (e) => removeFilter(champion_id))
        badge.appendChild(button)

        filters.appendChild(badge);
    }
}


select.addEventListener("change", filterChanged)


function updateFilters() {
    let champions_remaining = new Map()
    for (let composition of compositions) {
        let imgs = composition.getElementsByTagName("img")

        for (let img of imgs) {
            if (composition.style.display == "block" && !filters_.has(img.dataset.champion))
                champions_remaining.set(img.dataset.champion, img.alt)
        }
    }

    // clear it
    while (select.options.length > 0) {
        select.remove(0);
    }

    let mapAsc = new Map([...champions_remaining.entries()].sort());

    // fill it
    select.options.add(new Option("", "", true));
    for (const [champion_id, champion_name] of mapAsc.entries()) {
        select.options.add(new Option(champion_name, champion_id));
    }
}

updateFilters()