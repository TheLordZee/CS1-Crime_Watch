const $quickJoke = $('#quick-joke')

async function getRandomJoke(){
    const jokeRes = await axios({
       url: `${BASE_URL}api/jokes/random-joke`,
       method: 'GET'
    })
    console.log(jokeRes)
    handleJokeRes(jokeRes)
}

function handleJokeRes(res){
    const html = generateHtml(res['data'])
    $quickJoke.append(html)
}

function generateHtml(data){
    let html
    if(data['joke']){
        html = `
        <div class="card quick-card" id="${data['joke']['user_id']}">
            <div class="card-header row">
                <div class="header-right col-4">
                    <button class="btn p-0 mb-1">
                        <i class="far fa-star"></i>
                    </button>
                    <a href="/users/${data['joke']['user_id']}/profile" class="card-link">${data['joke']['username']}</a>
                </div>
                <div class="header-left d-flex flex-row justify-content-end col-8">
                    <span class="p-2">
                        <cite>${data['joke']['created_at']}</cite>
                    </span>
                    <span class="p-2">
                        <button class="btn mr-2 p-0 d-inline"   data-bs-toggle="tooltip"  data-bs-placement="top"     title="Report User">
                            <i class="fas fa-flag"></i>
                        </button>
                    </span>`

        if(data['user_id'] === sessionStorage.getItem('curr_user')){
            const joke_settings = `
            <span class="p-2">
                <button class="btn mr-2 p-0 d-inline" type="button"     id="dropdownMenuButton1" data-bs-toggle="dropdown"          aria-expanded="false">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu"   aria-labelledby="dropdownMenuButton1">
                    <li>
                        <a class="dropdown-item" href="/jokes/${data['joke']['id']}/edit">Edit Joke</a>
                    </li>
                    <li>
                        <a class="dropdown-item" href="/jokes/${data['joke']['id']}/delete">Delete Joke</a>
                    </li>
                </ul>
            </span>`
            html = html + joke_settings
        }

        const endHtml =`</div>
            </div>
            <div class="card-body row">
                <h5 class="card-title text-center">
                     ${data['joke']['setup']}
                </h5>
                <p class="card-text text-center">${data['joke']['body']}</p>
                <div class="mt-3 d-flex flex-row justify-content-center">
                    <div class="rate-btn p-2 m-2">
                        <button class="btn downrate-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="rate-btn p-2 m-2">
                        <button class="btn uprate-btn">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `

        html = html + endHtml
    } else {
        html = `
        <div class="card no-joke-card">
            <div class="card-body no-joke">
                <h5 class="card-title text-center">
                    Looks like we ran out of Jokes. Please do check back later for more!
               </h5>
            </div>
        </div>
        `
    }
    return html
}

getRandomJoke()