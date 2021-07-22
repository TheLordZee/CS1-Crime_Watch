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
    if(!res['data']['body']){
        res['data']['body'] = ''
    }
    const html = generateHtml(res['data'])
    $quickJoke.append(html)
}

function generateHtml(data){
    let html = `
    <div class="card quick-card" id="${data['user_id']}">
        <div class="card-header row">
            <div class="header-right col-4">
                <button class="btn p-0 mb-1">
                    <i class="far fa-star"></i>
                </button>
                <a href="/users/${data['user_id']}" class="card-link">${data['username']}</a>
                
            </div>
            <div class="header-left d-flex flex-row justify-content-end col-8">
                <span class="p-2">
                    <cite>${data['created_at']}</cite>
                </span>
                <span class="p-2">
                    <button class="btn mr-2 p-0 d-inline"   data-bs-toggle="tooltip"  data-bs-placement="top"     title="Report User">
                        <i class="fas fa-flag"></i>
                    </button>
                </span>
                <span class="p-2 edit-joke-btn">
                    <button class="btn mr-2 p-0 d-inline" type="button"     id="dropdownMenuButton1" data-bs-toggle="dropdown"      aria-expanded="false">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <ul class="dropdown-menu"   aria-labelledby="dropdownMenuButton1">
                        <li>
                            <a class="dropdown-item" href="/jokes/${data['id']}/edit">Edit Joke</a>
                        </li>
                        <li>
                            <a class="dropdown-item" href="/jokes/${data['id']}/delete">Delete Joke</a>
                        </li>
                    </ul>
                </span>
            </div>
        </div>
        <div class="card-body row">
            <h5 class="card-title text-center">
                 ${data['setup']}
            </h5>
            <p class="card-text text-center">${data['body']}</p>
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

    return html
}

getRandomJoke()