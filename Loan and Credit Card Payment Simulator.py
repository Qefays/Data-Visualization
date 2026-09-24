import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


# ------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------
st.set_page_config(
    page_title="Loan and Credit Card Payment Simulator",
    page_icon="🏦",
    layout="wide"
)


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def money(value):
    return f"RM {value:,.2f}"


def convert_to_excel(dataframe):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Amortization Schedule"
        )

    return output.getvalue()


def calculate_scheduled_payment(principal, annual_rate, years, interest_type):
    months = years * 12
    monthly_rate = annual_rate / 100 / 12

    if interest_type == "Flat Interest":
        total_interest = principal * (annual_rate / 100) * years
        total_repayment = principal + total_interest
        monthly_payment = total_repayment / months

    else:
        if monthly_rate == 0:
            monthly_payment = principal / months
        else:
            monthly_payment = (
                principal
                * monthly_rate
                / (1 - (1 + monthly_rate) ** (-months))
            )

        total_repayment = monthly_payment * months
        total_interest = total_repayment - principal

    return monthly_payment, total_interest, total_repayment


def create_amortization_schedule(
    principal,
    annual_rate,
    monthly_payment,
    interest_type,
    max_months=600
):
    monthly_rate = annual_rate / 100 / 12
    balance = principal
    cumulative_interest = 0
    rows = []

    for month in range(1, max_months + 1):
        opening_balance = balance

        if interest_type == "Flat Interest":
            interest = principal * monthly_rate
        else:
            interest = opening_balance * monthly_rate

        if monthly_payment > interest:
            principal_payment = min(
                monthly_payment - interest,
                opening_balance
            )
            actual_payment = principal_payment + interest
            closing_balance = opening_balance - principal_payment
        else:
            principal_payment = 0
            actual_payment = monthly_payment
            closing_balance = opening_balance + (interest - monthly_payment)

        cumulative_interest += interest

        rows.append({
            "Month": month,
            "Opening Balance": opening_balance,
            "Payment": actual_payment,
            "Principal": principal_payment,
            "Interest": interest,
            "Closing Balance": closing_balance,
            "Cumulative Interest": cumulative_interest
        })

        balance = closing_balance

        if balance <= 0.01:
            break

        # Safety stop if the balance grows too much.
        if balance > principal * 100:
            break

    schedule = pd.DataFrame(rows)
    paid_off = balance <= 0.01

    return schedule, paid_off


# ------------------------------------------------------------
# APP TITLE
# ------------------------------------------------------------
st.title("🏦 Loan and Credit Card Payment Simulator")
st.write(
    "Enter the loan details, calculate the scheduled payment, "
    "then adjust the monthly payment to see how repayment changes."
)


