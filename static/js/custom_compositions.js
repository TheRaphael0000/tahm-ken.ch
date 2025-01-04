let custom_compositions_form = document.querySelector("#custom_compositions_form")
let find = document.querySelector("#find")
let summoners = document.querySelectorAll(".summoners")
let region = document.querySelector("#region")

custom_compositions_form.addEventListener("submit", function (e) {
    e.preventDefault()
    let str = ""

    for (let i = 0; i < summoners.length; i++) {
        let summoner = summoners[i]
        str += summoner.value
        if (i + 1 < summoners.length) str += ","
    }

    let url = "/custom_compositions/" + region.value + "/" + str
    window.location.href = url
})
