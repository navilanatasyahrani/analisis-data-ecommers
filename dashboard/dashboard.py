import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_delivered_customer_date').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").price.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_byreview_df(df) :
    byreview_df = df.groupby(by="review_score").order_id.nunique().reset_index()
    byreview_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

    return byreview_df

def create_pie_chart(byreview_df):
    # Data for pie chart
    byreview_df = all_df.groupby(by="review_score").order_id.nunique().reset_index()
    byreview_df.rename(columns={
    "order_id": "order_count"
}, inplace=True)

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_rfm_df(df):
    rfm_df = main_df.groupby(by="customer_id", as_index=False).agg({
    "order_delivered_customer_date": "max", # mengambil tanggal order terakhir
    "order_id": "nunique", # menghitung jumlah order
    "price": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_delivered_customer_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

main_df = pd.read_csv("main_data.csv")

datetime_columns = ["order_estimated_delivery_date", "order_delivered_customer_date"]
main_df.sort_values(by="order_delivered_customer_date", inplace=True)
main_df.reset_index(inplace=True)

for column in datetime_columns:
    main_df[column] = pd.to_datetime(main_df[column])

min_date = main_df["order_delivered_customer_date"].min()
max_date = main_df["order_delivered_customer_date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("Butterfly logo.jpeg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = main_df[(main_df["order_delivered_customer_date"] >= str(start_date)) & 
                (main_df["order_delivered_customer_date"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
byreview_df = create_byreview_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Dashboard Penjualan :sparkles:')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_delivered_customer_date"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best and Worst Products that generate the revenue")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(50, 25))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
# Plot pertama
sns.barplot(x="price", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0], hue="product_category_name", legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Products that Generate the Best Revenue", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=20)

# Plot kedua
sns.barplot(x="price", y="product_category_name", data=sum_order_items_df.sort_values(by="price", ascending=True).head(5), palette=colors, ax=ax[1], hue="product_category_name", legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Products that generate the worst revenue", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=20)
 
st.pyplot(fig)

st.subheader("Number of Customer by States ")
fig, ax = plt.subplots(figsize=(10, 5))  # Mengatur ukuran subplot

# Menggambar plot pada subplot yang sudah ada
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    ax=ax  # Menetapkan subplot untuk menggambar plot
)
st.pyplot(fig)

st.subheader("Customers Review")
labels = byreview_df['review_score']
sizes = byreview_df['order_count']
fig, ax = plt.subplots(figsize=(8, 8))  # Membuat subplot baru dengan ukuran yang diinginkan
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
# Membuat pie chart pada subplot yang baru dibuat
ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
ax.set_title('Percentage of Orders by Review Score')  # Menambahkan judul pada subplot
ax.axis('equal')  # Memastikan pie chart menjadi lingkaran

st.pyplot(fig)  # Menampilkan subplot dengan menggunakan st.pyplot()



st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
   
st.pyplot(fig)
 
st.caption('Copyright (c) Navila Natasyahrani')