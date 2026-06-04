# PROOF: Freshdesk Onboarding/Issue Pipeline vs NXT — district-by-district evidence

*Audit companion. Every district below is backed by its Freshdesk ticket IDs, **ticket status**, type, classification, dates, a verbatim customer quote, and an NXT cross-check. Built from three sources, no inference without a citation.*

**Sources**
- **`Data for Dallas June 2 2026.xlsx` → sheet `PCS NXT Not Marked`** — 93 customer (Freshdesk/PCS) tickets **not linked to any NXT item**. Curated columns: District/County, Status, Type, Ticket Classification, Module, Created/Closed time, agent/customer interactions, PCS#. *The sheet name is itself the core evidence: these are customer tickets that did NOT convert to NXT work.*
- **`conversations_batch.jsonl`** — full message bodies for all 93 (verbatim quotes).
- **`Perseus Jira (5).csv`** — NXT cross-check (does the district appear in NXT at all / as a migration?).

## What the evidence actually supports (read this first)
- **93 customer tickets** across **34 entities**; after removing internal/test + vendor (**Edge District = 12 tickets**, **Simplot = 1**), **32 real customer districts** remain.
- **Ticket status:** {'Development': 3, 'Pending': 1, 'Closed': 84, 'Pending Release': 4, 'Resolved': 1} — **84 of 93 are Closed.** These are mostly *resolved* support/issue/training tickets, not an open migration backlog.
- **Ticket type:** {'Issue': 71, 'Implementation': 3, 'Question': 17, 'Request': 2}. **Ticket classification:** {'(blank)': 10, 'SchoolCafe Issue': 14, 'Pending/No Response': 13, 'Training/Demo/Question': 37, '2.0 SchoolCafe Issue': 5, 'Implementation Task': 14}.
- **Implementation/onboarding-flavored tickets** (Type=Implementation, or "Implementation Task" classification, or Import/migration in subject): **28 of 80**. So "mid-onboarding" is accurate for a **subset** — the rest are live-customer issues, training, and questions.
- **Honest read:** this proves a real base of **~32 active customer districts generating customer-specific work that is NOT tracked in NXT**. It does **not**, by itself, prove a $2–4M *migration* wave — most of these districts appear to be live/active on SC 2.0 and getting support, with only a subset in active implementation. Treat the forward-migration dollar figure as an extrapolation from the separately-evidenced NXT migrations (Dilworth/Washburn), not as something these 93 tickets prove.

## Summary table — all districts (real customers)
| District | FD tix | Impl-flavored | Statuses | Appears in NXT? | In NXT migration? |
|---|---|---|---|---|---|
| Southwest ISD | 13 | 4 | Closed 13 | 4 (Bug 3, Task 1) | no |
| Healdsburg Unified School District | 7 | 0 | Closed 7 | 1 (Bug 1) | no |
| Mankato Area School District ISD 77 | 6 | 3 | Closed 5, Resolved 1 | 2 (Story 2) | YES: NXT-68632, NXT-69850 |
| Adams 12 Five Star Schools | 5 | 1 | Closed 5 | 1 (Tech-Debt 1) | no |
| Old Colony Regional Vocational Technical | 5 | 0 | Closed 5 | no | no |
| Carl Junction Schools | 4 | 3 | Closed 4 | no | no |
| Mexico School District 59 | 4 | 2 | Closed 4 | 2 (Task 1, Bug 1) | no |
| Caring ISD | 3 | 1 | Closed 2, Development 1 | 1 (Tech-Debt 1) | no |
| Suffolk City Public Schools | 3 | 0 | Closed 2, Development 1 | no | no |
| Waller ISD | 3 | 0 | Closed 3 | 3 (Bug 1, Story 2) | no |
| Arkansas Arts Academy | 2 | 1 | Closed 2 | no | no |
| Carbon County School District #2 | 2 | 0 | Closed 2 | 1 (Story 1) | no |
| Clinton Graceville Beardsley Public Schools | 2 | 2 | Closed 2 | no | no |
| Elsberry R-2 School District | 2 | 2 | Closed 2 | no | no |
| Mashpee Public Schools | 2 | 0 | Closed 2 | 1 (Task 1) | no |
| Bolivar R-1 Schools | 1 | 1 | Closed 1 | no | no |
| Chequamegon School District | 1 | 0 | Closed 1 | 1 (Task 1) | no |
| Colorado School for the Deaf and Blind | 1 | 0 | Closed 1 | no | no |
| Franklin Public Schools | 1 | 0 | Closed 1 | 1 (Enhancement 1) | no |
| Future School of Fort Smith | 1 | 0 | Closed 1 | no | no |
| Glastonbury School District | 1 | 1 | Closed 1 | no | no |
| Greenfield Public Schools | 1 | 1 | Closed 1 | no | no |
| Institute for the Creative Arts | 1 | 1 | Closed 1 | no | no |
| Kernville Union School District | 1 | 0 | Closed 1 | no | no |
| Lake City Community School | 1 | 1 | Closed 1 | no | no |
| Liberty-Eylau Independent School District | 1 | 0 | Closed 1 | no | no |
| Morgan County School District | 1 | 1 | Closed 1 | no | no |
| Nauset Public Schools | 1 | 0 | Closed 1 | no | no |
| Phoenix School of Roseburg | 1 | 1 | Closed 1 | no | no |
| Shepherd Independent School District | 1 | 0 | Closed 1 | 1 (Epic 1) | no |
| South Fork Union School District | 1 | 1 | Closed 1 | no | no |
| St. Mary's Academy | 1 | 1 | Closed 1 | no | no |

