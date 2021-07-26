async function getCurrUser(){
    const res = await axios({
        url: `${BASE_URL}api/get_curr_user`,
        method: "GET"
    })

    if(res['data']['logged_in'] === true){
        console.log(res)
        const user = new User(res['data']['curr_user'])
        sessionStorage.setItem('curr_user', JSON.stringify(user))
        return user
    } else {
        console.log(res)
        sessionStorage.removeItem('curr_user')
        return false
    }
}

async function followUser(u_id){
    const res = await axios({
        url: `${BASE_URL}api/users/follow`,
        method: "POST",
        data: {
            u_id: u_id
        }
    })
    return res
}

async function rateJoke(joke_id, rating){
    const res = await axios({
        url: `${BASE_URL}api/jokes/${joke_id}/rate`,
        method: "POST",
        data: {
            rating: rating
        }
    })
    return res
}

async function favJoke(joke_id){
    const res = await axios({
        url: `${BASE_URL}api/jokes/favorite`,
        method: "POST",
        data: {
            joke_id: joke_id
        }
    })
    return res
}

async function reportJoke(joke_id, reason){
    const res = await axios({
        url: `${BASE_URL}api/report_joke`,
        method: "POST",
        data: {
            joke_id: joke_id,
            reason: reason
        }
    })
    return res
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