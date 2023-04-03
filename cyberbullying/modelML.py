# Utilities
import pandas as pd

# Machine Learning Modelling
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

# Pre-processing
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Vectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

# Oversampling
from imblearn.over_sampling import ADASYN

# Saving the model
import pickle



# Dataset 1 (Offensive Language and Hate Speech)
#Load first dataset
df1 = pd.read_csv('cyberbullying/dataset/dataset1-offensive-hatespeech.csv')

# Rename columns
df1.rename(columns={'class': 'Class', 'tweet': 'Text'}, inplace=True)

# Select columns
df1 = df1[['Text', 'Class']]

# Replacing values
df1['Class'] = df1['Class'].replace(0, 1).replace(2, 0)


# Dataset 2 (Sexism)
# Load Second Dataset
df2 = pd.read_csv('cyberbullying/dataset/dataset2-sexism.csv')

# Rename columns
df2.rename(columns={'oh_label': 'Class'}, inplace=True)

# Select columns
df2 = df2[['Text', 'Class']]

# Drop rows with NaN (null values)
df2.dropna(inplace=True)

# Convert 'Class' column into type integer
df2['Class'] = df2['Class'].astype(int)


# Concatenate two dataframe (combining 2 datasets)
df = pd.concat([df1, df2], ignore_index=True)


# Text Preprocessing
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
    text = text.split()  # word tokenize
    text = [lm.lemmatize(t) for t in text]  # lemmatization
    text = [word for word in text if word not in sw]  # remove stopwords
    return text


# Apply cleaned text on new column
df['Cleaned_Text'] = df.apply(lambda x: preprocessing(x['Text']), axis=1)


# Define independent variable and target variable
x_corpus = []
def listToStr(list):
    for i in list:
        i = ' '.join(map(str, i))
        x_corpus.append(i)


listToStr(df['Cleaned_Text'].values)
y_class = df['Class'].values


# Data splitting
Xtrain, Xtest, y_train, y_test = train_test_split(x_corpus, y_class, test_size=0.2, random_state=42)


# Vectorization
# TF-IDF
tfidf = TfidfVectorizer()
x_train = tfidf.fit_transform(Xtrain)
x_test = tfidf.transform(Xtest)


# Oversampling
# ADASYN
adasyn = ADASYN(random_state=42)
x_train_over, y_train_over = adasyn.fit_resample(x_train, y_train)


# Machine Learning Model
# Support Vector Classification (Linear SVM)
svc = LinearSVC(random_state=42)
svc.fit(x_train_over, y_train_over)
y_pred = svc.predict(x_test)
accuracy = accuracy_score(y_test, y_pred)


# Results
print('SVM Accuracy: ', accuracy)
print("\nClassification Report:\n\n", metrics.classification_report(y_test, y_pred))


# Save the model (Write in binary mode)
with open('svm_model_pickle', 'wb') as f:
    pickle.dump(svc, f)


# Save vectorizer
pickle.dump(tfidf, open("tfidf_vec.pickle", "wb"))





