# SMART FLIGHT BOOKING SIMULATION PLATFORM FOR CTHM-CSUCC: AN INTERACTIVE AND DATA-DRIVEN TRAINING TOOL FOR TOURISM EDUCATION

## CHAPTER IV (Continued): METHODOLOGY, RESULT AND DISCUSSION

### 4.3 The Developed System (Continuation from Payment & Confirmation)

Following the flight and seat selection process, the system moves into transactional validation, fulfillment, and departure control operations. Below is a detailed walkthrough of these stages as implemented in the platform's codebase.

#### 1. Simulated Payment Processing
When the student reaches the **Payment Stage**, they are presented with a simulated payment interface mimicking modern e-commerce gateways. The system integrates a sandbox simulation of the **PayMongo API**, allowing students to select between standard credit card processing, digital wallets (GCash/Maya), or over-the-counter payments.
- **Backend Flow:** To prevent client-side price tampering, the frontend sends only the `booking_id` and selected payment method to the backend endpoint `/api/payment/create-intent/`. The backend recalculates the authoritative price directly from the database schema:
  $$\text{Final Price} = \sum (\text{Base Fare} + \text{Add-ons} + \text{Insurance}) + \text{Taxes (12\\% VAT)} + \text{Terminal Fees (DPSC)}$$
- **Security Protocols:** Once validated, a checkout token is created, and the state transitions to `Pending`. The transaction is finalized securely via a mock webhook callback or direct token confirmation, updating the booking record to `Confirmed`.

#### 2. Booking Confirmation and E-Ticket Generation (PDF)
Upon successful payment validation, the system executes an automated post-payment transactional pipeline:
- **PNR Generation:** A unique 6-character alphanumeric **Passenger Name Record (PNR)** is generated (e.g., `QX7K9B`) using a randomized hash algorithm, serving as the master key for all subsequent manifest operations.
- **PDF Compilation:** The system invokes a backend Python service (`pdf_service.py`) using **ReportLab** to programmatically generate an official, print-ready E-Ticket. This document includes flight details, individual passenger breakdowns, bag-tag details, and an embedded QR code containing the PNR string.
- **Email Notification:** An integrated SMTP mailer (`email_service.py`) dispatches a customized HTML email containing the dynamic PNR, booking summary, and the generated PDF E-ticket as an attachment to the primary passenger’s registered email address.

```
┌─────────────────────────────────────────────────────────────┐
│                    POST-PAYMENT PIPELINE                    │
│                                                             │
│  1. PayMongo Webhook ──► 2. PNR Alphanumeric Generation      │
│                                  │                          │
│                                  ▼                          │
│  4. Email SMTP Dispatch ◄── 3. ReportLab PDF Generation     │
└─────────────────────────────────────────────────────────────┘
```

#### 3. Departure Control System (DCS) & Online Check-In
The transition from a passive passenger record to active flight boarding is managed by the Departure Control System (DCS). Students access this via the **Online Check-in Portal** by entering their PNR and Last Name. The system implements a strict **6-Step DCS Check-In Control Loop** to simulate real airport counter operations:
1. **Presence Verification:** Checks if the booking party matches the active manifest, verifying which passengers are checking in.
2. **Dossier Audit:** Simulates a visual inspection of travel credentials. The system checks input details (e.g., passport expiry, document validity) against security protocols.
3. **Clearance Check:** Validates safety clearances and checks for restricted passenger status.
4. **Measured Load:** Captures checked baggage weights. The system compares weights against the purchased allowance to calculate excess weight surcharges.
5. **Slot Assignment:** Links the checked-in passenger to a locked cabin seat coordinate.
6. **Audit & Boarding Pass Issuance:** Locks the seat permanently in the SQL database, generates a digital **Boarding Pass** with a dynamic barcode, and updates the manifest status to `Checked-In`.

---

### 4.4 Testing Results

Following the evaluation methodology, testing encompassed quantitative functionality validation (Technical Verification) and qualitative usability analysis (User Acceptance Testing) structured around the ISO/IEC 25010 software quality model.

#### 4.4.1 Technical Verification
System functions were executed across different modules to verify that all functional requirements achieved a $100\%$ pass rate under standard conditions.

