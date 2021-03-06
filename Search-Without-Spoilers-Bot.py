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
from os import environ


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


# url clean for getting a bigger cover photo
def url_clean(url):
    base, ext = os.path.splitext(url)
    i = url.count('@')
    s2 = url.split('@')[0]
    return s2 + '@' * i + ext


def find_series_release_date(media):
    # getting seasons of the series
    season = media.data['seasons']
    print('There are', len(season), 'seasons')
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

    # checking the date and return an answer
    if release_date is None:
        return "Sorry! There's no available release date yet."
    # ended series
    elif release_date < currentDate:
        if title[-2] == '–':
            return "The series has no new season soon."
        else:
            return "The series has ended."
    # next season is next year and only year is mentioned
    elif release_date.year > currentDate.year:
        return "The next season will start in " + release + "."
    # next season is this year and the format is %d %b %Y
    elif release_date > currentDate:
        return "The next season will start in " + release + "."
    # next season is this year and the format is %Y
    elif release_date.year == currentDate.year:
        return "The next season will start in " + release + "."


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

    release = extract_date(title)
    release_date = get_date(release)
    print(release_date)

    # checking the date and return an answer
    if release_date is None:
        return "Sorry! There's no available release date yet."
    # The movie has released
    elif release_date < currentDate:
        return "Release was on " + release + "."
    # The movie will release this year
    elif release_date.year == currentDate.year:
        return "Release is on " + release + "."
    # The movie will release in other year
    elif release_date > currentDate:
        return "Release is on " + release + "."


# Important declarations
bot_token = environ['bot_token']
bot = telebot.TeleBot(token=bot_token)
today = datetime.today().strftime('%d %b %Y')
currentDate = datetime.strptime(today, '%d %b %Y').date()
dataBase = imdb.IMDb()  # IMDB Database
media = None  # Global media variable for future results
commands = ['/start', '/about', '/help', '/rating', '/cast', '/poster', '/genre']  # List of commands
print("Bot is now running")


