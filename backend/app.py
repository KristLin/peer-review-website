from flask import Flask, request
from flask_restplus import Resource, Api, fields
from flask_cors import CORS

import json
from datetime import datetime

# import bcrypt
import requests

from database import DB
import utils


app = Flask(__name__)
CORS(app)
db = DB()

# store active users
active_users = {}

api = Api(
    app,
    version="1.0",
    #  Documentation Title
    title="Peer Review Database",
    #  Documentation Description
    description="Peer Review backend APIs.",
)

# set namespaces, remvoe the default namespace before adding new
api.namespaces.clear()
users = api.namespace("users", description="User APIs")
projects = api.namespace("projects", description="Project APIs")
files = api.namespace("files", description="File APIs")
comments = api.namespace("comments", description="File APIs")
likes = api.namespace("likes", description="Like APIs")
news = api.namespace("news", description="News APIs")
test = api.namespace("test", description="Test APIs")
# =============== app setting part end ===============

# =============== data model part start ===============
# user data model
user_model = api.model(
    "user",
    {
        "email": fields.String(
            # required=True,
            description="Email of the user",
            help="Email cannot be blank.",
        ),
        "name": fields.String,
        "password": fields.String,
        "major": fields.String,
        # following data will be set automatically before added
        # "createdTime": fields.String,
        # "commentNum": fields.Integer,
        # "likedNum": fields.Integer,
        # "topNum": fields.Integer,
        # "points": fields.Integer,
    },
)

# login data model
login_model = api.model(
    "login",
    {
        "email": fields.String(
            # required=True,
            description="Email of the user",
            help="Email cannot be blank.",
        ),
        "password": fields.String,
    },
)

# project data model
project_model = api.model(
    "project",
    {
        "user": fields.String,
        "major": fields.String,
        "title": fields.String,
        "description": fields.String,
        # "createdTime": fields.String,
        # "isOnTop": fields.Boolean,
        # "isOnTopTime": fields.String,
    },
)

# file data model
file_model = api.model(
    "file",
    {
        "project": fields.String,
        "user": fields.String,
        "title": fields.String,
        "content": fields.String,
        # "createdTime": fields.String,
        # "rating": fields.Float,
        # "ratingNum": fields.Integer
    },
)

# comment data model
comment_model = api.model(
    "comment",
    {
        "file": fields.String,
        "user": fields.String,
        "userName": fields.String,
        "content": fields.String,
        "rating": fields.Integer,

        # "createdTime": fields.String,
        # "likedNum": fields.Integer
    },
)

# like data model
like_model = api.model(
    "like",
    {
        "comment": fields.String,
        "user": fields.String,
    },
)
# =============== data model part end ===============

# ============ user API part start ============
@users.route("/")
class UsersAPI(Resource):
    @api.doc(description="Register a new user account")
    @api.expect(user_model, validate=True)
    def post(self):
        user_data = request.json
        # received user data is from signup form, need to add other default values
        user_data["createdTime"] = utils.datetime_to_str(datetime.now())
        user_data["likedNum"] = 0
        user_data["commentNum"] = 0
        user_data["topNum"] = 2
        user_data["points"] = 0

        if db.find_user_by_email(user_data["email"]):
            return "The email already exists!", 400
        else:
            if db.add_user(user_data):
                user_data = db.find_user_by_email(user_data["email"])
                # add the user data in the active user list
                active_users[user_data["email"]] = user_data
                return user_data["_id"] + " " + user_data["major"] + " " + user_data["name"], 200
            else:
                return "Error", 400

    @api.doc(description="get all users (only used for test)")
    def get(self):
        all_users = db.find_all_users()
        return all_users, 200


@users.route("/login")
class LoginAPI(Resource):
    @api.doc(description="Log in an user account")
    @api.expect(login_model, validate=True)
    def post(self):
        user_login_data = request.json
        # return user's info directly if user is already in the active user list
        if user_login_data["email"] in active_users:
            user_data = active_users[user_login_data["email"]]
            print(user_data["email"] + " has Already logged in")
            return user_data["_id"] + " " + user_data["major"] + " " + user_data["name"], 200
        
        # find user data using email input
        login_user = db.find_user_by_email(user_login_data["email"])
        if login_user == None:
            return "The user email does not exist", 400
        
        if login_user["password"] == user_login_data["password"]:
            # store active user info
            active_users[login_user["email"]] = login_user
            return login_user["_id"] + " " + login_user["major"] + " " + login_user["name"], 200
        else:
            return "Password is wrong", 400


