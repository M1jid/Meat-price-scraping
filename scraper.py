import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import pandas as pd
import plotly.graph_objects as go


# لیست محصولات گوسفندی و گوساله
sheep_products = [
    "قلوه گاه پیش ناف", "قلوه گاه", "ران و سردست", "سردست",
    "قلوه گاه با استخوان", "ماهیچه", "راسته مغزی", "خوردگی", "گردن", "خورده", "خرده", "ران", "راسته"
]

cow_products = [
    "ران و سردست", "ران", "گردن", "فیله", "سردست", "خوردگی", "خورده", "خرده", "راسته"
]

# ترکیب لیست محصولات
products_to_check = sheep_products + cow_products

# کلمات کلیدی برای حذف
exclude_keywords = ["مرغ", "بوقلمون", "جوجه", "کباب", "شاهپسند", "سوخاری"]

# تابع برای استخراج از mrghasab.com
def scrape_mrghasab():
    url = 'https://mrghasab.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', class_='product-thumb')

    product_list = []

    for product in products:
        name_tag = product.find('h4')
        name = name_tag.get_text(strip=True) if name_tag else "نام محصول موجود نیست"
        
        price_tag = product.find('p', class_='price')
        if price_tag:
            new_price = price_tag.find('span', class_='price-new')
            new_price_text = new_price.get_text(strip=True) if new_price else price_tag.get_text(strip=True)
            price_value = ''.join(filter(str.isdigit, new_price_text))
            if price_value:
                if any(keyword in name for keyword in products_to_check) and not any(exclude in name for exclude in exclude_keywords):
                    product_info = {
                        'name': name,
                        'price': price_value,
                        'site': 'mrghasab.com'
                    }
                    product_list.append(product_info)
    return product_list

# تابع برای استخراج از zaffar.ir
def scrape_zaffar():
    base_url = "https://www.zaffar.ir/product-category/red-meat/page/"
    pages = range(1, 6)
    all_products = []

    for page in pages:
        url = f"{base_url}{page}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('li', class_='jet-woo-builder-product')

        for product in products:
            product_name = product.find('h5', class_='jet-woo-builder-archive-product-title').text.strip()
            price = product.find('span', class_='woocommerce-Price-amount').text.strip()
            price_value = ''.join(filter(str.isdigit, price))
            
            if any(keyword in product_name for keyword in products_to_check) and not any(exclude in product_name for exclude in exclude_keywords):
                all_products.append({
                    'name': product_name,
                    'price': price_value,
                    'site': 'zaffar.ir'
                })
    return all_products

# تابع برای استخراج از ehsanstore.org
def scrape_ehsan():
    url = "https://ehsanstore.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', class_="row p-0 m-0")

    all_products = []

    for product in products:
        product_name_tag = product.find('div', class_='col-9 h6 p-0 m-0')
        if product_name_tag:
            product_name = product_name_tag.find('a').text.strip()
        else:
            product_name = "نام محصول موجود نیست"

        price_tag = product.find('div', class_='col-3 h6 p-0 m-0')
        if price_tag:
            price = price_tag.find('a', class_='p-0 m-0 text-dark').text.strip()
        else:
            price = "قیمت موجود نیست"

        price_value = ''.join(filter(str.isdigit, price))

        if any(keyword in product_name for keyword in products_to_check) and not any(exclude in product_name for exclude in exclude_keywords):
            if price_value:
                all_products.append({
                    'name': product_name,
                    'price': price_value,
                    'site': 'ehsanstore.org'
                })

    return all_products

# تابع برای ایجاد و بستن پایگاه داده
def create_database():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            site TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    return conn

