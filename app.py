from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from nltk import sent_tokenize
from transformers import T5Tokenizer, T5ForConditionalGeneration


app = Flask(__name__)

# Clé secrète pour les sessions
app.secret_key = os.urandom(24)

# Configuration de la base de données MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'flask'
}


# Connexion à la base de données
def get_db_connection():
    return mysql.connector.connect(**db_config)


# Validation de l'email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# Chargement du modèle NLP
tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-small-qg-prepend")
model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-small-qg-prepend")


# Fonction pour générer des questions et les enregistrer en base de données
def generate_questions_from_text(text, user_id, max_questions=5):
    sentences = sent_tokenize(text)[:max_questions]
    questions = []

    conn = get_db_connection()
    cursor = conn.cursor()

    for sentence in sentences:
        input_text = f"generate question: {sentence}"
        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        outputs = model.generate(input_ids, max_length=50, num_beams=8, no_repeat_ngram_size=2, early_stopping=True)
        question = tokenizer.decode(outputs[0], skip_special_tokens=True)
        questions.append(question)

        # Insérer la question dans la base de données
        query = "INSERT INTO generated_questions (user_id, question) VALUES (%s, %s)"
        cursor.execute(query, (user_id, question))

    conn.commit()
    cursor.close()
    conn.close()

    return questions


# Page principale (accessible uniquement aux utilisateurs connectés)
@app.route("/", methods=["GET", "POST"])
def index():
    if 'user_id' not in session:  # Vérifie si l'utilisateur est connecté
        return redirect(url_for('login'))  # Redirige vers la connexion

    questions = []
    if request.method == "POST":
        text = request.form.get("text-field")
        if text:
            user_id = session['user_id']
            questions = generate_questions_from_text(text, user_id)

    return render_template("index.html", questions=questions)


# Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')

        if password != confirm_password:
            return render_template('signup.html', error="Les mots de passe ne correspondent pas.")

        if not is_valid_email(email):
            return render_template('signup.html', error="L'email est invalide.")

        if len(password) < 6:
            return render_template('signup.html', error="Le mot de passe doit comporter au moins 6 caractères.")

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return render_template('signup.html', error="Cet email est déjà utilisé.")

            query = "INSERT INTO users (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (firstname, lastname, email, hashed_password))
            conn.commit()

            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            return render_template('signup.html', error=f"Erreur : {err}")
        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not username or not email or not subject or not message:
            return render_template('contact.html', error="Tous les champs sont requis.")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = "INSERT INTO contacts (username, email, subject, message) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, email, subject, message))
            conn.commit()

            return render_template('contact.html', success="Message envoyé avec succès!")

        except mysql.connector.Error as err:
            return render_template('contact.html', error=f"Erreur : {err}")

        finally:
            cursor.close()
            conn.close()

    return render_template('contact.html')



# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']  # Stocker l'ID utilisateur dans la session
                session['email'] = user['email']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Email ou mot de passe incorrect.")

        except mysql.connector.Error as err:
            return render_template('login.html', error=f"Erreur : {err}")

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/delete_question/<question_text>', methods=['POST'])
def delete_question(question_text):
    global questions
    questions = [q for q in questions if q != question_text]  # Retirer la question de la liste
    return redirect(url_for('index'))  # Rediriger vers la page d'accueil après la suppression


# Route pour se déconnecter
@app.route('/logout')
def logout():
    session.clear()  # Supprime toutes les données de session
    return redirect(url_for('login'))


# Autres pages (Accessibles sans connexion)
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/integrations')
def integrations():
    return render_template('integrations.html')


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@app.route('/')
def home():
    return render_template('home.html')


# Lancement de l'application
if __name__ == '_main_':
    app.run(debug=True)