import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

st.sidebar.title("📊 Chat Data Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload your exported chat (.txt)", type=["txt"])
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    if df.empty:
        st.error("❌ Could not process the file. Please check the format (ensure exported without media).")
    else:
        # fetch unique users safely
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis for", user_list)

        if st.sidebar.button("🚀 Run Analysis"):

            # Stats Area
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            st.title("📌 Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Messages", num_messages)
            with col2:
                st.metric("Total Words", words)
            with col3:
                st.metric("Media Shared", num_media_messages)
            with col4:
                st.metric("Links Shared", num_links)

            # monthly timeline
            st.header("🗓 Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            if not timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green', marker="o")
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("⚠️ No monthly timeline data available.")

            # daily timeline
            st.header("📅 Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            if not daily_timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("⚠️ No daily timeline data available.")

            # activity map
            st.header('📍 Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                if not busy_day.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.info("No day activity data.")

            with col2:
                st.subheader("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                if not busy_month.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.info("No month activity data.")

            st.subheader("⏰ Weekly Heatmap (Day vs Hour)")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if not user_heatmap.empty:
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, ax=ax, cmap="YlGnBu")
                st.pyplot(fig)
            else:
                st.warning("⚠️ Not enough data to generate heatmap.")

            # busiest users (group only)
            if selected_user == 'Overall':
                st.header('👥 Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                if not x.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig, ax = plt.subplots()
                        ax.bar(x.index, x.values, color='red')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)
                else:
                    st.info("No user activity data available.")

            # WordCloud
            st.header("☁️ WordCloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            if df_wc:
                fig, ax = plt.subplots()
                ax.imshow(df_wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.warning("⚠️ Not enough data for WordCloud.")

            # most common words
            st.header('🔠 Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            if not most_common_df.empty:
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1], color="skyblue")
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("⚠️ No common words found.")

            # emoji analysis
            st.header("😀 Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                    st.pyplot(fig)
            else:
                st.warning("⚠️ No emojis found in this chat.")
