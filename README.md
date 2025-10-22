# Microblog_API
API created with Django REST Framework to add Posts, Comments and share them with other people.
Its use is very simple and straightforward, below you can find a breakdown of the endpoints you can test so far:

* Users
    * POST /api/register/ → create user
    * POST /api/login/ → obtain token JWT
    * GET /api/users/\<id>/ → see profile (only public information)
* Posts
    * GET /api/posts/ → list of all the posts
    * POST /api/posts/ → create post (authentication required)
    * GET /api/posts/\<id>/ → detail of the post
    * PUT /api/posts/\<id>/ → edit post (only author)
    * DELETE /api/posts/\<id>/ → delete post (only author)
* Comentarios
    * GET /api/posts/\<id>/comments/ → list comments of the post
    * POST /api/posts/\<id>/comments/ → create comment (authentication required - another user's posts can be commented)
    * PUT /api/posts/\<id>/comments/\<id> → edit comment (authentication required)
    * DELETE /api/comments/\<id>/ → delete comment (only author)
* Likes
    * POST /api/posts/\<id>/like/ → mark/unmark like
    * GET /api/posts/\<id>/likes/ -> see all the users that liked the post
 
JSON Web Token (JWT) was used for authentication. When doing POST /api/login, both a refresh and access token will be provided. The 'access' token will expire after 5 minutes, thus a new one will be needed. You can get it by sending the request '**POST /api/token/refresh**' passing the 'refresh' token in the Body.

The user will be allowed to filter posts or comments either by author or key words, as well as ordering the list by title or date of creation.

## Run the application
All the required packages and dependencies are added into **requirements.txt** and will be installed in Docker containers
* make up

***NOTE***: the migrations are applied when you start the application, but in case you want to make some changes and want to migrate again, you can use the commands in Makefile.
