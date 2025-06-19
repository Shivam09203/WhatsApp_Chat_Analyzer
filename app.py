import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import emoji
import seaborn as sns
import plotly.express as px


st.set_page_config(page_title="Whatsapp Chat Analyzer", layout="wide")

st.title("WhatsChat🔎")
st.write("*Made by Shivam Gangal!👨🏻‍💻*")

st.sidebar.title("WhatsApp Chat Analyzer")
uploadedFile = st.sidebar.file_uploader("Choose a File🗃️. Only '.txt' format files are allowed.", type=['txt'])
if uploadedFile is not None:
    bytesData = uploadedFile.getvalue()
    finalData = bytesData.decode("utf-8")
    dataFrame = preprocessor.preprocess(finalData)
    #st.title("WhatsApp Chat Data")
    #st.dataframe(dataFrame.head())

    # fetch unique users
    userList = dataFrame["user"].unique().tolist()
    if "default" in userList:
        userList.remove("default")
    userList.sort()
    userList.insert(0, "Overall")
    selectedUser = st.sidebar.selectbox("Show Analysis🤔 WRT", userList)

    #if st.sidebar.button("Show Analysis🔢"):
    if (True):
        #top statistics
        numMessages, numWords, numMedia, numURL = helper.fetchStats(
            selectedUser, dataFrame)
        st.title("Top Statistics📈")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages🤳🏻")
            st.header(numMessages)
        with col2:
            st.header("Total Words💭")
            st.header(numWords)
        with col3:
            st.header("Media Shared🎥")
            st.header(numMedia)
        with col4:
            st.header("Links Shared🔗")
            st.header(numURL)

        #monthly timeline
        st.header("Monthly Timeline⌚")
        timeline = helper.monthlyTimeline(selectedUser, dataFrame)
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 3))
        plt.plot(timeline['time'], timeline['message'])
        plt.xticks(rotation='vertical')
        plt.xlabel('Month', color='yellow')
        plt.ylabel('Message Count', color='yellow')
        st.pyplot(plt)
        
        
        #monthly activity
        st.header("Monthly Activity📊")
        col1, col2 = st.columns(2)
        monthActivitySeries, monthActivity = helper.monthActivity(selectedUser, dataFrame)
        monthActivity = monthActivity.sort_values('message')
        month = monthActivity['monthName']
        messages = monthActivity['message']
        
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(messages.head(), labels=month.head().tolist(), autopct='%1.1f%%', colors=plt.cm.Dark2.colors)
            ax.axis('equal')
            plt.style.use('dark_background')
            st.pyplot(fig)
            
            
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(month, messages)
            ax.set_xlabel('Month of the Year', color="yellow")
            ax.set_ylabel('Number of Messages', color='yellow')
            plt.xticks(rotation='vertical')
            plt.style.use('dark_background')
            st.pyplot(fig)


        #daily timeline
        st.header("Daily Timeline📅")
        dailyTimeline = helper.dailyTimeline(selectedUser, dataFrame)
        plt.style.use('dark_background')
        plt.figure(figsize=(14, 3))
        plt.plot(dailyTimeline['onlyDate'], dailyTimeline['message'])
        plt.xticks(rotation='vertical')
        plt.xlabel('Date', color='yellow')
        plt.ylabel('Message Count', color='yellow')
        st.pyplot(plt)

        #daily activity
        st.header("Daily Activity📊")
        col1, col2 = st.columns(2)
        weekActivitySeries, weekActivity = helper.weekActivity(selectedUser, dataFrame)
        weekActivity = weekActivity.sort_values('message')
        days = weekActivity['dayName']
        messages = weekActivity['message']
        
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(messages, labels=days.tolist(), autopct='%1.1f%%', colors=plt.cm.Dark2.colors)
            ax.axis('equal')
            plt.style.use('dark_background')
            st.pyplot(fig)
            
            
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(days, messages)
            ax.set_xlabel('Day of the Week', color="yellow")
            ax.set_ylabel('Number of Messages', color='yellow')
            plt.style.use('dark_background')
            st.pyplot(fig)
        
        
        #weekly activity
        st.header("Weekly Activity by Time Period📲")
        activity = helper.activity(selectedUser, dataFrame)
        fig, ax = plt.subplots(figsize=(10, 2.5))
        ax = sns.heatmap(activity)
        ax.set_xlabel('Time Period', color='yellow')
        ax.set_ylabel('Name of the Day', color='yellow')
        plt.style.use('dark_background')
        st.pyplot(fig)
        
        
        #day-wise activity
        st.header("Day-wise Activity🗓️")
        h1, h2 = helper.hourActivity(selectedUser, dataFrame)
        tabs = st.multiselect("Select day(s) to display",['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        #tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in tabs:
            day_data = h2[h2['dayName'] == day]
            plot_placeholder = st.empty()
            with plot_placeholder:
                fig, axs = plt.subplots(figsize=(12, 3))
                axs.plot(day_data['hour'], day_data['message'])
                axs.set_title(day)
                axs.set_xlabel('Hour of the Day', color='yellow')
                axs.set_ylabel('Number of Messages', color='yellow')
                axs.set_xticks(range(0, 24, 2))
                axs.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig)


        #top chatters
        if selectedUser == 'Overall':
            st.header("Top Chatters🗣️")
            topChatter, topChatterPercent = helper.mostBusy(dataFrame)
            col1, col2 = st.columns(2)

            with col1:
                plt.style.use('dark_background')
                name = topChatter.index
                name = [emoji.emojize(n) for n in name]
                count = topChatter.values
                fig, ax = plt.subplots()
                plt.xlabel('Name').set_color('yellow')
                plt.ylabel('Messages Sent').set_color('yellow')
                ax.bar(name, count, width=0.8)
                plt.xticks(rotation='vertical')
                ax.tick_params(axis='both', which='major', labelsize=8)

                st.pyplot(fig)

            with col2:
                st.dataframe(topChatterPercent)

   
        #top words used
        mostCommon = helper.mostCommon(selectedUser, dataFrame)
        if (mostCommon.shape[0] != 0):
            st.header("Top Words Used🥇")

            fig, ax = plt.subplots()
            plt.ylabel('Message').set_color('yellow')
            plt.xlabel('Frequency').set_color('yellow')
            ax.barh(mostCommon['Message'], mostCommon['Frequency'])
            plt.xticks(rotation="vertical")
            st.pyplot(fig)
                
        
        #wordcloud
        df_wc = helper.wordCloud(selectedUser, dataFrame)
        
        col1, col2 = st.columns(2)
        with col1:
            st.header("Wordcloud🌬️")   
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)
            
        with col2:
            st.header("Top Words' Count🗣️")
            st.dataframe(mostCommon)
            
        

        # emoji analysis
        emoji_df = helper.mostEmoji(selectedUser, dataFrame)
        if (emoji_df.shape[0] != 0):
            st.header("Emoji Analysis😳")

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                color = ['#FFC107', '#2196F3', '#4CAF50', '#F44336', '#9C27B0']

                ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head().tolist(), autopct="%0.2f", colors=color)
                ax.set_title("Emoji Distribution", color='yellow')
                fig.set_facecolor('#121212')
                st.pyplot(fig)
        
        #message extractor
        st.header("Messages Extractor🪓")
        inputDate = st.text_input("Enter date in format : 19-08-2003")
        messageExtract = helper.messageExtractor(selectedUser, dataFrame, inputDate)
        if st.button("Extract"):
            if messageExtract is not None and messageExtract.shape[0]>0:
                st.dataframe(messageExtract, width=1400)
            else:
                st.write("No conversation(s) on", inputDate)  

        #reply time analysis
        st.header("Reply Time Analysis⏩")
        timeDifference, timeSelected = helper.replyTime(selectedUser, dataFrame)
        if (selectedUser!='Overall'):
            st.write("Average Reply Time by", selectedUser, "is", timeSelected)
        else:
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.bar(timeDifference['user'], timeDifference['replyTime'].dt.seconds)
                ax.set_xlabel('Participant', color='yellow')
                ax.set_ylabel('Average Reply Time (Seconds)', color='yellow')
                ax.set_title('')
                st.pyplot(plt)
            with col2:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(timeDifference['replyTime'].head(), labels=timeDifference['user'].head().tolist(), autopct='%1.1f%%', colors=plt.cm.Dark2.colors)
                ax.axis('equal')
                plt.style.use('dark_background')
                ax.set_title('')
                st.pyplot(fig)
                
        
        # User Sentiment Analysis
        st.header("Sentiment Analysis")

        # Perform sentiment analysis for the selected user or overall
        user_sentiments = helper.analyze_sentiment(selectedUser, dataFrame)

        # If the selected user is 'Overall', display sentiment for all users
        if selectedUser == 'Overall':
            overall_sentiment = {key: sum([user[key] for user in user_sentiments.values()])/len(user_sentiments) for key in ['pos', 'neu', 'neg', 'compound']}
            st.subheader("Overall")

            # Create a horizontal bar chart for the overall sentiment scores
            fig, ax = plt.subplots()
            ax.barh(list(overall_sentiment.keys()), list(overall_sentiment.values()), color=['green' if v >= 0 else 'red' for v in overall_sentiment.values()])
            ax.set_xlabel('Score', color='yellow')
            ax.set_title('Overall sentiment scores', color='yellow')
            st.pyplot(fig)
        else:
            # If the selected user exists in the sentiment analysis results
            if selectedUser in user_sentiments:
                sentiment_scores = user_sentiments[selectedUser]

                st.subheader(f"User: {selectedUser}")

                # Create a horizontal bar chart for the sentiment scores
                fig, ax = plt.subplots()
                ax.barh(list(sentiment_scores.keys()), list(sentiment_scores.values()), color=['yellow' if v >= 0 else 'red' for v in sentiment_scores.values()])
                ax.set_xlabel('Score')
                ax.set_title(f'Sentiment scores for {selectedUser}')
                st.pyplot(fig)
            else:
                st.write(f"No sentiment analysis results for {selectedUser}")

        ## Final results for the sentiment analysis

        # Perform sentiment analysis for the selected user or overall
        user_sentiments = helper.analyze_sentiment(selectedUser, dataFrame)

        # Display the sentiment score
        sentiment = helper.sentiment_score(user_sentiments, selectedUser)
        st.subheader(f"The sentiment of {selectedUser} is {sentiment}")
