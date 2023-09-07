from flask import Blueprint,  render_template, redirect, url_for, flash, request 
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user 

#internal imports
from rangers_shop.forms import RegisterForm, LoginForm
from rangers_shop.models import User, db 



#instantiate our  auth blueprint
             #name of blueprint  #import location
auth = Blueprint('auth', __name__, template_folder='auth_templates')


#creating our signup route/endpoint
@auth.route('/signup', methods=['GET', 'POST']) #as soon as we hit the 'register' button changes method from GET to POST
def signup():

    #we need to instantiate our form
    registerform = RegisterForm()

    if request.method == 'POST' and registerform.validate_on_submit():
        #grab the input data from the form & save it to variables
        first_name = registerform.first_name.data
        last_name = registerform.last_name.data 
        username = registerform.username.data
        email = registerform.email.data
        password = registerform.password.data
        print(email, password)

        #check the database for same username and/or email. Querying the database!
        if User.query.filter(User.username == username).first(): #if this comes back as something, that means user with username already exists
            flash('Username already exists. Please Try Again', category='warning')
            return redirect('/signup')

        if User.query.filter(User.email == email).first():
            flash('Email already exists. Please try again', category='warning')
            return redirect('/signup')
        

        #instantiate a user object & commit to the database
        user = User(username, email, password, first_name=first_name, last_name=last_name)

        #add the user object to our database & commit the changes
        db.session.add(user)
        db.session.commit()


        flash(f"You have successfully registered user {username}", category='success')
        return redirect('/signin') #we will add signin route 
    
    return render_template('sign_up.html', form=registerform) #passing the registerform into the html


@auth.route('/signin', methods = ['GET', 'POST'])
def signin():

    loginform = LoginForm()

    if request.method == 'POST' and loginform.validate_on_submit():
        email = loginform.email.data
        password = loginform.password.data
        print(email,password)


        user = User.query.filter(User.email == email).first()
        print(user)

        if user and check_password_hash(user.password, password): #if there is a user that matches the email & the passwords match
            login_user(user) #This we have access to because of the UserMixin we inherited 
            #using the user_loader() function we made so now that will be the current_user of our site
            flash(f"Successfully logged in user {email}", category='success')
            return redirect('/')
        else:
            flash(f"Invalid Email and/or Password, Please try again", category='warning')
            return redirect('/signin')
        
    return render_template('sign_in.html', form=loginform)

@auth.route('/logout') #if don't add methods = [] it defaults to 'GET'
def logout():
    logout_user() #whatever user is the current_user will be logged out. 
    return redirect('/')



