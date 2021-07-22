const $jokeList = $(".jokes-list");
const BASE_URL = 'http://127.0.0.1:5000/'

$jokeList.on("click", ".uprate-btn", async function(e){
    rateJoke(e, 1)
})

$jokeList.on("click", ".downrate-btn", async function(e){
    rateJoke(e, -1)
})

async function rateJoke(e, rating){
    let joke_id
    if(e.target.localName === "i"){
        joke_id = e.target.parentElement.parentElement.parentElement.parentElement.parentElement.id
    } else if(e.target.localName === "button"){
        joke_id = e.target.parentElement.parentElement.parentElement.parentElement.id
    }

    const res = await axios({
        url: `${BASE_URL}api/jokes/${joke_id}/rate`,
        method: "POST",
        data: {
            rating: rating
        }
    })
    handle_rating_res(e.target, res, rating)

}

function handle_rating_res(target, json, rating){
    if(json["error"] === true){
        return json["message"]
    } 

    let el

    if(rating === 1){
        if(target.localName==="i"){
            el = target.parentElement.parentElement.nextElementSibling
        }else{
            el = target.parentElement.nextElementSibling
        }
    }else if(rating === -1){
        if(target.localName==="i"){
            el = target.parentElement.parentElement.previousElementSibling
        }else{
            el = target.parentElement.previousElementSibling
        }
    }

    el_int = parseInt(el.innerText)

    switch(json["data"]["message"]){
        case "rating added":
            el.innerText = el_int + rating;
            break;
        case "rating removed":
            el.innerText = el_int - rating;
            break;
        case "rating updated":
            el.innerText = el_int + rating + rating
            break;
    }
}