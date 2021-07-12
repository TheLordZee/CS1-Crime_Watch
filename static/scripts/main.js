const $jokeList = $("#jokes-list");

// async function toggleUpRate(tar, id){

// };

$jokeList.on("click", ".uprate-btn", function(e){
    console.log(e)
    console.log(e.target)
    console.log(e.target.localName)
    if(e.target.localName === "i"){
        console.log(e.target.parentElement.parentElement.parentElement.parentElement.parentElement.id)
    } else if(e.target.localName === "button"){
        console.log(e.target.parentElement.parentElement.parentElement.parentElement.id)
    }
})