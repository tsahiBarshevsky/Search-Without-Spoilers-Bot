from urllib.request import urlopen
from datetime import datetime
from PIL import Image
from io import BytesIO
import requests
import telebot
import time
import imdb
import re
import os


def get_date(s_date):
    date_patterns = ["%d %b %Y", "%Y %b %d", "%d %B %Y", "%b %Y", "%Y"]
    for pattern in date_patterns:
        try:
            return datetime.strptime(s_date, pattern).date()
        except:
            pass


# Extract date from string in movie page
def extract_date(string):
    # Date format: %d %B %Y
    matches = re.findall(
        '(\d{1,2}[\/ ](\d{2}|January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|'
        'Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)[\/ ]\d{2,4})', string)
    if not matches:
        # Date format: %Y
        matches = re.findall('(\d{2,4})', string)
        return "".join(matches[0])
    for match in matches:
        return match[0]


def extract_code(string, movies_list):
    i = 0
    for item in movies_list:
        if item['title'] == string:
            return movies_list[i].getID()
        i += 1


def url_clean(url):
    base, ext = os.path.splitext(url)
    i = url.count('@')
    s2 = url.split('@')[0]
    return s2 + '@' * i + ext


def find_series_release_date(media):
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
    div_index = html.find('<div class="airdate">')
    start_index = div_index + len('<div class="airdate">')
    end_index = html.find('</div>', div_index)
    content = html[start_index:end_index]
    new_content = content.strip()  # remove \n from original string
    release = new_content.replace(".", "")  # remove . from month
    print(release)

    # releaseDate = datetime.strptime(release, '%d %b %Y').date()
    release_date = get_date(release)
    print(release_date)

    # extracting title for check if the series has ended
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    title_index = html.find('<title>')
    start_index_title = title_index + len('<title>')
    end_index_title = html.find('</title>')
    title = html[start_index_title:end_index_title]
    new_title = title.replace(") - IMDb", "")
    print(new_title)

    return release_date, release, new_title


def find_movie_release_date(media, code):
    url = dataBase.get_imdbURL(media)
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
    release = extract_date(title)
    release_date = get_date(release)
    print(release_date)
    return release_date, release


# Important declaration
bot_token = '1350001699:AAGgFC55g8IM8FbQzu4kCbmr1az2aFLXDjo'
bot = telebot.TeleBot(token=bot_token)
today = datetime.today().strftime('%d %b %Y')
currentDate = datetime.strptime(today, '%d %b %Y').date()
print("The bot is now running")

# Create database
dataBase = imdb.IMDb()
media_code = None
media = None


# Main function
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text != '/about' and msg.text != '/help'
                     and msg.text != '/rating' and msg.text != '/cast' and msg.text != '/poster')
