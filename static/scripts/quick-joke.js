const $quickJoke = $('#quick-joke')

let curr_joke

$quickJoke.on("click", ".like-btn", function(){
    rateJoke(curr_joke.id, 1)
    $(`#${curr_joke.id}`).remove()
    getRandomJoke()
})

$quickJoke.on("click", ".dislike-btn", function(){
    rateJoke(curr_joke.id, -1)
    $(`#${curr_joke.id}`).remove()
    getRandomJoke()
})

async function getRandomJoke(){
    const jokeRes = await axios({
       url: `${BASE_URL}api/jokes/random-joke`,
       method: 'GET'
    })
    handleJokeRes(jokeRes)
}

function handleJokeRes(res){
    let html;
    if(res['data']['joke']){
        if(!res['data']['joke']['body']){
           res['data']['joke']['body'] = ''
        }
        curr_joke = new Joke(res['data']['joke'])
        html = generateJokeHtml(curr_joke)
    } else {
        html = generateNoJokeHtml()
    }
    $quickJoke.append(html)
}

function generateJokeHtml(joke){
    html = `
        <div class="card quick-card" id="${joke.id}">
            <div class="card-header row">
                <div class="header-right col-4">`
    if(sessionStorage.getItem('curr_user')){
        const favBtn= `
                    <button class="btn p-0 mb-1">
                        <i class="far fa-star fav-btn" id="${joke.id}-star"></i>
                    </button>
                `
        html = html + favBtn
    }
    html = html + `<a href="/users/${joke.user_id}/profile" class="card-link">${joke.username}</a>
                </div>
                <div class="header-left col-8">
                    <span class="p-2">
                        <cite>${joke.created_at}</cite>
                    </span>
                    <span class="p-2">
                    <button class="btn mr-1 p-0 d-inline report" type="button" id="dropdownMenuButton2" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-flag"></i>
                    </button>
                    <ul class="dropdown-menu report-list" id="${joke.id}-report"    aria-labelledby="dropdownMenuButton2">
                        <li>
                            <button class="naj dropdown-item report-btn">Not A Joke</   button>
                        </li>
                        <li>
                            <button class="spam dropdown-item report-btn">Spam</button>
                        </li>
                        <li>
                            <button class="other dropdown-item report-btn">Other</  button>
                        </li>
                    </ul>
                    </span>`
    if(sessionStorage.getItem('curr_user')){
        if(joke.user_id === JSON.parse(sessionStorage.getItem('curr_user')).id){
            const joke_settings = `
            <span class="p-2">
                <button class="btn mr-2 p-0 d-inline" type="button"     id="dropdownMenuButton1" data-bs-toggle="dropdown"          aria-expanded="false">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu"   aria-labelledby="dropdownMenuButton1">
                    <li>
                        <a class="dropdown-item" href="/jokes/${joke.id}/edit">Edit Joke</a>
                    </li>
                    <li>
                        <a class="dropdown-item" href="/jokes/${joke.id}/delete">Delete Joke</a>
                    </li>
                </ul>
            </span>`
            html = html + joke_settings
        }
    }

        const endHtml =`</div>
            </div>
            <div class="card-body row">
                <h5 class="card-title text-center">
                     ${joke.setup}
                </h5>
                <p class="card-text text-center">${joke.body}</p>
                <div class="mt-3 d-flex flex-row justify-content-center">
                    <div class="rate-btn p-2 m-2">
                        <button class="btn dislike-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="rate-btn p-2 m-2">
                        <button class="btn like-btn">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `

        html = html + endHtml

    return html
}

function generateNoJokeHtml(){
    html = `
    <div class="card no-joke-card">
        <div class="card-body no-joke">
            <h5 class="card-title text-center">
                Looks like we ran out of Jokes. Please do check back later for more!
           </h5>
        </div>
    </div>
    `
    return html;
}

getRandomJoke()