| Test ID | Module | Test Description | Expected Output | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Student Auth | Student inputs valid email/password. | Redirect to Student Dashboard. | **Passed** |
| **TC-02** | Activity Gate | Student inputs active Activity Code. | Validation succeeds; redirects to booking. | **Passed** |
| **TC-03** | Flight Search | Search with Origin, Destination, and Date. | Returns list of schedules with ML-surged price. | **Passed** |
| **TC-04** | Fare Families | Select between Basic vs. Premium fares. | Premium sets standard baggage/seat price to ₱0. | **Passed** |
| **TC-05** | Seat Concurrency | User A and B select Seat 12A simultaneously. | First checkout succeeds; second gets `423 Locked`.| **Passed** |
| **TC-06** | Payment intent | Submit booking ID to PayMongo simulation. | Backend verifies base fare; issues transaction. | **Passed** |
| **TC-07** | Check-in Gate | Input valid PNR and Last Name in DCS. | Retrieves manifest data; opens check-in wizard. | **Passed** |
| **TC-08** | Grading Engine | Complete graded activity booking. | Auto-calculates grade based on 5 rubric areas. | **Passed** |
| **TC-09** | Admin Flight | Admin creates a new route and aircraft seat map. | Manifest database table updates dynamically. | **Passed** |

---

#### 4.4.2 User Acceptance Testing (UAT)

User Acceptance Testing was conducted with a total of **15 evaluators**, consisting of **1 Group Admin**, **4 CTHM Instructors**, and **10 CTHM Students**. Evaluation sessions took place in the computer laboratory, with student/instructor sessions lasting approximately 2 hours each to allow for full feature execution, while admin sessions focused on operational oversight and data seeding.

##### ISO/IEC 25010 Quality Model Evaluation Results
The system was rated based on a 5-point Likert scale (1 = Poor, 5 = Excellent) across the eight primary software quality characteristics defined by the ISO/IEC 25010 model.

```mermaid
radar-chart
    title "ISO/IEC 25010 Quality Rating Results (Mean Score: 4.44)"
    labels ["Functional Suitability", "Usability", "Performance Efficiency", "Compatibility", "Reliability", "Security", "Maintainability", "Portability"]
    data [4.65, 4.72, 4.58, 4.40, 4.52, 4.10, 4.15, 4.40]
```

##### Summary of ISO/IEC 25010 Evaluation Results

| Characteristic | Mean Score | Interpretation | Analysis & Insights |
| :--- | :---: | :--- | :--- |
| **Functional Suitability** | **4.65** | *Excellent* | Replicates all key reservation and check-in workflows. |
| **Usability** | **4.72** | *Excellent* | UI features clear step wizards, modern layout, and clean pink/slate aesthetics. |
| **Performance Efficiency**| **4.58** | *Excellent* | Search operations run smoothly, and page transitions are under 2 seconds. |
| **Compatibility** | **4.40** | *Excellent* | Works across Google Chrome, Firefox, and Microsoft Edge without breaks. |
| **Reliability** | **4.52** | *Excellent* | Database operations handle active requests without locking errors. |
| **Security** | **4.10** | *Very Good* | Implements JWT authentication, but security limits and session checks can be improved. |
| **Maintainability** | **4.15** | *Very Good* | Code is split into structured modules, though migrations require management. |
| **Portability** | **4.40** | *Excellent* | Full-stack deployment on Railway.app is responsive on both desktop and mobile views. |
| **OVERALL PRODUCT QUALITY** | **4.44** | **Excellent** | **Confirms the system is highly viable for educational training.** |

---

### 4.5 Discussion

The results confirm that the platform is effective as a simulated learning tool. The platform's performance is driven by three main technical components:

#### 1. The Hybrid Machine Learning (XGBoost) & Dynamic Pricing Engine
The system simulates realistic airline pricing using a two-stage calculation:
- **Stage 1 (Predictive Base):** An **XGBoost Regressor model** (`predictor.py`) uses historical airline trends to set a base price. It evaluates:
  $$\text{Base Price} = f(\text{Stops}, \text{Journey Day}, \text{Journey Month}, \text{Departure Hour}, \text{Duration Minutes})$$
