from urlextract import URLExtract
import pandas as pd
from collections import Counter
import emoji
import re
import regex
import streamlit as st
from datetime import datetime
from wordcloud import WordCloud
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


def fetchStats(selectedUser, dataFrame):
    if selectedUser != "Overall":
        dataFrame = dataFrame[dataFrame['user'] == selectedUser]
    totalMessages = dataFrame.shape[0]

    word = []
    for message in dataFrame['message']:
        if isinstance(message, str):
            word.extend(message.split())
    totalWords = len(word)

    totalMedia = dataFrame[dataFrame['message']
                           == '<Media omitted>\n'].shape[0]

    extractor = URLExtract()
    urls = extractor.find_urls(" ".join(word))
    totalURL = len(urls)

    return totalMessages, totalWords, totalMedia, totalURL


def mostBusy(x):
    topChatter = x['user'].value_counts().head()
    topChatterPercent = round((x['user'].value_counts()/x.shape[0])*100, 2).reset_index().rename(columns={'index': "Name", 'user': 'Percentage'})
    return topChatter, topChatterPercent


def mostCommon(selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    # remove stopwords and group notifications
    withoutGN = x[x['user'] != 'default']
    withoutGNMedia = withoutGN[withoutGN["message"] != '<Media omitted>\n']

    stopWords = open("stopwords-hinglish.txt", "r").read()

    words = []

    for message in withoutGNMedia['message']:
        for word in message.lower().split():
            if word not in stopWords:
                words.append(word)

    mC = Counter(words).most_common(20)
    mostCommon = pd.DataFrame(mC)
    mostCommon = mostCommon.rename(columns={0: 'Message', 1: 'Frequency'})

    return mostCommon


def wordCloud (selectedUser, dataFrame):
    stopWords = open("stopwords-hinglish.txt", "r").read()
    if selectedUser != "Overall":
        dataFrame = dataFrame[dataFrame['user'] == selectedUser]
    withoutGN = dataFrame[dataFrame['user'] != 'default']
    withoutGNMedia = withoutGN[withoutGN["message"] != '<Media omitted>\n']
    
    def removeStopWords (x):
        words = []
        for word in x.lower().split():
            if word not in stopWords:
                words.append(word)
        return " ".join(words)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    withoutGNMedia['message'] = withoutGNMedia['message'].apply(removeStopWords)
    df_wc = wc.generate(dataFrame['message'].str.cat(sep=" "))
    return df_wc


def mostEmoji(selectedUser, x):
    if selectedUser != 'Overall':
        x = x[x['user'] == selectedUser]
    emojis = []
    for message in x['message']:
        if isinstance(message, str):
            message_emojized = emoji.emojize(message, language='alias')
            emojis.extend(
                [c for c in message_emojized if c in emoji.EMOJI_DATA])

    emoji_counts = Counter(emojis)
    emoji_df = pd.DataFrame(list(emoji_counts.items()),
                            columns=['Emoji', 'Count'])
    emoji_df['Emoji'] = emoji_df['Emoji'].apply(
        lambda x: emoji.emojize(x, language='alias'))
    emoji_df = emoji_df.sort_values(
        'Count', ascending=False).reset_index(drop=True)

    return emoji_df


def monthlyTimeline(selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    timeline = x.groupby(['year', 'monthNum', 'month']).count()[
        'message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline


def dailyTimeline(selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    x['onlyDate'] = pd.to_datetime(x['date']).dt.date
    dailyTimeline = x.groupby("onlyDate").count()['message'].reset_index()
    return dailyTimeline


def weekActivity(selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    weekActivity = x.groupby("dayName").count()['message'].reset_index()
    return x['dayName'].value_counts(), weekActivity


def monthActivity(selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    monthActivity = x.groupby("monthName").count()['message'].reset_index()
    return x['monthName'].value_counts(), monthActivity


def hourActivity(selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    return x.groupby(['dayName', 'hour'])['message'].count(), x.groupby(['dayName', 'hour'])['message'].count().reset_index()



def messageExtractor (selectedUser, x, inputDate):
    #inputDate = "20-04-2023"
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    if (len(inputDate)==10):
        dd = inputDate[0:2]
        mm = inputDate[3:5]
        yyyy = inputDate[6:]
        if (dd[0]=='0'): dd = dd[1]
        if (mm[0]=='0'): mm = mm[1]
        mask = (x['day'].astype(str) == dd) & (x['monthNum'].astype(str) == mm) & (x['year'].astype(str) == yyyy)
        messageExtract = pd.DataFrame(x[mask])[['user', 'message']]
        if (messageExtract.shape[0]>0):
            messageExtract['time'] = x['hour'].astype(str) + ':' + x['minute'].astype(str)
            messageExtract['message'] = messageExtract['message'].str.replace('\n', '')
        #st.dataframe(messageExtract)

        return messageExtract

def activity (selectedUser, x):
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
    activityX = x.pivot_table(index='dayName', columns='period', values='message', aggfunc='count').fillna(0)
    return activityX

def replyTime (selectedUser, x):
    timeSelected = pd.Timedelta(0)
    timeDifference = x.groupby('user')['replyTime'].mean().reset_index().sort_values('replyTime', ascending=True).head(5)
    timeDifference = timeDifference[timeDifference['user'] != 'default']
    if selectedUser != "Overall":
        x = x[x['user'] == selectedUser]
        # Check if the filtered DataFrame is not empty before accessing .iloc[0]
        filtered_data = timeDifference[timeDifference['user'] == selectedUser]['replyTime']
        if not filtered_data.empty:
            timeSelected = filtered_data.iloc[0]
        else:
            timeSelected = None  # Or handle this case as needed (e.g., default value, error message)
    return timeDifference, timeSelected

# Sentiment analysis of each user based on the text and emojis used

nltk.download('vader_lexicon')

def analyze_sentiment(selected_user, x):
    sia = SentimentIntensityAnalyzer()
    user_sentiments = {}

    for index, row in x.iterrows():
        user = row['user']
        message = row['message']

        if user not in user_sentiments:
            user_sentiments[user] = {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}
        
        # Analyze text sentiment
        text_sentiment = sia.polarity_scores(message)
        for key in user_sentiments[user].keys():
            user_sentiments[user][key] += text_sentiment[key]

        # Analyze emoji sentiment
        emojis = [c for c in message if emoji.demojize(c) != c]
        for emo in emojis:
            emoji_sentiment = {
                                '😀': 1.0,  # Positive sentiment
                                '😢': -1.0,  # Negative sentiment
                                '😠': -1.0,  # Negative sentiment
                                '😍': 1.0,  # Positive sentiment
                                '😐': 0.0,  # Neutral sentiment
                            }
            if emo in emoji_sentiment:
                user_sentiments[user]['compound'] += emoji_sentiment[emo]

    # Average the sentiment scores
    for user, sentiment_scores in user_sentiments.items():
        total_messages = x[x['user'] == user].shape[0]
        for key in sentiment_scores.keys():
            sentiment_scores[key] /= total_messages

    if selected_user == 'Overall':
        return user_sentiments
    else:
        return {selected_user: user_sentiments.get(selected_user, {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0})}


def sentiment_score(user_sentiments, selected_user):
    if selected_user == 'Overall':
        pos = sum([user['pos'] for user in user_sentiments.values()])/len(user_sentiments)
        neg = sum([user['neg'] for user in user_sentiments.values()])/len(user_sentiments)
        neu = sum([user['neu'] for user in user_sentiments.values()])/len(user_sentiments)
    elif selected_user in user_sentiments:
        sentiment_scores = user_sentiments[selected_user]
        pos = sentiment_scores['pos']
        neg = sentiment_scores['neg']
        neu = sentiment_scores['neu']
    else:
        return "No sentiment analysis results for the selected user"

    if (pos > neg) and (pos > neu):
        return "Positive 😊"
    elif (neg > pos) and (neg > neu):
        return "Negative 😠"
    else:
        return "Neutral 🙂"