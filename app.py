from flask import Flask, render_template, request , redirect , url_for
import mysql.connector
import uuid
import datetime
import cv2
import face_recognition
import numpy as np
import time

app = Flask(__name__)

# Configure static URL path
app.static_url_path = '/static'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sample'


# Create connection
db = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)



# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


@app.route('/')
def start():
    return render_template('start.html')

@app.route('/Signup.html')
def Signup():
    return render_template('Signup.html')

@app.route('/voter_login.html')
def voter_login():
    return render_template('voter_login.html')

@app.route('/test1.html')
def test1():
    return render_template('test1.html')

@app.route('/signupAdmin',methods = ['POST'])
def signupAdmin():
    if request.method == 'POST':
        adminusername = request.form.get('username')
        adminEmail = request.form.get('email')
        adminPassword = request.form.get('password')
        sql = "INSERT INTO admin (email, name, password) VALUES (%s, %s, %s)"
        # Define the values to be inserted into the query
        values = (adminEmail, adminusername, adminPassword)
        try:
            cursor = db.cursor()
            # Execute the SQL query
            cursor.execute(sql, values)
            # Commit the transaction
            db.commit()
            return "Admin signup successful"
        except Exception as e:
            # If an error occurs, rollback the transaction
            db.rollback()
            return "An error occurred: " + str(e)
        finally:
            # Close the cursor object
            cursor.close()
    return

