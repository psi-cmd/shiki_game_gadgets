// pinyin in python has a fatal error of accuracy
var pinyin = require("pinyin")
var fusion = require("data/fusion_V2_dict.json")

fusion_pinyin = []

for (var i in fusion) {
    fusion_pinyin.push([fusion[i], pinyin(fusion[i][0], {
        style: pinyin.STYLE_NORMAL,
        heteronym: true
    })[0], pinyin(fusion[i][fusion[i].length - 1], {style: pinyin.STYLE_NORMAL, heteronym: true})[0]])
}

console.log(fusion_pinyin)

var content = JSON.stringify(fusion_pinyin)

var fs = require("fs")

fs.writeFile('./data/fusion_V2_dict.json', content, function (err) {
    if (err) {
        console.log(err)
    }
    console.log('ok')
})
