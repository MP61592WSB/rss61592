from flask import Flask, render_template, request, redirect	
from flask_mail import Mail, Message	
from flask_mysqldb import MySQL	
import feedparser	
import mysql.connector	


app = Flask(__name__)	

app.config['DEBUG'] = True	
app.config['TESTING'] = False	
app.config['MAIL_SERVER'] = 'poczta.o2.pl' #o dziwo po kilku próbach przestało mnie wykrywać jako spambota	
app.config['MAIL_PORT'] = 465	
app.config['MAIL_USE_TLS'] = False	
app.config['MAIL_USE_SSL'] = True	
#app.config['MAIL_DEBUG'] = True	
app.config['MAIL_USERNAME'] = '' #prywatny mail tu był	
app.config['MAIL_PASSWORD'] = ''	
app.config['MAIL_DEFAULT_SENDER'] = ''	
app.config['MAIL_MAX_EMAILS'] = 10	
#app.config['MAIL_SUPPRESS_SEND'] = False	
app.config['MAIL_ASCII_ATTACHMENTS'] = False	
app.config['MYSQL_HOST'] = '' # ty był host bazy	
app.config['MYSQL_USER'] = ''	
app.config['MYSQL_PASSWORD'] = ''	
app.config['MYSQL_DB'] = '' #to by w sumie mogło zostać ale też usunę	
app.config['MYSQL_PORT'] = 3306	
app.config['MYSQL_SSL_CA'] ='{ca-cert app.py}'	
app.config['MYSQL_SSL_VERIFY_CERT'] = 'true'	


mail = Mail(app)	
mysql = MySQL(app)	

@app.route('/', methods=['GET', 'POST'])	
def index():	

    if request.method == 'POST':	
        if request.form.get('Wyslij maila') == 'Wyslij maila':	
            msg = Message('Wiadomosci RSS', recipients=['#wiadomo'])	
            msg.html ="<html><body><h1>Newsy z swiata</h1>"+(prepare_news())+"</body></html>"	
            mail.send(msg)	

    cur = mysql.connection.cursor()	
    resultValue = cur.execute("SELECT * FROM rsslink")	
    if resultValue > 0:	
        details = cur.fetchall()	
        return render_template('index.html', details=details)	

    return render_template('index.html')	

@app.route('/add_rss', methods=['GET', 'POST'])	
def add_rss():	
    if request.method == 'POST':	
        if request.form.get('Zapisz RSS') == 'Zapisz RSS':	
            linkrss = request.form['URL_rss']	
            linkrss = str(linkrss)	
            cur9 = mysql.connection.cursor()	
            cur9.execute("INSERT INTO rsslink (link) VALUES (%s)", [linkrss])	
            mysql.connection.commit()	
            cur9.close()	
            return redirect('/')	
    return render_template('add_rss.html')	


#app.jinja_env.globals.update(usun_rss = usun_rss) #tu była próba zabawy z jinją żeby przyciskowi w index.html przypisac wywoływanie funkcji pythonowej	
                                                    #będę jeszcze na tym pracować	

def prepare_news(): #funkcja sklejająca kilka newsów w jedną html'ową całość żeby przekazać do funkcji wysłania maila i zwraca stringa z kodem html	
    cur1 = mysql.connection.cursor()	
    linia = cur1.execute("SELECT * FROM rsslink")	
    result = cur1.fetchall()	
    RSS_FEEDS = [x[0] for x in result]	
    cur1.close()	
    news_text = ""	
    count = 0	
    for y in RSS_FEEDS:	
        trigger = RSS_FEEDS[count]	
        news_text = news_text+(get_news(trigger))	
        count = count + 1	
    return news_text	


def get_news(publication): #funkcja która z podanego linku do rss rozbija go na html'owe części jak nagłówek, tytuł (z linkiem do pełnego artykułu), żeby móc skleić i wysłać w mailu jako html.	
    feed = feedparser.parse(publication)	
    first_article = feed['entries'][0]	
    return """	
        <b><a href={3}>{0}</a></b> </ br>	
        <i>{1}</i> </ br>	
        <p>{2}</p> </ br>	
        <hr />""".format(first_article.get("title"), first_article.get("published"), first_article.get("summary"), first_article.get("link"))	

if __name__ == '__main__':	
    app.run()