# تابع برای بررسی و افزودن/به‌روزرسانی محصولات
def update_database(products, conn):
    c = conn.cursor()
    
    # دریافت تاریخ آخرین بروز رسانی
    c.execute("SELECT date FROM products ORDER BY date DESC LIMIT 1")
    last_date = c.fetchone()
    
    # تاریخ امروز
    today_date = datetime.now().strftime("%Y/%m/%d")

    if last_date and last_date[0] == today_date:
        # تاریخ امروز مشابه است، فقط قیمت‌ها را به‌روزرسانی می‌کنیم
        for product_name, details in products.items():
            c.execute("SELECT price FROM products WHERE name = ?", (product_name,))
            existing_product = c.fetchone()
            
            if existing_product:
                existing_price = existing_product[0]
                if int(details['price']) != existing_price:
                    c.execute("UPDATE products SET price = ? WHERE name = ?", (details['price'], product_name))
            else:
                # محصول جدید اضافه می‌شود
                c.execute("INSERT INTO products (name, price, site, date) VALUES (?, ?, ?, ?)",
                          (product_name, details['price'], details['site'], today_date))
    else:
        # تاریخ امروز جدید است، همه محصولات را اضافه می‌کنیم
        for product_name, details in products.items():
            c.execute("INSERT INTO products (name, price, site, date) VALUES (?, ?, ?, ?)",
                      (product_name, details['price'], details['site'], today_date))

    conn.commit()

# تابع برای خواندن داده‌ها از دیتابیس
def read_database(conn):
    c = conn.cursor()
    c.execute("SELECT name, price, site, date FROM products")
    return c.fetchall()

# تنظیمات صفحه
st.set_page_config(page_title="اطلاعات قیمت گوشت", page_icon="🥩", layout="centered")

