import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
from babel.numbers import format_currency
from matplotlib.patches import Rectangle
sns.set(style='dark')
#pembuatan costumer rfm
def create_costumer_rfm_df(df):
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "total payment": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df
#pembuatan seller rfm
def create_seller_rfm_df(df):
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    rfm_df = df.groupby(by="seller_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "total payment": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["seller_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df
#pembuatan fungsi untuk menentukan produk terbaik
def create_best_category(df):
    category_sales=df.groupby('product_category_name')['total_sales'].sum().sort_values(ascending=False)
    top_5_categories = category_sales.nlargest(5)
    bottom_5_categories = category_sales.nsmallest(5)
    
    return top_5_categories,bottom_5_categories 
#pembuatan data untuk mencari hubungan delay dengan kota yang ada
def create_delay(df):
    # Hitung rata-rata delay berdasarkan state penjual dan pembeli
    average_delay_state = df.groupby(['seller_state', 'customer_state'])['delay'].mean().reset_index()
    #membuat pivot
    heatmap_data_state = average_delay_state.pivot(index='seller_state', columns='customer_state', values='delay')
    #merapihkan data yang akan ditampilkan
    heatmap_data_state_sorted = heatmap_data_state[heatmap_data_state.isnull().sum().sort_values().index]
    heatmap_data_state_sorted = heatmap_data_state_sorted.loc[heatmap_data_state_sorted.isnull().sum(axis=1).sort_values().index]
    return  heatmap_data_state_sorted
#mengabil data yang akan digunakan 
all_df = pd.read_csv("all_data.csv")



#mendefinisikan maksimal dan minimal dari data yang ada
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

if isinstance(min_date, pd.Timestamp):
    min_time = min_date.time()
elif isinstance(min_date, datetime.datetime):
    min_time = min_date.time()
else:
    # Handle other cases or raise an error
    raise TypeError("min_date is not a Timestamp or datetime object")

min_date=min_date.date.time()
max_date=max_date.date.time()
#membuat widget untuk mengambil input data dari pengguna
with st.sidebar:
    
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
#membuat main df yakni all_df untuk tanggal yang dimasukkan    
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]
#membuat data rfm
costumer_rfm_df = create_costumer_rfm_df(main_df)

st.subheader("Best Customer Based on RFM Parameters")

#membuat key point dari rfm costumer 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(costumer_rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(costumer_rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(costumer_rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=costumer_rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')
 
sns.barplot(y="frequency", x="customer_id", data=costumer_rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')
 
sns.barplot(y="monetary", x="customer_id", data=costumer_rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha='right')
st.pyplot(fig)

seller_rfm_df=create_seller_rfm_df(main_df)
#membuat key point dari rfm seller
col4, col5, col6 = st.columns(3)
st.subheader("Best Seller Based on RFM Parameters") 
with col4:
    avg_recency = round(seller_rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col5:
    avg_frequency = round(seller_rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col6:
    avg_frequency = format_currency(seller_rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

#membuat grafik rfm seller 
sns.barplot(y="recency", x="seller_id", data=seller_rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("seller_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')
 
sns.barplot(y="frequency", x="seller_id", data=seller_rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("seller_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')
 
sns.barplot(y="monetary", x="seller_id", data=seller_rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("seller_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha='right')
st.pyplot(fig)

#membuat grafik kategori dengan penjualan terbanyak dan paling sedikit
st.subheader("Kategori Produk dengan Penjualan Total Penjualan Terbesar dan Terkecil") 
top_5_categories,bottom_5_categories=create_best_category(main_df)
col7, col8 = st.columns(2)
with col7:
    st.subheader("Top 5 Kategori Produk")
    fig1, ax1 = plt.subplots(figsize=(7.5, 4))
    top_5_categories.plot(kind='bar', color='skyblue', ax=ax1)
    ax1.set_title('Top 5 Kategori Produk dengan Total Penjualan Terbesar')
    ax1.set_xlabel('Kategori Produk')
    ax1.set_ylabel('Total Penjualan')
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)
with col8:
    st.subheader("Bottom 5 Kategori Produk")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    bottom_5_categories.plot(kind='bar', color='lightcoral', ax=ax2)
    ax2.set_title('Top 5 Kategori Produk dengan Total Penjualan Terkecil', fontsize=14)
    ax2.set_xlabel('Kategori Produk', fontsize=12)
    ax2.set_ylabel('Total Penjualan', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig2)  # Menampilkan grafik di Streamlit
heatmap_data=create_delay(main_df)

fig3, ax3 = plt.subplots(figsize=(12, 8))

# Mask untuk nilai NaN
mask = heatmap_data.isnull()

# Buat colormap
cmap = sns.diverging_palette(240, 10, as_cmap=True)  # Biru ke merah dengan putih di tengah
cmap.set_bad(color='black') 
# Plot heatmap
sns.heatmap(
    heatmap_data,
    mask=mask,
    cmap=cmap,
    annot=False,
    fmt=".1f",
    cbar_kws={'label': 'Rata-Rata Delay (hari)'},
    linewidths=0.5,
    ax=ax3,
    center=0  # Pastikan nilai 0 berada di tengah gradasi warna
)

# Menambahkan kotak hitam sebagai legenda tambahan di bawah heatmap
ax3.add_patch(Rectangle((27, 17), 3, 4, color="black"))

# Menambahkan persegi hitam menggunakan Rectangle
ax3.add_patch(Rectangle((0.7, 22), 4, 4, color="black"))

# Menambahkan teks di samping kotak hitam
ax3.text(
    x=15,
    y=25,
    s="Data NaN atau tidak ada pengiriman",
    ha="left",
    va="center",
    fontsize=12,
    color="black", 
)

ax3.text(
    s="tes",
    color="black",
    x=29,
    y=25,
    bbox=dict(boxstyle="square,pad=0.3", facecolor="black", edgecolor="none")
)

# Menambahkan judul dan label sumbu
ax3.set_title('Rata-Rata Delay Pengiriman Berdasarkan State Penjual dan Pembeli')
ax3.set_xlabel('State Pembeli')
ax3.set_ylabel('State Penjual')

# Tampilkan plot di Streamlit
st.pyplot(fig3)
