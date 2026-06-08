<!--
DRAFTED GUIDE SECTION — Cluster C6 (Posting-engine entry rules).
This is grounded source for a refresh of Job 8 / Job 10 (+ a Job 2 prerequisite callout).
Every product-behavior sentence carries an inline <!-- Source: NXT-####:AC "verbatim quote" --> tracing to that ticket's Acceptance Criteria.
Backend transaction codes (TAXCLCTD, MEALSLS, PURCH, WD, ADDINV, INVTRFRFR/INVTRFRTO, WHIRCV, COMMUSG, RMBRSCLM/RMBRSRCVD, etc.) are translated to user-facing language in the prose; the raw code is preserved ONLY inside the citation comment.
STATUS HONESTY: NXT-70304 and NXT-66384 are Done Done = shipped (present tense). Everything else is upcoming and tagged "(Coming)".
RN is empty in this fixture; AC is the highest-trust source. `desc` (the "As a..." persona) is supporting context only and is never the sole basis for a behavior claim.
-->

# Job 8 / Job 10 deep-dive — What posting actually puts in your ledger

> **Where this lives.** This expands **Job 8 ("See what happened — Journal & Ledger")** and **Job 10 ("Why a posting fired or failed — Posting Activity Log")**. It also adds one prerequisite that belongs in **Job 2 (Account Mapping)**: the **Valuation Categories** page, which gates all inventory posting.

> **TL;DR.** The rest of this guide keeps telling you "posting is automatic." True — but it never shows you *what* it posts. This section opens the hood. When a period closes, the system writes balanced double-entry lines for you: a debit, a credit, an amount, a date, and a site. Two of these flows are **live today** (your meal-sales revenue and your sales-tax liability). The rest — the whole inventory side and reimbursements — are **(Coming)**. Read the live ones as fact; read the (Coming) ones as "this is what's being built, don't expect the buttons yet."

> ⚠️ **Read the status tags, not just the headings.** A line tagged **(Coming)** describes a backlog story, not a screen you can open today. If you go looking for it and it isn't there, the guide isn't wrong — the feature hasn't shipped. Live behavior is written in the present tense with no tag.

---

## Legacy → 2.0, for this section

| You used to think… | In 2.0 it's actually… |
|---|---|
| "Posting is a black box; money just appears in the GL." | Every posted line names its **debit account, credit account, amount, posting date, and source** — and you can open the entry to see them. <!-- Source: NXT-65485:AC "The output will show all the information needed for the ledger entry — which accounts are debited and credited, the amount, the date, and where the transaction came from." --> (engine: **(Coming)**) |
| "Sales tax is part of my meal revenue." | Sales tax is a **liability you owe**, posted separately from revenue — never counted as income. <!-- Source: NXT-70304:desc "*Sales Tax* = the tax amount collected on taxable sales (a *liability*, not revenue)." --> **(Live)** |
| "Inventory just needs GL accounts somewhere." | Inventory posts by **Valuation Category**, and each category needs **both** an Asset and an Expense account before it can post at all. <!-- Source: NXT-65482:AC "Every valuation category must have *both* an Asset Account and an Expense Account mapped before it can be used in postings." --> **(Coming)** |

---

## Part A — The two flows that are LIVE today

These two are **Done Done**. The entries described here are real lines you will see in the Journal and Ledger (Job 8) right now.

### A1. Meal-sales revenue → your ledger, when you close a POS period **(Live)**

🎯 **The job:** you close a POS period and your meal money lands in the general ledger automatically, split correctly between revenue and the prepaid balances customers drew down.

