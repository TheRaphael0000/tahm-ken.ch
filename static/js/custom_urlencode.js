// using base64 RFC 4648 §5
let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
let codeSize = Math.floor(Math.log2(characters.length))

let lookup_table = {}
let reverse_lookup_table = {}

let i = 0
for(let c of characters) {
    let step_i = i.toString(2).padStart(codeSize, "0")
    lookup_table[step_i] = c
    reverse_lookup_table[c] = step_i
    i++
}

function decodeURL(e) {
    let o = ""
    for(let c of e) {
        o += reverse_lookup_table[c]
    }
    // remove the leading 0s at the start
    o = o.replace(/^0+/, "")
    return o
}

function encodeURL(o) {
    // remove padding 0s at the start (the string must start with a 1)
    o = o.replace(/^0+/, "")
    let e = ""
    // add back 0s to encode all the bits
    let desiredLength = Math.ceil(o.length / codeSize) * codeSize
    o = o.padStart(desiredLength, "0")
    for(let i = 0; i < o.length; i += codeSize) {
        let subStr = o.substring(i, i + codeSize)
        e += lookup_table[subStr]
    }
    return e
}


function test() {
    console.log(codeSize)
    console.log(lookup_table)
    console.log(reverse_lookup_table)
    console.log(decodeURL("BA"))
    console.log(encodeURL("00000001111111"))
    console.log(encodeURL("101010101010101"))
    console.log(decodeURL(encode("101010101010101")))
}

// test()