def send_info(message):
    name = str(message.text.split())
    global movies  # Global list for search results
    movies = dataBase.search_movie(name)
    print(movies)
    # Nothing found - movies is empty
    if not movies:
        print("Sorry! I couldn't find any movie/series named " + str(message.text))
        bot.reply_to(message, "Sorry! I couldn't find any movie/series named " + str(message.text))
    # Only on result - len(movies)=1
    elif len(movies) == 1:
        code = movies[0].getID()
        global media_code
        media_code = code
        print(code)
        print(media_code)
        bot.send_message(message.chat.id, "OK! Searching info about " + movies[0]['title']
                         + " (" + movies[0]['kind'] + ")")
        print(movies[0]['title'] + movies[0]['kind'])
        global media
        media = dataBase.get_movie(code)  # Search for the movie/series by the ID
        if media['kind'] == 'tv series':
            # # getting seasons of the series
            # season = media.data['seasons']
            #
            # # getting rating of the series
            # # rating = series.data['rating']
            # # print(rating)
            #
            # # print the seasons
            # print('There are', len(season), 'seasons')
            # # Episode_Release_date = dataBase.get_movie_release_dates(code)
            # # for i in Episode_Release_date['data']['release dates']:
            # #    if 'USA' in i:
            # #        print(i)
            #
            # url = dataBase.get_imdbURL(media)
            # final_season = season[len(season) - 1]
            # url_final_season = url + 'episodes?season=' + final_season + '&ref_=tt_eps_sn_' + final_season
            # print(url)
            # print(url_final_season)
            #
            # # Get the release date of last season available
            # page = urlopen(url_final_season)
            # html_bytes = page.read()
            # html = html_bytes.decode("utf-8")
            # title_index = html.find('<div class="airdate">')
            # start_index = title_index + len('<div class="airdate">')
            # end_index = html.find('</div>', title_index)
            # title = html[start_index:end_index]
            # new_title = title.strip()  # remove \n from original string
            # release = new_title.replace(".", "")  # remove . from month
            # print(release)
            #
            # # releaseDate = datetime.strptime(release, '%d %b %Y').date()
            # release_date = get_date(release)
            # print(release_date)

            release_date, release, title = find_series_release_date(media)
            # there's no info yet
            if release_date is None:
                print("Sorry! There's no available release date yet")
                bot.send_message(message.chat.id, "Sorry! There's no available release date yet")
            # ended series
            elif release_date < currentDate:
                if title[-2] == '–':
                    print("The series has no new season soon")
                    bot.send_message(message.chat.id, "The series has no new season soon")
                else:
                    print("The series has ended")
                    bot.send_message(message.chat.id, "The series has ended")
            # next season is next year and only year is mentioned
            elif release_date.year > currentDate.year:
                print("The next season will start in " + release)
                bot.send_message(message.chat.id, "The next season will start in " + release)
            # next season is this year and the format is %d %b %Y
            elif release_date > currentDate:
                print("The next season will start in " + release)
                bot.send_message(message.chat.id, "The next season will start in " + release)
            # next season is this year and the format is %Y
            elif release_date.year == currentDate.year:
                print("The next season will start in " + release)
                bot.send_message(message.chat.id, "The next season will start in " + release)
        elif media['kind'] == 'movie':
            release_date, release = find_movie_release_date(media, code)

            # there's no info yet
            if release_date is None:
                print("Sorry! There's no available release date yet")
                bot.send_message(message.chat.id, "Sorry! There's no available release date yet")
            # The movie has released
            elif release_date < currentDate:
                print("Release was on " + release)
                bot.send_message(message.chat.id, "Release was on " + release)
            # The movie will release this year
            elif release_date.year == currentDate.year:
                print("Release is on " + release)
                bot.send_message(message.chat.id, "Release is on " + release)
            # The movie will release in other year
            elif release_date > currentDate:
                print("Release is on " + release)
                bot.send_message(message.chat.id, "Release is on " + release)
    else:
        options = telebot.types.InlineKeyboardMarkup()  # keyboard
        for movie in movies:
            if movie['kind'] == 'tv series' or movie['kind'] == 'movie':
                callback = extract_code(movie['title'], movies)  # every movie has a unique code
                options.row(telebot.types.InlineKeyboardButton
                            (movie['title'] + " (" + movie['kind'] + ")", callback_data=callback))
        if len(options.keyboard) >= 1:
            bot.send_message(message.chat.id, 'Oops! Seems like there are multiple options.\n'
                                              'What have you wanted to search for?', reply_markup=options)
        else:
            bot.send_message(message.chat.id, "Sorry! I couldn't find any movie/series named " + str(message.text))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        for i in range(len(movies)):
            if call.data == movies[i].getID():
                bot.send_message(call.message.chat.id, "OK! Searching info about " + movies[i]['title']
                                 + " (" + movies[i]['kind'] + ")")
                print(movies[i]['title'] + movies[i]['kind'])
    print(call.data)
    global media_code
    media_code = call.data
    global media
    media = dataBase.get_movie(call.data)  # Search for the movie/series by the ID
    if media['kind'] == 'tv series':

        release_date, release, title = find_series_release_date(media)
        print(release_date)

        # there's no info yet
        if release_date is None:
            print("Sorry! There's no available release date yet")
            bot.send_message(call.message.chat.id, "Sorry! There's no available release date yet")
        # ended series
        elif release_date < currentDate:
            if title[-2] == '–':
                print("The series has no new season soon")
                bot.send_message(call.message.chat.id, "The series has no new season soon")
            else:
                print("The series has ended")
                bot.send_message(call.message.chat.id, "The series has ended")
        # next season is next year and only year is mentioned
        elif release_date.year > currentDate.year:
            print("The next season will start in " + release)
            bot.send_message(call.message.chat.id, "The next season will start in " + release)
        # next season is this year and the format is %d %b %Y
        elif release_date > currentDate:
            print("The next season will start in " + release)
            bot.send_message(call.message.chat.id, "The next season will start in " + release)
        # next season is this year and the format is %Y
        elif release_date.year == currentDate.year:
            print("The next season will start in " + release)
            bot.send_message(call.message.chat.id, "The next season will start in " + release)
    elif media['kind'] == 'movie':
        release_date, release = find_movie_release_date(media, call.data)

        # there's no info yet
        if release_date is None:
            print("Sorry! There's no available release date yet")
            bot.send_message(call.message.chat.id, "Sorry! There's no available release date yet")
        # The movie has released
        elif release_date < currentDate:
            print("Release was on " + release)
            bot.send_message(call.message.chat.id, "Release was on " + release)
        # The movie will release this year
        elif release_date.year == currentDate.year:
            print("Release is on " + release)
            bot.send_message(call.message.chat.id, "Release is on " + release)
        # The movie will release in other year
        elif release_date > currentDate:
            print("Release is on " + release)
            bot.send_message(call.message.chat.id, "Release is on " + release)