@app.route('/signinAdmin', methods=['POST'])
def signinAdmin():
    if request.method == 'POST':
        adminEmail = request.form.get('email')
        adminPassword = request.form.get('password')

        # Fetch the password corresponding to the provided email from the database
        cursor = db.cursor()
        query = "SELECT name, password FROM admin WHERE email = %s"
        cursor.execute(query, (adminEmail,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            # If the email exists in the database, check if the provided password matches
            if result[1] == adminPassword:
                # Password is correct, use the name as the username
                username = result[0]
                return redirect(url_for('election_options', admin_name=username))
            else:
                # Password is incorrect
                return "Incorrect password"
        else:
            # Email not found in the database
            return "Email not found"
        
@app.route('/election_options/<admin_name>')
def election_options(admin_name):
    try:
        # Here, admin_name is already provided as a parameter to the function
        return render_template('election_options.html', admin_name=admin_name)
    except Exception as e:
        print("Error:", e)
        return "An error occurred while rendering the election options page."


@app.route('/election', methods=['GET', 'POST'])
def election():
    if request.method == 'POST':
        num_parties = int(request.form.get('num_parties'))
        admin_name = request.form.get('admin_name')
        return redirect(url_for('party_details', num_parties=num_parties, admin_name=admin_name))
    return render_template('election.html')


@app.route('/create_election/<admin_name>', methods=['GET', 'POST'])
def create_election(admin_name):
    if request.method == 'POST':
        # Handle form submission if needed
        pass
    # Redirect to election.html passing admin_name as a parameter
    return render_template('election.html', admin_name=admin_name)

@app.route('/party_details/<int:num_parties>/<admin_name>', methods=['GET', 'POST'])
def party_details(num_parties, admin_name):
    if request.method == 'POST':
        try:
            cursor = db.cursor()
            for i in range(num_parties):
                party_name = request.form.get(f'party_name_{i}')
                party_symbol = request.form.get(f'party_symbol_{i}')
                if party_name and party_symbol:  # Check if party details are not empty
                    sql = "INSERT INTO parties (partyName, partySymbol, noofVotes) VALUES (%s, %s , %s)"
                    val = (party_name, party_symbol , 0)
                    cursor.execute(sql, val)
                else:
                    # Handle empty party details
                    return "Party details cannot be empty."
            db.commit()
            cursor.close()
            success_message = "Parties added successfully!"
            return redirect(url_for('election_options', admin_name=admin_name, message=success_message))
        except Exception as e:
            # Handle database errors
            return f"An error occurred: {str(e)}"
    else:
        return render_template('party_details.html', num_parties=num_parties, admin_name=admin_name)



@app.route('/delete_election/<admin_name>', methods=['GET', 'POST'])
def delete_election(admin_name):
    if request.method == 'POST':
        return redirect(url_for('confirm_delete_election', admin_name=admin_name))
    return render_template('delete_election.html', admin_name=admin_name)

@app.route('/confirm_delete_election', methods=['POST'])
def confirm_delete_election():
    admin_name = request.form.get('admin_name')  # Assuming admin_name is passed in the form data
    if not admin_name:
        return "Admin name not provided."

    try:
        # Create a cursor object to execute SQL queries
        cursor = db.cursor()

        # Define the DELETE queries to delete all rows from both tables
        delete_queries = [
            "DELETE FROM votedvoters",
            "DELETE FROM parties"
        ]

        # Execute multiple DELETE queries
        for query in delete_queries:
            cursor.execute(query)
        # Commit the changes to the database
        db.commit()

        # Close the cursor
        cursor.close()
        # Redirect to the election options page
        return redirect(url_for('election_options', admin_name=admin_name))
    except mysql.connector.Error as err:
        # Handle any errors that occur during execution
        print("Error:", err)
        return "An error occurred while deleting election data."

@app.route('/view_election/<admin_name>')
def view_election(admin_name):
    try:
        cursor = db.cursor()

        # Fetch parties and count of voters for each party
        cursor.execute("SELECT partyName,noofVotes FROM parties")
        parties_data = cursor.fetchall()

        cursor.close()

        return render_template('view_election.html', parties_data=parties_data, admin_name=admin_name)
    except mysql.connector.Error as err:
        print("Error:", err)
        return "An error occurred while fetching election data."

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        Fname = request.form.get('Fname')
        Lname = request.form.get('Lname')
        Fathername = request.form.get('Fathername')
        Mothername = request.form.get('Mothername')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        nation = request.form.get('nation')
        religion = request.form.get('religion')
        Mstatus = request.form.get('Mstatus')
        mobile = request.form.get('mobile')
        Email = request.form.get('Email')
        aadhar = request.form.get('aadhar')
        address = request.form.get('address')
        zip_code = request.form.get('zip')
        
        # Perform data validation
        if not all([Fname, Lname, Fathername, Mothername, gender, dob, nation, religion, Mstatus, mobile, Email, aadhar, address, zip_code]):
            return 'Incomplete data. Please fill all fields.'

        # Calculate age from date of birth
        try:
            cursor = db.cursor()
            dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d')
            age = (datetime.datetime.now() - dob_date).days // 365  # Calculate age in years
        except ValueError:
            return 'Invalid date of birth format. Please use YYYY-MM-DD.'

        # Insert data into the database
        try:
            # Count existing records in the database
            cursor.execute("SELECT COUNT(*) FROM voter")
            count = cursor.fetchone()[0]
            
            # Generate a voter ID based on the count
            voterId = f"2024{count + 1:04d}"  # Example format: VOTER0001
            
            # Insert data into the database
            cursor.execute("INSERT INTO voter (voterId, firstName, lastName, fatherName, motherName, age, dateOfBirth, gender, nation, religion, mobileNumber, emailAddress, aadharNumber, address, zipCode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (voterId, Fname, Lname, Fathername, Mothername, age, dob, gender, nation, religion, mobile, Email, aadhar, address, zip_code))
            db.commit()
            cursor.close()
            detect_faces(voterId)
            return render_template('voter_created.html', voterId=voterId)
        except mysql.connector.Error as err:
            # Handle MySQL errors
            return f"MySQL Error: {err.msg}"
    return 'Invalid request'

def detect_faces(voterId):
    # Open a connection to the camera (0 represents the default camera)
    cap = cv2.VideoCapture(0)
    start_time = time.time()  # Initialize start time
    face_detected = False  # Flag to track if face is detected
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Perform face detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0:
            if not face_detected:
                start_time = time.time()  # Update start time if face is newly detected
            face_detected = True
            if time.time() - start_time >= 3:  # Check if face is continuously detected for 3 seconds
                # Draw rectangles around the detected faces
                for (x, y, w, h) in faces:
                    cursor = db.cursor()
                    face_roi = frame[y:y+h, x:x+w]
                    # Save the detected face image as a blob
                    _, img_encoded = cv2.imencode('.jpg', face_roi)
                    img_bytes = img_encoded.tobytes()
                    # Update the voterFace column in the database with the detected face image
                    cursor.execute("UPDATE voter SET voterFace = %s WHERE voterId = %s", (img_bytes, voterId))
                    db.commit()
                    cursor.close()
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        else:
            face_detected = False
        
        # Display the resulting frame
        cv2.imshow('Face Detection', frame)
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Release the camera and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/voter_verification', methods=['POST'])
def voter_verification():
    if request.method == 'POST':
        voter_id = request.form['voterId']

        # Cursor to execute SQL queries
        cursor = db.cursor()

        # Execute SQL query to check if the voterId exists
        cursor.execute("SELECT * FROM voter WHERE voterId = %s", (voter_id,))

        result = cursor.fetchone()
        cursor.close()
        if result:
            # If voterId is present, redirect to face_check.html with voterId
            voter_id_to_recognize = request.form['voterId']
            known_face_encoding = get_known_face_from_database(voter_id_to_recognize)
            if known_face_encoding is None:
                return render_template('t3.html', message="Provided voter ID not found in the database.")
            else:
                video_capture = cv2.VideoCapture(0)  # Use 0 for the default camera
                while True:
                    ret, frame = video_capture.read()
                    if recognize_face(known_face_encoding, frame):
                        video_capture.release()
                        cv2.destroyAllWindows()
                        return redirect(url_for('face_check', voterId=voter_id))
                    cv2.imshow('Video', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            return render_template('voter_login.html')
        
        else:
            return "Voter ID not found in the database!"

def encode_images(images):
    face_encodings = []
    for image in images:
        # Convert image to 8-bit format
        image_8bit = cv2.convertScaleAbs(image)

        # Convert image from BGR to RGB
        rgb_image = cv2.cvtColor(image_8bit, cv2.COLOR_BGR2RGB)

        # Encode face if detected
        face_encoding = face_recognition.face_encodings(rgb_image)
        if len(face_encoding) > 0:
            face_encodings.append(face_encoding[0])

    return face_encodings


def get_known_face_from_database(voter_id):
    conn = mysql.connector.connect(
        host="localhost",  # Change 'localhost' to your MySQL server host
        user="root",  # Change 'yourusername' to your MySQL username
        password="",  # Change 'yourpassword' to your MySQL password
        database="sample"  # Change 'yourdatabase' to your MySQL database name
    )
    c = conn.cursor()
    c.execute("SELECT voterFace FROM voter WHERE voterId = %s", (voter_id,))
    row = c.fetchone()
    if row:
        face_image = cv2.imdecode(np.frombuffer(row[0], np.uint8), cv2.IMREAD_COLOR)
        face_encoding = face_recognition.face_encodings(face_image)
        if face_encoding:
            return face_encoding[0]
    conn.close()
    return None


def recognize_face(known_face_encoding, unknown_frame, tolerance=0.4):
    unknown_face_encodings = face_recognition.face_encodings(unknown_frame)
    for unknown_face_encoding in unknown_face_encodings:
        match = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding, tolerance=tolerance)
        if match[0]:
            return True
    return False

# Define a route for face check page
@app.route('/face_check')
def face_check():
    voter_id = request.args.get('voterId')

    # Retrieve voter's name using voterId from the database
    cursor = db.cursor()
    cursor.execute("SELECT firstName,fatherName,motherName,age,mobileNumber FROM voter WHERE voterId = %s", (voter_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        voter_name = result[0]
        fatherName = result[1]
        motherName = result[2]
        age = result[3]
        mobileNumber = result[4]
        return render_template('face_check.html', voterId=voter_id, voterName=voter_name,fatherName = fatherName,motherName = motherName,age = age, mobileNumber = mobileNumber)
    else:
        return "Error: Voter ID not found in the database!"
    
# Define a route for the voting page


# Route for voting page
@app.route('/vote')
def vote():
    # Fetch the voter ID from the request parameters
    voter_id = request.args.get('voterId')
    cursor = db.cursor()
    if voter_id:
        # Check if the voter has already voted
        check_query = "SELECT * FROM votedvoters WHERE votersId = %s"
        cursor.execute(check_query, (voter_id,))
        result = cursor.fetchone()
        if result:
            # Voter has already voted, redirect to a page indicating they cannot vote again
            return render_template('already_voted.html')

    # Fetch all parties from the database
    cursor.execute("SELECT partyName, partySymbol FROM parties")
    parties = cursor.fetchall()
    cursor.close()
    return render_template('vote.html', parties=parties, voterId=voter_id)  # Pass voterId to the template

# Route for submitting the vote
@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if request.method == 'POST':
        cursor = db.cursor()
        # Retrieve the selected party and voter ID from the form data
        selected_party = request.form['party']
        voter_id = request.form['voterId']

        # Increment the number of votes for the selected party in the parties table
        update_query = "UPDATE parties SET noofVotes = noofVotes + 1 WHERE partyName = %s"
        cursor.execute(update_query, (selected_party,))
        db.commit()

        print("Value of voter_id:", voter_id)  # Print the value of voter_id for debugging purposes
        insert_query = "INSERT INTO votedvoters (votersId) VALUES (%s)"
        cursor.execute(insert_query, (voter_id,))
        db.commit()
        cursor.close()
        # Redirect back to the welcome page or any other page as needed
        return redirect(url_for('voter_login'))


if __name__ == '__main__':
    app.run(debug=True)