# Main bot function
@bot.message_handler(func=lambda msg: msg.text is not None and not any(command in msg.text for command in commands))
def send_info(message):
    name = str(message.text.split())
    global movies  # Global list for search results
    global media
    movies = dataBase.search_movie(name)
    print(movies)
    # Nothing found - movies is empty
    if not movies:
        print("Sorry! I couldn't find any movie/series named " + str(message.text) + ".")
        bot.reply_to(message, "Sorry! I couldn't find any movie/series named " + str(message.text) + ".")
    # Only on result - len(movies)=1
    elif len(movies) == 1:
        code = movies[0].getID()
        print(code)
        bot.send_message(message.chat.id, "OK! Searching information about " + movies[0]['title']
                         + " (" + movies[0]['kind'] + ")")
        print(movies[0]['title'] + movies[0]['kind'])
        media = dataBase.get_movie(code)  # Search for the movie/series by the ID
        try:
            media['kind']
        except KeyError:
            bot.send_message(message, "Oops! Looks like that " + movies[0]['title'] +
                             " is on development, so there's no information yet.")
            media = None
        else:
            if media['kind'] == 'tv series' or media['kind'] == 'tv mini series':
                ret = find_series_release_date(media)
                bot.send_message(message.chat.id, ret)
            elif media['kind'] == 'movie' or media['kind'] == 'short':
                ret = find_movie_release_date(media, code)
                bot.send_message(message.chat.id, ret)
    else:
        # Multiple options; callback = movie IDs
        options = telebot.types.InlineKeyboardMarkup()  # Keyboard
        for i, movie in enumerate(movies):
            if movie['kind'] == 'tv series' or movie['kind'] == 'movie' or \
                    movie['kind'] == 'tv miniseries' or movie['kind'] == 'short':
                index = i
                callback = extract_code(movie['title'], movies)  # every movie has a unique code
                options.row(telebot.types.InlineKeyboardButton
                            (movie['title'] + " (" + movie['kind'] + ")", callback_data=callback))
        if not options.keyboard:
            bot.send_message(message.chat.id, "Sorry! I couldn't find any movie/series named " + str(message.text))
        elif len(options.keyboard) == 1:
            # check if this is the exact input from user, if not, send to callback_inline
            if message.text.lower() == movies[index]['title'].lower():
                bot.send_message(message.chat.id, "OK! Searching information about " + movies[index]['title'])
                media = dataBase.get_movie(callback)  # Search for the movie/series by the ID
                try:
                    media['kind']
                except KeyError:
                    bot.send_message(message, "Oops! Looks like that " + movies[0]['title'] +
                                     " is on development, so there's no information yet.")
                    media = None
                else:
                    if media['kind'] == 'tv series' or media['kind'] == 'tv mini series':
                        ret = find_series_release_date(media)
                        bot.send_message(message.chat.id, ret)
                    elif media['kind'] == 'movie' or media['kind'] == 'short':
                        ret = find_movie_release_date(media, callback)
                        bot.send_message(message.chat.id, ret)
            else:
                bot.send_message(message.chat.id, "Oops! I couldn't find " + message.text + ".\n"
                                 "Maybe this is what you've wanted to search for?",
                                 reply_markup=options)
        else:
            bot.send_message(message.chat.id, 'Oops! Seems like there are multiple options.\n'
                                              'What have you wanted to search for?', reply_markup=options)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        for i in range(len(movies)):
            if call.data == movies[i].getID():
                try:
                    movies[i]['kind']
                except KeyError:
                    bot.send_message(call.message.chat.id, "Oops! Looks like that " + movies[index]['title'] +
                                     " is on development, so there's no information yet.")
                else:
                    bot.send_message(call.message.chat.id, "OK! Searching information about " + movies[i]['title']
                                     + " (" + movies[i]['kind'] + ")")
                    print(movies[i]['title'] + movies[i]['kind'])
                    index = i

    print(call.data)
    global media
    media = dataBase.get_movie(call.data)  # Search for the movie/series by the ID
    try:
        media['kind']
    except KeyError:
        bot.send_message(call.message.chat.id, "Oops! Looks like that " + movies[index]['title'] +
                         " is on development, so there's no information yet.")
        media = None
    else:
        if media['kind'] == 'tv series' or media['kind'] == 'tv mini series':
            ret = find_series_release_date(media)
            bot.send_message(call.message.chat.id, ret)
        elif media['kind'] == 'movie' or media['kind'] == 'short':
            ret = find_movie_release_date(media, call.data)
            bot.send_message(call.message.chat.id, ret)


@bot.message_handler(commands=['start'])
def start(message):
    start_string = "Hey, I'm the Search Without Spoilers Bot!\n" \
                   "I can search for you a release date of a series' new season " \
                   "or movie's release date. To start, just send me a name of the " \
                   "series or movie you want to search. For help, tap /help."
    bot.send_message(message.chat.id, start_string)


@bot.message_handler(commands=['about'])
def about(message):
    about_string = \
        "Want to search for information about a series or movie without being exposed to spoilers? " \
        "I'm your solution! To get some help about how I'm working, tap /help or choose it from the commands" \
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
                  "4. Get a partial list of a series/movie cast.\n" \
                  "5. Get a cover photo of a series/movie.\n" \
                  "6. Get the genres of the series/movie.\n" \
                  "All last four cases based on the last search."
    bot.send_message(message.chat.id, help_string)


@bot.message_handler(commands=['rating'])
def send_rating(message):
    if not media:
        string = "Search information about a series or movie first " \
                 "in order to use this command."
        bot.send_message(message.chat.id, string)
    else:
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
        try:
            bot.send_message(message.chat.id, "Just a moment...")
            cover_url = media['cover url']
            full_size_url = url_clean(cover_url)
            response = requests.get(full_size_url)
            photo = Image.open(BytesIO(response.content))
            bot.send_photo(message.chat.id, photo)
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, "Sorry! this " + media.data['kind'] + " has no cover photo yet.")


@bot.message_handler(commands=['genre'])
def send_genre(message):
    if not media:
        string = "Search information about a series or movie first " \
                 "in order to use this command."
        bot.send_message(message.chat.id, string)
    else:
        try:
            bot.send_message(message.chat.id, ', '.join(map(str, media['genres'])))
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, "Sorry! this " + media.data['kind'] + " has no genres yet.")


while True:
    try:
        bot.polling()
    except Exception as e:
        print(e)
        time.sleep(15)
