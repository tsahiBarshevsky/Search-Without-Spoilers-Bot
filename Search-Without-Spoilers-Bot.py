from urllib.request import urlopen
from datetime import datetime
import telebot
import time
import imdb
import re


def get_date(s_date):
    date_patterns = ["%d %b %Y", "%Y %b %d", "%d %B %Y", "%Y"]
    for pattern in date_patterns:
        try:
            return datetime.strptime(s_date, pattern).date()
        except:
            pass


def extract_date(string):
    matches = re.findall('(\d{2}[\/ ](\d{2}|January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|'
                         'Aug|September|Sep|October|Oct|November|Nov|December|Dec)[\/ ]\d{2,4})', string)
    for match in matches:
        return match[0]


bot_token = '1350001699:AAGgFC55g8IM8FbQzu4kCbmr1az2aFLXDjo'
bot = telebot.TeleBot(token=bot_token)
today = datetime.today().strftime('%d %b %Y')
currentDate = datetime.strptime(today, '%d %b %Y').date()
print("The bot is now running")

# Create database
dataBase = imdb.IMDb()


# Main function
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text != '/start')
def answer(message):
    movies = dataBase.search_movie(str(message.text.split()))
    code = movies[0].getID()  # Get series/movie code
    print(code)
    media = dataBase.get_movie(code)  # Search for the movie/series by the ID
    if media['kind'] == 'tv series':
        # getting seasons of the series
        season = media.data['seasons']

        # getting rating of the series
        # rating = series.data['rating']
        # print(rating)

        # print the seasons
        print('There are', len(season), 'seasons')
        # Episode_Release_date = dataBase.get_movie_release_dates(code)
        # for i in Episode_Release_date['data']['release dates']:
        #    if 'USA' in i:
        #        print(i)

        url = dataBase.get_imdbURL(media)
        final_season = season[len(season) - 1]
        url_final_season = url + 'episodes?season=' + final_season + '&ref_=tt_eps_sn_' + final_season
        print(url)
        print(url_final_season)

        # Get the release date of last season available
        page = urlopen(url_final_season)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        title_index = html.find('<div class="airdate">')
        start_index = title_index + len('<div class="airdate">')
        end_index = html.find('</div>', title_index)
        title = html[start_index:end_index]
        new_title = title.strip()  # remove \n from original string
        release = new_title.replace(".", "")  # remove . from month
        print(release)

        # releaseDate = datetime.strptime(release, '%d %b %Y').date()
        releaseDate = get_date(release)
        print(releaseDate)

        # there's no info yet
        if releaseDate is None:
            print("Sorry! There's no available release date yet")
            bot.reply_to(message, "Sorry! There's no available release date yet")
        # ended series
        elif releaseDate < currentDate:
            print("The series has no new season soon")
            bot.reply_to(message, "The series has no new season soon")
        # next season is next year and only year is mentioned
        elif releaseDate.year > currentDate.year:
            print("The next season will start in " + release)
            bot.reply_to(message, "The next season will start in " + release)
        # next season is this year and the format is %d %b %Y
        elif releaseDate > currentDate:
            print("The next season will start in " + release)
            bot.reply_to(message, "The next season will start in " + release)
        # next season is this year and the format is %Y
        elif releaseDate.year == currentDate.year:
            print("The next season will start in " + release)
            bot.reply_to(message, "The next season will start in " + release)
    elif media['kind'] == 'movie':
        url = dataBase.get_imdbURL(media)
        final_url = url + 'releaseinfo?ref_=tt_ov_inf'
        a_tag = '<a href="/title/tt' + code + '/releaseinfo"\ntitle="See more release dates" >'
        print(url)


        # Get the release date of last season available
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        title_index = html.find(a_tag)
        start_index = title_index + len(a_tag)
        end_index = html.find('</a>', title_index)
        title = html[start_index:end_index]

        # releaseDate = datetime.strptime(release, '%d %b %Y').date()
        releaseDate = extract_date(title)
        print(releaseDate)

        # there's no info yet
        if releaseDate is None:
            print("Sorry! There's no available release date yet")
            bot.reply_to(message, "Sorry! There's no available release date yet")
        else:
            print("Release was on " + releaseDate)
            bot.reply_to(message, "Release was on " + releaseDate)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Welcome!')


while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)
