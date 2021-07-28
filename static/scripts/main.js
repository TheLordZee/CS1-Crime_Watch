const $jokeList = $(".jokes-list");
const $followBtn = $(".follow-btn")
const $reportList = $(".report-list")
const BASE_URL = 'http://127.0.0.1:5000/'

getCurrUser()

$followBtn.on("click", async function(e){
  const res = await followUser(e.target.id)  
  if (res.data.error === false){
    if(res.data.type === "follow"){
        e.target.innerText = "Unfollow"
    } else {
        e.target.innerText = "Follow"
    }
  }
})

$jokeList.on("click", ".uprate-btn", async function(e){
    const joke_id = e.target.offsetParent.id
    await rateJoke(joke_id, 1).then((res) => {handle_rating_res(e.target, res, 1)})
})

$jokeList.on("click", ".downrate-btn", async function(e){
    const joke_id = e.target.offsetParent.id
    await rateJoke(joke_id, -1).then((res) => {handle_rating_res(e.target, res, -1)})
})

$jokeList.on("click", ".fav-btn", async function(e){
    const joke_id = e.target.offsetParent.id
    const res = await favJoke(joke_id)
    console.log(res)
    if(res['data']['error'] === false){
        $(`#${joke_id}-star`).toggleClass('fas far')
    }
})

$reportList.on("click", ".report-btn", async function(e){
    const joke_id = parseInt(e.target.parentElement.parentElement.id)
    const reason = e.target.classList[0]
    const res = await reportJoke(joke_id, reason)
    if(res.data.error === false){
        e.target.parentElement.parentElement.parentElement.offsetParent.innerHTML = `
            <h4 class="text-center">Joke reported</h4>
        `
    }
})

$jokeList.on("click", ".delete-btn", async function(e){
    const joke_id = parseInt(e.target.parentElement.parentElement.offsetParent.id)
    const res = await deleteJoke(joke_id)
    if(res.data.error === false){
        e.target.parentElement.parentElement.parentElement.offsetParent.innerHTML = `
            <h4 class="text-center">Joke deleted</h4>
        `
    }
})

$jokeList.on("click", ".cancel-btn", async function(e){
    const joke_id = parseInt(e.target.parentElement.parentElement.offsetParent.id)
    const res = await cancelReport(joke_id)
    if(res.data.error === false){
        e.target.parentElement.parentElement.parentElement.offsetParent.innerHTML = `
            <h4 class="text-center">Report Cancelled</h4>
        `
    }
})