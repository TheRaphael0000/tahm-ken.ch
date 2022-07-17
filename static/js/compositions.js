let selects = document.querySelectorAll(".filter_select")
let reset = document.querySelector("#reset")
let compositions = document.querySelectorAll(".composition")

function filterChanged() {
    let champions = []
    for (let select of selects) {
        let champion = select.selectedOptions[0].getAttribute("name")
        if (champion != null)
            champions.push(champion)
    }

    for (let composition of compositions) {
        let imgs = composition.getElementsByTagName("img")
        let comp_champs = []
        for (let img of imgs) {
            comp_champs.push(img.dataset.champion)
        }

        let intersection = champions.filter(value => comp_champs.includes(value));

        if (intersection.length >= champions.length)
            composition.style.display = "block";
        else
            composition.style.display = "none";
    }
}

function resetFilters() {
    for (let select of selects) {
        select.selectedIndex = 0;
        let evt = document.createEvent("HTMLEvents");
        evt.initEvent("change", false, true);
        select.dispatchEvent(evt);
    }
}

for (let select of selects) {
    select.addEventListener("change", filterChanged)
}

reset.addEventListener("click", resetFilters)