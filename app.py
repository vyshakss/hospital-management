from flask import Flask,render_template,request
import oracledb
app=Flask(__name__)
def getconn():
 return oracledb.connect(user="system", password="mypassword", dsn="localhost:1521/XE")
@app.route('/')
def home():
  return render_template('index.html')
#PATIENT ROUTES
@app.route('/submit_patient', methods=['POST'])
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
@app.route('/submit_bill',methods=['POST'])
def submit_bill():
  try:
      conn=getconn()
      cursor=conn.cursor()
      pid=request.form.get('patient_id')
      amt=request.form.get('amount')
      stat=request.form.get('status')
      sql = """
            INSERT INTO bills (patient_id, amount, status, bill_date) 
            VALUES (:1, :2, :3, CURRENT_DATE)
        """
      cursor.execute(sql,[pid,amt,stat])
      conn.commit()
      cursor.close()
      conn.close()
      return f"<h1>Success! added bill: {pid}</h1> <a href='/'>Go Back</a>"
  except Exception as e:
   return render_template('index.html', msg=f"Error: {e}", mode="bill")
@app.route('/get_bills',methods=['GET'])
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
      



     
 

    


  

if __name__=='__main__':
 app.run(debug=True)
