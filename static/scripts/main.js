const $jokeList = $(".jokes-list");
const BASE_URL = 'http://127.0.0.1:5000/'

async function getCurrUser(){
    const res = await axios({
        url: `${BASE_URL}api/get_curr_user`,
        method: "GET"
    })

    if(res['data']['logged_in'] === true){
        console.log(res)
        const user = new User(res['data']['curr_user'])
        sessionStorage.setItem('curr_user', JSON.stringify(user))
        return true
    } else {
        console.log(res)
        sessionStorage.removeItem('curr_user')
        return false
    }
}

getCurrUser()

$jokeList.on("click", ".uprate-btn", async function(e){
    let joke_id
    if(e.target.localName === "i"){
        joke_id = e.target.parentElement.parentElement.parentElement.parentElement.parentElement.id
    } else if(e.target.localName === "button"){
        joke_id = e.target.parentElement.parentElement.parentElement.parentElement.id
    }
    await rateJoke(joke_id, 1).then((res) => {handle_rating_res(e.target, res, 1)})
})

$jokeList.on("click", ".downrate-btn", async function(e){
    let joke_id
    if(e.target.localName === "i"){
        joke_id = e.target.parentElement.parentElement.parentElement.parentElement.parentElement.id
    } else if(e.target.localName === "button"){
        joke_id = e.target.parentElement.parentElement.parentElement.parentElement.id
    }
    await rateJoke(joke_id, -1).then((res) => {handle_rating_res(e.target, res, -1)})
})

async function rateJoke(joke_id, rating){
    const res = await axios({
        url: `${BASE_URL}api/jokes/${joke_id}/rate`,
        method: "POST",
        data: {
            rating: rating
        }
    })
    return await res

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