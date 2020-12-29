"""
Routes and views for the flask application.
"""
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request,url_for,  flash, redirect
from FlaskWebProject2 import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

import pyodbc
import pandas
conx_string = "driver={SQL SERVER}; server=DESKTOP-E9RIB71\SQLEXPRESS; database=Club Elections; trusted_connection=YES;"

############################# Form Classes #######################################################
class LoginForm(FlaskForm):  
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
######################################################################################################333
check=False
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    global check
    form = LoginForm()
    check=False
    if form.validate_on_submit():
        with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            cursor.execute('SELECT COUNT(1) FROM Student WHERE Email=?', form.email.data)
            data = cursor.fetchone()
            if data[0]>0:
                cursor.execute('SELECT Student_ID FROM Student WHERE Email=?', form.email.data)
                StudentID=cursor.fetchone()[0]
                check=True
                flash('You have been logged in!', 'success')
                return redirect(url_for('home',  st_id = StudentID))
            elif form.email.data == 'life@admin.habib.edu.pk' and form.password.data == 'password':
                flash('You have been logged in!', 'success')
                check=True
                return redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)




@app.route('/dashboard')
def dashboard():
    """Renders the home page."""
    
    global check
    if check:
        return render_template(
        'dashboard.html',
        title='Dashboard Page',
        year=datetime.now().year,
    )
    else:
        return redirect(url_for('login'))


@app.route('/election')
def election():
    return render_template('election.html')

@app.route('/candidate_approval')
def candidate_approval():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT (select Name from Student where Student_ID=C.Candidate_StudentID),(select [Club Name] from Club where Club_ID=C.Club_ID), (SELECT DesignationRole from Position where Position_ID=C.Position_ID),(SELECT ElectionYear from Election where ElectionID=C.ElectionID) from Candidate C where isApproved=0"
        cursor.execute(query1)
        data = cursor.fetchall()
        return render_template('candidate_approval.html', data=data)

@app.route('/candidate_approved')
def candidate_approved():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT (select Name from Student where Student_ID=C.Candidate_StudentID),(select [Club Name] from Club where Club_ID=C.Club_ID), (SELECT DesignationRole from Position where Position_ID=C.Position_ID),(SELECT ElectionYear from Election where ElectionID=C.ElectionID) from Candidate C where C.isApproved=1"
        cursor.execute(query1)
        data = cursor.fetchall()
        return render_template('candidate_approved.html', data=data)

@app.route('/candidate_display/candidate_approval/delete/<Name>')
def delete_candidate(Name):
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query="delete from Candidate where Candidate_StudentID=(select Student_ID from Student where Name=?)"
        cursor.execute(query,Name)
        return redirect(url_for('candidate_approval'))

@app.route('/candidate_display/candidate_approval/approve/<Name>')
def approve_candidate(Name):
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query="update Candidate set isApproved=1 where Candidate_StudentID=(select Student_ID from Student where Name=?)"
        cursor.execute(query,Name)
        return redirect(url_for('candidate_approval'))

@app.route('/candidate_display')
def candidate_display():
    return render_template('candidate_display.html')


@app.route('/add_club', methods=['GET', 'POST'])
def add_club():

    if request.method == 'POST':
        result=request.form
        name=result['Club Name']
        Description=result['Description']
        Patron=result['PatronName']
        ClubImagePath="static/assets/img/ClubImages/"+result['ClubImage']
        print(ClubImagePath)
        with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            query1="SELECT Patron_ID from Patron where Name=?"
            cursor.execute(query1, Patron)
            ID=int(cursor.fetchall()[0][0])
            if ID!=None:
                query="insert into Club ([Club Name], [Club Description], Patron_ID, Monogram) values(?,?,?,?)"
                cursor.execute(query,name, Description, ID, ClubImagePath)
        
                return render_template('dashboard.html', message="New Club Added")

        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        #return redirect(url_for('dashboard.html'))

    # show the form, it wasn't submitted
    return render_template('add_club.html')