@users.route("/logout/<string:user_id>")
class LogoutAPI(Resource):
    @api.doc(description="Log out an user account")
    def get(self, user_id):
        user_data = db.find_user_by_id(user_id)
        if user_data:
            if user_data["email"] in active_users:
                # remove the user from active user list
                del active_users[user_data["email"]]
            else:
                print("User is not in the active list, maybe the server has restarted.")
            return "Log out successfully", 200
        else:
            print("Received unknown user logout request, still send back success")
            return "OK", 200


@users.route("/<string:user_id>")
class UserAPI(Resource):
    @api.doc(description="Return user info (except password)")
    def get(self, user_id):
        userData = db.find_user_by_id(user_id)
        if userData:
            # will nor return user password data
            del userData["password"]
            return userData, 200
        else:
            return f"User with id {user_id} is not in the database!", 400
    
    @api.doc(description="Delete a user by its ID")
    def delete(self, user_id):
        delete_user = db.find_user_by_id(user_id)
        if delete_user:
            db.delete_user(user_id)
            msg = {"message": f"User = {user_id} is removed from the database!"}
            return msg, 200
        else:
            return f"User with id {user_id} is not in the database!", 400

@users.route("/exchange_topup")
class ExchangeTopUPAPI(Resource):
    @api.doc(description="Exchange top up number using points")
    @api.param("user_id", "user's id", required=True)
    @api.param("exchangeTopNum", "top up number user want to exchange", required=True, type=int)
    def get(self):
        # extract data from request
        exchangeTopNum = int(request.args.get("exchangeTopNum"))
        user_id = request.args.get("user_id")
        cost = exchangeTopNum * 10

        # find user data using user_id from request
        found_user = db.find_user_by_id(user_id)

        if found_user["points"] >= cost:
            db.update_user(user_id, {
                "points": found_user["points"]-cost, 
                "topNum": found_user["topNum"]+exchangeTopNum
            })
            return "Purchase is successful", 200
        else:
            return "Insufficent points!", 400

@users.route("/top10")
class Top10UsersAPI(Resource):
    @api.doc(description="Get top10 users with highest points")
    def get(self):
        all_users = db.find_all_users()
        return utils.get_top10_users(all_users), 200
# ============ user API part end ============

# ============ project API part start ============
@projects.route("/")
class ProjectsAPI(Resource):
    @api.doc(description="Create a new project")
    @api.expect(project_model, validate=True)
    def post(self):
        project_data = request.json
        # add default properties to the project data
        project_data["createdTime"] = utils.datetime_to_str(datetime.now())
        project_data["isOnTop"] = False
        project_data["isOnTopTime"] = ""
        
        # project files should be stored in file data model
        project_files = project_data["files"] 
        del project_data["files"]
        project_id = db.add_project(project_data)
        if project_id:
            # store project file independently
            for file in project_files:
                file["project"] = project_id
                file["user"] = project_data["user"]
                file["rating"] = 0.0
                file["ratingNum"] = 0
                file["createdTime"] = utils.datetime_to_str(datetime.now())
                db.add_file(file)
            return "Project is uploaded", 200
        else:
            return "Error", 400

    @api.doc(description="Get all projects")
    @api.param("major", "Get all projects of chosen major")
    def get(self):
        major = request.args.get("major")
        all_projects = db.find_all_projects(major)
        # attach files to project
        for project in all_projects:
            project["files"] = db.find_project_files(project["_id"])
        return utils.order_projects(all_projects), 200

@projects.route("/<string:project_id>")
class ProjectAPI(Resource):
    @api.doc(description="Get project by its id")
    def get(self, project_id):
        project_data = db.find_project_by_id(project_id)
        if project_data:
            return project_data, 200
        else:
            return f"Project with id {project_id} is not in the database!", 400
    
    @api.doc(description="Delete a project by its ID")
    def delete(self, project_id):
        delete_project = db.find_project_by_id(project_id)
        if delete_project:
            db.delete_project(project_id)
            msg = {"message": f"Project = {project_id} is removed from the database!"}
            return msg, 200
        else:
            return f"Project with id {project_id} is not in the database!", 400

