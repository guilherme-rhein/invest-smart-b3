# 💡 About the Project - Invest Smart B3
This project was developed to assist in analyzing stocks from the Brazilian stock exchange (B3), combining technical analysis indicators with fundamental data. An interactive app built with **Streamlit** to analyze and classify B3 stocks based on the **Relative Strength Index (RSI)**, supporting buy and sell decisions with both **technical and fundamental analysis**.

---

## 🚀 Highlights

- 📈 Automatic classification of B3 stocks using RSI
- 🔎 Dynamic filters by stock, RSI range, and classification
- 🧠 Integrated fundamental analysis using **Fundamentus** data
- 💾 Export filtered results to Excel (.xlsx)
- 🎯 Clean, responsive, and user-friendly interface powered by Streamlit

---

## 🎥 Demo
![Dash_Demo](https://raw.githubusercontent.com/guilherme-rhein/invest-smart-b3/refs/heads/main/IMG/PIC1.png)

![Dash_Demo](https://raw.githubusercontent.com/guilherme-rhein/invest-smart-b3/refs/heads/main/IMG/PIC2.png)

---

## 🛠️ Technologies Used

| Tool              | Description                               |
|-------------------|-------------------------------------------|
| Python            | Core logic and data processing             |
| Streamlit         | Interactive web interface                  |
| pandas            | Data manipulation and transformation       |
| yfinance          | Stock price data extraction                |
| ta (technical analysis) | RSI and other indicator calculations     |
| openpyxl / xlsxwriter | Excel file reading and exportation     |
| requests          | Web scraping of fundamentalist data        |

---

## ⚙️ How to Use
### 🚀 Access the Online App

You can use the app directly via the following link:

🔗 [invest-smart-b3.onrender.com](https://invest-smart-b3.onrender.com)

---

### 🖥️ Run Locally

If you prefer, you can download and run the app locally on your machine.

#### 🔧 Steps to run locally:

1. Clone the repository:
```bash
git clone https://github.com/guilherme-rhein/invest-smart-b3.git
```

2. Navigate to the local app folder:
```bash
cd invest-smart-b3/Local_Application
```

3. streamlit run app.py
```bash
streamlit run local_app.py
```

#### 📁 Example Data:
You can find sample data in the 'Import Data' folder.
The file can be uploaded directly in the app interface, allowing you to explore and test its features like filtering, visualization, and asset classification.

## 💡 About the Project
This project was developed to assist in analyzing stocks from the Brazilian stock exchange (B3), combining technical analysis indicators with fundamental data.
