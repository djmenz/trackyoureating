import web
import json
import datetime
import hashlib
web.config.debug = False

db = web.database(dbn='mysql', user='root', pw='', db='')

now = datetime.datetime.now()
selected_day = now
selected_day_year = now.year
selected_day_month = now.month
selected_day_day = now.day

selected_template = 'weekday'

month_words = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
days_of_the_week = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']


urls = (
    '/', 'index',
    '/add', 'add',
    '/addentry','addentry',g
    '/edittemplates','edittemplates',
    '/deletetemplateitems','deletetemplateitems',
    '/changeselectedtemplate','changeselectedtemplate',
    '/templateentry','templateentry',
    '/templateaddentry','templateaddentry',
    '/stats','stats',
    '/changedate','changedate',
    '/changedatetoday','changedatetoday',
    '/friendchangedate','friendchangedate',
    '/copyentries','copyentries',
    '/deleteitems','deleteitems',
    '/deletetableitems','deletetableitems',
    '/addweight','addweight',
    '/login','login',
    '/logout','logout',
    '/loginhandle','loginhandle',
    '/newuserhandle','newuserhandle',
    '/entries','entries',
    '/friends','friends',
    '/friendspage','friendspage',
    '/requestfriends','requestfriends',
    '/acceptfriends','acceptfriends',
    '/deletefriends','deletefriends',
    '/addnote','addnote',
    '/api/(.*)/(.*)','api'

)

app = web.application(urls, locals())
render = web.template.render('templates/')
web.config.session_parameters['timeout'] =  200000
web.config.session_parameters['ignore_expiry'] = False

session = web.session.Session(app, web.session.DiskStore('var/www/sessions'),initializer={'count': 0})

class index:
    def GET(self):
        print "Is logged in?"
        print session.count
        if (session.count == 0):
            return render.login()
        else:
            foods = db.query("select * from foods where Userid = "+ str(session.userid) + " order by name")
            return render.index(foods, session.username)

