class User {

    constructor({id, email, username, is_admin, show_nsfw, created_at}){
        this.id = id;
        this.email = email;
        this.username = username;
        this.is_admin = is_admin;
        this.show_nsfw = show_nsfw;
        this.created_at = created_at;
    }

}

class Joke {

    constructor({
        id, 
        user_id, 
        setup, 
        body, 
        created_at, 
        is_nsfw, 
        username
    }){
        this.id = id;
        this.user_id = user_id;
        this.setup = setup;
        this.body = body;
        this.created_at = created_at;
        this.is_nsfw = is_nsfw;
        this.username = username;
    }

}