@app.route('/view_club')
def view_club():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT Club_ID as Club_ID, [Club Name] as ClubName, [Club Description] as ClubDescription, PatronName= (SELECT Name from Patron where Patron_ID=C.Patron_ID), Monogram from Club C"
        cursor.execute(query1)
        rawdata = cursor.fetchall()
        data=[[column[0] for column in cursor.description],rawdata]
        return render_template('view_club.html', data=data)

@app.route('/edits_<ClubName>', methods=['GET', 'POST'])
def edit_club(ClubName):
    if request.method == 'POST':
        result=request.form
        name=result['Club Name']
        Description=result['Description']
        Patron=result['PatronName']
        ClubImagePath="static/assets/img/ClubImages/"+result['ClubImage']
        with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            query1="SELECT Patron_ID from Patron where Name=?"
            cursor.execute(query1, Patron)
            ID=int(cursor.fetchall()[0][0])
            if ID!=None:
                query="update Club set [Club Name]=? , [Club Description]=? , Patron_ID=?, Monogram=? where [Club Name]=?"
                cursor.execute(query,name, Description, ID, ClubImagePath, ClubName)
                return redirect(url_for('view_club'))
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT C.[Club Name], C.[Club Description], (select Name from Patron where Patron_ID=C.Patron_ID) FROM Club C where C.[Club Name]=?"
        cursor.execute(query1, ClubName)
        data=cursor.fetchone()[0]
        return render_template('edit_club.html', data=data)

    
    
@app.route('/view_election')
def view_election():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT ElectionID, [ElectionYear],PollingStartDate,PollingEndDate,ValidFrom,ValidTill from Election"
        cursor.execute(query1)
        rawdata = cursor.fetchall()
        data=[[column[0] for column in cursor.description],rawdata]
        return render_template('view_election.html', data=data)

     #return render_template('add_election.html')
@app.route('/delete_election/<ID>')
def delete_election(ID):
    print(ID)
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query="EXEC DeleteElection @ID = ?"
        cursor.execute(query,ID)
        return redirect(url_for('view_election'))



@app.route('/add_election', methods=['GET', 'POST'])
def add_election():
    if request.method == 'POST':
        result=request.form
        Id=result['Id']
        EYear=result['Year']
        Pstart=result['PollingStart']
        Pend=result['PollingEnd']
        Vstart=result['ValidFrom']
        Vend=result['ValidTill']
        with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            query="insert into Election (ElectionID, [ElectionYear],PollingStartDate,PollingEndDate,ValidFrom,ValidTill)values(?,?,cast(? as date),cast(? as date),cast(? as date),cast(? as date))"
            cursor.execute(query,Id,EYear, Pstart,Pend,Vstart,Vend)
            return render_template('dashboard.html', message="New Election Created")

        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        #return redirect(url_for('dashboard.html'))

    # show the form, it wasn't submitted
    return render_template('add_election.html')

    #return render_template('add_election.html')
@app.route('/delete_club/<ClubName>')
def delete_club(ClubName):
    print(ClubName)
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query="exec DeleteClub @ClubName=?"
        cursor.execute(query,ClubName)
        return redirect(url_for('view_club'))