class api:
    def GET(self, userid, tempdate):
        user_data = web.input()
        after = False

        
        try:
            user_data.after
            after = True
            tempdate = user_data.after
        except AttributeError:
            after = False


        if (tempdate == "" or after == True):
            tempquerydates = "select distinct Date from masterlist where Userid = " + userid + " order by Date"  
            dates = db.query(tempquerydates)
            if (after == False and tempdate == ""):
                tempdate = "20000101"


            #remove dates that are before the query date
            mainList = []
            for day in dates:
                tempquery = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where ( masterlist.Date = " + "\'" + str(day.Date) + "\'" + " AND masterlist.Userid = " + userid + ")"
                if ((datetime.datetime.strptime(tempdate, '%Y%m%d').date() - day.Date) < datetime.timedelta(days=1)):
                    print datetime.datetime.strptime(tempdate, '%Y%m%d').date() 
                    print day.Date
                    print datetime.datetime.strptime(tempdate, '%Y%m%d').date() - day.Date


                    one_day = db.query(tempquery)
                    days_calories = 0.0
                    days_fat = 0.0
                    days_carbs = 0.0
                    days_protein = 0.0
                    output = ""
                
                    for listitem in one_day:
                        days_calories = days_calories + listitem.calories * listitem.Quantity
                        days_fat = days_fat + listitem.fat * listitem.Quantity
                        days_protein = days_protein + listitem.protein*  listitem.Quantity
                        days_carbs = days_carbs + listitem.carbs * listitem.Quantity
                
                    output = output + str(day.Date) + " - Calorie total<br> = %d <br><br> P = %d <br> C = %d <br> F = %d"  % (days_calories, days_protein, days_carbs, days_fat)
                    #print output
                    
                    #make into nested json object 
                    pyDict = {
                    'date':str(day.Date),
                    'calories':days_calories,
                    'protein': days_protein,
                    'carbs':days_carbs,
                    'fats':days_fat
                    }
                    mainList.append(pyDict)

           
            web.header('Content-Type', 'application/json')
            return json.dumps(mainList)
              
        else:
            tempquery = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where ( masterlist.Date = " + "\'" + tempdate + "\'" + " AND masterlist.Userid = " + userid + ")"
            one_day = db.query(tempquery)
        
            days_calories = 0.0
            days_fat = 0.0
            days_carbs = 0.0
            days_protein = 0.0
            output = ""
        
            for listitem in one_day:
                days_calories = days_calories + listitem.calories * listitem.Quantity
                days_fat = days_fat + listitem.fat * listitem.Quantity
                days_protein = days_protein + listitem.protein*  listitem.Quantity
                days_carbs = days_carbs + listitem.carbs * listitem.Quantity
        
            output = output + "Calorie total<br> = %d <br><br> P = %d <br> C = %d <br> F = %d"  % (days_calories, days_protein, days_carbs, days_fat)

            pyDict = {
            'calories':days_calories,
            'protein': days_protein,
            'carbs':days_carbs,
            'fats':days_fat
            }
        
            web.header('Content-Type', 'application/json')
            return json.dumps(pyDict)


class friendspage:
    def GET(self):
        if (session.count == 0):
            return render.login()
        web_data = web.input(id=str(session.userid))
        friend_userid = web_data.id 
        #if friends, then print the correct page, otherwise display error message
        #if friend_userid 
        
        friends_connectedA = db.query("select Userid from friends left join users on friends.requestor = users.userid where status = 2 AND acceptor = " + str(session.userid)).list()
        friends_connectedB = db.query("select Userid from friends left join users on friends.acceptor = users.userid where status = 2 AND requestor = " + str(session.userid)).list()
        print "friends"
        friends_list = []
        for friends in friends_connectedA:
            friends_list.append(friends.Userid)
        for friends in friends_connectedB:
            friends_list.append(friends.Userid)
            
        print friends_list
        if int(friend_userid) not in friends_list:
            print "not friends"
            return web.seeother('/friends')
        else:
                            
       
            global month_words
            global days_of_the_week
            
            
            try:
                tempdate_obj = datetime.date(int(session.selected_day_year), int(session.selected_day_month), int(session.selected_day_day))
            except:
                now = datetime.datetime.now()
                selected_day = now
                session.selected_day_year = now.year
                session.selected_day_month = now.month
                session.selected_day_day = now.day
                tempdate_obj = datetime.date(int(selected_day_year), int(selected_day_month), int(selected_day_day))
            
            tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
            tempquery = "select foods.calories, foods.protein, foods.fat, foods.carbs, masterlist.Date, foods.name, masterlist.Quantity, masterlist.FoodID from masterlist left join foods on masterlist.FoodID = foods.FoodID where masterlist.Date = " + "\'" + tempdate + "\'" + " AND masterlist.Userid = " + str(friend_userid)
            
            masterlist = list(db.query(tempquery))
            try:
                for fooditem in range(0,len(masterlist)):
                    masterlist[fooditem].calories = masterlist[fooditem].calories * masterlist[fooditem].Quantity
                    masterlist[fooditem].carbs = masterlist[fooditem].carbs * masterlist[fooditem].Quantity
                    masterlist[fooditem].protein = masterlist[fooditem].protein * masterlist[fooditem].Quantity
                    masterlist[fooditem].fat = masterlist[fooditem].fat * masterlist[fooditem].Quantity
            except:
                print "nothin"
                

            t_day = ''
            for x in range(1,32):
                t_day  = t_day  + " <option value=\"" + str(x) + "\""
                if (x == int(session.selected_day_day)):
                    t_day = t_day + "selected=\"selected\""
                t_day = t_day + ">" + str(x)   
           
            t_month = ''
            for x in range(1,13):
                t_month  = t_month  + " <option value=\"" + str(x) + "\""
                if (x == int(session.selected_day_month)):
                    t_month = t_month + "selected=\"selected\""
                t_month = t_month + ">" + month_words[x-1]          
      
            t_year = ''
            for x in range(2014,2030):
                t_year  = t_year  + " <option value=\"" + str(x) + "\""
                if (x == int(session.selected_day_year)):
                    t_year = t_year + "selected=\"selected\""
                t_year = t_year + ">" + str(x)   
                
            tempquery2 = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where ( masterlist.Date = " + "\'" + tempdate + "\'" + " AND masterlist.Userid = " + str(friend_userid) + ")"
            one_day = db.query(tempquery2)
            tempstr = " "
           
            days_calories = 0.0
            days_fat = 0.0
            days_carbs = 0.0
            days_protein = 0.0
            output = " "
            for listitem in one_day:
                days_calories = days_calories + listitem.calories * listitem.Quantity
                days_fat = days_fat + listitem.fat * listitem.Quantity
                days_protein = days_protein + listitem.protein*  listitem.Quantity
                days_carbs = days_carbs + listitem.carbs * listitem.Quantity
            output = output + "Calorie total<br> = %d <br><br> P = %d <br> C = %d <br> F = %d"  % (days_calories, days_protein, days_carbs, days_fat)
            print "DATE test"

                
            start_of_week = (tempdate_obj.toordinal() - tempdate_obj.weekday()) 
            week_dates = []
            for x in range(0,7):
                print datetime.date.fromordinal(start_of_week+x)
                week_dates.append(datetime.date.fromordinal(start_of_week+x))
            list_week = []
            output_week = " "
            total_calories = 0.0
            total_carbs = 0.0
            total_fats = 0.0
            total_protein = 0.0
            days_used = 0
            for date in week_dates:
                days_calories = 0
                days_fat = 0
                days_carbs = 0
                days_protein = 0
                output_week = output_week +"%s\n" % (days_of_the_week[date.weekday()])
                list_week.append(days_of_the_week[date.weekday()] + " " + str(date.day) + "/" + str(date.month))
                
                tempquery = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where masterlist.Date = " + "\'" + str(date) + "\'" + " AND masterlist.Userid = " + str(friend_userid)
                one_day = db.query(tempquery)
                tempstr = " "
                for listitem in one_day:
                    days_calories = days_calories + listitem.calories * listitem.Quantity
                    days_fat = days_fat + listitem.fat * listitem.Quantity
                    days_protein = days_protein + listitem.protein*  listitem.Quantity
                    days_carbs = days_carbs + listitem.carbs * listitem.Quantity
                output_week  = output_week  + " Calorie Total %d - P:%d C:%d F:%d <br>" % (days_calories, days_protein, days_carbs, days_fat)
                if (days_calories > 0):
                    days_used = days_used + 1
                    total_calories = total_calories + days_calories
                    total_carbs = total_carbs + days_carbs
                    total_fats = total_fats + days_fat
                    total_protein = total_protein + days_protein
                
                list_week.append(str(days_calories))
                list_week.append(str(days_protein))
                list_week.append(str(days_carbs))
                list_week.append(str(days_fat))
            
            try:
                avg_week  = " Calorie Averages %d - P:%d C:%d F:%d - (%d/7 days)" % (total_calories/days_used, total_protein/days_used, total_carbs/days_used, total_fats/days_used, days_used)
            except:
                avg_week = " No data"
            
            note_obj = db.query("select notedata from notes where date = " + "\'" + tempdate + "\'" + "and userid = " + str(friend_userid))
            try:
                note_day = note_obj[0].notedata
            except:
                note_day = ""
    
            friends_name = db.query("select Username from users where userid = " + friend_userid)    
            temp_dates, output1 = stats.generate_stats(friend_userid)  
            return render.friendspage(masterlist, t_day, t_month, t_year, output, output_week, list_week, avg_week, note_day, friends_name[0].Username, temp_dates, output1 )    
        

class friends:
    def GET(self):
        potential_friends = db.query("select userid,username from users where userid not in (select requestor from friends where acceptor = " + str(session.userid) + " UNION select acceptor from friends where requestor = " + str(session.userid) + " UNION select userid from friends where userid = " + str(session.userid) + ")")
        friends_requested = db.query("select * from friends left join users on friends.acceptor = users.userid where requestor = " + str(session.userid) + " AND status =1") 
        friends_waiting = db.query("select * from friends left join users on friends.requestor = users.userid where acceptor = " + str(session.userid) + " AND status = 1")
        #friends_connected = db.query("select requestor from friends as friendname where status = 2 AND acceptor = 1 UNION select acceptor as friendname from friends where status = 2 AND requestor = 1 ")
        friends_connectedA = db.query("select requestor, Userid, Username from friends left join users on friends.requestor = users.userid where status = 2 AND acceptor = " + str(session.userid))
        friends_connectedB = db.query("select acceptor, Userid, Username from friends left join users on friends.acceptor = users.userid where status = 2 AND requestor = " + str(session.userid))
        
        friends_list = []
        friendmenu = " "
        for friends in friends_connectedA:
            friends_list.append(friends.Userid)
            temp_item = "<option label=\"" + str(friends.Username) + "\"value=\"" + str(friends.Userid) + "\">" + str(friends.Username)+ "</option>"
            friendmenu = friendmenu + temp_item 
        for friends in friends_connectedB:
            friends_list.append(friends.Userid)
            temp_item = "<option label=\"" + str(friends.Username) + "\"value=\"" + str(friends.Userid) + "\">" + str(friends.Username)+ "</option>"
            friendmenu = friendmenu + temp_item 
        #save iterator instead of requerying
        friends_connectedA = db.query("select requestor, Userid, Username from friends left join users on friends.requestor = users.userid where status = 2 AND acceptor = " + str(session.userid))
        friends_connectedB = db.query("select acceptor, Userid, Username from friends left join users on friends.acceptor = users.userid where status = 2 AND requestor = " + str(session.userid))
        return render.friends(potential_friends, friends_requested, friends_waiting, friends_connectedA, friends_connectedB, friendmenu)

class acceptfriends:
    def POST(self):
        i = web.input()
        print len(i)
        for item in i:
            print item
            db.query("update friends set status = 2 where requestor = " + item + " AND acceptor = " + str(session.userid))
        return web.seeother('/friends')

class deletefriends:
    def POST(self):
        i = web.input()
        for item in i:
            print item
            db.query("delete from friends where requestor = " + item + " AND acceptor = " + str(session.userid) + " AND status = 2")
            db.query("delete from friends where acceptor = " + item + " AND requestor = " + str(session.userid) + " AND status = 2")
        return web.seeother('/friends')

class requestfriends:
    def POST(self):
        i = web.input()
        for item in i:
            print item
            db.query("insert into friends values(" + str(session.userid) + "," + item + ",1)")
        return web.seeother('/friends') 

            
class changeselectedtemplate:
    def POST(self):
        global selected_template
        selected_template = web.input().templatetype
        raise web.seeother('/edittemplates')

class addnote:
    def POST(self):
        print "note_added"
        i = web.input()
        print i.notes     
        tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
        tempquery = "delete from notes where date = " + "\'" + tempdate + "\'" + "and userid = " + str(session.userid)
        db.query(tempquery)
        n = db.insert('notes', date = tempdate, notedata = i.notes, Userid = session.userid)
        
        
        raise web.seeother('/entries')

class edittemplates:
    def GET(self):
        if (session.count == 0):
            return render.login()
        global selected_template 
        tempquery = "select foods.calories, foods.protein, foods.fat, foods.carbs, foods.name, templatelist.Quantity, templatelist.FoodID from templatelist left join foods on templatelist.FoodID = foods.FoodID where templatelist.Type = " + "\'" + selected_template + "\'" + " AND templatelist.Userid = " + str(session.userid)
        masterlist = db.query(tempquery)
        masterlist2 = db.query(tempquery)
        foods = db.query('select * from foods order by name')
        
        days_calories = 0.0
        days_fat = 0.0
        days_carbs = 0.0
        days_protein = 0.0
        output = " "
        
        for listitem in masterlist2:
            days_calories = days_calories + listitem.calories * listitem.Quantity
            days_fat = days_fat + listitem.fat * listitem.Quantity
            days_protein = days_protein + listitem.protein*  listitem.Quantity
            days_carbs = days_carbs + listitem.carbs * listitem.Quantity
        output = output + "Calorie total<br> = %d <br><br> P = %d <br> C = %d <br> F = %d"  % (days_calories, days_protein, days_carbs, days_fat)
    
        template_select = " "
        weekday_bool = "selected=\"selected\""
        weekend_bool = " "
        if (selected_template == "weekend"):
            weekend_bool = "selected=\"selected\""
            weekday_bool = " "  
        
        template_select = template_select + "<option value=\"weekday\"" + weekday_bool + ">Weekday</option>"
        template_select = template_select + "<option value=\"weekend\"" + weekend_bool + " >Weekend</option>"
        
        autoselect = " "
        for listitem in foods:
            temp_item = "<option label=\"" + listitem.name + "\"value=\"" + listitem.name + "\"></option>"
            autoselect = autoselect + temp_item 
        return render.edittemplates(autoselect, masterlist,output, template_select)

class templateentry: #fix for weekend days
    def POST(self):
        global selected_day_year
        global selected_day_month
        global selected_day_day
        global selected_template
        selected_template = web.input().templatetype
        tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
        tempquery = "select foodID, Quantity from templatelist where Type =" + "\'" + selected_template + "\'" + " AND Userid = " + str(session.userid)
        tempFoodIDs = db.query(tempquery) 
        print tempFoodIDs    
        for tempid in tempFoodIDs:
            n = db.insert('masterlist', FoodID = tempid.foodID, quantity = tempid.Quantity, date = tempdate, Userid = session.userid) #construct date string and fix

        raise web.seeother('/entries')

class add:
    def POST(self):
        i = web.input()
        maxFoodID = db.query("SELECT MAX(FoodID) FROM foods") 
        tempMaxID = (maxFoodID[0]['MAX(FoodID)'] + 1)       
        if i.unit == 'kjs':
            i.calories = float(i.calories) / 4.186       
        n = db.insert('foods', name=i.name, protein = i.protein, carbs = i.carbs, fat = i.fat, calories = i.calories, defaultamount = 1, foodID = tempMaxID, Userid = session.userid)
        raise web.seeother('/')

class deleteitems:
    def POST(self):
        i = web.input()
        tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
        print len(i)
        for item in i:
            print item
            db.query("DELETE from masterlist where date="+"\'"+ tempdate+ "\'"+"AND FoodID =" + "\'"+ item + "\'" + " AND Userid = " + str(session.userid))
        raise web.seeother('/entries')
        
class deletetemplateitems:
    def POST(self):
        i = web.input()
        print len(i)
        for item in i:
            print item
            db.query("DELETE from templatelist where Type="+"\'"+ "Weekday"+ "\'"+"AND FoodID =" + "\'"+ item + "\'" + " AND Userid = " + str(session.userid))
        raise web.seeother('/edittemplates')
        
class deletetableitems:
    def POST(self):
        i = web.input()
        print len(i)
        for item in i:
            print item
            if (len(list(db.query("SELECT * from masterlist where FoodID =" + "\'"+ item + "\'" ))) == 0):
                db.query("DELETE from foods where foodID="+"\'"+ item+ "\'")
        raise web.seeother('/')

class addentry:
    def POST(self):
        global selected_day_year
        global selected_day_month
        global selected_day_day
        i = web.input()
        foods = db.select('foods');
        tempfoodname = i.whatfood
        
        try:
            tempquery = "select foodID from foods where name like \"" + i.whatfood + "%\"" # only getting first word of i.whatfood
            tempFoodID = db.query(tempquery) 
            tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
            n = db.insert('masterlist', FoodID = (tempFoodID[0]['foodID']), quantity = i.foodamount, date = tempdate, Userid = session.userid) #construct date string and fix
        except:
            pass
        raise web.seeother('/entries')
        
class templateaddentry:
    def POST(self):
        global selected_template
        i = web.input()
        foods = db.select('foods');
        tempfoodname = i.whatfood
        try:
            tempquery = "select foodID from foods where name like \"" + i.whatfood + "%\"" # only getting first word of i.whatfood
            tempFoodID = db.query(tempquery) 
            n = db.insert('templatelist', FoodID = (tempFoodID[0]['foodID']), quantity = i.foodamount, Type = selected_template, Userid = session.userid) 
        except:
            pass
        raise web.seeother('/edittemplates')        
        

class copyentries:
    def POST(self):
        global selected_day_year
        global selected_day_month
        global selected_day_day
        tempdate = str(selected_day_year) + "-" + str(selected_day_month) + "-" + str(selected_day_day)
        print tempdate
        tempdate_obj = datetime.date(int(selected_day_year), int(selected_day_month), int(selected_day_day))
        date_yesterday = (datetime.date.fromordinal(tempdate_obj.toordinal()-1)).strftime('%Y/%m/%d')
        print date_yesterday
        tempquery = "select * from masterlist where Date = " + "\'" + date_yesterday + "\'"
        one_day = db.query(tempquery)
        tempstr = " "
        for listitem in one_day:
            print listitem.Quantity
            n = db.insert('masterlist', FoodID = listitem.FoodID, quantity = listitem.Quantity, date = tempdate)
        raise web.seeother('/entries')
        
class changedate:
    def POST(self):
        i = web.input()
        session.selected_day_year = i.year
        session.selected_day_month = i.month
        session.selected_day_day = i.day
        raise web.seeother('/entries')

class friendchangedate:
    def POST(self):
        i = web.input()
        session.selected_day_year = i.year
        session.selected_day_month = i.month
        session.selected_day_day = i.day
        raise web.seeother('/friendspage?id=2')

class changedatetoday:
    def POST(self):

        
        now = datetime.datetime.now()
        selected_day = now

        session.selected_day_year = now.year
        session.selected_day_month = now.month
        session.selected_day_day = now.day
        raise web.seeother('/entries')

class addweight:
    def POST(self):
        i = web.input()
        tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
        tempdeletequery = "delete from bodyweight where date = " + "\'" + tempdate + "\'" + "and userid = " + str(session.userid)
        db.query(tempdeletequery)
        n = db.insert('bodyweight', date = tempdate, weight = i.weight, Userid = session.userid)
        
        raise web.seeother('/entries')

class login:
    def GET(self):
        return render.login()

class newuserhandle:
    def POST(self):
        i = web.input()
        maxUserID = db.query("SELECT MAX(Userid) FROM users") 
        tempmaxUserID = (maxUserID[0]['MAX(Userid)'] + 1)
        m = hashlib.sha1()
        m.update(i.newpassword)
        print (m.hexdigest())   
        n = db.insert('users', Username = i.new_user_name, Password = m.hexdigest(), Email = i.email, Fullname = i.full_name)
        raise web.seeother('/login')
     
class loginhandle:
    def POST(self):
        i = web.input()
        tempuserid_obj = db.query("select * from users where Username = " + "\'" + i.user_name + "\'")
        
        
        m = hashlib.sha1()
        n = hashlib.sha1()
                
        
        if (tempuserid_obj):
            temp_obj = tempuserid_obj[0]
            tempuserid = temp_obj.Userid
            m.update(temp_obj.Password)
            n.update(i.password)
            print "TESTINSGDGFDDF"
            print n.hexdigest()
            print m.hexdigest()
            if (n.hexdigest() == temp_obj.Password):
                    session.count = 1
                    session.username = i.user_name
                    session.userid = tempuserid
                    now = datetime.datetime.now()
                    session.selected_day_year = now.year
                    session.selected_day_month = now.month
                    session.selected_day_day = now.day
                    raise web.seeother('/entries')
            else:
                raise web.seeother('/login')
        else:
            raise web.seeother('/login')
           
class logout:
    def GET(self):
        session.count = 0
        raise web.seeother('/login')

class stats:
    @classmethod
    def generate_stats(self, uid):
        temp_dates = list(db.query("select distinct date from masterlist where Userid = " + str(uid) + " order by date"))
        list_dates = []
        output = " "
        if (len(temp_dates) == 0):
            temp_dates = list(db.query("select distinct date from masterlist order by date"))
               
        for x in range(0, len(temp_dates)):
            list_dates.append(temp_dates[x]['date'])
            
        start_of_stats = (list_dates[0].toordinal() - list_dates[0].weekday())
        weeks_total = ((list_dates[-1].toordinal() - list_dates[-1].weekday()) - start_of_stats)/7
        print datetime.date.fromordinal(start_of_stats)
        print weeks_total
        list_weekstarts = []
        for x in range(0,weeks_total):
            list_weekstarts.append((start_of_stats + ((x+1)*7)))

        output = " " 
        for wkdates in list_weekstarts:
            week_dates = []
            for x in range(0,7):
                week_dates.append(datetime.date.fromordinal(wkdates+x))
            list_week = []
            output_week = " "
            total_calories = 0.0
            total_carbs = 0.0
            total_fats = 0.0
            total_protein = 0.0
            days_used = 0
            tempbws = " "
            for date in week_dates:
                week_weights = db.query("select weight from bodyweight where date =" + "\'" + str(date) + "\'" + " AND Userid = " + str(uid))
                try:
                    tempbws = tempbws + " " + str(week_weights[0].weight) + " "
                except:
                    tempbws = tempbws + " _ "
                days_calories = 0
                days_fat = 0
                days_carbs = 0
                days_protein = 0
                output_week = output_week +"%s\n" % (days_of_the_week[date.weekday()])
                list_week.append(days_of_the_week[date.weekday()] + " " + str(date.day) + "/" + str(date.month))
                
                tempquery = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where masterlist.Date = " + "\'" + str(date) + "\'" + " AND masterlist.Userid = " + str(uid)
                one_day = db.query(tempquery)
                tempstr = " "
                for listitem in one_day:
                    days_calories = days_calories + listitem.calories * listitem.Quantity
                    days_fat = days_fat + listitem.fat * listitem.Quantity
                    days_protein = days_protein + listitem.protein*  listitem.Quantity
                    days_carbs = days_carbs + listitem.carbs * listitem.Quantity
                output_week  = output_week  + " Calorie Total %d - P:%d C:%d F:%d <br>" % (days_calories, days_protein, days_carbs, days_fat)
                if (days_calories > 0):
                    days_used = days_used + 1
                    total_calories = total_calories + days_calories
                    total_carbs = total_carbs + days_carbs
                    total_fats = total_fats + days_fat
                    total_protein = total_protein + days_protein
                
                list_week.append(str(days_calories))
                list_week.append(str(days_protein))
                list_week.append(str(days_carbs))
                list_week.append(str(days_fat))
            output = output + "Week starting " + str(datetime.date.fromordinal(wkdates))
            if (days_used != 7):
                output = output + " - "
            else:
                output = output + " - "

            if ((days_used != 7) and (days_used > 0)):
                output = output + "Calories %d  -  P:%d   C:%d   F:%d " % (total_calories/days_used, total_protein/days_used, total_carbs/days_used, total_fats/days_used) + "Incomplete data " + str(days_used) + "/7"
            elif (days_used == 0):
                output = output + " No Data"     
            else:
                output = output + "Calories %d  -  P:%d   C:%d   F:%d " % (total_calories/7, total_protein/7, total_carbs/7, total_fats/7)
            output = output + " ---> BWs: " + tempbws +  "<br>"
        return (temp_dates, output)

    def GET(self):
        if (session.count == 0):
            return render.login()
        temp_dates, output = self.generate_stats(session.userid)
        return render.stats(temp_dates, output)
    
    def simple():
        return (1,2)
        
class entries:
    def GET(self):
        if (session.count == 0):
            return render.login()
        global month_words
        global days_of_the_week
        global selected_day_year
        global selected_day_month
        global selected_day_day
        
        try:
            tempdate_obj = datetime.date(int(session.selected_day_year), int(session.selected_day_month), int(session.selected_day_day))
        except:
            now = datetime.datetime.now()
            selected_day = now
            session.selected_day_year = now.year
            session.selected_day_month = now.month
            session.selected_day_day = now.day
            tempdate_obj = datetime.date(int(selected_day_year), int(selected_day_month), int(selected_day_day))
        
        tempdate = str(session.selected_day_year) + "-" + str(session.selected_day_month) + "-" + str(session.selected_day_day)
        tempquery = "select foods.calories, foods.protein, foods.fat, foods.carbs, masterlist.Date, foods.name, masterlist.Quantity, masterlist.FoodID from masterlist left join foods on masterlist.FoodID = foods.FoodID where masterlist.Date = " + "\'" + tempdate + "\'" + " AND masterlist.Userid = " + str(session.userid)
        
        masterlist = list(db.query(tempquery))
        try:
            for fooditem in range(0,len(masterlist)):
                masterlist[fooditem].calories = masterlist[fooditem].calories * masterlist[fooditem].Quantity
                masterlist[fooditem].carbs = masterlist[fooditem].carbs * masterlist[fooditem].Quantity
                masterlist[fooditem].protein = masterlist[fooditem].protein * masterlist[fooditem].Quantity
                masterlist[fooditem].fat = masterlist[fooditem].fat * masterlist[fooditem].Quantity
        except:
            print "nothin"
            
        foods = db.query("select * from foods where Userid = " + str(session.userid) +  " order by name")

        t_day = ''
        for x in range(1,32):
            t_day  = t_day  + " <option value=\"" + str(x) + "\""
            if (x == int(session.selected_day_day)):
                t_day = t_day + "selected=\"selected\""
            t_day = t_day + ">" + str(x)   
       
        t_month = ''
        for x in range(1,13):
            t_month  = t_month  + " <option value=\"" + str(x) + "\""
            if (x == int(session.selected_day_month)):
                t_month = t_month + "selected=\"selected\""
            t_month = t_month + ">" + month_words[x-1]          
  
        t_year = ''
        for x in range(2014,2030):
            t_year  = t_year  + " <option value=\"" + str(x) + "\""
            if (x == int(session.selected_day_year)):
                t_year = t_year + "selected=\"selected\""
            t_year = t_year + ">" + str(x)   
            
        tempquery2 = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where ( masterlist.Date = " + "\'" + tempdate + "\'" + " AND masterlist.Userid = " + str(session.userid) + ")"
        one_day = db.query(tempquery2)
        tempstr = " "
        autoselect = " "
        
        for listitem in foods:
            temp_item = "<option label=\"" + listitem.name + " [Cals:" + str(listitem.calories) + " P:" + str(listitem.protein) + " C:" + str(listitem.carbs) + " F:" + str(listitem.fat) + "]" + "\"value=\"" + listitem.name + "\"></option>"
            autoselect = autoselect + temp_item 

        days_calories = 0.0
        days_fat = 0.0
        days_carbs = 0.0
        days_protein = 0.0
        output = " "
        for listitem in one_day:
            days_calories = days_calories + listitem.calories * listitem.Quantity
            days_fat = days_fat + listitem.fat * listitem.Quantity
            days_protein = days_protein + listitem.protein*  listitem.Quantity
            days_carbs = days_carbs + listitem.carbs * listitem.Quantity
        output = output + "Calorie total<br> = %d <br><br> P = %d <br> C = %d <br> F = %d"  % (days_calories, days_protein, days_carbs, days_fat)
        print "DATE test"

            
        start_of_week = (tempdate_obj.toordinal() - tempdate_obj.weekday()) 
        week_dates = []
        for x in range(0,7):
            print datetime.date.fromordinal(start_of_week+x)
            week_dates.append(datetime.date.fromordinal(start_of_week+x))
        list_week = []
        output_week = " "
        total_calories = 0.0
        total_carbs = 0.0
        total_fats = 0.0
        total_protein = 0.0
        days_used = 0
        for date in week_dates:
            days_calories = 0
            days_fat = 0
            days_carbs = 0
            days_protein = 0
            output_week = output_week +"%s\n" % (days_of_the_week[date.weekday()])
            list_week.append(days_of_the_week[date.weekday()] + " " + str(date.day) + "/" + str(date.month))
            
            tempquery = "select foods.name, foods.calories,foods.protein, foods.fat, foods.carbs, masterlist.Quantity from masterlist left join foods on masterlist.FoodID = foods.FoodID where masterlist.Date = " + "\'" + str(date) + "\'" + " AND masterlist.Userid = " + str(session.userid)
            one_day = db.query(tempquery)
            tempstr = " "
            for listitem in one_day:
                days_calories = days_calories + listitem.calories * listitem.Quantity
                days_fat = days_fat + listitem.fat * listitem.Quantity
                days_protein = days_protein + listitem.protein*  listitem.Quantity
                days_carbs = days_carbs + listitem.carbs * listitem.Quantity
            output_week  = output_week  + " Calorie Total %d - P:%d C:%d F:%d <br>" % (days_calories, days_protein, days_carbs, days_fat)
            if (days_calories > 0):
                days_used = days_used + 1
                total_calories = total_calories + days_calories
                total_carbs = total_carbs + days_carbs
                total_fats = total_fats + days_fat
                total_protein = total_protein + days_protein
            
            list_week.append(str(days_calories))
            list_week.append(str(days_protein))
            list_week.append(str(days_carbs))
            list_week.append(str(days_fat))
        
        try:
            avg_week  = " Calorie Averages %d - P:%d C:%d F:%d - (%d/7 days)" % (total_calories/days_used, total_protein/days_used, total_carbs/days_used, total_fats/days_used, days_used)
        except:
            avg_week = " No data"
        
        template_select = " "
        weekday_bool = "selected=\"selected\""
        weekend_bool = " "
        if (selected_template == "weekend"):
            weekend_bool = "selected=\"selected\""
            weekday_bool = " "  
        
        template_select = template_select + "<option value=\"weekday\"" + weekday_bool + ">Weekday</option>"
        template_select = template_select + "<option value=\"weekend\"" + weekend_bool + " >Weekend</option>"
        print list_week
        note_obj = db.query("select notedata from notes where date = " + "\'" + tempdate + "\'" + "and userid = " + str(session.userid))
        try:
            note_day = note_obj[0].notedata
        except:
            note_day = ""
        return render.entries(masterlist, foods, t_day, t_month, t_year, output, autoselect, output_week, list_week, template_select, avg_week, note_day ,session.username)        

class MySessionExpired(web.HTTPError):
     def __init__(self, message):
         message = render.login()
         web.HTTPError.__init__(self, '200 OK', {}, data=message)

        
if __name__ == "__main__":

    #app = web.application(urls, globals())
    web.session.SessionExpired = MySessionExpired    
    app.run()

# Form to add food
#LOAD DATA LOCAL INFILE '//home/daniel/Documents/LearnPython/macros/bin/macros_list.csv' INTO TABLE foods;
