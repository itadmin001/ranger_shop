#external imports
from flask import Flask 
from flask_migrate import Migrate 
from flask_cors import CORS
from flask_jwt_extended import JWTManager


#internal imports
from config import Config
from .blueprints.site.routes import site
from .blueprints.auth.routes import auth
from .blueprints.api.routes import api 
from .models import login_manager, db
from .helpers import JSONENcoder



app = Flask(__name__)
app.config.from_object(Config)
app.json_encoder = JSONENcoder  #were not instantiating an object of this class, we are just pointing to this class
jwt = JWTManager(app) #anywhere in our app we can use this @jwt decorator to protect our routes 


login_manager.init_app(app)
login_manager.login_view = 'auth.sign_in'
login_manager.login_message = "Hey you! Login please :)"
login_manager.login_message_category = "warning"


app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(api)


# @app.route('/') #this is a route decorator 
# def hello_world():
#     return 'Hello, World!'

db.init_app(app)
migrate = Migrate(app, db)
CORS(app) #allows other apps to talk to our application 
