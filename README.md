# 🥩 **Meat-price-scraping** 🥩

## **Project Overview** 🌍

**Meat-price-scraping** is an online system that collects **real-time meat prices** from multiple trusted websites and displays them in a sleek, user-friendly web application. Built using **Streamlit**, **SQLite**, and **Python**, this project combines **web scraping**, **data processing**, and **visualization** for optimal performance and usability.

---

## **Features** 🌟

### 🔍 **Fetching Prices from Multiple Sources**
Prices are collected from trusted websites like:
- [mrghasab.com](https://mrghasab.com)
- [zaffar.ir](https://zaffar.ir)
- [ehsanstore.org](https://ehsanstore.org)

### 💾 **SQLite Database Storage**
All prices are stored in an **SQLite database**, ensuring fast and efficient access to data. Query and analyze data easily! 📊

### 📈 **Displaying Prices in a Table**
Prices are displayed in an interactive table with filtering and searching options. 🧑‍💻

### 🔄 **Real-time Updates**
Users can click on the **"Update Prices"** button to refresh the data in real-time. 📲

### 🗂️ **Exporting Data to Excel**
Easily export collected data to an **Excel file** for further analysis or reporting. 📑

---

## **How It Works** ⚙️

### 1. 🏷️ **Fetching Prices**
The system scrapes real-time meat prices from trusted websites on a regular basis.

### 2. 💾 **Storing Data**
Collected data is stored in an **SQLite database** for fast retrieval.

### 3. 👀 **Displaying and Updating**
The user can click on **"Update Prices"** to refresh the data and see live changes on the table.

---

## **Requirements** 📦

Before running the project, install the following libraries:

- `streamlit` – To build and run the web application.
- `requests` – For making HTTP requests and scraping data.
- `beautifulsoup4` – For scraping HTML data from websites.
- `sqlite3` – For database storage.
- `pandas` – For data manipulation and processing.
- `plotly` – For creating interactive visualizations.

To install the libraries, use the following command:

```bash
pip install streamlit requests beautifulsoup4 pandas plotly
```


#How to Use 🚀
1. Run the Streamlit Application
Start by running the following command in your terminal:

```bash
streamlit run app.py
```

Interact with the Application:

Once the app loads, you'll see a table displaying current meat prices.
Click on the "Update Prices" button to fetch the latest data from the websites.
The app will refresh the table with the updated prices and store them in the SQLite database.
You can also export the data to an Excel file for further analysis.


##Project Structure 📂
database.py: Handles SQLite database management (data storage and retrieval). 💾
scraper.py: The script for scraping data from various websites. 🔧


##Future Development Steps 🚧
Add Graphs 📊: For visualizing the trends in meat prices over time.
Statistical Analysis 📉: Implement analysis such as average prices, highest price changes, and more.
Support More Sources 🌐: Expand the list of trusted websites for fetching prices.


##License 📝
This project is licensed under the MIT License.

##Contributing 🤝
If you'd like to contribute to this project, feel free to fork the repository and submit pull requests! Please make sure to follow the code style and write meaningful commit messages.




##Contact 📫
If you have any questions or suggestions, feel free to contact the project creator at m.nargesi.as@gmail.com.