@projects.route("/topup")
class TopUpAPI(Resource):
    @api.doc(description="Top up a project", required=True)
    @api.param("user_id", "user's id", required=True)
    @api.param("project_id", "project's id")
    def get(self):
        # extract data from request
        user_id = request.args.get("user_id")
        project_id = request.args.get("project_id")

        # find user data using user_id from request
        found_user = db.find_user_by_id(user_id)

        # check if user has sufficient top up number
        if found_user["topNum"] >= 1:
            db.update_user(user_id, {"topNum": found_user["topNum"]-1})
            db.update_project(project_id, {"isOnTop": True, "isOnTopTime": utils.datetime_to_str(datetime.now())})
            return "Project is topped up", 200
        else:
            return "Insufficient top up number!", 400

@projects.route("/cancel_topup")
class CancelTopUpAPI(Resource):
    @api.doc(description="Cancel topping up a project", required=True)
    @api.param("user_id", "user's id", required=True)
    @api.param("project_id", "project's id")
    def get(self):
        user_id = request.args.get("user_id")
        project_id = request.args.get("project_id")
        db.update_project(project_id, {"isOnTop": False, "isOnTopTime": ""})
        return "Project is not topped up now", 200

@projects.route("/user/<string:user_id>")
class ProjectsOfUserAPI(Resource):
    @api.doc(description="Get projects of user")
    def get(self, user_id):
        projects_of_user = db.find_user_projects(user_id)
        # attach files to project
        for project in projects_of_user:
            project["files"] = db.find_project_files(project["_id"])
        return utils.order_projects(projects_of_user), 200
# ============ project API part end ============

# ============ file API part start ============
@files.route("/")
class FilesAPI(Resource):
    @api.doc(description="Create a file")
    @api.expect(file_model, validate=True)
    def post(self):
        if db.add_files(files):
            return "Files are uploaded", 200
        else:
            return "Error", 400

@files.route("/project/<string:project_id>")
class FilesOfProjectAPI(Resource):
    @api.doc(description="Get all files of a project")
    def get(self, project_id):
        files = db.find_project_files(project_id)
        return files, 200    

@files.route("/<string:file_id>")
class FileAPI(Resource):
     def get(self, file_id):
        file_data = db.find_file_by_id(file_id)
        if file_data:
            return file_data, 200
        else:
            return f"File with id {file_id} is not in the database!", 400
# ============ file API part end ============

# ============ comment API part start ============
@comments.route("/")
class CommentsAPI(Resource):
    @api.doc(description="Upload a comment")
    def post(self):
        comment = request.json
        # add default properties to comment data
        comment["createdTime"] = utils.datetime_to_str(datetime.now())
        comment["likedNum"] = 0

        db.add_comment(comment)
        return "Comment uploaded", 200

@comments.route("/file/<string:file_id>")
class CommentsOfFileAPI(Resource):
    @api.doc(description="get file's comments")
    @api.param("user_id", "used for checking if user has liked the comment")
    def get(self, file_id):
        file_comments = db.find_file_comments(file_id)
        user_id = request.args.get("user_id")
        # order the comments by liked number
        file_comments = utils.order_comments(file_comments)
        # need to check if user has liked comment when logged in
        if user_id:
            # add "hasLiked" property to all comment objects
            for comment in file_comments:
                comment["hasLiked"] = db.user_has_liked_comment(user_id, comment["_id"])
            return file_comments, 200
        else:
            return file_comments, 200
# ============ comment API part end ============

# ============ like API part start ============
@likes.route("/")
class LikesAPI(Resource):
    @api.doc(description="like a comment")
    @api.param("user_id", "user's id", required=True)
    @api.param("comment_id", "comment's id", required=True)
    def get(self):
        user_id = request.args.get("user_id")
        comment_id = request.args.get("comment_id")
        db.add_like(user_id, comment_id)
        return "liked successfully", 200
# ============ like API part end ============

# ============ news API part start ============
@news.route("/")
class NewsAPI(Resource):
    @api.param("major", "specify news subject/major (CSE, Business, Medical or Literature)")
    def get(self):
        major = request.args.get("major")
        return utils.get_news(major), 200

# run the app
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