- **Stage 2 (Dynamic Overlays):** A dynamic pricing service (`dynamic_pricing.py`) applies real-time modifiers to simulate market forces:
  - *Time-Based Seasonality:* Applies holiday multipliers based on a 2026 Philippine calendar (e.g., Sinulog CEB flights x1.35, December Christmas surge x1.60).
  - *Urgency Booking Curve:* An exponential decay curve surges prices if the booking date is close to departure:
    $$\text{Urgency Factor} = 1.0 + 2.80 \times e^{-0.10 \times \text{Days Remaining}}$$
  - *Inventory Occupancy Surcharge:* Price scales dynamically as seat availability drops below $20\%$, teaching students how demand impacts cost.
  - *Psychological Rounding:* Formats final prices to end in "99" (e.g., ₱2,431.50 becomes ₱2,499.00) for a realistic commercial feel.

#### 2. The Multi-Criteria Automated Grading Algorithm
Instructors can assign flight activities with specific booking parameters (e.g., "Book a Premium, Round-trip flight from Manila to Cebu for 2 Adults with wheelchair assistance"). The system grades student attempts in real time using a 5-part rubric breakdown ($20\%$ each):

1. **Accuracy of Booking ($20\\%$):** Compares booked route, dates, flight numbers, and travel class against the target activity.
2. **Technical Skill ($20\\%$):** Verifies passenger details, passport formatting, and nationality inputs.
3. **Organization of Steps ($20\\%$):** Checks seat assignments on all legs and verifies step sequence completeness.
4. **Completeness ($20\\%$):** Validates passenger counts and ensures specific ancillary add-ons (meals, baggage) match instructions.
5. **Professionalism ($20\\%$):** Measures time management by checking if the booking was completed before the countdown expired.

```
┌─────────────────────────────────────────────────────────────┐
│                    GRADING RUBRIC MATRIX                    │
│                                                             │
│   Accuracy of Booking (20%)   ──►   Technical Skill (20%)    │
│   Organization (20%)          ──►   Completeness (20%)       │
│   Professionalism (20%)       ──►   Earned Score             │
└─────────────────────────────────────────────────────────────┘
```

#### 3. Pessimistic Concurrency Control (Row-Level Locking)
To simulate high-demand booking scenarios, the database must prevent double-booking identical seats when multiple students checkout at the same millisecond. 
- The system uses a **Soft-Lock -> Hard-Lock** architecture.
- When selecting a seat, a temporary **Soft-Lock** is placed with a session ID and 15-minute expiry in memory.
- During final payment, the backend transaction uses **Django's `select_for_update()`** database query. This applies a row-level lock on the database seat index, forcing concurrent updates to wait, which prevents dirty writes and ensures transaction integrity.

---

## CHAPTER V: CONCLUSIONS AND RECOMMENDATIONS

### 5.1 Conclusion

The development of the "Smart Flight Booking Simulation Platform for CTHM-CSUCC" successfully addresses the lack of interactive training tools in tourism education. The system achieves several key outcomes:
1. **Practical Experience:** Bridges the gap between theoretical classroom learning and real-world application by simulating authentic reservation, pricing, and check-in procedures.
2. **Automated Evaluation:** Simplifies grading for instructors by replacing manual verification with a real-time rubric-based grading engine.
3. **Data Integrity & Realism:** Successfully implements professional web technologies (Vue 3, Django, PostgreSQL) along with commercial-grade pricing, concurrency control, and tax compliance systems.
4. **Proven Quality:** Achieved an overall product quality score of **4.44 (Excellent)** in ISO/IEC 25010 evaluations, confirming its readiness for academic use.

In conclusion, the platform provides an effective, secure, and data-driven training environment that helps prepare CTHM-CSUCC students for professional roles in the travel and hospitality industry.

---

### 5.2 Recommendations

To expand the capabilities of the simulation platform, the following recommendations are proposed:
1. **Support for International Flights:** Expand the flight routes database to include international destinations and integrate simulated foreign currency exchange rates.
2. **Post-Booking Operations:** Add simulation flows for passenger rebooking, flight cancellations, and promotional voucher processing.
3. **Global Distribution System (GDS) Interface:** Implement optional terminal views mirroring Amadeus or Sabre systems to teach both legacy command-line and modern web booking methods.
4. **Enhanced Analytics:** Expand the instructor dashboard with predictive data analytics to identify common mistakes and areas where students need extra help.
5. **Advanced Database Security:** Add strict database encryption and automated audit logs to improve system-wide security and protect simulated student data.
