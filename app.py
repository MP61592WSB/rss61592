from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import feedparser
import mysql.connector
import time


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'poczta.o2.pl'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'rssmail61592@o2.pl'
app.config['MAIL_PASSWORD'] = 'Tu_bylo_haslo_do_maila'
app.config['MAIL_DEFAULT_SENDER'] = 'rssmail61592@o2.pl'
app.config['MAIL_MAX_EMAILS'] = 10 
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MYSQL_HOST'] = 'rssbaza.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'rssadmin@rssbaza'
app.config['MYSQL_PASSWORD'] = 'Tu_bylo_haslo_do_bazt'
app.config['MYSQL_DB'] = 'mydb'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_SSL_CA'] ='{ca-cert app.py}'
app.config['MYSQL_SSL_VERIFY_CERT'] = 'true'


mail = Mail(app)
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if request.form.get('Wyslij maila') == 'Wyslij maila':
            cur16 = mysql.connection.cursor()
            resultValue1 = cur16.execute("SELECT email FROM mails")
            odbiorcy = cur16.fetchall()
            if resultValue1 > 0:
                RSS_MAILS = [x[0] for x in odbiorcy]
                for y in RSS_MAILS:
                    msg = Message('Wiadomosci RSS', recipients = [y])
                    msg.html ="<html><body><h1>Newsy z swiata</h1>"+(prepare_news())+"</body></html>"
                    time.sleep(2)
                    mail.send(msg)
            else: 
                    msg = Message('Wiadomosci RSS', recipients = ['marcinpilarski200@gmail.com'])
                    msg.html ="<html><body><h1>Newsy z swiata</h1>"+(prepare_news())+"</body></html>"
                    mail.send(msg)

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM rsslink")
    if resultValue > 0:
        details = cur.fetchall()
        wiadomosc = prepare_news()
        return render_template('index.html', details=details, wiadomosc = wiadomosc)

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
        elif request.form.get('Usun RSS') == 'Usun RSS':
            removerss = request.form['remove_rss']
            removerss = int(removerss)
            cur10 = mysql.connection.cursor()
            cur10.execute("DELETE FROM rsslink WHERE id=%s", [removerss])
            mysql.connection.commit()
            cur10.close()
            return redirect('/')
        
    cur12 = mysql.connection.cursor()
    resultValue = cur12.execute("SELECT * FROM rsslink")
    if resultValue > 0:
        details = cur12.fetchall()
        return render_template('add_rss.html', details=details)  
    
    return render_template('add_rss.html')


@app.route('/add_mail', methods=['GET', 'POST'])
def add_mail():
    if request.method == 'POST':
        if request.form.get('Zapisz MAIL') == 'Zapisz MAIL':
            mailrss = request.form['MAIL_rss']
            mailrss = str(mailrss)
            cur13 = mysql.connection.cursor()
            cur13.execute("INSERT INTO mails (email) VALUES (%s)", [mailrss])
            mysql.connection.commit()
            cur13.close()
            return redirect('/')
        elif request.form.get('Usun MAIL') == 'Usun MAIL':
            removemail = request.form['remove_mail']
            removemail = int(removemail)
            cur14 = mysql.connection.cursor()
            cur14.execute("DELETE FROM mails WHERE id=%s", [removemail])
            mysql.connection.commit()
            cur14.close()
            return redirect('/')
        
    cur15 = mysql.connection.cursor()
    resultValue = cur15.execute("SELECT * FROM mails")
    if resultValue > 0:
        details = cur15.fetchall()
        return render_template('add_mail.html', details=details)  
    
    return render_template('add_mail.html')


def prepare_news(): #funkcja sklejająca kilka newsów w jedną html'ową całość żeby przekazać do funkcji wysłania maila i zwraca stringa z kodem html
    cur1 = mysql.connection.cursor()
    linia = cur1.execute("SELECT link FROM rsslink")
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
