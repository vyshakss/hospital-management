from flask import Flask,render_template,request,redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import oracledb
app=Flask(__name__)
app.secret_key='super_secret_key'
#LOGIN SETUP
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
class User(UserMixin):
   def __init__(self,username,role):
      self.id=username
      self.role = role
@login_manager.user_loader
def load_user(username):
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM app_users WHERE username=:1", [username])
    res = cursor.fetchone()
    conn.close()
    if res:
        return User(res[0],res[1]) # Create user with Role
    return None
def getconn():
 return oracledb.connect(user="system", password="mypassword", dsn="localhost:1521/XE")
# --- 3. LOGIN ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = getconn()
        cursor = conn.cursor()
        # Check if username/password match in DB
        cursor.execute("SELECT username, role FROM app_users WHERE username=:1 AND password=:2", [username, password])
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            # user_data[0] is username, user_data[1] is role
            user_obj = User(user_data[0], user_data[1])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/')
@login_required
def home():
  return render_template('index.html')
#PATIENT ROUTES
@app.route('/submit_patient', methods=['POST'])
@login_required
def submit_patient():
  fname_input=request.form.get('first_name')
  lname_input=request.form.get('last_name')
  age_input=request.form.get('age')
  dob=request.form.get('dob')
  add=request.form.get('address')
  phno=request.form.get('phone')

  try:
   conn=getconn()
   cursor=conn.cursor()
   sql="INSERT INTO patients (first_name, last_name, dob, age,address,phone_number) VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4,:5,:6)"
   cursor.execute(sql,[fname_input,lname_input,dob,age_input,add,phno])
   conn.commit()
   cursor.close()
   conn.close()
   return f"<h1>Success! Added Patient: {fname_input}</h1> <a href='/'>Go Back</a>"

  except oracledb.Error as e:
    return f"<h1>Error!</h1> <p>{e}</p>"
@app.route('/get_patients',methods=['GET']) 
@login_required
def get_patient():
 try:
  conn = oracledb.connect(user="system", password="mypassword", dsn="localhost:1521/XE")
  cursor = conn.cursor()
  cursor.execute("select*from patients")
  all_patients=cursor.fetchall()
  cursor.close()
  conn.close()
  display_text = ""
  for row in all_patients:
      display_text += f"ID: {row[0]} | FirstName: {row[1]} | LastName: {row[2]} | DOB: {row[3]} | Age: {row[4]} | address:{row[5]} | phone number:{row[6]}\n"
        
  if not display_text:
           display_text = "No records found in the database."
  return render_template('index.html', msg=display_text)
 except oracledb.Error as e:
        return render_template('index.html', msg=f"Error: {e}")
@app.route('/delete_patient',methods=['POST'])
@login_required
def delete_patient():
 try:
  conn=getconn()
  cursor=conn.cursor()
  pid=request.form.get('delete_id')
  
  sql="DELETE FROM patients where patient_id=:1"
  cursor.execute(sql,[pid])
  if cursor.rowcount == 0:
            msg = f"Error: Patient ID {pid} not found."
  else:
            msg = f"Success: Patient ID {pid} deleted."
  conn.commit()
  conn.close()
  return render_template('index.html', msg=msg, mode="patient")
 except Exception as e:
  return render_template('index.html', msg=f"Error: Cannot delete. {e}", mode="patient")
#DOCTOR ROUTES
@app.route('/submit_doctor',methods=['POST'])
@login_required
def submit_doctor():
 try:
  conn=getconn()
  cursor=conn.cursor()
  dname=request.form.get('doc_name')
  dspecal=request.form.get('specialization')
  sql="INSERT INTO doctors (specialization,name) VALUES(:1,:2)"
  cursor.execute(sql,[dspecal,dname])
  conn.commit()
  cursor.close()
  conn.close()
  return f"<h1>Success! added doctor: {dname}</h1> <a href='/'>Go Back</a>"
 except oracledb.Error as e:
    return f"<h1>Error!</h1> <p>{e}</p>"
@app.route('/get_doctors',methods=['GET'])
@login_required
def get_doctor():
 try:
  conn = oracledb.connect(user="system", password="mypassword", dsn="localhost:1521/XE")
  cursor = conn.cursor()
  cursor.execute("select*from doctors")
  all_doctors=cursor.fetchall()
  cursor.close()
  conn.close()
  display_text = ""
  for row in all_doctors:
      display_text += f"ID: {row[0]} | Name: {row[1]} | Specialization: {row[2]} | \n"

  if not display_text:
           display_text = "No records found in the database."
  return render_template('index.html', msg=display_text, mode="doctor")
 except oracledb.Error as e:
        return render_template('index.html', msg=f"Error: {e}")
