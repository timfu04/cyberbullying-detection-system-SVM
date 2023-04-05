import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pickle
import re
import pandas as pd
from datetime import datetime
from winreg import OpenKey, HKEY_CURRENT_USER, QueryValueEx

import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request
from cyberbullying import app, db, bcrypt, twitterAPI
from cyberbullying.forms import (RegisterForm, LoginForm, UpdateProfileForm, UserInputForm, FileInputForm,
                                 TwitterInputForm, TwitterUserForm)
from cyberbullying.modelsDB import User, History
from flask_login import login_user, current_user, logout_user, login_required

# Load machine learning model (Linear SVM)
with open('cyberbullying/svm_model_pickle', 'rb') as f:
    model = pickle.load(f)

# Load Vectorizer (TF-IDF)
vectorizer = pickle.load(open("cyberbullying/tfidf_vec.pickle", "rb"))


# Text preprocessing
def preprocessing(text):
    sw = stopwords.words('english')
    # list of negation
    sw_remove = []
    for i in sw:
        x = re.findall(r'[\']t$|not?', i)
        if x:
            sw_remove.append(i)
    # remove negation in stopwords list
    for i in sw_remove:
        if i in sw:
            sw.remove(i)
    lm = WordNetLemmatizer()
    text = re.sub(r'RT[\s]', ' ', text)  # remove RT keyword
    text = re.sub(r'@[a-zA-Z0-9_]+', ' ', text)  # remove username
    text = re.sub(r'https?://[a-zA-Z0-9/.]+', ' ', text)  # remove URL
    text = re.sub(r'[^\w\s]', ' ', text)  # remove punctuation
    text = re.sub(r'\d+', ' ', text)  # remove digits
    text = text.lower()  # convert text to lower case
    text = text.split()  # word tokenization
    text = [lm.lemmatize(t) for t in text]  # lemmatization
    text = [word for word in text if word not in sw]  # remove stopwords
    return text


# Routes

# Main page
@app.route("/")
@app.route("/main")
def main():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("main.html")


# Register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()

    # Collect register data, hash password and save to database
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)


# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    # Check email and password
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # Redirect user to the initial chosen page after logged in
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check Email and Password.', 'danger')
    return render_template("login.html", title="Login", form=form)


# Save Profile Picture
def save_picture(form_profile_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_profile_pic.filename)  # Split the file name and extension
    picture_filename = random_hex + f_ext  # Replace file name into random hex + extension
    picture_path = os.path.join(app.root_path, 'static/profile_pic', picture_filename)
    output_size = (125, 125)  # Set to size 125x125
    img = Image.open(form_profile_pic)
    img.thumbnail(output_size)
    img.save(picture_path)
    return picture_filename


# Profile Page
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.profile_pic.data:  # If picture is uploaded
            picture_file = save_picture(form.profile_pic.data)  # Get file name
            current_user.profile_img = picture_file  # Set uploaded picture as profile picture
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_img = url_for('static', filename='profile_pic/' + current_user.profile_img)
    return render_template("profile.html", title="Profile", image_file=profile_img, form=form)


# Convert list to string
def list2str(s):
    str1 = " "
    return (str1.join(s))


# Get value from list
def output_text(user_pred):
    for i in user_pred:
        return str(i)


# Pre-process text and make prediction
def make_pred(text):
    input_vector = []
    clean_input = preprocessing(text)
    input_vector.append(list2str(clean_input))
    new_test = vectorizer.transform(input_vector)
    new_pred = model.predict(new_test)
    final_output = output_text(new_pred)
    return final_output