# ------------------------------------------------------------
# LOAN INPUTS
# ------------------------------------------------------------
with st.form("loan_form"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        loan_amount = st.number_input(
            "Loan amount (RM)",
            min_value=100.0,
            value=50000.0,
            step=1000.0
        )

    with col2:
        annual_rate = st.number_input(
            "Annual interest rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.1
        )

    with col3:
        loan_term = st.number_input(
            "Loan term (years)",
            min_value=1,
            max_value=40,
            value=5,
            step=1
        )

    with col4:
        interest_type = st.selectbox(
            "Interest type",
            ["Flat Interest", "Reducing Balance"]
        )

    calculate = st.form_submit_button("Calculate Loan")


# ------------------------------------------------------------
# SAVE THE CALCULATION
# ------------------------------------------------------------
if calculate:
    scheduled_payment, scheduled_interest, scheduled_total = (
        calculate_scheduled_payment(
            loan_amount,
            annual_rate,
            loan_term,
            interest_type
        )
    )

    st.session_state.loan_data = {
        "principal": loan_amount,
        "rate": annual_rate,
        "term": loan_term,
        "interest_type": interest_type,
        "scheduled_payment": scheduled_payment,
        "scheduled_interest": scheduled_interest,
        "scheduled_total": scheduled_total
    }

    st.session_state.monthly_payment = float(scheduled_payment)


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------
if "loan_data" in st.session_state:
    data = st.session_state.loan_data

    principal = data["principal"]
    rate = data["rate"]
    term = data["term"]
    interest_type = data["interest_type"]
    scheduled_payment = data["scheduled_payment"]
    scheduled_interest = data["scheduled_interest"]
    scheduled_total = data["scheduled_total"]

    st.divider()
    st.subheader("Scheduled Loan Summary")

    m1, m2, m3 = st.columns(3)
    m1.metric("Scheduled Monthly Payment", money(scheduled_payment))
    m2.metric("Scheduled Total Interest", money(scheduled_interest))
    m3.metric("Scheduled Total Repayment", money(scheduled_total))

    st.divider()
    st.subheader("Payment Simulation")
    st.write(
        "Change the monthly payment below to simulate early, on-time, "
        "or late repayment."
    )

    slider_max = max(scheduled_payment * 2, scheduled_payment + 1000)
    slider_step = 10.0 if scheduled_payment >= 100 else 1.0

    monthly_payment = st.slider(
        "Monthly payment (RM)",
        min_value=1.0,
        max_value=float(slider_max),
        step=slider_step,
        key="monthly_payment"
    )

    schedule, paid_off = create_amortization_schedule(
        principal,
        rate,
        monthly_payment,
        interest_type
    )

    months_used = len(schedule)
    target_months = term * 12
    total_interest = schedule["Interest"].sum()
    total_repayment = schedule["Payment"].sum()

    if not paid_off:
        payment_status = "Late / Not fully repaid within 600 months"
        st.error(payment_status)
    elif months_used < target_months:
        payment_status = "Early Payment"
        st.success(f"{payment_status}: loan paid off in {months_used} months.")
    elif months_used == target_months:
        payment_status = "On Time"
        st.info(f"{payment_status}: loan paid off in {months_used} months.")
    else:
        payment_status = "Late Payment"
        st.warning(f"{payment_status}: loan paid off in {months_used} months.")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Monthly Payment", money(monthly_payment))
    r2.metric("Repayment Time", f"{months_used} months")
    r3.metric("Total Interest", money(total_interest))
    r4.metric("Total Repayment", money(total_repayment))

    st.divider()
    st.subheader("Graphs")

    # Graph 1: Remaining balance over time
    st.write("**Remaining Loan Balance**")

    fig1, ax1 = plt.subplots()
    ax1.plot(
        schedule["Month"],
        schedule["Closing Balance"]
    )
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Balance (RM)")
    ax1.set_title("Loan Balance Over Time")
    ax1.grid(True)

    st.pyplot(fig1)
    plt.close(fig1)

    # Create early and late payment examples for the bar chart.
    early_payment = scheduled_payment * 1.20
    late_payment = scheduled_payment * 0.80

    # Make sure the late payment still covers the first month's interest.
    first_month_interest = principal * (rate / 100 / 12)
    late_payment = max(late_payment, first_month_interest + 1)

    early_schedule, _ = create_amortization_schedule(
        principal,
        rate,
        early_payment,
        interest_type
    )

    late_schedule, _ = create_amortization_schedule(
        principal,
        rate,
        late_payment,
        interest_type
    )

    early_interest = early_schedule["Interest"].sum()
    late_interest = late_schedule["Interest"].sum()

    graph2, graph3 = st.columns(2)

    # Graph 2: Pie chart
    with graph2:
        st.write("**Principal vs Interest**")

        fig2, ax2 = plt.subplots()
        ax2.pie(
            [principal, total_interest],
            labels=["Principal", "Interest"],
            autopct="%1.1f%%"
        )
        ax2.set_title("Total Repayment Composition")

        st.pyplot(fig2)
        plt.close(fig2)

    # Graph 3: Bar chart
    with graph3:
        st.write("**Early vs Late Payment Interest**")

        fig3, ax3 = plt.subplots()
        ax3.bar(
            ["Early Payment", "Late Payment"],
            [early_interest, late_interest]
        )
        ax3.set_ylabel("Total Interest (RM)")
        ax3.set_title("Interest Comparison")

        st.pyplot(fig3)
        plt.close(fig3)

        st.caption(
            "Early payment = 120% of scheduled payment. "
            "Late payment = about 80% of scheduled payment."
        )

    st.divider()
    st.subheader("Amortization Table")

    display_table = schedule.copy()

    money_columns = [
        "Opening Balance",
        "Payment",
        "Principal",
        "Interest",
        "Closing Balance",
        "Cumulative Interest"
    ]

    for column in money_columns:
        display_table[column] = display_table[column].round(2)

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    excel_file = convert_to_excel(display_table)

    st.download_button(
        label="Download Amortization Schedule as Excel",
        data=excel_file,
        file_name="lumen_amortization_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
