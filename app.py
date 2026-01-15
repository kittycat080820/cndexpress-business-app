import streamlit as st
import pandas as pd
import datetime

# --- SETTINGS ---
PAYDAY_DATES = [1, 3, 15, 30, 31]

# --- FUNCTIONS ---
def is_payday(date_obj):
    if date_obj.day in PAYDAY_DATES:
        return True
    return False

# Load data (with a failsafe if file doesn't exist)
try:
    df = pd.read_csv('transaction_history.csv', parse_dates=['Date'])
except FileNotFoundError:
    st.error("No data file found! Please create 'transaction_history.csv' first.")
    st.stop()

# --- THE WEBSITE LAYOUT ---
st.title("CND EXPRESS 가계부 시스템")

# TAB 1: LOG NEW DATA
with st.expander("새 매출 기록하기 (클릭하여 열기)"):
    st.write("특정 날짜에 지출된 현금을 입력하세요:")
    
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("날짜", datetime.date.today())
    with col2:
        amount_input = st.number_input("금액 ($)", min_value=0, step=100)
        
    if st.button("저장하기"):
        # Save to CSV
        new_row = pd.DataFrame({'Date': [date_input], 'Cash_Dispensed': [amount_input]})
        # Append to the file
        new_row.to_csv('transaction_history.csv', mode='a', header=False, index=False)
        st.success(f"Saved ${amount_input} for {date_input}!")
        # Reload the page so the new data shows up
        st.rerun()

# TAB 2: THE PREDICTION
st.divider()
st.subheader("주간 현금 예측")

# Calculate averages
df['Is_Payday'] = df['Date'].apply(is_payday)
payday_data = df[df['Is_Payday'] == True]
normal_data = df[df['Is_Payday'] == False]

normal_averages = normal_data.groupby(normal_data['Date'].dt.day_name())['Cash_Dispensed'].mean()
avg_payday_amount = payday_data['Cash_Dispensed'].mean()

# Predict
today = datetime.datetime.now()
forecast_data = []

# --- KOREAN SETTINGS ---
# Dictionary to translate English days to Korean
korean_days = {
    'Monday': '월요일',
    'Tuesday': '화요일',
    'Wednesday': '수요일',
    'Thursday': '목요일',
    'Friday': '금요일',
    'Saturday': '토요일',
    'Sunday': '일요일'
}

# Predict loop
for i in range(1, 8):
    next_date = today + datetime.timedelta(days=i)
    english_day = next_date.strftime('%A')
    korean_day = korean_days[english_day] # Convert to Korean
    
    if is_payday(next_date):
        predicted = avg_payday_amount
        day_type = "월급날 🚨" # "Payday" in Korean
    else:
        predicted = normal_averages.get(english_day, 5000)
        day_type = korean_day
        
    safe_cash = predicted * 1.10
    
    forecast_data.append({
        "날짜": next_date.strftime('%Y-%m-%d'),   # "Date"
        "구분": day_type,                        # "Type" / "Classification"
        "준비할 현금": f"${safe_cash:,.0f}"        # "Cash to Prepare"
    })

# Show the table beautifully
st.dataframe(pd.DataFrame(forecast_data), use_container_width=True)

# Show a chart
st.divider()
st.subheader("매출 추이")
st.line_chart(df.set_index("Date")['Cash_Dispensed'])