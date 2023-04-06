# __Cyberbullying Detection System__

## __1. Description__
- A machine learning-based web application using Support Vector Machine (SVM) to classify textual content from tweets into non-hate speech (non-cyberbullying) or hate speech (cyberbullying).

## __2. Screenshots__
<div align="center">

![main](https://user-images.githubusercontent.com/70854339/230318261-f2cbd21d-e8f9-48c2-a9da-ac5260db0829.png)
*Main page*

![register](https://user-images.githubusercontent.com/70854339/230318281-e49dd948-e2a2-4464-90ff-d2c49137dc3b.png)
*Register page*

![login](https://user-images.githubusercontent.com/70854339/230318268-656a1db1-6313-41bf-8b49-317c1df780b7.png)
*Login page*

![home](https://user-images.githubusercontent.com/70854339/230318251-cd0f1b71-895e-419e-8e7b-a1b9a8ddad21.png)
*Home page*

![user search](https://user-images.githubusercontent.com/70854339/230318288-cc612d72-5077-4afb-af8b-0fdc96a51af7.png)
*User search page*

![history](https://user-images.githubusercontent.com/70854339/230318242-4897be15-2cef-4a5b-8d4f-82ab31e5b92b.png)
*History page*

![profile](https://user-images.githubusercontent.com/70854339/230318276-2d04e263-8e67-410a-a2d3-74bfc9f5cf04.png)
*Profile page*
</div>

## __3. Features__
- Register an account
- Login to the account with email and password
- Update user profile (username, email and profile picture)
- Scrape tweets based on keywords and classify them into non-cyberbullying or cyberbullying
- Scrape tweets based on Twitter username and classify them into non-cyberbullying or cyberbullying
- Manually insert text and classify it into non-cyberbullying or cyberbullying
- Upload data from CSV file and classify them into non-cyberbullying or cyberbullying
- Add or remove data from database (history)
- Export history in CSV file format to local computer
- Logout from the account

## __4. Live Demo__
- https://cyberbullying-detection-system.onrender.com

## __5. Installation__
- Make sure you have __Git__ and __Python__ installed on your computer to clone and run this application.

    ## __1. Clone this repository__
        git clone https://github.com/timfu04/cyberbullying-detection-system-SVM.git

    ## __2. Go into the repository__
        cd cyberbullying-detection-system-SVM
    
    ## __3. Create Virtual Environment (venv)__
        python -m venv venv
    
    ## __4. Activate Virtual Environment__
        venv\Scripts\activate.bat

    ## __5. Install dependencies__
        pip install -r requirements.txt

    ## __6. Run the app__
        python run.py
