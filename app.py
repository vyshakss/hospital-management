from flask import Flask,render_template,request
import oracledb
app=Flask(__name__)
@app.route('/')
def home():
  return render_template('index.html')
@app.route('/submit', methods=['POST'])
def submit_data():
  name_input=request.form.get('patient_name')
  age_input=request.form.get('patient_age')
  try:
   conn=oracledb.connect(user="system", password="mypassword", dsn="localhost:1521/XE")
   cursor=conn.cursor()
   sql="INSERT INTO patients (name,age) values(:1,:2)"
   cursor.execute(sql,[name_input,age_input])
   conn.commit()
   cursor.close()
   conn.close()
   return f"<h1>Success! Added Patient: {name_input}</h1> <a href='/'>Go Back</a>"

  except oracledb.Error as e:
    return f"<h1>Error!</h1> <p>{e}</p>"
@app.route('/get_data',methods=['GET']) 
def show_data():
 try:
  conn = oracledb.connect(user="system", password="mypassword", dsn="localhost:1521/XE")
  cursor = conn.cursor()
  cursor.execute("select*from patients")
  all_patients=cursor.fetchall()
  cursor.close()
  conn.close()
  display_text = ""
  for row in all_patients:
      display_text += f"ID: {row[0]} | Name: {row[1]} | Age: {row[2]}\n"
        
  if not display_text:
           display_text = "No records found in the database."
  return render_template('index.html', msg=display_text)
 except oracledb.Error as e:
        return render_template('index.html', msg=f"Error: {e}") 
if __name__=='__main__':
 app.run(debug=True)
