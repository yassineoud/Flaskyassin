from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route for Home page
# Load the model and tokenizer
tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-small-qg-prepend")
model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-small-qg-prepend")

# Function to generate questions
def generate_questions_from_text(text, max_questions=5):
    sentences = sent_tokenize(text)
    sentences = sentences[:max_questions]
    questions = []
    for sentence in sentences:
        input_text = f"generate question: {sentence}"
        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        outputs = model.generate(
            input_ids,
            max_length=50,
            num_beams=8,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        question = tokenizer.decode(outputs[0], skip_special_tokens=True)
        questions.append(question)
    return questions

@app.route("/", methods=["GET", "POST"])
def index():
    questions = []
    if request.method == "POST":
        text = request.form["text"]
        if text:
            questions = generate_questions_from_text(text)
    return render_template("index.html", questions=questions)



# Route for About page
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/')
def home():
    return render_template('index.html')  # or another home page template you want to use

# Route for Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Here you can handle the email sending logic, e.g., using smtplib or any other method
        # For example, send email with the collected data:
        # send_email(username, email, subject, message)

        # Redirect to a success page or show a success message
    return render_template('contact.html')



# Route for Login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for Sign-up page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route for Blog page
@app.route('/blog')
def blog():
    return render_template('blog.html')

# Route for Integrations page
@app.route('/integrations')
def integrations():
    return render_template('integrations.html')

# Route for Support page
@app.route('/support')
def support():
    return render_template('support.html')

# Route for Testimonials page
@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

# Route for Services page
@app.route('/service')
def service():
    return render_template('service.html')

# Route for FAQ page
@app.route('/faq')
def faq():
    return render_template('faq.html')

# Route for Our Team page
@app.route('/team')
def team():
    return render_template('team.html')

# Route for Error page (404)
@app.route('/error')
def error():
    return render_template('error.html')
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')  # Replace with your actual template for the privacy policy





# Route for Support

# Route for Disclaimer
@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')  # Ensure the disclaimer.html template exists


if __name__ == '__main__':
    app.run(debug=True)
