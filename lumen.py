# ================================================================
# LUMEN
# LOAN & CREDIT CARD PAYMENT SIMULATION PLATFORM
# ================================================================

import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ================================================================
# PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="LUMEN | Finance Simulator",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ================================================================
# REQUIRE MODERN STREAMLIT
# ================================================================

if not hasattr(st, "html"):
    st.error(
        "This application requires a newer Streamlit version.\n\n"
        "Run:\n\n"
        "pip install -U streamlit"
    )
    st.stop()


# ================================================================
# SESSION STATE
# ================================================================

DEFAULT_STATE = {
    "page": "Home",
    "currency": "RM",
    "accent": "#3B82F6",
    "appearance": "Dark",
    "loan_ready": False,
    "loan_config": None,
    "simulation_count": 0,
    "chat_history": [],
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ================================================================
# GENERAL HELPERS
# ================================================================

def hex_to_rgb(hex_color):

    hex_color = (
        hex_color
        .lstrip("#")
    )

    return tuple(
        int(
            hex_color[i:i + 2],
            16
        )
        for i in (
            0,
            2,
            4,
        )
    )


def rgba(
    hex_color,
    alpha,
):

    r, g, b = hex_to_rgb(
        hex_color
    )

    return (
        f"rgba("
        f"{r},"
        f"{g},"
        f"{b},"
        f"{alpha}"
        f")"
    )


def blend_with_white(
    hex_color,
    amount=.35,
):

    r, g, b = hex_to_rgb(
        hex_color
    )

    r = int(
        r
        + (255 - r)
        * amount
    )

    g = int(
        g
        + (255 - g)
        * amount
    )

    b = int(
        b
        + (255 - b)
        * amount
    )

    return (
        f"#{r:02X}"
        f"{g:02X}"
        f"{b:02X}"
    )


def money(value):

    return (
        f"{st.session_state.currency}"
        f"{value:,.2f}"
    )


def format_duration(months):

    months = int(
        abs(months)
    )

    years = (
        months // 12
    )

    remaining_months = (
        months % 12
    )

    parts = []

    if years:

        parts.append(
            f"{years} "
            f"{'year' if years == 1 else 'years'}"
        )

    if remaining_months:

        parts.append(
            f"{remaining_months} "
            f"{'month' if remaining_months == 1 else 'months'}"
        )

    if not parts:

        return "0 months"

    return " ".join(
        parts
    )


# ================================================================
# THEME
# ================================================================

ACCENT = (
    st.session_state.accent
)

APPEARANCE = (
    st.session_state.appearance
)


if APPEARANCE == "Dark":

    THEME = {
        "bg":
            "#070A12",

        "sidebar":
            "#090D18",

        "panel":
            "#0E1422",

        "panel_soft":
            "#111929",

        "text":
            "#F4F7FF",

        "muted":
            "#929DB8",

        "border":
            "rgba(255,255,255,.09)",

        "grid":
            "rgba(255,255,255,.07)",

        "plot":
            "rgba(0,0,0,0)",
    }

else:

    THEME = {
        "bg":
            "#F5F7FB",

        "sidebar":
            "#FFFFFF",

        "panel":
            "#FFFFFF",

        "panel_soft":
            "#F0F4FA",

        "text":
            "#111827",

        "muted":
            "#667085",

        "border":
            "rgba(15,23,42,.11)",

        "grid":
            "rgba(15,23,42,.09)",

        "plot":
            "rgba(255,255,255,0)",
    }


GLOBAL_CSS = """
<style>

:root {
    --accent: __ACCENT__;
    --accent-soft: __ACCENT_SOFT__;
    --background: __BG__;
    --sidebar: __SIDEBAR__;
    --panel: __PANEL__;
    --panel-soft: __PANEL_SOFT__;
    --text: __TEXT__;
    --muted: __MUTED__;
    --border: __BORDER__;
}


/* ------------------------------------------------
   APPLICATION
------------------------------------------------ */

.stApp {

    background:
        radial-gradient(
            circle at 90% 5%,
            __ACCENT_GLOW__,
            transparent 28%
        ),
        radial-gradient(
            circle at 5% 100%,
            __ACCENT_GLOW_2__,
            transparent 30%
        ),
        var(--background);

    color:
        var(--text);
}


/* ------------------------------------------------
   SIDEBAR
------------------------------------------------ */

section[data-testid="stSidebar"] {

    background:
        var(--sidebar);

    border-right:
        1px solid
        var(--border);
}


section[data-testid="stSidebar"]
[data-testid="stMarkdownContainer"] p {

    color:
        var(--muted);
}


/* ------------------------------------------------
   PRIMARY BUTTONS
------------------------------------------------ */

button[kind="primary"] {

    background:
        var(--accent) !important;

    border-color:
        var(--accent) !important;

    color:
        white !important;
}


.stButton > button {

    border-radius:
        11px;

    font-weight:
        650;
}


/* ------------------------------------------------
   METRICS
------------------------------------------------ */

[data-testid="stMetric"] {

    background:
        var(--panel);

    border:
        1px solid
        var(--border);

    border-radius:
        17px;

    padding:
        15px 17px;

    box-shadow:
        0 12px 40px
        rgba(0,0,0,.08);
}


[data-testid="stMetricValue"] {

    color:
        var(--text);

    font-weight:
        800;

    letter-spacing:
        -1px;
}


/* ------------------------------------------------
   FORMS
------------------------------------------------ */

div[data-testid="stForm"] {

    background:
        var(--panel);

    border:
        1px solid
        var(--border);

    border-radius:
        20px;

    padding:
        17px;
}


/* ------------------------------------------------
   HERO
------------------------------------------------ */

.hero {

    position:
        relative;

    overflow:
        hidden;

    display:
        grid;

    grid-template-columns:
        minmax(0, 1.35fr)
        minmax(290px, .65fr);

    align-items:
        center;

    gap:
        55px;

    min-height:
        410px;

    padding:
        52px 56px;

    border:
        1px solid
        var(--border);

    border-radius:
        30px;

    background:
        linear-gradient(
            135deg,
            __ACCENT_HERO__,
            transparent 62%
        ),
        var(--panel);

    box-shadow:
        0 30px 90px
        rgba(0,0,0,.14);

    margin-bottom:
        28px;
}


.hero-copy {

    position:
        relative;

    z-index:
        2;

    min-width:
        0;
}


.hero-badge {

    display:
        inline-block;

    margin-bottom:
        20px;

    padding:
        7px 13px;

    border:
        1px solid
        var(--accent);

    border-radius:
        100px;

    color:
        var(--accent);

    font-size:
        .73rem;

    letter-spacing:
        1.7px;

    font-weight:
        700;
}


.hero h1 {

    color:
        var(--text);

    margin:
        0;

    max-width:
        790px;

    font-size:
        clamp(
            45px,
            6vw,
            80px
        );

    letter-spacing:
        -5px;

    line-height:
        .98;
}


.hero p {

    color:
        var(--muted);

    margin:
        25px 0 0 0;

    max-width:
        720px;

    font-size:
        1.04rem;

    line-height:
        1.8;
}


/* ------------------------------------------------
   CREDIT CARD
------------------------------------------------ */

.hero-card-wrapper {

    position:
        relative;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    width:
        100%;

    min-width:
        0;
}


.credit-card {

    position:
        relative;

    width:
        min(
            100%,
            340px
        );

    aspect-ratio:
        1.6 / 1;

    border-radius:
        22px;

    overflow:
        hidden;

    background:
        linear-gradient(
            140deg,
            var(--accent),
            #3944DB 55%,
            #111827
        );

    border:
        1px solid
        rgba(255,255,255,.28);

    box-shadow:
        0 35px 75px
        rgba(0,0,0,.28);

    transform:
        rotate(5deg);

    animation:
        floatingCard
        4s ease-in-out
        infinite;
}


.credit-card::after {

    content:
        "";

    position:
        absolute;

    width:
        220px;

    height:
        220px;

    right:
        -100px;

    top:
        -120px;

    border-radius:
        50%;

    background:
        rgba(255,255,255,.12);
}


@keyframes floatingCard {

    0% {
        transform:
            rotate(5deg)
            translateY(0);
    }

    50% {
        transform:
            rotate(3deg)
            translateY(-10px);
    }

    100% {
        transform:
            rotate(5deg)
            translateY(0);
    }
}


.card-chip {

    position:
        absolute;

    top:
        24%;

    left:
        9%;

    width:
        48px;

    height:
        34px;

    border-radius:
        8px;

    background:
        linear-gradient(
            135deg,
            #FFE794,
            #C49B37
        );
}


.card-number {

    position:
        absolute;

    left:
        9%;

    right:
        9%;

    top:
        57%;

    white-space:
        nowrap;

    overflow:
        hidden;

    color:
        white;

    font-family:
        monospace;

    font-size:
        clamp(
            12px,
            1.15vw,
            17px
        );

    font-weight:
        800;

    letter-spacing:
        2px;
}


.card-bottom {

    position:
        absolute;

    left:
        9%;

    right:
        9%;

    bottom:
        10%;

    display:
        flex;

    justify-content:
        space-between;

    color:
        rgba(255,255,255,.76);

    font-size:
        10px;

    letter-spacing:
        1px;
}


/* ------------------------------------------------
   SECTIONS
------------------------------------------------ */

.section-kicker {

    color:
        var(--accent);

    font-size:
        .72rem;

    font-weight:
        800;

    letter-spacing:
        1.8px;

    margin-top:
        10px;

    margin-bottom:
        7px;
}


.section-title {

    color:
        var(--text);

    font-size:
        2rem;

    font-weight:
        800;

    letter-spacing:
        -1.4px;

    margin-bottom:
        18px;
}


.feature-card {

    min-height:
        170px;

    padding:
        21px;

    border:
        1px solid
        var(--border);

    border-radius:
        19px;

    background:
        var(--panel);

    transition:
        transform .2s ease,
        border-color .2s ease;
}


.feature-card:hover {

    transform:
        translateY(-4px);

    border-color:
        var(--accent);
}


.feature-icon {

    font-size:
        1.8rem;

    margin-bottom:
        10px;
}


.feature-card h3 {

    margin:
        0 0 8px 0;

    color:
        var(--text);
}


.feature-card p {

    margin:
        0;

    color:
        var(--muted);

    line-height:
        1.6;

    font-size:
        .88rem;
}


/* ------------------------------------------------
   STATUS / INFO CARDS
------------------------------------------------ */

.simulation-note {

    padding:
        16px 19px;

    border:
        1px solid
        var(--border);

    border-radius:
        16px;

    color:
        var(--muted);

    background:
        var(--panel);
}


/* ------------------------------------------------
   FOOTER
------------------------------------------------ */

.footer {

    margin-top:
        45px;

    padding:
        25px 10px 12px 10px;

    border-top:
        1px solid
        var(--border);

    text-align:
        center;

    color:
        var(--muted);

    font-size:
        .78rem;
}


/* ------------------------------------------------
   RESPONSIVE
------------------------------------------------ */

@media (
    max-width: 980px
) {

    .hero {

        grid-template-columns:
            1fr;

        gap:
            35px;

        padding:
            36px 30px;
    }


    .hero h1 {

        letter-spacing:
            -3px;
    }


    .hero-card-wrapper {

        justify-content:
            flex-start;
    }


    .credit-card {

        max-width:
            320px;
    }
}

</style>
"""


GLOBAL_CSS = (
    GLOBAL_CSS

    .replace(
        "__ACCENT__",
        ACCENT
    )

    .replace(
        "__ACCENT_SOFT__",
        blend_with_white(
            ACCENT,
            .30
        )
    )

    .replace(
        "__ACCENT_GLOW__",
        rgba(
            ACCENT,
            .15
        )
    )

    .replace(
        "__ACCENT_GLOW_2__",
        rgba(
            ACCENT,
            .08
        )
    )

    .replace(
        "__ACCENT_HERO__",
        rgba(
            ACCENT,
            .18
        )
    )

    .replace(
        "__BG__",
        THEME["bg"]
    )

    .replace(
        "__SIDEBAR__",
        THEME["sidebar"]
    )

    .replace(
        "__PANEL__",
        THEME["panel"]
    )

    .replace(
        "__PANEL_SOFT__",
        THEME["panel_soft"]
    )

    .replace(
        "__TEXT__",
        THEME["text"]
    )

    .replace(
        "__MUTED__",
        THEME["muted"]
    )

    .replace(
        "__BORDER__",
        THEME["border"]
    )
)


st.html(
    GLOBAL_CSS
)


# ================================================================
# SETTINGS DIALOG
# ================================================================

CURRENCY_OPTIONS = {
    "Malaysian Ringgit — RM":
        "RM",

    "US Dollar — $":
        "$",

    "Singapore Dollar — S$":
        "S$",

    "British Pound — £":
        "£",

    "Euro — €":
        "€",
}


@st.dialog(
    "⚙️ Settings"
)
def settings_dialog():

    current_currency_label = next(
        key
        for key, value
        in CURRENCY_OPTIONS.items()
        if value
        == st.session_state.currency
    )


    with st.form(
        "settings_form"
    ):

        st.subheader(
            "Application Settings"
        )


        selected_appearance = st.radio(
            "Appearance",
            [
                "Dark",
                "Light",
            ],
            horizontal=True,
            index=(
                0
                if st.session_state.appearance
                == "Dark"
                else 1
            ),
        )


        selected_accent = st.color_picker(
            "Accent color",
            st.session_state.accent,
        )


        labels = list(
            CURRENCY_OPTIONS.keys()
        )


        selected_currency_label = st.selectbox(
            "Currency",
            labels,
            index=labels.index(
                current_currency_label
            ),
        )


        st.divider()


        apply_settings = (
            st.form_submit_button(
                "Apply Settings",
                use_container_width=True,
            )
        )


    if apply_settings:

        st.session_state.appearance = (
            selected_appearance
        )

        st.session_state.accent = (
            selected_accent
        )

        st.session_state.currency = (
            CURRENCY_OPTIONS[
                selected_currency_label
            ]
        )

        st.rerun()


# ================================================================
# SIDEBAR NAVIGATION
# ================================================================

with st.sidebar:

    st.markdown(
        "## ◈ LUMEN"
    )

    st.caption(
        "Finance Simulation Suite"
    )


    st.divider()


    st.markdown(
        "### Page Navigation"
    )


    NAVIGATION = [
        (
            "Home",
            "🏠 Home",
        ),
        (
            "Loan Simulator",
            "🏦 Loan Simulator",
        ),
        (
            "Credit Card Simulator",
            "💳 Credit Card Simulator",
        ),
        (
            "Debt Planner",
            "🧭 Debt Planner",
        ),
        (
            "Finance Assistant",
            "🤖 Finance Assistant",
        ),
    ]


    for page_name, button_label in NAVIGATION:

        active = (
            st.session_state.page
            == page_name
        )


        if st.button(
            button_label,
            key=f"nav_{page_name}",
            use_container_width=True,
            type=(
                "primary"
                if active
                else "secondary"
            ),
        ):

            st.session_state.page = (
                page_name
            )

            st.rerun()


    st.html(
        """
        <div style="
            height: 14vh;
        ">
        </div>
        """
    )


    st.divider()


    if st.button(
        "⚙️ Settings",
        use_container_width=True,
    ):

        settings_dialog()


# ================================================================
# PAGE VARIABLE
# ================================================================

page = (
    st.session_state.page
)


# ================================================================
# SECTION HEADER
# ================================================================

def section_header(
    kicker,
    title,
):

    st.html(
        f"""
        <div class="section-kicker">
            {kicker}
        </div>

        <div class="section-title">
            {title}
        </div>
        """
    )


# ================================================================
# PLOTLY THEME
# ================================================================

def style_plot(
    fig,
    height=430,
    legend=True,
):

    fig.update_layout(

        height=
            height,

        paper_bgcolor=
            THEME["plot"],

        plot_bgcolor=
            THEME["plot"],

        margin=dict(
            l=25,
            r=25,
            t=40,
            b=65,
        ),

        font=dict(
            color=
                THEME["text"]
        ),

        xaxis=dict(
            gridcolor=
                THEME["grid"],

            zeroline=
                False,
        ),

        yaxis=dict(
            gridcolor=
                THEME["grid"],

            zeroline=
                False,
        ),

        showlegend=
            legend,

        legend=dict(
            orientation=
                "h",

            yanchor=
                "top",

            y=
                -.18,

            xanchor=
                "center",

            x=
                .5,
        ),
    )

    return fig


# ================================================================
# LOAN ENGINE
# ================================================================

def scheduled_loan_terms(
    principal,
    annual_rate,
    years,
    interest_type,
):

    months = max(
        1,
        int(
            round(
                years * 12
            )
        )
    )


    annual_decimal = (
        annual_rate
        / 100
    )


    monthly_rate = (
        annual_decimal
        / 12
    )


    if (
        interest_type
        == "Flat Interest"
    ):

        monthly_interest = (
            principal
            * monthly_rate
        )


        monthly_principal = (
            principal
            / months
        )


        payment = (
            monthly_principal
            + monthly_interest
        )


        total_interest = (
            monthly_interest
            * months
        )


    else:

        if monthly_rate == 0:

            payment = (
                principal
                / months
            )

        else:

            payment = (
                principal
                * monthly_rate
                /
                (
                    1
                    -
                    (
                        1
                        + monthly_rate
                    )
                    ** (-months)
                )
            )


        total_interest = (
            payment
            * months
            - principal
        )


    total_repayment = (
        principal
        + total_interest
    )


    return (
        float(payment),
        float(total_interest),
        float(total_repayment),
    )


# ================================================================
# VARIABLE-PAYMENT LOAN SIMULATOR
# ================================================================

def simulate_loan_payment(
    principal,
    annual_rate,
    monthly_payment,
    interest_type,
    max_months=600,
):

    monthly_rate = (
        annual_rate
        / 100
        / 12
    )


    balance = float(
        principal
    )


    rows = []


    cumulative_interest = 0.0


    paid_off = False


    for month in range(
        1,
        max_months + 1
    ):

        opening = (
            balance
        )


        if (
            interest_type
            == "Flat Interest"
        ):

            interest = (
                principal
                * monthly_rate
            )

        else:

            interest = (
                opening
                * monthly_rate
            )


        # --------------------------------------------
        # Payment is sufficient to reduce principal
        # --------------------------------------------

        if monthly_payment > interest:

            principal_payment = min(
                opening,
                monthly_payment
                - interest,
            )


            actual_payment = (
                interest
                + principal_payment
            )


            closing = max(
                0,
                opening
                - principal_payment
            )


        # --------------------------------------------
        # Payment does not cover interest
        # --------------------------------------------

        else:

            actual_payment = (
                monthly_payment
            )


            principal_payment = (
                0
            )


            unpaid_interest = (
                interest
                - monthly_payment
            )


            closing = (
                opening
                + unpaid_interest
            )


        cumulative_interest += (
            interest
        )


        rows.append(
            {
                "Month":
                    month,

                "Opening Balance":
                    opening,

                "Payment":
                    actual_payment,

                "Principal":
                    principal_payment,

                "Interest":
                    interest,

                "Closing Balance":
                    closing,

                "Cumulative Interest":
                    cumulative_interest,
            }
        )


        balance = (
            closing
        )


        if balance <= .01:

            paid_off = (
                True
            )

            break


        # Stop extreme negative amortization
        if (
            balance
            > principal * 1_000_000
        ):

            break


    return (
        pd.DataFrame(
            rows
        ),
        paid_off,
    )


# ================================================================
# EFFECTIVE ANNUAL RATE FROM ACTUAL CASH FLOWS
# ================================================================

def effective_annual_rate(
    principal,
    payments,
):

    payments = list(
        payments
    )


    if not payments:

        return None


    if sum(payments) <= principal:

        return 0.0


    def npv(rate):

        result = (
            -principal
        )


        for index, payment in enumerate(
            payments,
            start=1,
        ):

            result += (
                payment
                /
                (
                    1
                    + rate
                )
                ** index
            )


        return result


    low = (
        0.0
    )

    high = (
        1.0
    )


    while (
        npv(high) > 0
        and high < 100
    ):

        high *= (
            2
        )


    for _ in range(
        120
    ):

        mid = (
            low
            + high
        ) / 2


        if npv(mid) > 0:

            low = (
                mid
            )

        else:

            high = (
                mid
            )


    monthly_irr = (
        low
        + high
    ) / 2


    annual_effective = (
        (
            1
            + monthly_irr
        )
        ** 12
        - 1
    )


    return (
        annual_effective
        * 100
    )


# ================================================================
# CREDIT CARD ENGINE
# ================================================================

@st.cache_data
def credit_card_schedule(
    starting_balance,
    apr,
    new_spending,
    strategy,
    minimum_percent,
    minimum_floor,
    fixed_payment,
    max_months=360,
):

    monthly_rate = (
        apr
        / 100
        / 12
    )


    balance = float(
        starting_balance
    )


    cumulative_interest = (
        0.0
    )


    rows = []


    for month in range(
        1,
        max_months + 1
    ):

        opening = (
            balance
        )


        interest = (
            opening
            * monthly_rate
        )


        balance_before_payment = (
            opening
            + interest
            + new_spending
        )


        if strategy == "Minimum Payment":

            payment = max(
                minimum_floor,
                balance_before_payment
                * minimum_percent
                / 100,
            )


        elif strategy == "Fixed Payment":

            payment = (
                fixed_payment
            )


        else:

            payment = (
                balance_before_payment
            )


        payment = min(
            payment,
            balance_before_payment
        )


        closing = max(
            0,
            balance_before_payment
            - payment
        )


        cumulative_interest += (
            interest
        )


        rows.append(
            {
                "Month":
                    month,

                "Opening Balance":
                    opening,

                "Interest":
                    interest,

                "New Spending":
                    new_spending,

                "Payment":
                    payment,

                "Closing Balance":
                    closing,

                "Cumulative Interest":
                    cumulative_interest,
            }
        )


        balance = (
            closing
        )


        if (
            balance <= .01
            and new_spending == 0
        ):

            break


    paid_off = (
        balance <= .01
        and new_spending == 0
    )


    return (
        pd.DataFrame(
            rows
        ),
        paid_off,
    )


# ================================================================
# DEBT PLANNER ENGINE
# ================================================================

def debt_payoff_simulation(
    debt_df,
    monthly_budget,
    strategy,
    max_months=600,
):

    debts = []


    for _, row in debt_df.iterrows():

        debts.append(
            {
                "name":
                    str(
                        row["Debt"]
                    ),

                "balance":
                    max(
                        0,
                        float(
                            row["Balance"]
                        )
                    ),

                "apr":
                    max(
                        0,
                        float(
                            row["APR %"]
                        )
                    ),

                "minimum":
                    max(
                        0,
                        float(
                            row[
                                "Minimum Payment"
                            ]
                        )
                    ),
            }
        )


    history = []


    total_interest = (
        0.0
    )


    payoff_months = {
        debt["name"]:
            None
        for debt in debts
    }


    for month in range(
        1,
        max_months + 1
    ):

        active = [
            debt
            for debt in debts
            if debt["balance"] > .01
        ]


        if not active:

            break


        monthly_interest = (
            0
        )


        # Apply interest
        for debt in active:

            interest = (
                debt["balance"]
                * debt["apr"]
                / 100
                / 12
            )


            debt["balance"] += (
                interest
            )


            monthly_interest += (
                interest
            )


        total_interest += (
            monthly_interest
        )


        total_payment = (
            0
        )


        # Required payments
        for debt in active:

            payment = min(
                debt["minimum"],
                debt["balance"],
            )


            debt["balance"] -= (
                payment
            )


            total_payment += (
                payment
            )


        extra = max(
            0,
            monthly_budget
            - total_payment
        )


        # Allocate remaining budget
        while extra > .01:

            active = [
                debt
                for debt in debts
                if debt["balance"] > .01
            ]


            if not active:

                break


            if strategy == "Debt Avalanche":

                target = max(
                    active,
                    key=lambda debt:
                        debt["apr"],
                )

            else:

                target = min(
                    active,
                    key=lambda debt:
                        debt["balance"],
                )


            extra_payment = min(
                extra,
                target["balance"],
            )


            target["balance"] -= (
                extra_payment
            )


            extra -= (
                extra_payment
            )


            total_payment += (
                extra_payment
            )


        for debt in debts:

            if (
                debt["balance"] <= .01
                and payoff_months[
                    debt["name"]
                ]
                is None
            ):

                payoff_months[
                    debt["name"]
                ] = (
                    month
                )


        total_balance = sum(
            debt["balance"]
            for debt in debts
        )


        history.append(
            {
                "Month":
                    month,

                "Total Balance":
                    total_balance,

                "Interest":
                    monthly_interest,

                "Payment":
                    total_payment,
            }
        )


        if total_balance <= .01:

            break


    history_df = pd.DataFrame(
        history
    )


    payoff_df = pd.DataFrame(
        [
            {
                "Debt":
                    debt_name,

                "Paid Off Month":
                    month
                    if month is not None
                    else "Not paid",
            }

            for debt_name, month
            in payoff_months.items()
        ]
    )


    paid_off = (
        len(history_df) > 0
        and history_df.iloc[-1][
            "Total Balance"
        ]
        <= .01
    )


    return (
        history_df,
        payoff_df,
        total_interest,
        paid_off,
    )


# ================================================================
# FINANCE ASSISTANT
# ================================================================

def finance_assistant_reply(
    prompt,
):

    text = (
        prompt.lower()
    )


    if "flat" in text:

        return (
            "With flat interest, the interest charge is based "
            "on the original principal rather than the declining "
            "balance. In LUMEN's simulator, the flat monthly "
            "interest amount stays constant while principal is "
            "being repaid."
        )


    if (
        "reducing" in text
        or "declining" in text
    ):

        return (
            "Reducing-balance interest is calculated from the "
            "outstanding principal. As the balance decreases, "
            "the interest portion generally decreases as well."
        )


    if "minimum" in text:

        return (
            "A minimum credit-card payment can reduce required "
            "cash outflow in the short term, but a smaller "
            "payment normally means the balance remains "
            "outstanding for longer and more interest can accrue."
        )


    if "avalanche" in text:

        return (
            "Debt Avalanche directs additional payment toward "
            "the highest-APR debt while maintaining required "
            "payments on the others."
        )


    if "snowball" in text:

        return (
            "Debt Snowball directs additional payment toward "
            "the smallest outstanding balance first."
        )


    if "apr" in text:

        return (
            "APR is an annualized interest-rate measure. "
            "Actual finance-charge calculations can depend on "
            "the product's compounding and balance method."
        )


    if (
        "early" in text
        or "extra payment" in text
    ):

        return (
            "A larger monthly payment normally reduces principal "
            "faster. In the Loan Simulator you can move the "
            "payment slider upward and see the payoff date, "
            "interest cost and graph update immediately."
        )


    return (
        "I can explain the simulation mechanics for loans, "
        "credit cards, APR, flat interest, reducing balance, "
        "early repayment, Debt Avalanche and Debt Snowball."
    )


# ================================================================
# HOME
# ================================================================

if page == "Home":

    st.html(
        """
        <div class="hero">

            <div class="hero-copy">

                <div class="hero-badge">
                    FINANCE SIMULATION PLATFORM
                </div>

                <h1>
                    See where your payments go.
                </h1>

                <p>
                    Model loans, credit-card balances,
                    repayment strategies and interest costs
                    using interactive simulations that respond
                    instantly when the numbers change.
                </p>

            </div>


            <div class="hero-card-wrapper">

                <div class="credit-card">

                    <div class="card-chip">
                    </div>

                    <div class="card-number">
                        5412&nbsp;&nbsp;89••&nbsp;&nbsp;••••&nbsp;&nbsp;2048
                    </div>

                    <div class="card-bottom">

                        <span>
                            LUMEN
                        </span>

                        <span>
                            ◉◉
                        </span>

                    </div>

                </div>

            </div>

        </div>
        """
    )


    section_header(
        "SIMULATION TOOLS",
        "Everything in one finance workspace."
    )


    c1, c2, c3 = st.columns(
        3
    )


    with c1:

        st.html(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🏦
                </div>

                <h3>
                    Loan Simulator
                </h3>

                <p>
                    Model repayment duration, interest cost,
                    early payments, late payments and
                    amortization.
                </p>

            </div>
            """
        )


        if st.button(
            "Open Loan Simulator",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Loan Simulator"
            )

            st.rerun()


    with c2:

        st.html(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    💳
                </div>

                <h3>
                    Credit Card Simulator
                </h3>

                <p>
                    Model revolving balances, APR,
                    new spending and different monthly
                    payment strategies.
                </p>

            </div>
            """
        )


        if st.button(
            "Open Card Simulator",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Credit Card Simulator"
            )

            st.rerun()


    with c3:

        st.html(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🧭
                </div>

                <h3>
                    Debt Planner
                </h3>

                <p>
                    Combine multiple debts and compare
                    Avalanche and Snowball payoff
                    simulations.
                </p>

            </div>
            """
        )


        if st.button(
            "Open Debt Planner",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Debt Planner"
            )

            st.rerun()


    st.divider()


    section_header(
        "QUICK SNAPSHOT",
        "Monthly debt-to-income simulation"
    )


    q1, q2, q3 = st.columns(
        [
            1,
            1,
            1.35,
        ]
    )


    with q1:

        monthly_income = st.number_input(
            "Monthly income",
            min_value=0.0,
            value=5000.0,
            step=100.0,
        )


    with q2:

        monthly_debt = st.number_input(
            "Monthly debt payments",
            min_value=0.0,
            value=1200.0,
            step=100.0,
        )


    dti = (
        monthly_debt
        /
        monthly_income
        * 100

        if monthly_income > 0

        else 0
    )


    with q3:

        dti_fig = go.Figure(
            go.Indicator(

                mode=
                    "gauge+number",

                value=
                    dti,

                number={
                    "suffix":
                        "%"
                },

                title={
                    "text":
                        "Debt-to-Income"
                },

                gauge={
                    "axis": {
                        "range":
                            [0, 100]
                    },

                    "bar": {
                        "color":
                            ACCENT
                    },

                    "bgcolor":
                        THEME[
                            "panel_soft"
                        ],

                    "borderwidth":
                        0,
                },
            )
        )


        dti_fig.update_layout(

            height=
                240,

            margin=dict(
                l=30,
                r=30,
                t=50,
                b=20,
            ),

            paper_bgcolor=
                THEME["plot"],

            font=dict(
                color=
                    THEME["text"]
            ),
        )


        st.plotly_chart(
            dti_fig,
            use_container_width=True,
        )


# ================================================================
# LOAN SIMULATOR
# ================================================================

elif page == "Loan Simulator":

    section_header(
        "LOAN LABORATORY",
        "Welcome to Loan and Credit Card Payment Simulator"
    )


    st.write(
        """
        Experiment with loan structure and see how the same
        headline rate can produce very different repayment
        behaviour.
        """
    )


    # ------------------------------------------------------------
    # INITIAL LOAN FORM
    # ------------------------------------------------------------

    with st.form(
        "loan_input_form"
    ):

        c1, c2, c3, c4 = st.columns(
            4
        )


        with c1:

            input_principal = st.number_input(
                "Loan amount",
                min_value=100.0,
                value=50000.0,
                step=1000.0,
            )


        with c2:

            input_rate = st.number_input(
                "Annual interest rate (%)",
                min_value=1.0,
                max_value=100.0,
                value=5.0,
                step=.1,
            )


        with c3:

            input_term = st.number_input(
                "Loan term (years)",
                min_value=1,
                max_value=40,
                value=5,
                step=1,
            )


        with c4:

            input_interest_type = st.selectbox(
                "Interest model",
                [
                    "Flat Interest",
                    "Reducing Balance",
                ],
            )


        calculate_loan = (
            st.form_submit_button(
                "Calculate Loan",
                use_container_width=True,
            )
        )


    # ------------------------------------------------------------
    # STORE INITIAL CALCULATION
    # ------------------------------------------------------------

    if calculate_loan:

        (
            initial_payment,
            _,
            _,
        ) = scheduled_loan_terms(
            input_principal,
            input_rate,
            input_term,
            input_interest_type,
        )


        st.session_state.loan_config = {
            "principal":
                float(
                    input_principal
                ),

            "initial_rate":
                float(
                    input_rate
                ),

            "initial_term":
                int(
                    input_term
                ),

            "interest_type":
                input_interest_type,

            "initial_payment":
                float(
                    initial_payment
                ),
        }


        st.session_state.loan_ready = (
            True
        )


        st.session_state.sim_payment = (
            float(
                initial_payment
            )
        )


        st.session_state.sim_rate = (
            float(
                input_rate
            )
        )


        st.session_state.sim_term = (
            int(
                input_term
            )
        )


        st.session_state.simulation_count += (
            1
        )


        st.toast(
            "Loan simulation initialized.",
            icon="🏦",
        )


    # ------------------------------------------------------------
    # BEFORE CALCULATION
    # ------------------------------------------------------------

    if not st.session_state.loan_ready:

        st.html(
            """
            <div class="simulation-note">
                Enter the loan details above and press
                <b>Calculate Loan</b> to initialize the
                live payment simulation.
            </div>
            """
        )


    # ------------------------------------------------------------
    # LOAN SIMULATION RESULTS
    # ------------------------------------------------------------

    else:

        config = (
            st.session_state.loan_config
        )


        principal = (
            config["principal"]
        )


        interest_type = (
            config["interest_type"]
        )


        initial_payment = (
            config["initial_payment"]
        )


        # --------------------------------------------------------
        # Current slider values already exist in session state
        # BEFORE widgets render, allowing metrics above sliders
        # to update immediately.
        # --------------------------------------------------------

        sim_payment = float(
            st.session_state.get(
                "sim_payment",
                initial_payment,
            )
        )


        sim_rate = float(
            st.session_state.get(
                "sim_rate",
                config["initial_rate"],
            )
        )


        sim_term = int(
            st.session_state.get(
                "sim_term",
                config["initial_term"],
            )
        )


        target_months = (
            sim_term
            * 12
        )


        (
            scheduled_payment,
            scheduled_interest,
            scheduled_repayment,
        ) = scheduled_loan_terms(
            principal,
            sim_rate,
            sim_term,
            interest_type,
        )


        (
            actual_schedule,
            paid_off,
        ) = simulate_loan_payment(
            principal,
            sim_rate,
            sim_payment,
            interest_type,
        )


        actual_months = (
            len(
                actual_schedule
            )
        )


        total_interest = float(
            actual_schedule[
                "Interest"
            ].sum()
        )


        total_repayment = float(
            actual_schedule[
                "Payment"
            ].sum()
        )


        interest_difference = (
            total_interest
            - scheduled_interest
        )


        # --------------------------------------------------------
        # PAYMENT BEHAVIOUR
        # --------------------------------------------------------

        if not paid_off:

            payment_status = (
                "LATE PAY"
            )

            status_icon = (
                "●"
            )

            status_color = (
                "#FF4D67"
            )

            month_difference = (
                actual_months
                - target_months
            )


        else:

            month_difference = (
                actual_months
                - target_months
            )


            if (
                abs(
                    month_difference
                )
                <= 1
            ):

                payment_status = (
                    "ON TIME"
                )

                status_icon = (
                    "●"
                )

                status_color = (
                    "#2F80FF"
                )


            elif month_difference < 0:

                payment_status = (
                    "EARLY PAY"
                )

                status_icon = (
                    "●"
                )

                status_color = (
                    "#24C875"
                )


            else:

                payment_status = (
                    "LATE PAY"
                )

                status_icon = (
                    "●"
                )

                status_color = (
                    "#FF4D67"
                )


        status_light = (
            blend_with_white(
                status_color,
                .38
            )
        )


        # --------------------------------------------------------
        # LOAN PAGE DYNAMIC THEME
        # --------------------------------------------------------

        st.html(
            f"""
            <style>

            :root {{
                --loan-accent:
                    {status_color};
            }}


            [data-testid="stMetric"] {{
                border-top:
                    2px solid
                    var(--loan-accent)
                    !important;
            }}


            div[data-testid="stSlider"]
            div[role="slider"] {{

                background:
                    var(--loan-accent)
                    !important;

                border-color:
                    var(--loan-accent)
                    !important;
            }}


            .loan-status-card {{

                background:
                    linear-gradient(
                        135deg,
                        {rgba(status_color, .17)},
                        transparent
                    ),
                    {THEME["panel"]};

                border:
                    1px solid
                    {rgba(status_color, .55)};

                border-left:
                    5px solid
                    {status_color};

                border-radius:
                    20px;

                padding:
                    22px 24px;

                margin:
                    17px 0 18px 0;
            }}


            .loan-status-top {{

                display:
                    flex;

                align-items:
                    center;

                gap:
                    10px;

                color:
                    {status_color};

                font-size:
                    .8rem;

                letter-spacing:
                    1.7px;

                font-weight:
                    800;
            }}


            .loan-status-main {{

                margin-top:
                    6px;

                font-size:
                    2.2rem;

                line-height:
                    1.05;

                font-weight:
                    900;

                color:
                    {THEME["text"]};
            }}


            .loan-status-grid {{

                margin-top:
                    18px;

                display:
                    grid;

                grid-template-columns:
                    repeat(
                        3,
                        minmax(
                            0,
                            1fr
                        )
                    );

                gap:
                    12px;
            }}


            .loan-status-stat {{

                background:
                    {THEME["panel_soft"]};

                border:
                    1px solid
                    {THEME["border"]};

                border-radius:
                    13px;

                padding:
                    13px;
            }}


            .loan-status-stat small {{

                color:
                    {THEME["muted"]};

                display:
                    block;

                margin-bottom:
                    4px;
            }}


            .loan-status-stat b {{

                color:
                    {THEME["text"]};
            }}


            @media (
                max-width: 800px
            ) {{

                .loan-status-grid {{

                    grid-template-columns:
                        1fr;
                }}
            }}

            </style>
            """
        )


        # --------------------------------------------------------
        # EFFECTIVE RATE
        # --------------------------------------------------------

        if paid_off:

            effective_rate = (
                effective_annual_rate(
                    principal,
                    actual_schedule[
                        "Payment"
                    ].tolist(),
                )
            )

        else:

            effective_rate = (
                None
            )


        # --------------------------------------------------------
        # METRICS
        # --------------------------------------------------------

        m1, m2, m3, m4 = st.columns(
            4
        )


        m1.metric(
            "Monthly Payment",
            money(
                sim_payment
            ),
            delta=(
                f"{money(sim_payment - scheduled_payment)} "
                f"vs scheduled"
            ),
        )


        m2.metric(
            "Total Interest",
            money(
                total_interest
            ),
            delta=(
                f"{money(interest_difference)} "
                f"vs scheduled"
            ),
            delta_color=(
                "inverse"
            ),
        )


        m3.metric(
            "Total Repayment",
            money(
                total_repayment
            ),
        )


        m4.metric(
            "Estimated Effective Annual Rate",
            (
                f"{effective_rate:.2f}%"
                if effective_rate
                is not None
                else "N/A"
            ),
        )


        # --------------------------------------------------------
        # STATUS DETAILS
        # --------------------------------------------------------

        if payment_status == "ON TIME":

            timing_description = (
                "Matches the selected repayment term"
            )


        elif payment_status == "EARLY PAY":

            timing_description = (
                f"{format_duration(month_difference)} early"
            )


        elif paid_off:

            timing_description = (
                f"{format_duration(month_difference)} late"
            )


        else:

            timing_description = (
                f"Not fully repaid within "
                f"{actual_months} simulated months"
            )


        if abs(
            interest_difference
        ) < .01:

            interest_description = (
                f"{money(0)} difference"
            )


        elif interest_difference < 0:

            interest_description = (
                f"{money(abs(interest_difference))} "
                f"less interest"
            )


        else:

            interest_description = (
                f"{money(interest_difference)} "
                f"more interest"
            )


        payoff_text = (
            f"{actual_months} months "
            f"({actual_months / 12:.2f} years)"

            if paid_off

            else f"{actual_months}+ months"
        )


        st.html(
            f"""
            <div class="loan-status-card">

                <div class="loan-status-top">

                    <span>
                        {status_icon}
                    </span>

                    PAYMENT BEHAVIOUR

                </div>


                <div class="loan-status-main">
                    {payment_status}
                </div>


                <div class="loan-status-grid">


                    <div class="loan-status-stat">

                        <small>
                            Timing
                        </small>

                        <b>
                            {timing_description}
                        </b>

                    </div>


                    <div class="loan-status-stat">

                        <small>
                            Simulated Payoff
                        </small>

                        <b>
                            {payoff_text}
                        </b>

                    </div>


                    <div class="loan-status-stat">

                        <small>
                            Interest Difference
                        </small>

                        <b style="
                            color:{status_color};
                        ">
                            {interest_description}
                        </b>

                    </div>


                </div>

            </div>
            """
        )


        # --------------------------------------------------------
        # LIVE CONTROLS
        # --------------------------------------------------------

        st.subheader(
            "Live Payment Controls"
        )


        st.caption(
            "Move any slider and the metrics, status, "
            "repayment duration and graphs update instantly."
        )


        s1, s2, s3 = st.columns(
            3
        )


        with s1:

            st.slider(
                "Monthly Payment",
                min_value=
                    1.0,

                max_value=
                    float(
                        initial_payment
                        + 1000
                    ),

                step=
                    1.0,

                key=
                    "sim_payment",

                format=
                    f"{st.session_state.currency} %.2f",
            )


        with s2:

            st.slider(
                "Annual Interest Rate",
                min_value=
                    1.0,

                max_value=
                    100.0,

                step=
                    .1,

                key=
                    "sim_rate",

                format=
                    "%.1f%%",
            )


        with s3:

            st.slider(
                "Loan Term",
                min_value=
                    1,

                max_value=
                    40,

                step=
                    1,

                key=
                    "sim_term",

                format=
                    "%d years",
            )


        # --------------------------------------------------------
        # GRAPH RESULTS
        # --------------------------------------------------------

        st.divider()


        section_header(
            "VISUAL ANALYSIS",
            "Graph Results"
        )


        # --------------------------------------------------------
        # FULL-WIDTH BALANCE GRAPH
        # --------------------------------------------------------

        balance_fig = go.Figure()


        balance_fig.add_trace(
            go.Scatter(

                x=
                    actual_schedule[
                        "Month"
                    ],

                y=
                    actual_schedule[
                        "Closing Balance"
                    ],

                mode=
                    "lines",

                fill=
                    "tozeroy",

                name=
                    "Remaining Balance",

                line=dict(
                    width=
                        3,

                    color=
                        status_color,
                ),

                fillcolor=
                    rgba(
                        status_color,
                        .20
                    ),

                hovertemplate=(
                    "Month %{x}"
                    "<br>"
                    "Balance: "
                    + st.session_state.currency
                    + "%{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )


        # Scheduled target term marker
        balance_fig.add_vline(

            x=
                target_months,

            line_dash=
                "dash",

            line_color=
                status_light,

            annotation_text=
                "Target term",

            annotation_position=
                "top",
        )


        style_plot(
            balance_fig,
            height=470,
        )


        balance_fig.update_xaxes(
            title=
                "Month"
        )


        balance_fig.update_yaxes(
            title=
                f"Balance "
                f"({st.session_state.currency})"
        )


        st.plotly_chart(
            balance_fig,
            use_container_width=True,
        )


        # --------------------------------------------------------
        # EARLY/LATE COMPARISON SCENARIOS
        # --------------------------------------------------------

        early_payment = (
            scheduled_payment
            * 1.20
        )


        late_payment = (
            scheduled_payment
            * .80
        )


        # Ensure the late scenario still has a chance to amortize
        monthly_rate = (
            sim_rate
            / 100
            / 12
        )


        if (
            interest_type
            == "Flat Interest"
        ):

            minimum_interest_cover = (
                principal
                * monthly_rate
                + 1
            )

        else:

            minimum_interest_cover = (
                principal
                * monthly_rate
                + 1
            )


        late_payment = max(
            late_payment,
            minimum_interest_cover,
        )


        (
            early_schedule,
            early_paid,
        ) = simulate_loan_payment(
            principal,
            sim_rate,
            early_payment,
            interest_type,
        )


        (
            late_schedule,
            late_paid,
        ) = simulate_loan_payment(
            principal,
            sim_rate,
            late_payment,
            interest_type,
        )


        early_interest = float(
            early_schedule[
                "Interest"
            ].sum()
        )


        late_interest = float(
            late_schedule[
                "Interest"
            ].sum()
        )


        g1, g2 = st.columns(
            2
        )


        # --------------------------------------------------------
        # PIE CHART
        # --------------------------------------------------------

        with g1:

            st.markdown(
                "#### Principal vs Interest"
            )


            pie_fig = go.Figure(
                go.Pie(

                    labels=[
                        "Principal",
                        "Interest",
                    ],

                    values=[
                        principal,
                        total_interest,
                    ],

                    hole=
                        .67,

                    marker=dict(
                        colors=[
                            status_color,
                            status_light,
                        ]
                    ),

                    textinfo=
                        "label+percent",
                )
            )


            pie_fig.update_layout(

                height=
                    420,

                paper_bgcolor=
                    THEME["plot"],

                font=dict(
                    color=
                        THEME["text"]
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=30,
                    b=30,
                ),

                showlegend=
                    False,

                annotations=[
                    dict(
                        text=
                            "Payment<br>Composition",

                        x=
                            .5,

                        y=
                            .5,

                        showarrow=
                            False,

                        font=dict(
                            size=
                                16,

                            color=
                                THEME[
                                    "text"
                                ],
                        ),
                    )
                ],
            )


            st.plotly_chart(
                pie_fig,
                use_container_width=True,
            )


        # --------------------------------------------------------
        # INTEREST COMPARISON BAR CHART
        # --------------------------------------------------------

        with g2:

            st.markdown(
                "#### Early vs Late Interest"
            )


            bar_fig = go.Figure(
                go.Bar(

                    x=[
                        "Early Payment",
                        "Late Payment",
                    ],

                    y=[
                        early_interest,
                        late_interest,
                    ],

                    marker=dict(
                        color=[
                            status_color,
                            status_light,
                        ]
                    ),

                    text=[
                        money(
                            early_interest
                        ),
                        money(
                            late_interest
                        ),
                    ],

                    textposition=
                        "outside",

                    hovertemplate=(
                        "%{x}"
                        "<br>"
                        "Total interest: "
                        + st.session_state.currency
                        + "%{y:,.2f}"
                        "<extra></extra>"
                    ),
                )
            )


            style_plot(
                bar_fig,
                height=420,
                legend=False,
            )


            bar_fig.update_yaxes(
                title=
                    f"Total Interest "
                    f"({st.session_state.currency})"
            )


            st.plotly_chart(
                bar_fig,
                use_container_width=True,
            )


            st.caption(
                "Early scenario uses 120% of the scheduled "
                "payment. Late scenario uses approximately "
                "80% while remaining above the initial "
                "interest charge."
            )


        # --------------------------------------------------------
        # AMORTIZATION DROPDOWN
        # --------------------------------------------------------

        with st.expander(
            "📊 Amortization Details",
            expanded=False,
        ):

            st.subheader(
                "Payment Breakdown"
            )


            amort_fig = go.Figure()


            amort_fig.add_trace(
                go.Bar(

                    x=
                        actual_schedule[
                            "Month"
                        ],

                    y=
                        actual_schedule[
                            "Principal"
                        ],

                    name=
                        "Principal",

                    marker_color=
                        status_color,
                )
            )


            amort_fig.add_trace(
                go.Bar(

                    x=
                        actual_schedule[
                            "Month"
                        ],

                    y=
                        actual_schedule[
                            "Interest"
                        ],

                    name=
                        "Interest",

                    marker_color=
                        status_light,
                )
            )


            amort_fig.update_layout(
                barmode=
                    "stack"
            )


            style_plot(
                amort_fig,
                height=430,
            )


            amort_fig.update_xaxes(
                title=
                    "Month"
            )


            amort_fig.update_yaxes(
                title=
                    f"Payment "
                    f"({st.session_state.currency})"
            )


            st.plotly_chart(
                amort_fig,
                use_container_width=True,
            )


            amortization_table = (
                actual_schedule.copy()
            )


            for column in [
                "Opening Balance",
                "Payment",
                "Principal",
                "Interest",
                "Closing Balance",
                "Cumulative Interest",
            ]:

                amortization_table[
                    column
                ] = (
                    amortization_table[
                        column
                    ]
                    .round(
                        2
                    )
                )


            st.dataframe(
                amortization_table,
                use_container_width=True,
                hide_index=True,
            )


            st.download_button(
                "⬇ Download Amortization Schedule",

                data=(
                    amortization_table

                    .to_csv(
                        index=False
                    )

                    .encode(
                        "utf-8"
                    )
                ),

                file_name=
                    "lumen_loan_amortization.csv",

                mime=
                    "text/csv",
            )


# ================================================================
# CREDIT CARD SIMULATOR
# ================================================================

elif page == "Credit Card Simulator":

    section_header(
        "CREDIT CARD SIMULATOR",
        "Model the balance behind the card."
    )


    st.write(
        """
        Adjust card balance, APR, monthly spending and payment
        behaviour to simulate how a revolving balance changes
        over time.
        """
    )


    with st.form(
        "credit_card_form"
    ):

        c1, c2, c3 = st.columns(
            3
        )


        with c1:

            card_balance = st.number_input(
                "Current card balance",
                min_value=0.0,
                value=8000.0,
                step=100.0,
            )


            card_apr = st.number_input(
                "APR (%)",
                min_value=0.0,
                max_value=100.0,
                value=18.0,
                step=.1,
            )


        with c2:

            new_spending = st.number_input(
                "New monthly spending",
                min_value=0.0,
                value=0.0,
                step=50.0,
            )


            card_strategy = st.selectbox(
                "Payment strategy",
                [
                    "Minimum Payment",
                    "Fixed Payment",
                    "Full Balance",
                ],
            )


        with c3:

            min_percent = st.number_input(
                "Minimum payment (%)",
                min_value=.1,
                max_value=100.0,
                value=5.0,
                step=.5,
            )


            min_floor = st.number_input(
                "Minimum payment floor",
                min_value=0.0,
                value=50.0,
                step=10.0,
            )


        fixed_card_payment = st.number_input(
            "Fixed monthly payment",
            min_value=0.0,
            value=500.0,
            step=50.0,
            disabled=(
                card_strategy
                != "Fixed Payment"
            ),
        )


        run_card = (
            st.form_submit_button(
                "Run Credit Card Simulation",
                use_container_width=True,
            )
        )


    if run_card:

        st.session_state.simulation_count += (
            1
        )


        st.toast(
            "Credit-card simulation updated.",
            icon="💳",
        )


    (
        card_df,
        card_paid_off,
    ) = credit_card_schedule(
        card_balance,
        card_apr,
        new_spending,
        card_strategy,
        min_percent,
        min_floor,
        fixed_card_payment,
    )


    total_card_interest = float(
        card_df[
            "Interest"
        ].sum()
    )


    total_card_payments = float(
        card_df[
            "Payment"
        ].sum()
    )


    ending_balance = float(
        card_df.iloc[-1][
            "Closing Balance"
        ]
        if len(card_df)
        else 0
    )


    c1, c2, c3, c4 = st.columns(
        4
    )


    c1.metric(
        "Months Simulated",
        len(
            card_df
        ),
    )


    c2.metric(
        "Total Interest",
        money(
            total_card_interest
        ),
    )


    c3.metric(
        "Total Payments",
        money(
            total_card_payments
        ),
    )


    c4.metric(
        "Ending Balance",
        money(
            ending_balance
        ),
    )


    if (
        card_paid_off
        and new_spending == 0
    ):

        st.success(
            f"Balance reaches zero after approximately "
            f"{len(card_df)} months."
        )


    elif (
        not card_paid_off
        and new_spending == 0
    ):

        st.warning(
            "The balance does not reach zero within the "
            "30-year simulation horizon."
        )


    else:

        st.info(
            "Ongoing purchases are enabled, so this simulation "
            "models a revolving balance rather than a fixed "
            "one-time payoff."
        )


    card_fig = go.Figure()


    card_fig.add_trace(
        go.Scatter(

            x=
                card_df[
                    "Month"
                ],

            y=
                card_df[
                    "Closing Balance"
                ],

            mode=
                "lines",

            fill=
                "tozeroy",

            name=
                "Card Balance",

            line=dict(
                color=
                    ACCENT,

                width=
                    3,
            ),

            fillcolor=
                rgba(
                    ACCENT,
                    .18
                ),
        )
    )


    card_fig.add_trace(
        go.Scatter(

            x=
                card_df[
                    "Month"
                ],

            y=
                card_df[
                    "Cumulative Interest"
                ],

            mode=
                "lines",

            name=
                "Cumulative Interest",

            line=dict(
                width=
                    2,

                dash=
                    "dot",
            ),
        )
    )


    style_plot(
        card_fig,
        height=460,
    )


    card_fig.update_xaxes(
        title=
            "Month"
    )


    card_fig.update_yaxes(
        title=
            st.session_state.currency
    )


    st.plotly_chart(
        card_fig,
        use_container_width=True,
    )


    with st.expander(
        "📋 Credit Card Simulation Table"
    ):

        card_table = (
            card_df.round(
                2
            )
        )


        st.dataframe(
            card_table,
            use_container_width=True,
            hide_index=True,
        )


        st.download_button(
            "⬇ Download Card Simulation",

            data=(
                card_table
                .to_csv(
                    index=False
                )
                .encode(
                    "utf-8"
                )
            ),

            file_name=
                "lumen_credit_card_simulation.csv",

            mime=
                "text/csv",
        )


# ================================================================
# DEBT PLANNER
# ================================================================

elif page == "Debt Planner":

    section_header(
        "DEBT PLANNER",
        "Turn multiple balances into one repayment plan."
    )


    st.write(
        """
        Enter multiple debts and compare repayment behaviour
        under Avalanche and Snowball allocation strategies.
        """
    )


    default_debts = pd.DataFrame(
        {
            "Debt": [
                "Credit Card",
                "Personal Loan",
                "Study Loan",
            ],

            "Balance": [
                6500.0,
                12000.0,
                8000.0,
            ],

            "APR %": [
                18.0,
                8.0,
                4.0,
            ],

            "Minimum Payment": [
                250.0,
                300.0,
                120.0,
            ],
        }
    )


    uploaded_debts = st.file_uploader(
        "Upload debt CSV (optional)",
        type=[
            "csv"
        ],
    )


    if uploaded_debts is not None:

        try:

            uploaded_df = pd.read_csv(
                uploaded_debts
            )


            required_columns = {
                "Debt",
                "Balance",
                "APR %",
                "Minimum Payment",
            }


            if required_columns.issubset(
                uploaded_df.columns
            ):

                default_debts = (
                    uploaded_df[
                        [
                            "Debt",
                            "Balance",
                            "APR %",
                            "Minimum Payment",
                        ]
                    ]
                )

            else:

                st.warning(
                    "The uploaded CSV does not contain all "
                    "required columns."
                )


        except Exception:

            st.error(
                "Unable to read the uploaded CSV."
            )


    debt_data = st.data_editor(
        default_debts,
        num_rows=
            "dynamic",
        use_container_width=
            True,
        hide_index=
            True,
        column_config={

            "Balance":
                st.column_config.NumberColumn(
                    "Balance",
                    min_value=0.0,
                    format="%.2f",
                ),

            "APR %":
                st.column_config.NumberColumn(
                    "APR %",
                    min_value=0.0,
                    max_value=100.0,
                    format="%.2f",
                ),

            "Minimum Payment":
                st.column_config.NumberColumn(
                    "Minimum Payment",
                    min_value=0.0,
                    format="%.2f",
                ),
        },
    )


    minimum_required = float(
        debt_data[
            "Minimum Payment"
        ].sum()
    )


    total_debt = float(
        debt_data[
            "Balance"
        ].sum()
    )


    d1, d2, d3 = st.columns(
        3
    )


    with d1:

        debt_strategy = st.radio(
            "Repayment strategy",
            [
                "Debt Avalanche",
                "Debt Snowball",
            ],
        )


    with d2:

        debt_budget = st.number_input(
            "Monthly repayment budget",
            min_value=0.0,
            value=float(
                minimum_required
                + 500
            ),
            step=50.0,
        )


    with d3:

        st.metric(
            "Total Debt",
            money(
                total_debt
            ),
        )


        st.metric(
            "Combined Minimum",
            money(
                minimum_required
            ),
        )


    if (
        debt_budget
        < minimum_required
    ):

        st.error(
            "Monthly budget is below the combined minimum "
            "payments."
        )


    else:

        (
            debt_history,
            payoff_table,
            debt_interest,
            debt_paid_off,
        ) = debt_payoff_simulation(
            debt_data,
            debt_budget,
            debt_strategy,
        )


        m1, m2, m3 = st.columns(
            3
        )


        m1.metric(
            "Estimated Payoff",
            (
                f"{len(debt_history)} months"

                if debt_paid_off

                else "600+ months"
            ),
        )


        m2.metric(
            "Simulated Interest",
            money(
                debt_interest
            ),
        )


        m3.metric(
            "Monthly Budget",
            money(
                debt_budget
            ),
        )


        debt_fig = go.Figure()


        debt_fig.add_trace(
            go.Scatter(

                x=
                    debt_history[
                        "Month"
                    ],

                y=
                    debt_history[
                        "Total Balance"
                    ],

                mode=
                    "lines",

                fill=
                    "tozeroy",

                line=dict(
                    color=
                        ACCENT,

                    width=
                        3,
                ),

                fillcolor=
                    rgba(
                        ACCENT,
                        .18
                    ),

                name=
                    "Total Debt",
            )
        )


        style_plot(
            debt_fig,
            height=450,
        )


        debt_fig.update_xaxes(
            title=
                "Month"
        )


        debt_fig.update_yaxes(
            title=
                f"Debt "
                f"({st.session_state.currency})"
        )


        st.plotly_chart(
            debt_fig,
            use_container_width=True,
        )


        with st.expander(
            "📍 Payoff Milestones"
        ):

            st.dataframe(
                payoff_table,
                use_container_width=True,
                hide_index=True,
            )


        st.subheader(
            "Avalanche vs Snowball"
        )


        (
            avalanche_history,
            _,
            avalanche_interest,
            avalanche_paid,
        ) = debt_payoff_simulation(
            debt_data,
            debt_budget,
            "Debt Avalanche",
        )


        (
            snowball_history,
            _,
            snowball_interest,
            snowball_paid,
        ) = debt_payoff_simulation(
            debt_data,
            debt_budget,
            "Debt Snowball",
        )


        comparison = pd.DataFrame(
            {
                "Strategy": [
                    "Debt Avalanche",
                    "Debt Snowball",
                ],

                "Payoff Months": [
                    len(
                        avalanche_history
                    ),
                    len(
                        snowball_history
                    ),
                ],

                "Total Interest": [
                    round(
                        avalanche_interest,
                        2
                    ),
                    round(
                        snowball_interest,
                        2
                    ),
                ],

                "Paid Within Horizon": [
                    avalanche_paid,
                    snowball_paid,
                ],
            }
        )


        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True,
        )


# ================================================================
# FINANCE ASSISTANT
# ================================================================

elif page == "Finance Assistant":

    section_header(
        "FINANCE ASSISTANT",
        "Ask about the simulation mechanics."
    )


    st.write(
        """
        Ask about loans, flat interest, reducing balances,
        early payments, APR, credit cards or debt strategies.
        """
    )


    if not st.session_state.chat_history:

        st.session_state.chat_history = [
            {
                "role":
                    "assistant",

                "content":
                    (
                        "Hi. Ask me something such as "
                        "'What happens if I increase my loan "
                        "payment?', 'What is flat interest?' "
                        "or 'How does Debt Avalanche work?'"
                    ),
            }
        ]


    for message in (
        st.session_state.chat_history
    ):

        with st.chat_message(
            message[
                "role"
            ]
        ):

            st.write(
                message[
                    "content"
                ]
            )


    user_prompt = st.chat_input(
        "Ask about a finance simulation..."
    )


    if user_prompt:

        st.session_state.chat_history.append(
            {
                "role":
                    "user",

                "content":
                    user_prompt,
            }
        )


        with st.chat_message(
            "user"
        ):

            st.write(
                user_prompt
            )


        answer = finance_assistant_reply(
            user_prompt
        )


        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Calculating response..."
            ):

                time.sleep(
                    .20
                )


            st.write(
                answer
            )


        st.session_state.chat_history.append(
            {
                "role":
                    "assistant",

                "content":
                    answer,
            }
        )


    st.divider()


    if st.button(
        "Clear Conversation"
    ):

        st.session_state.chat_history = (
            []
        )

        st.rerun()


# ================================================================
# FOOTER
# ================================================================

st.html(
    f"""
    <div class="footer">

        LUMEN FINANCE SIMULATION SUITE

        &nbsp;•&nbsp;

        Simulations this session:
        {st.session_state.simulation_count}

        <br><br>

        Simulation outputs are estimates and can vary
        from product-specific calculations.

    </div>
    """
)