@app.route('/add_member',methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        result=request.form
        CN=result['Selected Club']
        SN=result['Selected Student']
        print(SN)
        Tstart=result['TenureStart']
        Tend=result['TenureEnd']
        with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            query="insert into Membership values((select Student_ID from Student where Name=?), (Select Club_ID from Club where [Club Name]=?) ,cast(? as date),cast(? as date),1)"
            cursor.execute(query,SN,CN, Tstart, Tend)
            return render_template('dashboard.html', message="New Election Created")
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT [Club Name] FROM Club C"
        cursor.execute(query1)
        clubs=cursor.fetchall()
        query="SELECT Name from Student"
        cursor.execute(query)
        names=cursor.fetchall()
    return render_template('add_member.html', names=names, clubs=clubs)

@app.route('/view_member')
def view_member():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT (select Name from Student where Student_ID=M.Student_ID),(select [Club Name] from Club where Club_ID=M.Club_ID),TenureStart,TenureEnd, isActive, M.Student_ID, M.Club_ID from Membership M"
        cursor.execute(query1)
        data = cursor.fetchall()
        return render_template('view_members.html', data=data)
 
@app.route('/delete_member_<MemberID>_<ClubID>')
def delete_member(MemberID, ClubID):
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query="EXEC DeleteMember @ID=? , @ClubID=? "
        cursor.execute(query,MemberID, ClubID)
        return redirect(url_for('view_member'))



@app.route('/stats')
def stats():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT ElectionID, [ElectionYear],PollingStartDate,PollingEndDate,ValidFrom,ValidTill from Election where ElectionYear=DATEPART(year, getdate())"
        cursor.execute(query1)
        enabled = cursor.fetchall()
        query2="SELECT ElectionID, [ElectionYear],PollingStartDate,PollingEndDate,ValidFrom,ValidTill from Election where ElectionYear<DATEPART(year, getdate())"
        cursor.execute(query2)
        past = cursor.fetchall()
        query3="SELECT ElectionID, [ElectionYear],PollingStartDate,PollingEndDate,ValidFrom,ValidTill from Election where ElectionYear>DATEPART(year, getdate())"
        cursor.execute(query3)
        disabled = cursor.fetchall()
        return render_template('stats.html', enabled=enabled, past=past, disabled=disabled)

@app.route('/current_stats')
def current_stats():
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query1="SELECT Club_ID as Club_ID, [Club Name] as ClubName, Monogram from Club"
        cursor.execute(query1)
        Clubs = cursor.fetchall()
        return render_template('current_stats.html', Clubs=Clubs)

@app.route('/showResults_<ClubID>')
def showResults(ClubID):
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        query="Select [Club Name] from Club where Club_ID=?"
        cursor.execute(query, ClubID)
        ClubName=str(cursor.fetchall()[0][0]).strip()
        print(ClubName)
        query1="exec GetResults @ClubID=?, @PositionID=?"
        cursor.execute(query1, ClubID, 1)
        Results1 = cursor.fetchall()
        candidates1 = [x[0] for x in Results1]
        y_pos = np.arange(len(candidates1))
        votes1 =  [x[1] for x in Results1]
        plt.bar(y_pos, votes1, align='center', alpha=0.5)
        plt.xticks(y_pos, candidates1)
        plt.ylabel('Votes')
        plt.title('President Election Results')
        path1='C:/Users/HP/source/repos/FlaskWebProject2/FlaskWebProject2/FlaskWebProject2/static/assets/img/plots/'+ClubName+'/President.png'
        plt.savefig(path1)
        plt.cla()
        plt.clf()
        cursor.execute(query1, ClubID, 2)
        Results2 = cursor.fetchall()
        candidates2 = [x[0] for x in Results2]
        y_pos = np.arange(len(candidates2))
        votes2 =  [x[1] for x in Results2]
        plt.bar(y_pos, votes2, align='center', alpha=0.5)
        plt.xticks(y_pos, candidates2)
        plt.ylabel('Votes')
        plt.title('Vice President Election Results')
        path2='C:/Users/HP/source/repos/FlaskWebProject2/FlaskWebProject2/FlaskWebProject2/static/assets/img/plots/'+ClubName+'/VPresident.png'
        plt.savefig(path2)
        plt.cla()
        plt.clf()
        cursor.execute(query1, ClubID, 3)
        Results3 = cursor.fetchall()
        candidates3 = [x[0] for x in Results3]
        y_pos = np.arange(len(candidates3))
        votes3 =  [x[1] for x in Results3]
        plt.bar(y_pos, votes3, align='center', alpha=0.5)
        plt.xticks(y_pos, candidates3)
        plt.ylabel('Votes')
        plt.title('Treasurer Election Results')
        path3='C:/Users/HP/source/repos/FlaskWebProject2/FlaskWebProject2/FlaskWebProject2/static/assets/img/plots/'+ClubName+'/Treasurer.png'
        plt.savefig(path3)
        plt.cla()
        plt.clf()
        #plt.savefig('static/assets/img/plots/<ClubName>/Treasurer.png')
        cursor.execute(query1, ClubID, 4)
        Results4 = cursor.fetchall()
        candidates4 = [x[0] for x in Results4]
        y_pos = np.arange(len(candidates4))
        votes4 =  [x[1] for x in Results4]
        plt.bar(y_pos, votes4, align='center', alpha=0.5)
        plt.xticks(y_pos, candidates4)
        plt.ylabel('Votes')
        plt.title('GeneralSecretary Election Results')
        path4='C:/Users/HP/source/repos/FlaskWebProject2/FlaskWebProject2/FlaskWebProject2/static/assets/img/plots/'+ClubName+'/GS.png'
        plt.savefig(path4)
        plt.cla()
        plt.clf()
        #plt.savefig('static/assets/img/plots/<ClubName>/GS.png')
    return render_template('showResults.html', ClubName=ClubName)
    


#############################################################################################3


@app.route('/home_<st_id>')
def home(st_id):
    
    global check
    if check:
        with pyodbc.connect(conx_string) as conx:
           query1 = "SELECT Club.Club_ID, Monogram, [Club Name] FROM Club, Membership WHERE Club.Club_ID = Membership.Club_ID AND Membership.Student_ID = ?"
           cursor = conx.cursor()
           cursor.execute(query1, st_id)
           #Query = pd.read_sql_query(query1, conx)
           #Clubs = pd.DataFrame(Query, columns = ['ClubID', 'ClubName', 'Monogram'])

           Clubs = cursor.fetchall()
           if len(Clubs)==1:
               Clubs.extend([['-1','static/assets/img/ClubImages/empty.png','No Clubs to Add'],['-1','static/assets/img/ClubImages/empty.png','No Clubs to Add'],['-1','static/assets/img/ClubImages/empty.png','No Clubs to Add']])
           if len(Clubs)==1:
               Clubs.extend(['-1','static/assets/img/ClubImages/empty.png','No Clubs to Add'],['-1','static/assets/img/ClubImages/empty.png','No Clubs to Add'])
           if (len(Clubs))==2:
               Clubs.append(['-1','static/assets/img/ClubImages/empty.png','No Clubs to Add'])
           cursor.execute('SELECT Cast(PollingStartDate as date) FROM Election where ElectionYear=DATEPART(year, getdate())+1')
           ED = cursor.fetchone()[0]
           cursor.execute("SELECT [Name], Image from Student Where Student_ID = ?", st_id)
           name = cursor.fetchone()
           return render_template('home.html', title = "Home", Clubs = Clubs, ed = ED, st_id = st_id, name = name)
    else:
        return redirect(url_for('login'))

@app.route('/home_<st_id>_club_<club_id>')
def club(club_id, st_id):
    #with pyodbc.connect(conx_string) as conx:
        #cursor = conx.cursor()
     #   query1 = "SELECT Club.Club_ID, Club.[Club Description] ,[Club Name], Monogram, Club.Patron_ID,  Patron.[Name], Patron.Description FROM Club, Patron WHERE Club.Patron_ID =Patron.Patron_ID AND Club_ID= 2"
      #  Query = pd.read_sql_query(query1, conx)
       # Clubs = pd.DataFrame(Query, columns = ['clubID', 'ClubDescription','ClubName', 'Monograme', 'PatronID', 'PatronName', 'PatronDescription' ] )
    
    with pyodbc.connect(conx_string) as conx:
        query1 = "SELECT Club.Club_ID, Club.[Club Description] ,[Club Name], Monogram, Club.Patron_ID,  Patron.[Name], Patron.Description FROM Club, Patron WHERE  Club.Patron_ID =Patron.Patron_ID and Club_ID= ?"
        cursor = conx.cursor()
        cursor.execute(query1, int(club_id))
        data = cursor.fetchone() 

        xd = conx.cursor()
        xd.execute("SELECT [Name],[Image],  DesignationRole FROM Student, ExecutiveBody, Position WHERE ExecutiveBody.Position = Position.Position_ID AND ExecutiveBody.Student_ID = Student.Student_ID AND ClubID = ?", club_id)  
        exec = xd.fetchall() 
        
        cursor = conx.cursor()
        cursor.execute("SELECT [Name] from Student Where Student_ID = ?", st_id)
        name = cursor.fetchone()[0]
        return render_template('club.html', data= data, exec = exec, name = name,  st_id = st_id)




@app.route('/home_<string:st_id>_club_<string:club_id>_vote')
def vote(st_id,club_id):
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        cursor.execute("SELECT [Name] from Student Where Student_ID = ?", st_id)
        name = cursor.fetchone()[0]
        return render_template('vote.html', clubid= club_id, name=name, st_id = st_id)



@app.route('/home_<st_id>_club_<club_id>_vote_<pos>_candidate', methods = ['GET', 'POST'])
def candidate(st_id, club_id, pos):
    if request.method == 'POST':
        c_id  = request.form['vote']
        with pyodbc.connect(conx_string) as conx:
            E_cursor = conx.cursor()
            query1 = "SELECT ElectionID from Election where ElectionYear=DATEPART(year, getdate())"
            E_cursor.execute(query1)
            elc = E_cursor.fetchone()[0]
            cursor = conx.cursor()
            query = "Insert into Vote(Student_Voter_ID, PositionID, ElectionID, ClubID, Student_CandidateID) values (?,?,?,?,?)"
            print(st_id, int(pos), int(elc), int(club_id), c_id);
            cursor.execute(query, st_id, int(pos), int(elc), int(club_id), c_id )

            return render_template('vote.html',st_id = st_id, clubid= club_id, )
    with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            query = "select Student_ID, [Image], [Name], MajorName,Mandate from Student, Candidate, Major where Student_ID=Candidate_StudentID and Student.MajorID = Major.MajorID and Position_ID = ? and Club_ID = ?"
            cursor.execute(query, pos, club_id)
            CD = cursor.fetchall()

            cursor = conx.cursor()
            cursor.execute("SELECT [Name] from Student Where Student_ID = ?", st_id)
            name = cursor.fetchone()[0]
            return render_template('candidate.html', CD = CD, name = name)



@app.route('/home_<st_id>_club_<club_id>_register', methods=['GET', 'POST'])
def register( st_id, club_id,):
    if request.method == 'POST':
        result=request.form
        st_id =result['sID']
        desc = result['experience']
        Position = request.form['P']
        with pyodbc.connect(conx_string) as conx:
            cursor = conx.cursor()
            query1="SELECT ElectionID from Election where ElectionYear=DATEPART(year, getdate())"
            cursor.execute(query1)
            E_id = cursor.fetchone()[0]
            cursor = conx.cursor()
            query="insert into Candidate(Candidate_StudentID, Club_ID, Position_ID, ElectionID, Mandate, isApproved) values(?,?,?,?,?,0)"
            cursor.execute(query, st_id , int(club_id), int(Position) , int(E_id), desc)
        
            return redirect(url_for('home', st_id=st_id))

        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        #return redirect(url_for('dashboard.html'))

    # show the form, it wasn't submitted
    with pyodbc.connect(conx_string) as conx:
        cursor = conx.cursor()
        cursor.execute("SELECT [Name] from Student Where Student_ID = ?", st_id)
        name = cursor.fetchone()[0]
        return render_template('register.html', clubid= club_id, name=name, st_id = st_id)