@app.route('/delete_doctor',methods=['POST'])
@login_required
def delete_doctors():
  try:

   pid=request.form.get('delete_id')
   conn=getconn()
   cursor=conn.cursor()
   sql=("DELETE FROM DOCTORS where DOCTOR_ID=:1")
   cursor.execute(sql,[pid])
   if cursor.rowcount == 0:
            msg = f"Error: Patient ID {pid} not found."
   else:
            msg = f"Success: Doctor ID {pid} deleted."
   conn.commit()
   conn.close()
   return render_template('index.html', msg=msg, mode="doctor")
  except Exception as e:
   return render_template('index.html', msg=f"Error: Cannot delete. {e}", mode="patient")
###BILLING ROUTES###

@app.route('/submit_bill', methods=['POST'])
@login_required
def submit_bill():
    try:
        conn = getconn()
        cursor = conn.cursor()
        
        # TCL: SAVEPOINT (Optional, marks a spot to save)
        cursor.execute("SAVEPOINT start_transaction")

        sql = "INSERT INTO bills (patient_id, amount, status, bill_date) VALUES (:1, :2, :3, CURRENT_DATE)"
        cursor.execute(sql, [request.form.get('patient_id'), request.form.get('amount'), request.form.get('status')])
        
        # TCL: COMMIT (Saves data permanently)
        conn.commit() 
        conn.close()
        return render_template('index.html', msg="Success! Bill Created.", mode="bill")
        
    except Exception as e:
        # TCL: ROLLBACK (Undoes changes if error occurs)
        if 'conn' in locals():
            conn.rollback() 
            conn.close()
        return render_template('index.html', msg=f"Transaction Failed & Rolled Back: {e}", mode="bill")
@app.route('/get_bills',methods=['GET'])
@login_required
def get_bill():
 try:
  conn = getconn()
  cursor = conn.cursor()
  cursor.execute("select*from bills")
  all_bill=cursor.fetchall()
  cursor.close()
  conn.close()
  display_text = ""
  for row in all_bill:
      display_text += f"Bill #{row[0]} | Patient ID: {row[1]} | Amount: ${row[2]} | Status: {row[3]} | Date: {row[4]}\n"
  if not display_text:
           display_text = "No records found in the database."
  return render_template('index.html', msg=display_text,mode="bill")
 except oracledb.Error as e:
        return render_template('index.html', msg=f"Error: {e}")
@app.route('/update_bill',methods=['POST'])
@login_required
def update_bill():
 try:
   conn=getconn()
   cursor=conn.cursor()
   billid=request.form.get('bill_id')
   stat=request.form.get('new_status')
   sql=("UPDATE bills set status=:1 where bill_id=:2")
   cursor.execute(sql,[stat,billid])
   conn.commit() 
   conn.close()
   return f"<h1>Success! added bill: {billid}</h1> <a href='/'>Go Back</a>"
 except Exception as e:
   return render_template('index.html', msg=f"Error: {e}", mode="bill")
##ADMISSSION ROUTES##
@app.route('/submit_admission',methods=['POST'])
@login_required
def submit_admission():
   try:
      conn=getconn()
      cursor=conn.cursor()
      pid=request.form.get('patient_id')
      dia=request.form.get('diagnosis')
      dd=request.form.get('discharge_date')
      sql=("INSERT into admissions (patient_id,admission_date,discharge_date,diagnosis) values(:1,current_date,TO_DATE(:2, 'YYYY-MM-DD'),:3)")
      cursor.execute(sql,[pid,dd,dia])
      conn.commit()
      conn.close()
      return render_template('index.html', msg="Success! Patient Admitted.", mode="admission")
   except Exception as e:
     return render_template('index.html', msg=f"Error: {e}", mode="bill")

@app.route('/get_admissions',methods=['GET'])
@login_required
def get_admision():
   try:
      conn=getconn()
      cursor=conn.cursor()
      sql = "SELECT admission_id, patient_id, diagnosis, admission_date, discharge_date FROM admissions ORDER BY admission_id DESC"
      cursor.execute(sql)
      all_add=cursor.fetchall()
      cursor.close()
      conn.close()
      display_text = ""
      for row in all_add:
         display_text += f"Admission #{row[0]} | Patient ID: {row[1]} | Diagnosis: {row[2]} | Admission Date: {row[3]} | Discharge Date: {row[4]}\n"
      if not display_text:
           display_text = "No records found in the database."
      return render_template('index.html', msg=display_text,mode="admission")
   except oracledb.Error as e:
        return render_template('index.html', msg=f"Error: {e}", mode="admission")
