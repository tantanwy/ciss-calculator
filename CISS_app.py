from shiny import App, reactive, render, ui, run_app
from typing import List

app_ui = ui.page_fluid(
    ui.tags.style(),
    ui.h2("Cognitive Impairment Scoring System (CISS) Calculator"),
    ui.layout_sidebar(
        # Side Bar object
        ui.sidebar(
            ui.h3("I. Patient Characteristics"),
            ui.input_radio_buttons(
                "sex", "Gender", choices=["Female", "Male"], selected="Female"
            ),
            ui.input_slider(
                "age", "Age", min=45, max=115, value=65, step=1, ticks=True
            ),
            ui.input_select(
                "race",
                "Ethnicity",
                {"0": "Chinese", "1": "Malay", "2": "Indian", "3": "Others"},
            ),
            ui.input_select(
                "edu",
                "Education (years)",
                {
                    "0": "No formal education",
                    "1": "Primary (1-6 years)",
                    "2": "Secondary (7-12 years)",
                    "3": "Tertiary (>12 years)",
                },
            ),
            # BMI: 10–60, default 21, step 1 (adjust step if needed)
            ui.input_slider(
                "bmi",
                "Body mass index (BMI) kg/m2",
                min=10,
                max=60,
                value=21,
                step=1,
                ticks=True,
            ),
            ui.input_radio_buttons(
                "smoke", "Smoking", choices=["Current/Ever", "Never"], selected="Never"
            ),
            ui.input_select(
                "sbp",
                "Blood Pressure Systolic (mmHg)",
                {"0": "< 140", "1": "140 – 160", "2": "> 160"},
            ),
            ui.input_radio_buttons(
                "dm", "Diabetes", choices=["Present", "Absent"], selected="Absent"
            ),
            ui.input_radio_buttons(
                "hld",
                "High cholesterol",
                choices=["Present", "Absent"],
                selected="Absent",
            ),
            ui.input_radio_buttons(
                "stroke", "Have stroke history", choices=["Yes", "No"], selected="No"
            ),
            ui.input_slider(
                "GDS", "GDS score", min=0, max=20, value=0, step=1, ticks=True
            ),
            ui.input_action_button("action_button", "Start"),
            width=400,
            style="background-color:#f5f5f5; border-right:1px solid #e0e0e0; padding:16px;",
        ),

        
        ui.navset_tab(
            ui.nav_panel(
                "Main",
                ui.h2("Calculated CISS Scores"),
                ui.card(
                    ui.row(
                        ui.column(6,
                            ui.h4("Basic Score (Max 100):"),
                            ui.span(
                                ui.output_text("basic_score", inline=True),
                                style="font-size: 24px; color: #1E88E5; font-weight: bold;"
                            )
                        ),
                        ui.column(6,
                            ui.h4("Likelihood of CIND"),
                            ui.span(
                                ui.output_text("prob", inline=True),
                                style="font-size: 24px; color: #D81B60; font-weight: bold;"
                            )
                        )
                    )
                ),
                ui.hr(),
                ui.h3("Score Interpretation"),
                ui.p("The CISS estimate the likelihood of cognitive impairment. A higher score indicates a higher risk."),
                ui.p("Risk categories based on Basic Score:"),
                ui.tags.ul(
                    ui.tags.li("Low risk: Basic Score < 35"),
                    ui.tags.li("Intermediate risk: Basic Score 36–50"),
                    ui.tags.li("High risk: Basic Score > 50"),
                ),
                ui.h3("Clinical action"),
                ui.strong(ui.output_text("clinical_action", inline=True)),
                ui.p(
                    ui.strong("Note:"),
                    " This calculator only serve as a guide for assessing cognitive impairment and and should not be used as a replacement for professional medical evaluation.",
                    style="margin-top: 5rem; font-size: 0.9rem;"
                ),
            ),
        ui.nav_panel(
            "About",
            ui.h2("Introduction"),
            ui.p("TThis calculator computes the likelihood of Cognitive Impairment for the general population based on 11 factors."),
            ui.h2("Instructions"),
            ui.tags.ol(
                ui.tags.li("Enter information at left side bar"),
                ui.tags.li("Click Start to compute the score"),
                ui.tags.li("Gather scores, interpret and check clincal action"),
                ),
            ui.p(
                ui.strong("Source:"),
                " Tan et al. A point-based cognitive impairment scoring system for southeast Asian adults. ",
                "JPAD. 2025 Apr 1;12(4):100069. ",
                ui.a("https://doi.org/10.1016/j.tjpad.2025.100069", href="https://doi.org/10.1016/j.tjpad.2025.100069"),
                style="margin-top: 10rem; font-size: 0.7rem;"
            ),)
        )
    )  # <-- closes ui.layout_sidebar
)    # <-- closes ui.page_fluid

# --- Server Logic Definition ---


def server(input, output, session):
    from shiny import reactive, render

    # Reactive expression to calculate the CISS scores
    @reactive.Calc
    @reactive.event(input.action_button)  # run only when Start is clicked
    def calculate_ciss():
        basic_score = 0

        # Age
        age = input.age()
        if 60 <= age <= 75:
            basic_score += 9
        elif age > 75:
            basic_score += 15

        # Sex
        if input.sex() == "Female":
            basic_score += 3

        # Ethnicity (non-Chinese)
        if input.race() != "0":
            basic_score += 10

        # BMI
        bmi = float(input.bmi())
        if bmi < 18.5:
            basic_score += 11
        elif bmi <= 30:
            basic_score += 0
        else:  # >30
            basic_score += 6

        # Education
        edu = input.edu()
        if edu in ("0", "1"):  # ≤6 years
            basic_score += 12
        elif edu == "2":  # 7–12 years
            basic_score += 4
        # Else (e.g., "3" tertiary >12 years): 0 points

        # SBP categories: "0" <140, "1" 140–160, "2" >160
        sbp_cat = input.sbp()
        if sbp_cat == "1":
            basic_score += 4
        elif sbp_cat == "2":
            basic_score += 11

        if input.smoke() == "Current/Former":
            basic_score += 5

        if input.dm() == "Present":
            basic_score += 8
        if input.hld() == "Present":
            basic_score += 7
        if input.stroke() == "Yes":
            basic_score += 9

        gds = input.GDS()
        if gds > 0:
            basic_score += 9

        return {"basic": basic_score}

    # Output the Basic Score
    @output
    @render.text
    def basic_score():
        return str(calculate_ciss()["basic"])

    @output
    @render.text
    def clinical_action():
        score = calculate_ciss()["basic"]
        if score < 35:
            return "To follow-up in 12 months"
        elif score > 50:
            return "To be referred to specialist clinic"
        else:
            return "To encourage lifestyle modification and follow-up in 6 months"

    @output
    @render.text
    def prob():
        score = calculate_ciss()["basic"]
    
        if 0 <= score <= 4:
            return "6%"
        elif 5 <= score <= 10:
            return "8%"
        elif 10 < score <= 14:  # 10 maps to 8% per previous range
            return "13%"
        elif 15 <= score <= 19:
            return "19%"
        elif 20 <= score <= 24:
            return "28%"
        elif 25 <= score <= 29:
            return "38%"
        elif 30 <= score <= 34:
            return "50%"
        elif 35 <= score <= 39:
            return "61%"
        elif 40 <= score <= 44:
            return "72%"
        elif 45 <= score <= 49:
            return "80%"
        elif 50 <= score <= 54:
            return "87%"
        elif score >= 55:
            return "> 90%"
        else:
            return "N/A"

app = App(app_ui, server)
