let include_select = document.querySelector("#include_select")
let exclude_select = document.querySelector("#exclude_select")
let compositions = document.querySelectorAll(".composition")
let filters = document.querySelector("#filters")
let include_filters = new Map()
let exclude_filters = new Map()

function filterChanged(e, reset) {
    let option = e.target.selectedOptions[0]
    if (e.target == include_select)
        include_filters.set(option.value, option.innerHTML)
    else if (e.target == exclude_select)
        exclude_filters.set(option.value, option.innerHTML)

    updateFilterElements()
    filterCompositions()
    updateFilters()

    if (reset)
        e.target.selectedIndex = 0
}

function filterCompositions() {
    let include_champions = new Set(Array.from(include_filters.keys()))
    let exclude_champions = new Set(Array.from(exclude_filters.keys()))

    for (let composition of compositions) {
        let imgs = composition.getElementsByTagName("img")
        let composition_champions = new Set()

        for (let img of imgs) {
            composition_champions.add(img.dataset.champion)
        }

        let include_intersection = new Set([...composition_champions].filter(x => include_champions.has(x)));
        let exclude_intersection = new Set([...composition_champions].filter(x => exclude_champions.has(x)));

        if (exclude_intersection.size > 0 || include_intersection.size < include_champions.size)
            composition.style.display = "none"
        else
            composition.style.display = "block"
    }
}

function updateFilterElements() {
    filters.innerHTML = ""

    function add_filter_element(champion_id, champion_name, color) {
        function removeFilter(id_) {
            include_filters.delete(id_)
            exclude_filters.delete(id_)
            updateFilterElements()
            filterCompositions()
            updateFilters()
        }

        let badge = document.createElement("span")
        badge.classList.add("badge")
        badge.classList.add(color)
        badge.innerText = new DOMParser().parseFromString(champion_name, "text/html").documentElement.textContent + " "
        badge.addEventListener("click", (e) => removeFilter(champion_id))


        let button = document.createElement("button")
        button.type = "button"
        button.classList.add("btn-close")
        button.addEventListener("click", (e) => removeFilter(champion_id))
        badge.appendChild(button)

        filters.appendChild(badge);
    }

    for (let [champion_id, champion_name] of include_filters) {
        add_filter_element(champion_id, champion_name, "text-bg-success")
    }
    for (let [champion_id, champion_name] of exclude_filters) {
        add_filter_element(champion_id, champion_name, "text-bg-danger")
    }
}


include_select.addEventListener("change", (e) => filterChanged(e, true))
exclude_select.addEventListener("change", (e) => filterChanged(e, true))


function updateFilters() {
    let champions_remaining = new Map()

    for (let composition of compositions) {
        let imgs = composition.getElementsByTagName("img")

        for (let img of imgs) {
            if (["block", ""].includes(composition.style.display) && !include_filters.has(img.dataset.champion))
                champions_remaining.set(img.dataset.champion, img.alt)
        }
    }

    for (let select of [include_select, exclude_select]) {
        // clear it
        while (select.options.length > 0) {
            select.remove(0);
        }

        let mapAsc = new Map([...champions_remaining.entries()].sort())

        // fill it
        select.options.add(new Option("", "", true));
        for (const [champion_id, champion_name] of mapAsc.entries()) {
            select.options.add(new Option(champion_name, champion_id))
        }
    }
}

updateFilters()