from urllib.request import urlopen
from datetime import datetime
import telebot
import time
import imdb


def get_date(s_date):
    date_patterns = ["%d %b %Y", "%Y %b %d", "%Y"]
    for pattern in date_patterns:
        try:
            return datetime.strptime(s_date, pattern).date()
        except:
            pass


bot_token = '1350001699:AAGgFC55g8IM8FbQzu4kCbmr1az2aFLXDjo'
bot = telebot.TeleBot(token=bot_token)
today = datetime.today().strftime('%d %b %Y')
currentDate = datetime.strptime(today, '%d %b %Y').date()
print("The bot is now running")

# Create database
dataBase = imdb.IMDb()


# Main function
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text is not '/start')
def answer(message):
    movies = dataBase.search_movie(str(message.text.split()))
    code = movies[0].getID()
    print(code)
    series = dataBase.get_movie(code)

    # getting seasons of the series
    season = series.data['seasons']

    # getting rating of the series
    # rating = series.data['rating']
    # print(rating)

    # print the seasons
    print('There are', len(season), 'seasons')
    # Episode_Release_date = dataBase.get_movie_release_dates(code)
    # for i in Episode_Release_date['data']['release dates']:
    #    if 'USA' in i:
    #        print(i)

    url = dataBase.get_imdbURL(series)
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


    # if releaseDate.year > currentDate.year:
    #     print("The next season will start in: " + release)
    #     bot.reply_to(message, "The next season will start in: " + release)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Welcome!')


while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)