@app.route('/advanced_reports', methods=['GET'])
@login_required
def advanced_reports():
    if current_user.role != 'admin':
        return render_template('index.html', msg="⛔ ACCESS DENIED.", mode="patient")
    
    try:
        conn = getconn()
        cursor = conn.cursor()

        # THIS QUERY COVERS:
        # Aggregates: COUNT, SUM, AVG, MAX, MIN
        # String Funcs: UPPER, LOWER, SUBSTR, LENGTH, CONCAT (||)
        # Date Funcs: EXTRACT, SYSDATE
        # Clauses: WHERE, GROUP BY, HAVING, ORDER BY, LIKE
        
        sql = """
            SELECT 
                UPPER(p.first_name) || ' ' || LOWER(p.last_name) AS formatted_name,
                LENGTH(p.address) as addr_len,
                COUNT(b.bill_id) as total_bills,
                NVL(SUM(b.amount), 0) as total_spent,
                ROUND(AVG(b.amount), 2) as avg_spent,
                MAX(b.amount) as max_bill,
                MIN(b.amount) as min_bill,
                EXTRACT(YEAR FROM SYSDATE) - EXTRACT(YEAR FROM p.dob) as calc_age
            FROM patients p
            LEFT JOIN bills b ON p.patient_id = b.patient_id
            WHERE p.address LIKE '%Street%' OR p.address LIKE '%Road%' 
            GROUP BY p.first_name, p.last_name, p.address, p.dob
            HAVING COUNT(b.bill_id) >= 0
            ORDER BY total_spent DESC
        """
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        report_text = "--- 📊 COMPLEX SQL ANALYTICS REPORT ---\n"
        report_text += "(Demonstrates: Aggregates, String/Date Funcs, Joins, Group By)\n\n"
        
        for r in rows:
            report_text += f"Patient: {r[0]} (Len: {r[1]}) | Age: {r[7]}\n"
            report_text += f"Bills: {r[2]} | Total: ${r[3]} | Avg: ${r[4]} | Max: ${r[5]} | Min: ${r[6]}\n"
            report_text += "-" * 40 + "\n"

        conn.close()
        return render_template('index.html', msg=report_text, mode="master")

    except Exception as e:
        return render_template('index.html', msg=f"Error: {e}", mode="master")
# ==========================================
#           MASTER VIEW ROUTE
# ==========================================
@app.route('/get_master_view', methods=['GET'])
@login_required
def get_master_view():
    # 1. SECURITY CHECK: Only Admins allowed
    if current_user.role != 'admin':
        return render_template('index.html', msg="⛔ ACCESS DENIED: You do not have permission to view Master Records.", mode="patient")

    try:
        conn = getconn()
        cursor = conn.cursor()
        
        # --- PART A: FETCH PATIENTS ---
        cursor.execute("SELECT patient_id, first_name, last_name FROM patients ORDER BY patient_id")
        patients = cursor.fetchall()
        
        # --- PART B: FETCH DOCTORS ---
        cursor.execute("SELECT doctor_id, name, specialization FROM doctors ORDER BY doctor_id")
        doctors = cursor.fetchall()

        # --- PART C: FETCH BILLS ---
        cursor.execute("SELECT bill_id, amount, status FROM bills ORDER BY bill_id")
        bills = cursor.fetchall()
        
        conn.close()

        # --- BUILD THE REPORT STRING ---
        display_text = "=== 🏥 HOSPITAL MASTER RECORDS ===\n\n"
        
        display_text += f"--- PATIENTS ({len(patients)} Total) ---\n"
        for p in patients:
            display_text += f"ID: {p[0]} | Name: {p[1]} {p[2]}\n"
        
        display_text += f"\n--- DOCTORS ({len(doctors)} Total) ---\n"
        for d in doctors:
            display_text += f"ID: {d[0]} | Dr. {d[1]} ({d[2]})\n"
            
        display_text += f"\n--- BILLS ({len(bills)} Total) ---\n"
        for b in bills:
            display_text += f"ID: {b[0]} | Amt: ${b[1]} | Status: {b[2]}\n"

        return render_template('index.html', msg=display_text, mode="master")

    except Exception as e:
        return render_template('index.html', msg=f"System Error: {e}", mode="master")


     
 

    


  

if __name__=='__main__':
 app.run(debug=True)