# Home page
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    # Text input form
    form = UserInputForm()
    final_output = None

    # Classify user input(text) and save it to database
    if form.validate_on_submit():
        text = str(form.user_text.data)
        final_output = make_pred(text)
        historical = History(content=form.user_text.data, status=final_output, author=current_user)
        db.session.add(historical)
        db.session.commit()
        flash('Text is added to history.', 'success')


    # File input form
    form2 = FileInputForm()
    file_df = pd.DataFrame()

    # Create dataframe based on uploaded file
    if form2.validate_on_submit():
        if form2.csv_file.data:
            file_text = form2.csv_file.data
            file_csv = pd.read_csv(file_text, names=['Text'])
            file_df = pd.DataFrame(file_csv)

            # Classify all file content and save all to the database
            if not file_df.empty:
                file_df['Class'] = file_df.apply(lambda x: make_pred(x['Text']), axis=1)
                for text, status in zip(file_df['Text'], file_df['Class']):
                    historical = History(content=text, status=status, author=current_user)
                    db.session.add(historical)
                    db.session.commit()
                flash('File content is added to history.', 'success')
            else:
                flash('File uploaded is empty. Please try again.', 'danger')
                return redirect(url_for('home'))


    # Twitter keyword search form
    tweets_df = pd.DataFrame()
    form3 = TwitterInputForm()

    # Collect 20 tweets based on keyword and classify each of them
    if form3.validate_on_submit():
        search = str(form3.tweet_search.data)
        if not isinstance(request.form.get('add'), str):
            tweets_df = twitterAPI.get_tweets(search)
            if not tweets_df.empty:  # if dataframe not empty
                tweets_df['Class'] = tweets_df.apply(lambda x: make_pred(x['tweet_text']), axis=1)
                tweets_df.to_csv('cyberbullying/temp_tweets.csv', index=False)

        # Save selected tweet by the user to the database
        if request.method == "POST":
            if isinstance(request.form.get('add'), str):
                tweets_df = pd.read_csv('cyberbullying/temp_tweets.csv')
                tweet_index = request.form.get('add')
                tweet_index = int(tweet_index)
                tweet_string = tweets_df['tweet_text'].iloc[tweet_index]
                tweet_status = int(tweets_df['Class'].iloc[tweet_index])
                historical = History(content=tweet_string, status=tweet_status, author=current_user)
                db.session.add(historical)
                db.session.commit()
                flash('Tweet is added to history.', 'success')

    return render_template("home.html", title="Home", form=form, final_output=final_output, form2=form2,
                           file_df=file_df, form3=form3, tweets_df=tweets_df)


# User ID Search
@app.route("/search", methods=['GET', 'POST'])
@login_required
def user_search():
    user_df = pd.DataFrame()
    form = TwitterUserForm()

    # Collect most recent 20 tweets based on Twitter User ID and classify each of them
    if form.validate_on_submit():
        search = str(form.user_search.data)
        if not request.form.get('add_all') == 'add_all':
            user_df = twitterAPI.userid_search(search)
            if not user_df.empty:
                user_df['Class'] = user_df.apply(lambda x: make_pred(x['tweet_text']), axis=1)
                user_df.to_csv('cyberbullying/temp_tweets.csv', index=False) # save dataframe to CSV file
            else:
                flash('Twitter User ID is not available.', 'danger')

        # Save all collected tweets to the database
        if request.method == "POST":
            if request.form.get('add_all') == 'add_all':
                user_df = pd.read_csv('cyberbullying/temp_tweets.csv')  # read CSV file to get dataframe
                for text, status in zip(user_df['tweet_text'], user_df['Class']):
                    historical = History(content=text, status=status, author=current_user)
                    db.session.add(historical)
                    db.session.commit()
                flash('Tweets are added to history.', 'success')

    return render_template("user_search.html", title="User Search", form=form, user_df=user_df)


# History page
@app.route("/history", methods=['GET', 'POST'])
@login_required
def history():
    historical = History.query.all()  # get all data from History table (show history)

    # Remove history which are selected by the user
    if request.method == "POST":
        history_id = request.form.get('remove')
        historical2 = History.query.get(history_id)
        if historical2:
            db.session.delete(historical2)
            db.session.commit()
            return redirect(url_for('history'))

    return render_template("history.html", title="History", historical=historical)


# Export history
@app.route("/export", methods=['POST'])
@login_required
def export_history():
    if request.method == "POST":
        historical = History.query.all()  # get all data from History table
        
        # Create arrays to create a dictionary, then create dataframe with that dictionary
        if historical != []:
            date_arr = []
            content_arr = []
            status_arr = []
            for historical_records in historical:
                date = historical_records.date.strftime('%d-%m-%Y')
                date_arr.append(date)
                content = historical_records.content
                content_arr.append(content)
                status = historical_records.status
                status_arr.append(status)
            history_dict = {'Date': date_arr, 'Text': content_arr, 'Class': status_arr}
            history_df = pd.DataFrame(history_dict)
            
            # Get "Downloads" folder path with Windows Registry UUIDs
            with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
                source_path = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

            # current datetime string in "DDMMYYY_HHMMSS" format
            datetime_string = datetime.now().strftime("%d%m%Y_%H%M%S")
            export_file_name = f"history_{datetime_string}"
            export_file_path = f"{source_path}\{export_file_name}.csv"
            
            # Export CSV in user's Downloads folder
            if not history_df.empty:
                history_df.to_csv(export_file_path, index=False, header=True) 
                            
        return redirect(url_for('history'))


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))
