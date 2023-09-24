import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_user_df(df):
    daily_user_df = df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    daily_user_df = daily_user_df.reset_index()
    daily_user_df.rename(columns={
        "instant": "instant_count",
        "cnt": "total_user"
    }, inplace=True)
    
    return daily_user_df

def create_sum_user_df(df):
    sum_user_df = df.groupby(by="weathersit").instant.nunique().sort_values(ascending=False).reset_index()
    return sum_user_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season").instant.nunique().reset_index()
    byseason_df.rename(columns={
        "instant": "instant_count"
    }, inplace=True)
    
    return byseason_df

def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by="workingday").instant.nunique().reset_index()
    byworkingday_df.rename(columns={
        "instant": "instant_count"
    }, inplace=True)
    byworkingday_df['workingday'] = byworkingday_df.workingday.apply(lambda x: "Holiday" if x <= 0 else ("Workday" if x > 0 else ""))
    byworkingday_df['workingday'] = pd.Categorical(byworkingday_df['workingday'], ["Workday", "Holiday"])
    
    return byworkingday_df

def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit").instant.nunique().reset_index()
    byweather_df.rename(columns={
        "instant": "instant_count"
    }, inplace=True)
    
    return byweather_df


# Load cleaned data
all_df = pd.read_csv("all_data.csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://cdn0-production-images-kly.akamaized.net/gT4v771Q6sAnGTmsn0esUczVvzI=/800x450/smart/filters:quality(75):strip_icc():format(webp)/kly-media-production/medias/1458352/original/077981200_1483458012-1.JPG")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

# st.dataframe(main_df)

# # Menyiapkan berbagai dataframe
daily_user_df = create_daily_user_df(main_df)
sum_user_df = create_sum_user_df(main_df)
byseason_df = create_byseason_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byweather_df = create_byweather_df(main_df)


# plot number of daily orders (2012)
st.header('Capital BikeShare System Dashboard :sparkles:')
st.subheader('Record')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_user_df.instant_count.sum()
    st.metric("Total record", value=total_orders)

with col2:
    total_revenue = daily_user_df.total_user.sum()
    st.metric("Total User", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_user_df["dteday"],
    daily_user_df["total_user"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# Product performance
st.subheader("Best & Worst Weather to Ride")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="weathersit", y="instant", data=sum_user_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Weather Condition", fontsize=30)
ax[0].set_title("Best Weather to ride", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="instant", y="weathersit", data=sum_user_df.sort_values(by="instant", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Users", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Weather to ride", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# customer demographic
st.subheader("Customer By Season & WorkingDay")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y="season", 
        x="instant_count",
        data=byseason_df.sort_values(by="instant_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of User by season", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="instant_count", 
        x="workingday",
        data=byworkingday_df.sort_values(by="workingday", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of User by Workingday", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)


st.caption('Copyright © Yudisdwi 2023')