# راست‌چین کردن عنوان و زیرعنوان با استفاده از CSS
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
        font-family: 'Arial', sans-serif;
    }
    .title {
        color: #ff4b4b;
        text-align: right;  /* راست‌چین کردن */
        font-weight: bold;
        font-size: 36px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .subtitle {
        color: #6c757d;
        text-align: right;  /* راست‌چین کردن */
        font-size: 18px;
        margin-bottom: 20px;
    }
    .button {
        background-color: #ff4b4b !important;
        color: white !important;
        font-weight: bold !important;
        padding: 10px 20px;  /* بزرگ‌تر کردن دکمه */
        font-size: 18px;
        border-radius: 5px;
        text-align: center;  /* وسط‌چین کردن متن در دکمه */
    }
    </style>
    <div class="title">🥩 سامانه آنلاین قیمت</div>
    <div class="subtitle">آخرین قیمت‌های گوشت گوسفند و گوساله از منابع معتبر</div>
""", unsafe_allow_html=True)

# دکمه به‌روزرسانی سمت راست و بزرگ‌تر
col1, col2 = st.columns([3, 1])  # تقسیم فضای صفحه به دو ستون
with col1:
    st.write("")  # فضای خالی برای راست‌چین کردن
with col2:
    if st.button("به‌روزرسانی قیمت‌ها", key="scrape", help="دریافت آخرین قیمت‌های امروز", use_container_width=True):
        with st.spinner("در حال دریافت قیمت‌ها..."):
            mrghasab_products = scrape_mrghasab()
            zaffar_products = scrape_zaffar()
            ehsan_products = scrape_ehsan()

            all_products = mrghasab_products + zaffar_products + ehsan_products

            unique_products = {}
            for product in all_products:
                product_name = product['name']
                product_price = product['price']

                if product_price.isdigit():
                    product_price = int(product_price)
                unique_products[product_name] = {
                    'price': product['price'],
                    'site': product['site']
                }

            conn = create_database()
            update_database(unique_products, conn)

            st.success("قیمت‌ها با موفقیت دریافت شدند!")

# خواندن داده‌ها و نمایش در جدول
conn = create_database()
data = read_database(conn)

# نمایش داده‌ها با قابلیت جستجو، دانلود و اسکرول
if data:
    df = pd.DataFrame(data, columns=["نام محصول", "قیمت (تومان)", "سایت", "تاریخ"])
    
    # راست‌چین کردن نام محصولات و اضافه کردن قابلیت اسکرول
    df_styled = df.style.set_properties(subset=['نام محصول'], **{'text-align': 'right'})
    
    # نمایش جدول با قابلیت اسکرول و دانلود
    st.dataframe(df_styled, use_container_width=True, height=400)
else:
    st.warning("هیچ اطلاعاتی برای نمایش وجود ندارد.")



# انتخاب محصول برای نمایش نمودار قیمت
product_names = [row[0] for row in data]
selected_product = st.selectbox("محصول را انتخاب کنید:", product_names)

# دریافت داده‌های قیمت برای محصول انتخابی
if selected_product:
    conn = create_database()
    c = conn.cursor()
    c.execute("SELECT date, price FROM products WHERE name = ? ORDER BY date", (selected_product,))
    price_history = c.fetchall()
    conn.close()

    # اگر داده‌ها موجود باشد، نمودار را رسم کن
    if price_history:
        dates, prices = zip(*price_history)

        # رسم نمودار
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name=selected_product,
            line=dict(color='royalblue', width=2),
            marker=dict(size=6, color='orange')
        ))

        # تنظیمات چیدمان
        fig.update_layout(
            title=f"نمودار قیمت {selected_product}",
            xaxis_title="تاریخ",
            yaxis_title="قیمت (تومان)",
            plot_bgcolor='white',  # رنگ پس‌زمینه نمودار
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='lightgray',  # رنگ پس‌زمینه کلی نمودار
            font=dict(color='black'),  # رنگ متن کل نمودار
            xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),  # رنگ متن محور x
            yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'), tickmode='array', tickvals=prices, ticktext=[f"{price} تومان" for price in prices])  # رنگ متن محور y و نمایش کامل قیمت‌ها
        )


# تابع برای بررسی تغییرات قیمت نسبت به دیروز (بدون تغییر)
def get_price_changes():
    conn = create_database()  # ایجاد اتصال جدید به پایگاه داده
    c = conn.cursor()

    # تاریخ دیروز و امروز
    yesterday_date = (datetime.now() - pd.Timedelta(days=1)).strftime("%Y/%m/%d")
    today_date = datetime.now().strftime("%Y/%m/%d")

    # دریافت قیمت‌های دیروز
    c.execute("SELECT name, price FROM products WHERE date = ?", (yesterday_date,))
    yesterday_prices = {row[0]: row[1] for row in c.fetchall()}

    # دریافت قیمت‌های امروز
    c.execute("SELECT name, price FROM products WHERE date = ?", (today_date,))
    today_prices = {row[0]: row[1] for row in c.fetchall()}

    # بررسی افزایش قیمت
    price_increases = []
    for product_name, today_price in today_prices.items():
        yesterday_price = yesterday_prices.get(product_name)
        if yesterday_price and int(today_price) > int(yesterday_price):
            price_increases.append({
                'name': product_name,
                'yesterday_price': yesterday_price,
                'today_price': today_price,
            })

    conn.close()  # بستن اتصال به پایگاه داده
    return price_increases

# دریافت داده‌های قیمت برای محصول انتخابی
if selected_product:
    conn = create_database()
    c = conn.cursor()
    c.execute("SELECT date, price FROM products WHERE name = ? ORDER BY date", (selected_product,))
    price_history = c.fetchall()
    conn.close()

    # اگر داده‌ها موجود باشد، نمودار را رسم کن
    if price_history:
        dates, prices = zip(*price_history)

        # رسم نمودار
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name=selected_product,
            line=dict(color='royalblue', width=2),
            marker=dict(size=6, color='orange')
        ))

        # تنظیمات چیدمان
        fig.update_layout(
            title=f"نمودار قیمت {selected_product}",
            xaxis_title="تاریخ",
            yaxis_title="قیمت (تومان)",
            plot_bgcolor='white',  # رنگ پس‌زمینه نمودار
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='lightgray',  # رنگ پس‌زمینه کلی نمودار
            font=dict(color='black'),  # رنگ متن کل نمودار
            xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),  # رنگ متن محور x
            yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'), tickmode='array', tickvals=prices, ticktext=[f"{price} تومان" for price in prices])  # رنگ متن محور y و نمایش کامل قیمت‌ها
        )

        # نمایش نمودار
        st.plotly_chart(fig)

# بررسی و نمایش تغییرات قیمت
price_changes = get_price_changes()

# ایجاد کادر مخصوص برای نمایش تغییرات قیمت زیر نمودار
st.markdown("### تغییرات قیمت محصولات:")
if price_changes:
    for change in price_changes:
        st.markdown(f"**{change['name']}**: از **{change['yesterday_price']} تومان** به **{change['today_price']} تومان** افزایش داشته است.")
else:
    st.markdown("هیچ محصولی افزایش قیمت نداشته است.")