@bot.message_handler(commands=['about'])
def about(message):
    about_string = \
        "Want to search for information about a series or movie without being exposed to spoilers? " \
        "I'm your solution! To get some help about how I'm working, tap /help or chose it from the commands" \
        " menu below 👇🏼"
    bot.send_message(message.chat.id, about_string)


@bot.message_handler(commands=['help'])
def help_user(message):
    help_string = "What can I do?\n" \
                  "1. Search for a series new season release date.\n" \
                  "2. Search for a movie release date.\n" \
                  "In both cases, type the name of the series/movie. " \
                  "If I'll find some multiple choices, I'll present to you all the " \
                  "options, so you can pick the right one.\n" \
                  "3. Get the rating of a series/movie.\n" \
                  "4. Get a partial of a series/movie cast.\n" \
                  "5. Get a cover photo of a series/movie.\n" \
                  "All last three cases based on the last search."
    bot.send_message(message.chat.id, help_string)


@bot.message_handler(commands=['rating'])
def send_rating(message):
    if not media:
        string = "Search information about a series or movie first " \
                 "in order to use this command."
        bot.send_message(message.chat.id, string)
    else:
        # bot.send_message(message.chat.id, media_code)
        try:
            media_rating = media.data['rating']
        except KeyError:
            bot.send_message(message.chat.id, "Sorry! this " + media.data['kind'] + " has no rating yet.")
        else:
            bot.send_message(message.chat.id, media.data['title'] + " got a rating of " + str(media_rating))


@bot.message_handler(commands=['cast'])
def send_cast(message):
    if not media:
        string = "Search information about a series or movie first " \
                 "in order to use this command."
        bot.send_message(message.chat.id, string)
    else:
        # global media
        # media = dataBase.get_movie(media_code)
        cast = media.get('cast')
        if not cast:
            bot.send_message(message.chat.id, "Sorry! this " + media.data['kind'] + " has no cast yet.")
        else:
            ret = []
            for actor in cast[:10]:
                ret.append("{0} as {1}".format(actor['name'], actor.currentRole))
            url = dataBase.get_imdbURL(media)
            cast_url = url + 'fullcredits?ref_=tt_cl_sm#cast'
            ret.append("\nThis is a partial list. You can see full cast here:")
            ret.append(cast_url)
            bot.send_message(message.chat.id, '\n'.join(map(str, ret)))


@bot.message_handler(commands=['poster'])
def send_poster(message):
    if not media:
        string = "Search information about a series or movie first " \
                 "in order to use this command."
        bot.send_message(message.chat.id, string)
    else:
        # global media
        # media = dataBase.get_movie(media_code)
        try:
            cover_url = media['cover url']
            full_size_url = url_clean(cover_url)
            response = requests.get(full_size_url)
            photo = Image.open(BytesIO(response.content))
            bot.send_photo(message.chat.id, photo)
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, "Sorry! this " + media.data['kind'] + " has no cover photo yet.")


while True:
    try:
        bot.polling()
    except Exception as e:
        print(e)
        time.sleep(15)