## Internal / non-customer entities (excluded from the count)
- **Edge District** — 12 tickets. Flagged by you as an internal test environment.
  - FD#318729 [Pending Release] SC Training Site - Unable to complete a Production Withdrawal
  - FD#318682 [Pending Release] SC Training Site - Missing Error Message for Vendor Pricing/Effective Date
  - FD#318648 [Pending Release] SC Training - Have to enter vendor# twice to contract
- **Simplot** — 1 tickets. Food-service vendor, not a school district.
  - FD#320558 [Pending] SC Implementation - Simplot - Import URLs as Images/Docs

## District-by-district evidence (verbatim)

### Southwest ISD  —  13 Freshdesk tickets
*Statuses: Closed 13 · Implementation-flavored: 4/13 · NXT: 4 (Bug 3, Task 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 291201 | Closed | Issue | Implementation Task | Production 2.0 | 2025-08-07 | 2025-08-11 |
| 291477 | Closed | Issue | SchoolCafe Issue | Production 2.0 | 2025-08-08 | 2025-08-11 |
| 304575 | Closed | Issue | Training/Demo/Question | System 2.0 | 2025-11-13 | 2025-11-20 |
| 306217 | Closed | Issue | SchoolCafe Issue | Inventory 2.0 | 2025-12-03 | 2025-12-17 |
| 308796 | Closed | Issue | 2.0 SchoolCafe Issue | Production 2.0 | 2026-01-09 | 2026-01-14 |
| 312950 | Closed | Question | SchoolCafe Issue | Item Management 2.0 | 2026-02-26 | 2026-03-17 |
| 314864 | Closed | Question | Pending/No Response | Item Management 2.0 | 2026-03-19 | 2026-04-07 |
| 315178 | Closed | Issue | Training/Demo/Question | Item Management 2.0 | 2026-03-24 | 2026-03-31 |
| 318264 | Closed | Issue | Training/Demo/Question | Menu Planning 2.0 | 2026-04-27 | 2026-05-04 |
| 319079 | Closed | Issue | Training/Demo/Question | Menu Planning 2.0 | 2026-05-06 | 2026-05-18 |
| 319142 | Closed | Issue | Training/Demo/Question | Menu Planning 2.0 | 2026-05-06 | 2026-05-08 |
| 319511 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2026-05-08 | 2026-05-16 |
| 320501 | Closed | Issue | SchoolCafe Issue | Item Management 2.0 | 2026-05-19 | 2026-05-27 |

> **Verbatim (FD#291201, "2.0 Southwest ISD - Variety Fruit Production Plan Counts"):** "For some fruit items in the variety fruit, when toggling on, there is no way to enter counts."

### Healdsburg Unified School District  —  7 Freshdesk tickets
*Statuses: Closed 7 · Implementation-flavored: 0/7 · NXT: 1 (Bug 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 289958 | Closed | Issue | SchoolCafe Issue | Menu Planning 2.0 | 2025-07-29 | 2025-08-19 |
| 289964 | Closed | Question | Pending/No Response | Menu Planning 2.0 | 2025-07-29 | 2025-08-13 |
| 290925 | Closed | Question | Training/Demo/Question | Menu Planning 2.0 | 2025-08-05 | 2025-08-27 |
| 296709 | Closed | Issue | Training/Demo/Question | Item Management 2.0 | 2025-09-10 | 2025-09-22 |
| 310398 | Closed | Question | Training/Demo/Question | Production 2.0 | 2026-01-28 | 2026-01-30 |
| 319694 | Closed | Question | Training/Demo/Question | Menu Planning 2.0 | 2026-05-11 | 2026-05-28 |
| 319912 | Closed | Issue | Pending/No Response | Item Management 2.0 | 2026-05-13 | 2026-05-27 |

> **Verbatim (FD#289958, "SchoolCafe 2.0 - Healdsburg Unified School District - Disappearing men"):** "The district reported an issues after copying a menu cycle where fruit items that are added to the menu disappear once other fruit items are removed. They did mention that this is not a regular occurrence though happens enough to be frustrating and is an issue Please see recording link of issue below Menu Cycle used: Junior High Lunch Nov/Dec 2025 Healdsburg Unified School District SchoolCafe 2.0 - Disappearing menu "

### Mankato Area School District ISD 77  —  6 Freshdesk tickets
*Statuses: Closed 5, Resolved 1 · Implementation-flavored: 3/6 · NXT: 2 (Story 2) · NXT migration: YES: NXT-68632, NXT-69850*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 313240 | Closed | Request | Training/Demo/Question | Menu Planning 2.0 | 2026-03-02 | 2026-03-11 |
| 315525 | Closed | Issue | Pending/No Response | Production 2.0 | 2026-03-27 | 2026-04-07 |
| 315535 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2026-03-27 | 2026-04-01 |
| 316608 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2026-04-08 | 2026-04-17 |
| 318389 | Resolved | Issue |  | Inventory 2.0 | 2026-04-28 | — |
| 318599 | Closed | Issue | Training/Demo/Question | Inventory 2.0 | 2026-04-30 | 2026-05-07 |

> **Verbatim (FD#313240, "PE to SC Migration - Mankato - OVS information missing on all menus"):** "The Offer vs Serve determination did not transfer over with the rest of the menu data. For example, all Elementary, Middle, and High School menus for breakfast and lunch were indicated as OVS being used for all applicable age groups."

### Adams 12 Five Star Schools  —  5 Freshdesk tickets
*Statuses: Closed 5 · Implementation-flavored: 1/5 · NXT: 1 (Tech-Debt 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 290930 | Closed | Issue | 2.0 SchoolCafe Issue | Menu Planning 2.0 | 2025-08-05 | 2025-08-11 |
| 304177 | Closed | Issue | Pending/No Response | Production 2.0 | 2025-11-10 | 2025-12-11 |
| 307330 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2025-12-15 | 2026-01-27 |
| 313716 | Closed | Issue | 2.0 SchoolCafe Issue | Production 2.0 | 2026-03-05 | 2026-04-29 |
| 314514 | Closed | Implementation | Training/Demo/Question | Import/Export | 2026-03-16 | 2026-03-16 |

> **Verbatim (FD#314514, "SC Implementation - Adams 12 - Request for Item export"):** "Adams 12 needs to update their items to implement inventory. Requesting an export of all items"

### Old Colony Regional Vocational Technical  —  5 Freshdesk tickets
*Statuses: Closed 5 · Implementation-flavored: 0/5 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 302460 | Closed | Question |  | Item Management 2.0 | 2025-10-24 | 2025-11-04 |
| 311738 | Closed | Question | Pending/No Response | Inventory 2.0 | 2026-02-12 | 2026-03-03 |
| 313689 | Closed | Question | Pending/No Response | Item Management 2.0 | 2026-03-05 | 2026-03-23 |
| 315980 | Closed | Question | Pending/No Response | Inventory 2.0 | 2026-04-01 | 2026-04-13 |
| 316604 | Closed | Issue | Pending/No Response | Inventory 2.0 | 2026-04-08 | 2026-04-29 |

> **Verbatim (FD#302460, "Old Colony RVTHS - unable to edit pack sizes"):** "She is having issues removing the pack size from this cookie, but also the cookie is showing twice and it should only be here once, preferably the one with the price. These are the two items in question right now: Sugar Cookie: and Raisins:"

### Carl Junction Schools  —  4 Freshdesk tickets
*Statuses: Closed 4 · Implementation-flavored: 3/4 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 287828 | Closed | Issue | Implementation Task | Item Management 2.0 | 2025-07-09 | 2025-07-17 |
| 287918 | Closed | Issue | Implementation Task | Menu Planning 2.0 | 2025-07-09 | 2025-07-28 |
| 291257 | Closed | Issue | 2.0 SchoolCafe Issue | Item Management 2.0 | 2025-08-07 | 2025-08-20 |
| 294887 | Closed | Question | Implementation Task | Menu Planning 2.0 | 2025-08-29 | 2025-09-09 |

> **Verbatim (FD#287828, "Carl Junction Schools / vendor item number issue"):** "I keep getting a message that my vendor id number is a duplicate, but I can’t find the duplicate number when I search it. Lindsey Stevenson Nutrition and Wellness Director Carl Junction R-1 School District"

### Mexico School District 59  —  4 Freshdesk tickets
*Statuses: Closed 4 · Implementation-flavored: 2/4 · NXT: 2 (Task 1, Bug 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 290909 | Closed | Issue | SchoolCafe Issue | Inventory | 2025-08-05 | 2025-08-06 |
| 298909 | Closed | Issue | SchoolCafe Issue | Item Management 2.0 | 2025-09-26 | 2025-09-30 |
| 313038 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2026-02-26 | 2026-03-11 |
| 315109 | Closed | Issue | Training/Demo/Question | Menu Planning 2.0 | 2026-03-24 | 2026-03-30 |

> **Verbatim (FD#290909, "SC Implementation - Mexico School District 59- Not able to add new ite"):** "Please see screenshot below. Item LI-0901 has an inventory pack size/price and is ready to add to inventory, however, the item is not showing up to add to vendor (Prairie Farms). District has reported this is occurring to all recently added items."

### Caring ISD  —  3 Freshdesk tickets
*Statuses: Closed 2, Development 1 · Implementation-flavored: 1/3 · NXT: 1 (Tech-Debt 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 304367 | Closed | Issue | Training/Demo/Question | Item Management 2.0 | 2025-11-12 | 2025-11-13 |
| 307844 | Closed | Issue | Implementation Task | Item Management 2.0 | 2025-12-19 | 2025-12-29 |
| 321240 | Development | Issue |  | Item Management 2.0 | 2026-05-27 | — |

> **Verbatim (FD#307844, "SC Implementation - All Districts - Set All Prices Entry Issue"):** "When trying to set $0.50 as the price in the Set Price for All entry box, it will not allow you to enter the decimal first. Once I enter a number, I can then add the decimal in front of the initial number. I also found that when I clicked the Backspace button, it only partially deleted the number before, and no longer allowed the remaining numbers to be deleted. I had to move the cursor using the arrow buttons a few "

### Suffolk City Public Schools  —  3 Freshdesk tickets
*Statuses: Closed 2, Development 1 · Implementation-flavored: 0/3 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 318653 | Closed | Issue | Training/Demo/Question | Item Management 2.0 | 2026-04-30 | 2026-05-06 |
| 318874 | Closed | Question | Training/Demo/Question | Production 2.0 | 2026-05-04 | 2026-05-07 |
| 319505 | Development | Issue |  | Item Management 2.0 | 2026-05-08 | — |

> **Verbatim (FD#318653, "SchoolCafe - Suffolk City Public Schools - Help with a recipe"):** "Good Afternoon, I have a recipe that is complete but when I pull it into Menu planning the meal contribution is blank. Have you seen that before? Chree Emerson Suffolk Public Schools Food & Nutrition Services Coordinator I (757) 925-5789 ext. 672108"

### Waller ISD  —  3 Freshdesk tickets
*Statuses: Closed 3 · Implementation-flavored: 0/3 · NXT: 3 (Bug 1, Story 2) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 291200 | Closed | Question | Pending/No Response | Menu Planning 2.0 | 2025-08-07 | 2025-08-20 |
| 291385 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2025-08-08 | 2025-08-26 |
| 305234 | Closed | Question | Pending/No Response | Inventory 2.0 | 2025-11-19 | 2025-12-08 |

> **Verbatim (FD#291200, "SC - Waller ISD - Elementary Lunch Menu Calendar Report w Nutrients Er"):** "When we run the Lunch Menu Calendar Report with Nutrients for Elementary Schools we do not see the carbohydrate information for multiple menu items (entrees, vegetables, fruits, milk, and condiments). For example we can see that chocolate milk has 18g on the breakfast menu calendar report for Elementary Schools, however it does not show any data on the lunch menu calendar report. Attached are the Breakfast and Lunch "

### Arkansas Arts Academy  —  2 Freshdesk tickets
*Statuses: Closed 2 · Implementation-flavored: 1/2 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 295542 | Closed | Issue | Implementation Task | Menu Planning 2.0 | 2025-09-03 | 2025-09-16 |
| 297884 | Closed | Question | Training/Demo/Question | Menu Planning 2.0 | 2025-09-18 | 2025-09-30 |

> **Verbatim (FD#295542, "SC Implementation -Arkansas Arts Academy - Contribution Not Flowing to"):** "Carrots, Raw in Menu: MN-LUN-912-082525-154955 in Menu Cycle: HS Lunch Sept week 1 contributions will not flow to menus. In the menu item the carrots 1/2 cup sliced contribution is 1/2 cup R/O Blank Contribution"

### Carbon County School District #2  —  2 Freshdesk tickets
*Statuses: Closed 2 · Implementation-flavored: 0/2 · NXT: 1 (Story 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 299245 | Closed | Issue | 2.0 SchoolCafe Issue | Inventory 2.0 | 2025-09-29 | 2025-10-09 |
| 310339 | Closed | Question | Training/Demo/Question | Item Management 2.0 | 2026-01-27 | 2026-01-30 |

> **Verbatim (FD#299245, "SC - Carbon Co SD #2 - printing inventory for Hanna"):** "Hello, I was trying to print inventory valuation for Hanna from 7/15/25 when I exported it to PDF. It kept coming up with the same three pages, not what I was seeing as a report. I was able to go around it with I ctrl+P I was able to save it as a pdf. I have put both what was coming up and what it should look like. Thank you -- Josalyn (Josie) Miller District Head Cook Carbon Co SD #2 phone 307-710-7022 SMILE School "

### Clinton Graceville Beardsley Public Schools  —  2 Freshdesk tickets
*Statuses: Closed 2 · Implementation-flavored: 2/2 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 294917 | Closed | Issue | Implementation Task | Menu Planning 2.0 | 2025-08-29 | 2025-09-09 |
| 298216 | Closed | Issue | Implementation Task | Menu Planning 2.0 | 2025-09-22 | 2025-09-29 |

> **Verbatim (FD#298216, "SC Implementation - Clinton Graceville Beardsley Public Schools - Menu"):** "Janine cannot add menu items to her Chicken Nuggets menu. Menu Cycle: Week 2 - Lunch Menu"

### Elsberry R-2 School District  —  2 Freshdesk tickets
*Statuses: Closed 2 · Implementation-flavored: 2/2 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 303897 | Closed | Issue | Training/Demo/Question | Inventory 2.0 | 2025-11-07 | 2025-11-10 |
| 306404 | Closed | Issue | Training/Demo/Question | System 2.0 | 2025-12-04 | 2025-12-08 |

> **Verbatim (FD#303897, "SC Implementation - Elsberry R-2 School District- Item Export request"):** "District is starting Inventory and we need all of their item information exported out to our item details sheet."

### Mashpee Public Schools  —  2 Freshdesk tickets
*Statuses: Closed 2 · Implementation-flavored: 0/2 · NXT: 1 (Task 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 311415 | Closed | Issue | Training/Demo/Question | Menu Planning | 2026-02-09 | 2026-02-24 |
| 315737 | Closed | Issue | Pending/No Response | Menu Planning 2.0 | 2026-03-31 | 2026-04-29 |

> **Verbatim (FD#311415, "Mashpee Public Schools - Menu Planner"):** "Hi, I am working with the menu planner on SchoolCafe. I am trying to understand why the calories are inputting different with the same exact menu when I select k-5 vs k-8. The calories should not be changing if it is the same menu. Thanks, Kristen Hurlburt Assistant Director of Food Services [https://ci3.googleusercontent.com/mail-sig/AIorK4x7lhhAic6h6Ajnfy6ArIULQ_OcylCSKVi7XNhJg4kVuIRWvsAZqK7v8kOWTdt0ZuZzH9nSbkU] Ma"

### Bolivar R-1 Schools  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 304242 | Closed | Issue | Implementation Task | Inventory 2.0 | 2025-11-11 | 2025-11-12 |

> **Verbatim (FD#304242, "SC Implementation - Bolivar R-1 Schools- Item export request"):** "Please export out the districts items in our item import template"

### Chequamegon School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: 1 (Task 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 318890 | Closed | Issue | SchoolCafe Issue | Item Management 2.0 | 2026-05-04 | 2026-05-15 |

> **Verbatim (FD#318890, "SC Issue- Chequamegon School District- Item onboarding export not matc"):** "When exporting items out of the item onboarding tool the item numbers and order of items does not match."

### Colorado School for the Deaf and Blind  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 313312 | Closed | Issue | Training/Demo/Question | Item Management 2.0 | 2026-03-02 | 2026-03-18 |

> **Verbatim (FD#313312, "SC Issue- Colorado School for the Deaf and Blind- Find and replace not"):** "Used find and replace to replace MI-0021 with MI-0494. Menu for next week did not update with the new menu item assigned"

### Franklin Public Schools  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: 1 (Enhancement 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 304857 | Closed | Issue | SchoolCafe Issue | Menu Planning 2.0 | 2025-11-17 | 2025-11-19 |

> **Verbatim (FD#304857, "Franklin Public Schools / Can't assign- menus"):** "Hello, I'm trying to assign a menu day for Jan 5th for our K-5 schools and it won't let me assign any menu for this day. The other days are working okay. I did check the days off and 1/5/26 is not a day we have off or are marked off. Thanks! -- Jessie Christensen, MS, RD, CD Food Service Manager Food Service Department 8222 S 51st st Franklin, WI, 53132 (414)-423-4656 x7023"

### Future School of Fort Smith  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 309367 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2026-01-14 | 2026-02-24 |

> **Verbatim (FD#309367, "Future School of Fort Smith - SchoolCafe2.0 - Carryover Issue"):** "We have a carryover issue with our item MI-0210 Lettuce Tomato Setup. I went through last week production and we had 9 carryovered to 1/9 and they were all served that day. On Mondaty, we produced more and have carryovered each day this week. Today it shows that they were originally from 1/6 and we cannot carry them over. This would only be the third carryover for this week. What else is happening here? Teressa Teres"

### Glastonbury School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 288917 | Closed | Issue | SchoolCafe Issue | Item Management 2.0 | 2025-07-18 | 2025-07-23 |

> **Verbatim (FD#288917, "SC Implementation - Glastonbury SD - Incorrect nutritionals for VMI"):** "VMI for Assorted Fruit is showing nutritionals that are too high. All items are a 1/2 Fruit contribution, none of them are over 157 calories. Current amount is showing 157."

### Greenfield Public Schools  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 301377 | Closed | Issue | Training/Demo/Question | Import/Export | 2025-10-15 | 2025-10-20 |

> **Verbatim (FD#301377, "SC Implementation - Greenfield Public Schools- Item export request"):** "District is resuming back office implementation with a new director. We will need their items exported from the system into our template"

### Institute for the Creative Arts  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 288469 | Closed | Question | Implementation Task | Menu Planning 2.0 | 2025-07-15 | 2025-07-21 |

> **Verbatim (FD#288469, "Institute for the Creative Arts / Menu Module/Variety Menu Items"):** "Good morning, I am creating a breakfast template with variety menu items. It appears that the analysis only considers non-variety menu items in the calorie count. In my example, the Granola Packet. Is this how it is supposed to calculate? I have checked my variety items and all have correct average nutrition information calculated. Teressa -- Teressa Gasque Child Nutrition Director Institute for the Creative Arts 110"

### Kernville Union School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 318414 | Closed | Issue | SchoolCafe Issue | Item Management 2.0 | 2026-04-28 | 2026-05-06 |

> **Verbatim (FD#318414, "Recipes "<-- Back" button takes to Item Page and not Recipes Page"):** "While working and creating recipes at times the "<-- Back" button that is the recipe page it takes me back to the Items module. Wanted to double check to make sure not a bug."

### Lake City Community School  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 300122 | Closed | Issue | Implementation Task | Import/Export | 2025-10-03 | 2025-10-08 |

> **Verbatim (FD#300122, "SC Implementation - Lake City Community School- Item export request"):** "District completed inventory items, we now need to work on ingredients. Requesting an export of all the districts items from the system"

### Liberty-Eylau Independent School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 317212 | Closed | Issue | Training/Demo/Question | Item Management 2.0 | 2026-04-15 | 2026-04-17 |

> **Verbatim (FD#317212, "SC Issue- Liberty-Eylau Independent School District- Unable to delete "):** "Duplicate item in session #1 for district we need to remove. Get an error when deleting."

### Morgan County School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 295567 | Closed | Issue | Implementation Task | Production 2.0 | 2025-09-03 | 2025-09-05 |

> **Verbatim (FD#295567, "Cold hold items"):** "Just wondering why there are so many temperature boxes on cold hold items on the production records. The hot hold items only have one box. Thanks Jan Jan Holding RD,CD Director of Nutrition Services Morgan School District 801-499-7287 jan.holding@morgansd.org"

### Nauset Public Schools  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 309961 | Closed | Issue | Training/Demo/Question | Production 2.0 | 2026-01-22 | 2026-02-26 |

> **Verbatim (FD#309961, "Nauset PS - Entering planned count numbers delay."):** "Susan Murray called regarding performance issues with the production records module. Susan Murray reported that the production records module is lagging significantly, making it difficult to complete tasks efficiently. They are currently working on records for December, specifically for the high school breakfast program. Keith Noury confirmed the lagging issue and created a support ticket to document the problem."

### Phoenix School of Roseburg  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 291735 | Closed | Issue | Implementation Task | System 2.0 | 2025-08-11 | 2025-08-15 |

> **Verbatim (FD#291735, "SC Implementation - Phoenix School of Roseburg - Import Did Not Read I"):** "Cherry tomatoes is an example of an item that had Is Food Item set to yes but imported without the initial item attributes set"

### Shepherd Independent School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 0/1 · NXT: 1 (Epic 1) · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 311759 | Closed | Issue | Pending/No Response | Item Management 2.0 | 2026-02-12 | 2026-02-24 |

> **Verbatim (FD#311759, "SC Issue-Shepherd Independent School District- Bulk tool duplicate men"):** "While showing a customer the bulk tool, we were only able to publish two of the items. One of the items is unpublishable due to duplicate menu item description"

### South Fork Union School District  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 312922 | Closed | Request | Implementation Task | System 2.0 | 2026-02-26 | 2026-03-02 |

> **Verbatim (FD#312922, "SC Request - South Fork Union - Request to run custom query for all it"):** "Please run a custom query for all items with allergens. I need to be able cross check the allergens for all items to make sure we have set up the items correctly for data entry."

### St. Mary's Academy  —  1 Freshdesk tickets
*Statuses: Closed 1 · Implementation-flavored: 1/1 · NXT: no · NXT migration: no*

| FD# | Status | Type | Classification | Module | Created | Closed |
|---|---|---|---|---|---|---|
| 308370 | Closed | Issue | SchoolCafe Issue | Item Management 2.0 | 2026-01-06 | 2026-01-12 |

> **Verbatim (FD#308370, "SC Implementation - St. Mary's Academy- Menu item Category not saving"):** "Menu item category "Sandwich" was added. Not an option in the item category drop down"

## Methodology & caveats
- "Real customer districts" = curated `District/County` values minus Edge District (internal test, user-flagged) and Simplot (vendor).
- "Impl-flavored" = Type=Implementation OR Classification contains "Implementation" OR subject contains Import/migration. A heuristic — the per-district tables show the raw fields so you can re-judge.
- NXT cross-check matches a distinctive district token against all fields of the NXT export; "In NXT migration" = that token appears in an NXT ticket whose summary contains "migration". Absence is evidence the district has not generated an NXT migration cluster (consistent with the sheet being "NXT Not Marked").
- **Status matters:** 84/93 tickets are Closed — resolved support/issue/training, not open onboarding. The pipeline is real but is NOT a queue of pending $250K migrations; the forward-$ figure is an extrapolation from the two evidenced NXT migrations, not from these tickets.
- Verbatim quotes are the first substantive customer turn from `conversations_batch.jsonl`; CAUTION banners stripped.