When a POS period is closed for a site, the system posts your meal-sales revenue to the ledger without a manual journal entry. <!-- Source: NXT-66384:AC "*When a POS period is closed:* * Backend accesses the <meal sales revenue source> from the accountability database * Ledger Entries are created in the tables associated with the given district" --> The entry is labeled **Meal Sales Revenue**. <!-- Source: NXT-66384:AC "*Transaction Code:* MEALSLS ** *Transaction Description:* Meal Sales Revenue" --> (Backend transaction code: `MEALSLS` — you don't type this; it's the system's internal tag for the entry.)

What the entry contains:

- **Debit side** — your **Cash in Bank** account *and* the **prepaid balance** account, by site. <!-- Source: NXT-66384:AC "*Accounts Debited:* <Cash In Bank GL Site Sub Account> AND <Prepaid Account GL Site Sub Account>" --> (Why prepaid is debited: when a student spends down money they paid earlier, that prepaid liability goes down — so it sits on the debit side here.)
- **Credit side** — your **meal-sales** and **à la carte sales** revenue accounts, by site. <!-- Source: NXT-66384:AC "*Accounts Credited:* <Meal Sales AND A La Carte Sales GL Site Sub Accounts>" -->
- The meal-sales account follows the **revenue program** the money came from (for example, the School Breakfast Program), and the à la carte account follows the **meal type** (for example, Breakfast). <!-- Source: NXT-66384:AC "The *meal sales account* must align to the *student revenue source* (e.g., School Breakfast Program), and the *a la carte account* must align to the *student meal type* (e.g., Breakfast)." -->

🔧 **Implementer note — this is why one GL account can show two different totals on your P&L.** Each debit/credit line is tagged with the exact data point it came from, so the Profit & Loss report can total *by data point* even when several data points map to the same GL account. <!-- Source: NXT-66384:AC "each debit/credit line must be attributed to the originating data point / data source (e.g., the specific meal sales revenue data point or reimbursement data point) so the Profit & Loss report can calculate totals by data point even when one GL account is mapped to multiple data points." --> If you've ever wondered how the P&L splits a shared account, this is the mechanism.

⚠️ **Watch-outs before this will post:**

- Every meal-sales revenue data point must be mapped to a GL account first. <!-- Source: NXT-66384:AC "All Meal Sales Revenue accounts mapped to GL Accounts" --> (That's a Job 2 task.)
- The financial period has to be **open** from the posting date through today. <!-- Source: NXT-66384:AC "Financial periods must be open from the date of posting to the current date." -->
- **Every** POS period that falls inside the financial period's date range has to be **closed**. <!-- Source: NXT-66384:AC "All POS periods that fall in the selected Financial period's date range need to be closed." -->
- The entry posts dated to the **last day of the POS period**, not the day you close it. <!-- Source: NXT-66384:AC "The last day of the POS Period is used as the Posting date." -->

> 📌 **The lines always balance.** There may be several accounts on each side; the system validates that total debits equal total credits before it posts. <!-- Source: NXT-66384:AC "Note that there may be multiple accounts involved on either side of the transaction. Validate that debit and credit totals are equal." -->

---

### A2. Sales tax → posted as a liability you owe, not as revenue **(Live)**

🎯 **The job:** the tax you collected at the register is tracked as money you owe the state, ready to remit — and it never inflates your revenue.

When a POS period closes for a site, the system creates **exactly one** sales-tax entry for that site and period. <!-- Source: NXT-70304:AC "*Then* the system creates *exactly one* TAXCLCTD journal entry for that *site + POS period*." --> (Backend code: `TAXCLCTD`, "tax collected.") The entry has **two lines only**:

1. **Debit: Cash in Bank** — the net sales tax. <!-- Source: NXT-70304:AC "*Debit:* Cash in Bank = Net Sales Tax" -->
2. **Credit: Sales Tax Owed (a liability)** — the net sales tax. <!-- Source: NXT-70304:AC "*Credit:* Sales Tax Owed (Liability) = Net Sales Tax" -->

The amount is **net** tax: tax collected minus tax reversed (voids and returns) in that same POS period. <!-- Source: NXT-70304:AC "Posted Amount = *Tax Collected – Tax Reversed* (same POS period)." --> It posts dated to the **last day of the POS period**. <!-- Source: NXT-70304:AC "Posting Date = *last day of the POS period*." --> Like every posting, debits equal credits. <!-- Source: NXT-70304:AC "Total Debits = Total Credits for TAXCLCTD." -->

🔧 **Implementer note — where you'll see it on the close screen.** On the POS Period Close job for that period, this shows up as **"Sales Tax Collected."** <!-- Source: NXT-70304:AC "Appears as 'Sales Tax Collected' in POS Period Close job corresponding to the period." -->

⚠️ **Watch-out — an inactive account silently skips the tax posting.** If either the Cash in Bank account or the Sales Tax Owed account is inactive when posting runs, the system **skips** the sales-tax entry. <!-- Source: NXT-70304:AC "*Given* Cash in Bank or Sales Tax Owed is inactive *When* posting runs *Then* skip TAXCLCTD" --> Keep both accounts active or your tax liability won't post.

> 💡 **Why this matters for accuracy.** Meal-sales revenue is the **tax-exclusive** amount — the gross/total figure that includes tax must never be used for revenue posting. <!-- Source: NXT-70304:desc "*Meal Sales Revenue* = the tax-exclusive revenue amount (does *not* include sales tax)." --> <!-- Source: NXT-70304:desc "*Total / Gross Amount* = Meal Sales Revenue *plus* Sales Tax (may exist in POS, but must not be used for revenue posting)." --> That separation is what keeps your reported revenue honest.

---

## Part B — The inventory side **(Coming)**

> ⚠️ **All of Part B is upcoming.** None of these inventory entries post yet. Read this as "here's how inventory will hit your ledger," and complete the prerequisite in B1 now so you're ready when it ships.

### B1. Prerequisite — set up Valuation Categories first **(Coming)**

🎯 **The job:** tell Financials how each kind of inventory is valued and which GL accounts it should hit — *before* any inventory can post.

This is a **Job 2 prerequisite**, not an afterthought: a Valuation Category cannot be used in postings until it has **both** an Asset account (for inventory value) and an Expense account (for usage) mapped. <!-- Source: NXT-65482:AC "Every valuation category must have *both* an Asset Account and an Expense Account mapped before it can be used in postings." --> Both account fields start blank and you fill them from a searchable dropdown of your GL accounts. <!-- Source: NXT-65482:AC "Asset Account (GL account for inventory value) (this is blank and to be filled in by the user, make it a searchable dropdown of all GL accounts so they can pick the relevant one)" -->

The page shows, per category: the category name, its **valuation method** (such as FIFO, Last Received Price, Moving Average, Replacement Value, or Standard Price), the Asset account, the Expense account, and the data source. <!-- Source: NXT-65482:AC "* Valuation Category ** Valuation Method (e.g., FIFO, Last Received Price, Moving Average, Replacement Value, Standard Price) ** Asset Account ... ** Expense Account ... ** Data Source (e.g., Local, State Level, Food Distribution)" -->

⚠️ **Watch-outs that bite later:**

- **One account, one category.** Each asset or expense account can be linked to **only one** Valuation Category. <!-- Source: NXT-65482:AC "Each asset and expense account can only be linked to one valuation category." -->
- **Mapping changes are not retroactive.** Changing a category's accounts or valuation method affects **future postings only** — it never restates what's already posted. <!-- Source: NXT-65482:AC "Changes to account mappings or valuation method only affect *future postings* and do not retroactively change historical posted values." -->
- **Once it's posted, it's locked.** After a Valuation Category has any posted activity, its Asset and Expense accounts are **permanently locked**; to use different accounts you create a *new* category and move items to it. <!-- Source: NXT-65482:AC "Once a valuation category has any posted activity, its Asset and Expense GL accounts become permanently locked and cannot be edited." --> <!-- Source: NXT-65482:AC "If a district needs to change the GL accounts, they must create a new valuation category and begin using that going forward; historical categories remain frozen for audit integrity." --> The system warns you when you hit this. <!-- Source: NXT-65482:AC "Provide warning 'This valuation category already has posted activity, so its GL accounts can't be changed. To use different accounts, create a new valuation category and move the items to it. Historical mappings are locked for audit integrity.'" -->
- **You can't orphan a mapped account.** If you try to delete an asset or expense account that's linked to a category, the system blocks it and tells you to assign a different account first. <!-- Source: NXT-65482:AC "If the user tries to delete an asset or expense account linked to a valuation category on the GL Accounts page, block it and inform the user that they must first assign a different account to that valuation group" -->

> 📌 **Open question (label):** AC sources this data from "Item Management > Item Configuration > Valuation Categories" but does not state the exact in-Financials menu path or page title a user clicks to reach the mapping view. <!-- Source: NXT-65482:AC "Data is sourced from Item Managemnt > Item Configuration > Valuation Categories" --> Confirm the customer-facing navigation label with the SME before publishing.

---

### B2. What inventory close will post **(Coming)**

🎯 **The job:** when an inventory period closes, your food and supply costs land in the ledger automatically — no manual journal entries — grouped the way your reports expect.

When an inventory period transitions to **Closed** for a site, the system will start a posting job named **"Inventory Posting"** for that site and period, with no manual trigger. <!-- Source: NXT-70295:AC "*Then* the system automatically initiates a posting job named \"Inventory Posting\" for that site-period with no manual trigger required" --> Every entry is dated the **last day of the inventory period**. <!-- Source: NXT-70295:AC "*Then* every entry in the batch has a posting date of 2026-01-31" -->

**Grouping (the grain).** The system creates **one entry per entry type, per Valuation Category, per site, per period**, and each entry balances on its own. <!-- Source: NXT-70295:AC "*Then* the system creates exactly two WD entries for Site A — one for $2,000 (Purchased Food) and one for $800 (USDA Foods)" --> <!-- Source: NXT-70295:AC "*Then* total debits = total credits on that entry" --> So if one site used food from two categories, you get two separate withdrawal entries, not one blended line.

**The entry types and the lines each one writes** (all amounts come from the Inventory **Usage Report**):

| In plain language | Debit | Credit | Amount comes from |
|---|---|---|---|
| **Purchases** — stock bought in | the category's **Asset** account | **Cash in Bank** (one configured account, *not* from the category mapping) | the Purchases column <!-- Source: NXT-70295:AC "Debit → Valuation Category's Asset GL Account ** Credit → Cash in Bank GL Account (single configured account, not derived from Valuation Category mapping) ** Amount = Purchases column value from Usage Report" --> |
| **Withdrawals / usage** — stock consumed in production | the category's **Expense** account | the category's **Asset** account | the Usage value <!-- Source: NXT-70295:AC "Debit → Valuation Category's Expense GL Account ** Credit → Valuation Category's Asset GL Account ** Amount = Usage value from Usage Report" --> |
| **Add to inventory** — stock added back | the category's **Asset** account | the category's **Expense** account | the Add to Inventory value <!-- Source: NXT-70295:AC "Debit → Valuation Category's Asset GL Account ** Credit → Valuation Category's Expense GL Account ** Amount = Add to Inventory value from Usage Report" --> |
| **Transfer out** — stock sent to another site | the category's **Expense** account | the category's **Asset** account | the Transfers value <!-- Source: NXT-70295:AC "*Scenario: Transfer-out posting* ... Debit → Valuation Category's Expense GL Account ** Credit → Valuation Category's Asset GL Account ** Amount = Transfers In value from Usage Report" --> |
| **Transfer in** — stock received from another site | the category's **Asset** account | the category's **Expense** account | the Transfers value <!-- Source: NXT-70295:AC "*Scenario: Transfer-in posting* ... Debit → Valuation Category's Asset GL Account ** Credit → Valuation Category's Expense GL Account ** Amount = Transfers In value from Usage Report" --> |

(Backend codes for the curious — you never type these: purchases `PURCH`, withdrawals `WD`, add-to-inventory `ADDINV`, transfer-out `INVTRFRFR`, transfer-in `INVTRFRTO`.) <!-- Source: NXT-70295:desc "Period-close batch postings for 5 entry types: PURCH, WD, ADDINV, INVTRFRFR, INVTRFRTO." -->

🔧 **Implementer note — Purchases is the odd one out.** For every other entry type, both the debit and the credit come from the same Valuation Category mapping. Purchases is the only type where the credit side is a **single configured Cash in Bank account** instead. <!-- Source: NXT-70295:AC "Credit → Cash in Bank GL Account (single configured account, not derived from Valuation Category mapping)" --> Configure that one Cash in Bank account when you set up inventory posting.

⚠️ **Watch-out — one missing mapping blocks the entire site-period.** If *any* Valuation Category in scope is missing its Asset **or** Expense account, **nothing posts for that site-period** — not even the entry types that don't touch the unmapped category. <!-- Source: NXT-70295:AC "*Then* no posting job runs for any entry type in that site-period — including entry types that do not use the Valuation Category with the missing mapping" --> Finish all your category mappings (B1) before you expect a clean close.

⚠️ **Watch-out — it's all-or-nothing on validation.** If one entry type in the batch fails validation (for example a rounding imbalance), the **whole** site-period batch is rejected, zero entries are created, and the reason is logged. <!-- Source: NXT-70295:AC "*Then* zero entries are created for the entire site-period batch" --> <!-- Source: NXT-70295:AC "*Then* the entire posting batch for that site-period is rejected and the error is logged in the Posting Activity Log" -->

---

### B3. What you'll see in Job 8 (Journal/Ledger) and Job 10 (Activity Log) for inventory **(Coming)**

Posted inventory entries will appear in the **Journal and Ledger right alongside** your POS and manual entries. <!-- Source: NXT-70295:AC "*Then* the posted inventory entries appear alongside POS and manual entries" --> You'll be able to tell them apart: each one shows its **source module ("Inventory")**, its entry-type code and name (for example "Withdrawals"), the site, and the Valuation Category. <!-- Source: NXT-70295:AC "*Then* it displays source module (\"Inventory\"), entry type code and name (e.g., \"WD — Withdrawals\"), site, and Valuation Category" --> Open any entry and the detail will show the entry type, the Valuation Category, the **list of source transaction IDs** from inventory that were rolled into it, the posting date, and the site. <!-- Source: NXT-70295:AC "** Entry type (e.g., \"WD — Inventory Withdrawals\") ** Valuation Category ** List of source transaction IDs from the inventory module that were aggregated into the entry ** Posting date ** Site" --> You can filter the ledger by site, fiscal year, financial period, GL account, and entry type. <!-- Source: NXT-70295:AC "*Then* entries are filterable by site, fiscal year, financial period, GL account, and entry type" -->

In **Job 10 (Posting Activity Log)**, a successful inventory close logs a confirmation for the site-period; a failure logs the **specific reason**. <!-- Source: NXT-70295:AC "*Then* a log entry confirms successful completion for that site-period" --> <!-- Source: NXT-70295:AC "*Then* a log entry shows the specific failure reason for that site-period" -->

🔧 **Implementer note — reopening and re-closing a period (how corrections work).** If you reopen a posted inventory period, the posting batch in the Periods view shows that state. <!-- Source: NXT-70295:AC "*Then* the corresponding posting batch in the Periods view reflects this state" --> When you re-close it, the system reposts **only if you have the repost setting enabled** in Periods — otherwise nothing happens. <!-- Source: NXT-70295:AC "*Then* the system automatically initiates a repost for that site-period" --> <!-- Source: NXT-70295:AC "*Given* a previously-posted inventory period has been reopened and the user has the repost setting disabled in Periods *When* the period is re-closed *Then* no repost is initiated" --> A repost never edits or deletes the original entries — they stay in the ledger with their original values. <!-- Source: NXT-70295:AC "*Then* the original entries remain unmodified and undeleted with their original values" --> Instead it writes **reversal entries** dated to the **original posting date** (not today), with every amount inverted (debits become credits), each referencing the entry it reverses; then it posts a fresh batch under the same rules. <!-- Source: NXT-70295:AC "*Then* each reversal entry's posting date equals the original entry's posting date (last day of the inventory period), not today's date" --> <!-- Source: NXT-70295:AC "*Then* all amounts are the exact inverse of the originals (debits become credits, credits become debits) and each reversal references the original entry it reverses" -->

> ⚠️ **Known limitation — two kinds of waste won't tie out.** Waste recorded through a withdrawal reason code **is** included in the withdrawal postings above. Production-record waste (from Insights) uses fair-market-value estimates and **will not reconcile** to those withdrawal-based postings. This is a documented product limitation, not a bug. <!-- Source: NXT-70295:AC "Waste/spoilage via withdrawal reason codes is included in WD postings." --> <!-- Source: NXT-70295:AC "Production-record waste (Insights) uses fair market value estimates and will not reconcile to withdrawal-based postings." --> <!-- Source: NXT-70295:desc "This is a *documented product limitation*, not a bug." -->

> 📌 **Source-of-truth note:** every dollar amount in inventory postings comes from the inventory module's own valuation (the Valuation/Usage reports). Financials does **not** recompute inventory values — it consumes what inventory provides. <!-- Source: NXT-70295:desc "Financials does not independently calculate inventory values; it consumes what inventory provides." -->

---

### B4. A finer purchase grain is being added: by Vendor **(Coming)**

🎯 **The job:** keep purchase postings manageable in the GL while still being able to reconcile them back to what each vendor was paid.

A later refinement will post purchases at **Valuation Category × Vendor** detail — one total per site, period, vendor, and category. <!-- Source: NXT-70620:AC "*Then* exactly 3 debit/credit pairs are created (V1/Food, V1/NonFood, V2/Food), and no receipt/item-level pairs exist." --> Each pair debits the category's **Inventory Asset** account and credits the configured **Cash in Bank** account. <!-- Source: NXT-70620:AC "*Then* Debit = VC's Inventory Asset GL *And* Credit = configured Cash in Bank GL." --> The posted amount uses the **Total Receipt Amount**, not market value. <!-- Source: NXT-70620:AC "the posted total equals *Total Receipt Amount / Amount*, not Market Value." -->

⚠️ **Watch-outs (when this ships):**

- A receipt with no vendor is grouped under **"Unknown Vendor"** and still posts; totals still tie to the period's Total Receipt Amount. <!-- Source: NXT-70620:AC "*Then* amounts from those receipts are included under Vendor = \"Unknown Vendor\" *And* totals still tie to the period's Total Receipt Amount." -->
- A missing category mapping blocks posting and the error **lists every** missing mapping, not just the first. <!-- Source: NXT-70620:AC "*Then* nothing posts *And* the error lists VC2 as missing (and any other missing mappings)." -->
- A closed period with **zero receipts** posts nothing and the job is still marked **successful** with "0 entries created." <!-- Source: NXT-70620:AC "*Then* zero PURCH entries are created *And* job is marked successful with \"0 entries created.\"" -->

> 📌 **Open relationship note:** NXT-70620 (Vendor-level detail) and NXT-70295's purchase entry (category-level) both describe the purchase posting and are at different refinement stages. Confirm with the SME which grain ships first so the guide states one, not both, as current. *(Interpretation, not from AC.)*

---

## Part C — Reimbursements and other inventory entries on the roadmap **(Coming)**

> ⚠️ Everything in Part C is upcoming (status **New**). These are specified but not built; treat as roadmap.

### C1. Reimbursement Claim and Reimbursement Received **(Coming)**

🎯 **The job:** your state and federal meal-program money flows into the ledger as receivables when you claim it, then as cash when it arrives.

Two separate entries, created **by site**: <!-- Source: NXT-66385:AC "Ledger entries are created by site for each claim and reimbursement." -->

- **Reimbursement Claim** — **Debit: Due from Federal Funds** (a receivable), **Credit: the reimbursement revenue account**; dated the **last day of the claim period**. <!-- Source: NXT-66385:AC "*Reimbursement Claim* *** *Debit:* Due from Federal Funds (Asset) *** *Credit:* Reimbursement Program System Accounts (Revenue)" --> <!-- Source: NXT-66385:AC "_Reimbursement Claim_ (GLEntryTypeCd = RMBRSCLM) entries use the last day of the claim period as posting date." --> (Backend codes: `RMBRSCLM`; receivable `DUEFEDF`; revenue `RMBRSMNT`.)
- **Reimbursement Received** — **Debit: Cash in Bank**, **Credit: Due from Federal Funds** (clearing the receivable); dated the **current date**. <!-- Source: NXT-66385:AC "*Reimbursement Received* *** *Debit:* Cash in Bank (Asset) *** *Credit:* Due from Federal Funds (Asset)" --> <!-- Source: NXT-66385:AC "_Reimbursement Received_ (GLEntryTypeCd = RMBRSRCVD) entries use the current date as posting date." --> (Backend codes: `RMBRSRCVD`; cash `CASHBNK`.)

These entries will be visible in the General Ledger journal and View Ledger, with site-level drill-down, and flow into financial statements as revenue and assets. <!-- Source: NXT-66385:AC "Entries are visible in the General Ledger journal and View Ledger pages. ** Users can drill down to see site-level breakdowns. ** Reimbursement claim and received amounts flow into financial statements as revenue and assets." -->

⚠️ **Watch-out (when this ships) — resubmitting a claim reverses the old one first.** If a claim is recreated and resubmitted, the system auto-generates rollback entries that reverse the originals (the debit/credit sides swap) **before** posting the new claim and received entries from the updated data. <!-- Source: NXT-66385:AC "If a claim is recreated and resubmitted, rollback ledgers are automatically generated before new postings." --> <!-- Source: NXT-66385:AC "After rollback entries are posted, the new Claim and Reimbursement entries are created using the updated data." -->

> 📌 **Conflict to flag (don't pick silently):** NXT-66385 says Reimbursement *Received* posts to the **current date**, while the inventory-side stories post everything to the period's last day. These are different flows, so both can be right — but confirm the **Received = current date** rule with the SME, since it's the one posting in this whole section that does *not* use a period-end date. <!-- Source: NXT-66385:AC "_Reimbursement Received_ (GLEntryTypeCd = RMBRSRCVD) entries use the current date as posting date." -->

### C2. Other inventory entries specified but not yet built **(Coming)**

These overlap with the inventory engine in B2 and are tracked separately; the consistent rule across all of them is **posting date = last day of the inventory period** and **rollbacks reverse the entries** on a repost. <!-- Source: NXT-66386:AC "Posting date = last day of inventory period." --> <!-- Source: NXT-66386:AC "Rollbacks: Reverse entries if reposted." -->

- **Inventory usage, including commodity (USDA) usage** — usage debits Expense, credits Asset; commodity usage is the same shape valued at **Standard Price**, and both flow to the P&L as food expense and reduce inventory on the Balance Sheet. <!-- Source: NXT-66386:AC "_Usage (GLEntryTypeCd: WD)_ → Debit Expense, Credit Asset. ** _Commodity Usage (GLEntryTypeCd: COMMUSG, Value = Standard Price)_ → Debit Expense, Credit Asset." --> <!-- Source: NXT-66386:AC "Entries visible in GL journal/View Ledger, flow to P&L as food expense and Balance Sheet as reduced inventory." -->
- **Withdrawals / waste** — debits Expense, credits Asset, so unusable stock leaves assets and is recorded as waste expense. <!-- Source: NXT-66389:AC "_Withdrawal/Waste (GLEntryTypeCd: WD or WASTE depending on setup)_ → Debit Expense, Credit Asset." --> <!-- Source: NXT-66389:AC "Entries flow into GL and financial statements as waste expense." -->
- **Inventory transfers (site ↔ warehouse)** — debits the receiving site's Asset, credits the warehouse's Asset, so stock movement shifts balances between locations with **zero net effect** across the district. <!-- Source: NXT-66387:AC "_Warehouse Receives (GLEntryTypeCd: WHIRCV, Multisite)_ → Debit Site Asset, Credit Warehouse Asset." --> <!-- Source: NXT-66387:AC "net effect is zero across district but shifts balances between locations." -->
- **Warehouse fees (delivery, processing)** — debits the site's Expense, credits the warehouse's Expense, capturing those costs as operational expense. <!-- Source: NXT-66388:AC "_Warehouse Receives Commodity Fees (GLEntryTypeCd: None, Multisite)_ → Debit Site Expense, Credit Warehouse Expense." --> <!-- Source: NXT-66388:AC "Entries flow into food cost/operational expense reporting." -->

⚠️ **Watch-out — these stories contradict the "Approve/Post buttons are gone" promise.** Usage/commodity posting AC describes an **Approve / Post / Reapprove** control governed by a checkbox-state matrix. <!-- Source: NXT-66386:AC "The availability of Approve, Post, and Reapprove follows the checkbox state matrix (see attached rules)." --> That conflicts with the guide's headline claim that posting is fully automatic with no Post button. This is part of the broader Job 10 contradiction (Cluster C1) — flag it; do not present "fully automatic, no buttons" as settled while these stories are in flight.

> 📌 **Open question (warehouse codes):** NXT-66388 (warehouse fees) and one transfer line in NXT-66387 state the entry type code as "None," and NXT-66389 says the waste code is "`WD` or `WASTE` depending on setup." <!-- Source: NXT-66388:AC "_Warehouse Receives Commodity Fees (GLEntryTypeCd: None, Multisite)_" --> <!-- Source: NXT-66389:AC "_Withdrawal/Waste (GLEntryTypeCd: WD or WASTE depending on setup)_" --> The user-facing entry-type label is not finalized in AC — leave it as a placeholder and confirm with the SME before publishing.

---

## Under the hood — why this all balances (for the curious) **(Coming)**

🔧 You don't operate this directly, but it's worth knowing what produces these lines. A single posting engine takes each source transaction (meal sales, inventory, payroll), looks up the matching debit/credit rule in one central rules table, and swaps the system-account codes in that rule for **your** district's actual GL accounts using your account mapping. <!-- Source: NXT-65485:AC "For each transaction, it finds the matching debit and credit rule from our central rules table." --> <!-- Source: NXT-65485:AC "It replaces the system account codes from the rule with the correct GL accounts for that customer, using their account mapping." --> It writes one debit line and one credit line per transaction with matching amounts so the ledger stays balanced. <!-- Source: NXT-65485:AC "It creates one debit line and one credit line for each transaction, making sure the amounts match so the ledger stays balanced." -->

This is why two things in this guide are reliably true: a transaction that **can't** find a rule or a mapped account still shows up — flagged as needing a fix rather than silently dropped <!-- Source: NXT-65485:AC "If a transaction can't find a matching rule or account mapping, it still shows in the results, but is marked as needing a fix." --> — and re-running posting for the same period and data always produces the **same** result. <!-- Source: NXT-65485:AC "Running the procedure again for the same period and data will always give the same results." -->

---

## Quick reference — what posts, what's live

| Flow | Debit | Credit | When it posts | Status |
|---|---|---|---|---|
| Meal-sales revenue | Cash in Bank + Prepaid balance | Meal sales + À la carte | POS period close, dated period's last day | **Live** |
| Sales tax | Cash in Bank | Sales Tax Owed (liability) | POS period close, dated period's last day | **Live** |
| Purchases | Category Asset | Cash in Bank (one configured acct) | Inventory period close, dated period's last day | (Coming) |
| Withdrawals / usage / waste | Category Expense | Category Asset | Inventory period close | (Coming) |
| Add to inventory | Category Asset | Category Expense | Inventory period close | (Coming) |
| Transfer in / out | Asset ↔ Expense (per direction) | (per direction) | Inventory period close | (Coming) |
| Reimbursement Claim | Due from Federal Funds | Reimbursement revenue | Claim period's last day | (Coming) |
| Reimbursement Received | Cash in Bank | Due from Federal Funds | Current date | (Coming) |

<!-- Live rows traced above to NXT-70304 / NXT-66384 AC; (Coming) rows to NXT-70295 / NXT-70620 / NXT-66385 AC. -->

---

### Drafting notes (not for the published guide)

- **Live vs Coming:** only NXT-70304 (sales tax) and NXT-66384 (meal sales) are Done Done and written in present tense. Everything in Parts B and C is upcoming and tagged **(Coming)** per status honesty.
- **Jargon translated:** TAXCLCTD→"sales-tax entry," MEALSLS→"Meal Sales Revenue entry," PURCH/WD/ADDINV/INVTRFRFR/INVTRFRTO→plain names, WHIRCV/COMMUSG→plain names, RMBRSCLM/RMBRSRCVD/DUEFEDF/CASHBNK/RMBRSMNT→plain names. Raw codes survive only inside `<!-- Source -->` comments.
- **No invented specifics:** every exact label/value (account names, "Sales Tax Collected," "Inventory Posting," "Unknown Vendor," "0 entries created") is quoted from AC. Where AC gave no user-facing label (Valuation Categories nav path; warehouse/waste entry-type codes), an **Open question** is raised instead of inventing one.
- **Contradictions surfaced, not resolved:** the NXT-66386 Approve/Post checkbox-matrix vs. the guide's "buttons are gone" promise (ties to Cluster C1); Reimbursement Received's current-date posting; and the NXT-70620 vs NXT-70295 purchase-grain overlap are all flagged for SME decision rather than silently picked.
