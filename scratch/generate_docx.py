import os
import sys
import subprocess

# Secure python-docx dependency check
try:
    import docx
except ImportError:
    print("Installing python-docx library dynamically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_element(name):
    return OxmlElement(name)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set explicit cell margins (padding) in twentieths of a point (dxa)"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    """Set background color of a cell using hex value"""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def add_heading_styled(doc, text, level):
    heading = doc.add_paragraph()
    heading.paragraph_format.space_before = Pt(12)
    heading.paragraph_format.space_after = Pt(6)
    heading_run = heading.add_run(text)
    heading_run.font.name = 'Times New Roman'
    heading_run.bold = True
    
    if level == 1:
        heading_run.font.size = Pt(14)
        heading_run.font.color.rgb = RGBColor(15, 23, 42) # Slate Grey
    elif level == 2:
        heading_run.font.size = Pt(13)
        heading_run.font.color.rgb = RGBColor(15, 23, 42)
    else:
        heading_run.font.size = Pt(12)
        heading_run.font.color.rgb = RGBColor(71, 85, 105)
    return heading

def main():
    doc = Document()
    
    # Page setup - Standard Capstone margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Set default styles to Times New Roman
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.space_after = Pt(6)
    
    # ------------------ TITLE ------------------
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(24)
    title_run = title_p.add_run("CHAPTER III: TECHNICAL BACKGROUND")
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(16)
    title_run.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    
    intro_p = doc.add_paragraph(
        "This chapter presents the technical background, architectural framework, development stack, and "
        "operational workflows of the \"Smart Flight Booking Simulation Platform for CTHM-CSUCC.\" It details "
        "the technical complexities solved, the software and hardware components utilized, and the sequential "
        "logic driving the simulation platform."
    )
    
    # ------------------ 3.1 ------------------
    add_heading_styled(doc, "3.1 Technicality of the Project", 1)
    
    doc.add_paragraph(
        "The \"Smart Flight Booking Simulation Platform for CTHM-CSUCC\" is not merely a static booking web interface; "
        "it is a highly decoupled, data-driven, and authoritative educational system. It solves complex software engineering "
        "challenges to replicate commercial Passenger Service Systems (PSS) and Departure Control Systems (DCS). The core "
        "technical complexities addressed by the platform are detailed below."
    )
    
    # 3.1.1
    add_heading_styled(doc, "3.1.1 Decoupled Single-Page Application (SPA) Architectural Paradigm", 2)
    doc.add_paragraph(
        "The project is built on a Decoupled Single Page Application (SPA) architecture. The presentation layer (frontend) "
        "is fully separated from the business logic and persistence layers (backend), communicating exclusively through asynchronous "
        "API boundaries. The system operates on three discrete layers:"
    )
    
    # Bullet points for 3.1.1
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Presentation Tier: ")
    r.bold = True
    p.add_run("A compiled, static Vue 3 application executing entirely within the client's browser environment.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Application Tier: ")
    r.bold = True
    p.add_run("A Django REST Framework API that exposes stateless endpoints for search, booking, authentication, and grading operations.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Integration Boundary: ")
    r.bold = True
    p.add_run("All communication is performed asynchronously using Axios. The frontend implements interceptors that intercept every outgoing HTTP request to inject JSON Web Token (JWT) authorization headers (Bearer <token>) and intercept incoming responses to gracefully handle token expiration or API exceptions.")

    # 3.1.2
    add_heading_styled(doc, "3.1.2 Centralized Reactive State Machine & Session Persistence", 2)
    doc.add_paragraph(
        "Replicating a multi-step airline booking flow (Search -> Flight Selection -> Passenger Forms -> Add-ons -> Seat Selection -> Review -> Payment) "
        "requires managing a complex state across various routes. The platform resolves this through a multi-tier state persistence engine:"
    )
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Centralized Client State (Pinia): ")
    r.bold = True
    p.add_run("A centralized state management library (bookingStore.js) is used as the frontend \"single source of truth.\" It maintains responsive data variables representing selected flights, traveler credentials, seat assignments, and supplementary ancillaries.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Local Dynamic Sync (LocalStorage): ")
    r.bold = True
    p.add_run("To protect students against browser crashes, network drops, or accidental page refreshes, the Pinia state is dynamically synchronized with the browser's localStorage via custom store-subscription middleware.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Session Snapshot Recovery Engine (snapshotToServer()): ")
    r.bold = True
    p.add_run("A background sync engine periodically pushes JSON representations of the student's active booking progress to the backend database. This allows students to pause their activity in the computer lab and resume it from another terminal without losing their progress.")

    # 3.1.3
    add_heading_styled(doc, "3.1.3 Hybrid Predictive-Dynamic Pricing Engine (XGBoost + Business Rules)", 2)
    doc.add_paragraph(
        "To provide students with a realistic industry experience, the platform calculates fares in real time using a two-stage hybrid calculation "
        "combining machine learning predictions with rule-based airline business overlays."
    )
    
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq1 = p_eq1.add_run("P_base = f( stops, day, month, departure_hour, duration_minutes, Airline, Route )")
    r_eq1.italic = True
    r_eq1.bold = True
    
    doc.add_paragraph(
        "Stage 1 (ML Price Prediction): The backend feeds search variables into a pre-trained XGBoost Regression model (flight_xgb.pkl) trained "
        "on historical flight datasets. Features evaluated include total stops, journey dates, duration, arrival/departure hours, and one-hot "
        "encoded airlines and routes."
    )
    
    doc.add_paragraph(
        "Stage 2 (Dynamic Modifiers): Once the baseline fare is calculated, the system applies sequential modifiers to simulate real market-driven "
        "economics according to the following formula:"
    )
    
    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq2 = p_eq2.add_run("P_final = P_base * F_time * F_urgency * F_demand * F_inventory * F_random")
    r_eq2.italic = True
    r_eq2.bold = True
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Time and Seasonality Modifiers (F_time): ")
    r.bold = True
    p.add_run("Surges are applied during rush hour (1.12), weekends (1.08), peak vacation months (1.20), and specific holiday weeks such as Christmas and the Sinulog Festival (1.30 to 1.60).")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Urgency Modifiers (F_urgency): ")
    r.bold = True
    p.add_run("To penalize last-minute bookings, the system uses an exponential decay curve: F_urgency = 1.0 + 2.80 * e^(-0.10 * d), where d represents days remaining until takeoff. Emergency booking within 3 days incurs up to a +35% surge.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Inventory and Occupancy Modifiers (F_inventory): ")
    r.bold = True
    p.add_run("Seat pricing scales up by +20% as aircraft occupancy exceeds 80%, and decreases by -10% if occupancy is below 20% to simulate demand stimulation.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Psychological Rounding Algorithm: ")
    r.bold = True
    p.add_run("To mirror real-world commercial branding, prices are dynamically rounded to the nearest 500 block minus one (e.g., ₱2,341.50 becomes ₱2,499.00; ₱1,180.20 becomes ₱999.00).")

    # 3.1.4
    add_heading_styled(doc, "3.1.4 Pessimistic Concurrency Control & Row-Level Database Locking", 2)
    doc.add_paragraph(
        "In flight inventory management, preventing double-bookings of identical seat coordinates (e.g., Seat 12A) when multiple users checkout "
        "at the exact same millisecond is critical. The system handles concurrency via a two-tier locking model:"
    )
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Transient Memory Soft-Locks: ")
    r.bold = True
    p.add_run("When a student clicks a seat map coordinate, a transient lock with a 15-minute expiration is placed in the memory cache. This holds the seat while they fill out the passenger forms.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Pessimistic Database Hard-Locks: ")
    r.bold = True
    p.add_run("During final payment confirmation, the transaction executes Django's select_for_update() database lock. This translates to an atomic SELECT ... FOR UPDATE database transaction, locking the PostgreSQL row. Parallel checkout threads are forced to wait, preventing dirty writes and ensuring transaction consistency.")

    # 3.1.5
    add_heading_styled(doc, "3.1.5 Automated Rubric-Based Grading Engine", 2)
    doc.add_paragraph(
        "To replace tedious manual grading, the backend implements an automated grading engine (grading_service.py). The engine is executed upon booking "
        "confirmation, scoring the student out of a master point total defined by the instructor based on five core assessment areas (20% weight each):"
    )
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Accuracy of Booking (20%): ")
    r.bold = True
    p.add_run("Validates if the selected trip type, origin, destination, schedules, travel class, and dates match the instructor's briefing requirements.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Technical Skill (20%): ")
    r.bold = True
    p.add_run("Verifies the passenger dossier input, performing checks on name spelling, date of birth matching, gender-title alignment, nationality mapping, and passport format compliance.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Organization of Steps (20%): ")
    r.bold = True
    p.add_run("Evaluates if the flight reservation followed correct industry steps, ensuring that interactive seat selection was successfully executed for all passengers across all flight legs.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Completeness (20%): ")
    r.bold = True
    p.add_run("Validates passenger counts (Adults, Children, Infants) and checks if specific ancillary services (particular meals, extra baggage allowances, or wheelchair assistance) match the instructor's requirements.")
    
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Professionalism (20%): ")
    r.bold = True
    p.add_run("Measures time management by verifying if the booking transaction was finalized before the 15-minute countdown expired, penalizing students who fail to complete the reservation within industry-standard holding windows.")

    # ------------------ 3.2 ------------------
    add_heading_styled(doc, "3.2 Details of the Technologies to be Used", 1)
    doc.add_paragraph(
        "The platform is built using a modern, open-source stack. Each component is selected for its high performance, reliability, and ease of deployment."
    )
    
    # Technology Stack Table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Light Shading Accent 1'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Layer'
    hdr_cells[1].text = 'Technology Used'
    hdr_cells[2].text = 'Purpose & Rationale'
    
    for cell in hdr_cells:
        set_cell_background(cell, "0F172A") # Dark Slate
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.bold = True
                run.font.name = 'Times New Roman'
                
    tech_data = [
        ("Frontend Tier", "Vue.js 3, Vite, Pinia, Tailwind CSS 4, Axios", 
         "Handles responsive SPA navigation, persistent booking wizard sessions via Pinia stores, and Axios HTTP interceptors."),
        ("Backend Tier", "Django 5.x/6.0, Django REST Framework, Python 3.13", 
         "Exposes class-based views, serializers, stateless JWT tokens, and executes student grading algorithms securely."),
        ("Database & ML Tier", "PostgreSQL (Supabase), XGBoost, Scikit-learn, Pandas", 
         "Stores ACID-compliant transaction records, locks database seats, and loads trained regression weights to predict baseline fares."),
        ("Simulated Integrations", "PayMongo API Sandbox, ReportLab, SMTP Mailer", 
         "Simulates e-commerce GCash/credit card checkout, compiles official PDF tickets with embedded QR codes, and dispatches email confirmations.")
    ]
    
    for layer, tech, purp in tech_data:
        row_cells = table.add_row().cells
        row_cells[0].text = layer
        row_cells[1].text = tech
        row_cells[2].text = purp
        for i, cell in enumerate(row_cells):
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10)
                    if i == 0:
                        run.font.bold = True

    doc.add_paragraph().paragraph_format.space_before = Pt(12)

    # ------------------ 3.3 ------------------
    add_heading_styled(doc, "3.3 How the Project Will Work", 1)
    doc.add_paragraph(
        "The platform is designed around a fully integrated academic-to-operational workflow, converting classroom instructions "
        "into practical simulations. The system operates through three primary user roles: Student, Instructor, and Administrator."
    )
    
    add_heading_styled(doc, "3.3.1 Step-by-Step Functional Workflow", 2)
    
    # Phase 0
    p = doc.add_paragraph()
    r = p.add_run("Phase 0: Activity Initialization (Academic Setup)\n")
    r.bold = True
    p.add_run(
        "1. The CTHM Instructor accesses their portal, creates a graded flight booking assignment, and enters custom booking criteria "
        "(e.g., flight route, travel class, passenger count, mandatory baggage limits, and specific meal codes).\n"
        "2. The system stores the requirements and generates an 8-character Activity Code (e.g., ACT-8921).\n"
        "3. The instructor distributes the Activity Code to the class."
    )
    
    # Phase 1
    p = doc.add_paragraph()
    r = p.add_run("Phase 1: Booking Protocol (Student Simulation)\n")
    r.bold = True
    p.add_run(
        "1. The Student enters the Activity Code in their dashboard, which automatically locks the booking fields to guide their simulation parameters.\n"
        "2. During flight search, the backend's XGBoost & Dynamic Pricing Engine calculates realistic flight pricing dynamically.\n"
        "3. The student selects the flight, inputs traveler dossier information, selects seats from the interactive map (initiating a 15-minute soft-lock in memory), and chooses required add-ons.\n"
        "4. The student checks out using the simulated PayMongo sandbox environment.\n"
        "5. The backend executes a postgres row-level lock (select_for_update()) on the selected seats, records payment, updates status to confirmed, generates a unique Passenger Name Record (PNR), compiles an official PDF E-ticket using ReportLab, and dispatches it via SMTP."
    )
    
    # Phase 2
    p = doc.add_paragraph()
    r = p.add_run("Phase 2: Departure Control System (DCS) Check-In\n")
    r.bold = True
    p.add_run(
        "To replicate airport terminal passenger check-in procedures, the system integrates a 6-Step DCS Check-In counter counter-loop:\n"
        "  - Step 1 (Presence Verification): Checks-in passengers from the active manifest.\n"
        "  - Step 2 (Dossier Validation): Verifies student inputs (passport expiry dates, visa requirements).\n"
        "  - Step 3 (Security Clearance): Enforces acceptance of safety, security, and hazardous material declarations.\n"
        "  - Step 4 (Measured Load): Evaluates actual baggage scale weight inputs against purchased baggage allowances, assessing excess weight penalties.\n"
        "  - Step 5 (Slot Allocation): Allocates final cabin seating rows.\n"
        "  - Step 6 (Audit & Dispatch): Locks the flight manifest and issues a digital Boarding Pass PDF complete with a boarding QR code."
    )
    
    # Phase 3
    p = doc.add_paragraph()
    r = p.add_run("Phase 3: Performance Analysis & Grading\n")
    r.bold = True
    p.add_run(
        "1. Upon check-in success, the backend Automated Grading Engine (grading_service.py) automatically processes the booking manifest.\n"
        "2. It performs a comparison against the activity rules and computes scores based on Accuracy, Technical Skill, Organization, Completeness, and Professionalism.\n"
        "3. Grade records and rubric JSON breakdowns are permanently archived and displayed on both the student's dashboard and the instructor's master grade registry."
    )
    
    # Create the output docs folder if not exists
    os.makedirs(os.path.dirname(r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\docs\CHAPTER_III_TECHNICAL_BACKGROUND.docx"), exist_ok=True)
    
    doc.save(r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\docs\CHAPTER_III_TECHNICAL_BACKGROUND.docx")
    print("SUCCESS: MS Word Document 'CHAPTER_III_TECHNICAL_BACKGROUND.docx' generated in docs/ folder.")

if __name__ == "__main__":
    main()
