<!--
GUIDE UPDATE — Cluster C5
Source coverage row: FINANCIALS-2.0-COVERAGE-REPORT.md §3, Cluster C5 (P1)
Maps to: Job 2 — Account Mapping (+ "What changed in 2.0" framing)
Grounding: every product-behavior sentence carries an inline <!-- Source: NXT-####:AC "verbatim" --> comment.
RN is empty in this fixture; AC is the highest-trust source. `desc` is supporting context only and is never
the sole basis for a behavior claim. Backend codes (PPACC, RTNCHCKPOS, TAXCLCTDPP, MEALSLS, PREPLIAB-RECLASS)
are translated to user-facing language in prose; the raw code stays inside the citation comment only.
STATUS: NXT-70305, NXT-70909, NXT-69981 are all status=New -> everything in this section is UPCOMING and is
tagged "(Coming)". Nothing here is present-tense shipped behavior.
Citation comments are STRIPPED before any customer-facing build (same rule as the guide).
-->

# Job 2 refresh — the single "Prepaid Account" bucket is splitting into two

> **Where this lands.** This is an addition to **Job 2 — "Tell the system where to post each kind of transaction"** and a correction to two lines in the **"What changed in 2.0"** table and the **Glossary**. It does not replace Job 3 (the per-site vs. per-district radio button) — that choice still applies; see the watch-out at the end.

> ⚠️ **Status: this whole section is (Coming).** Every behavior below comes from stories that are still **New** in Jira (NXT-70305, NXT-70909, NXT-69981). None of it is live yet. Read it so you map correctly when it ships and so you don't promise a customer the *old* single-bucket behavior during Phase 2/3 setup — but do **not** demo it as working today.

---

## (Coming) What's changing, in one breath

**TL;DR:** The one legacy "Prepaid Account" bucket is going away. In its place you'll map **two** prepaid liability buckets — one for money taken at the register, one for money taken online — and the system will sort prepayments into them by how the funds were collected. Sales tax is also being pulled out of revenue into its own liability bucket, and cash-drawer over/short gets its own bucket too. All three are mapping decisions you make on the Account Mapping page, so getting them right is part of Job 2.

This matters because **mis-mapping here moves real money to the wrong place.** A prepaid liability mapped to the wrong GL account, or sales tax left sitting in revenue, is the kind of error a district auditor finds — not the kind the posting engine catches for you.

---

## (Coming) Change 1 — One prepaid bucket becomes two: POS vs. Online

In legacy and in today's guide there is a single prepaid bucket. That is being retired. <!-- Source: NXT-70909:AC "\"Prepaid Account\" (PPACC) is no longer referenced in active posting rules, business rules drawers, dropdowns, template entries, or new configuration/UI surfaces. Historical journal entries and migration artifacts are not in scope." --> When this ships, opening Account Mapping and looking under the customer-accounts area of Liabilities will show that the single prepaid data point is gone, replaced by two new ones: a **POS prepaid liability** bucket and an **Online prepaid liability** bucket. <!-- Source: NXT-70305:AC "the single \"Prepaid Account\" data point no longer exists and has been replaced by two new data points: *POS Prepaid Liability* and *Online Prepaid Liability*" -->

The split is by **how the funds were collected**, not by program or by student:

- The **POS** bucket is for physical funds — cash and check — taken at the register. <!-- Source: NXT-70305:AC "Description|Liability account for physical funds (Cash/Check) received at the Point of Sale" -->
- The **Online** bucket is for digital funds — credit card and bank draft (ACH) — taken online or through a third-party payment source. <!-- Source: NXT-70305:AC "Liability account for digital funds (Credit/ACH) received via Online or 3rd Party sources" -->

Both new buckets fill automatically — they're driven by the POS period close, not entered by hand — so on the mapping page they behave like the other automatic data points: you point each one at a GL account, you don't post to them manually. <!-- Source: NXT-70305:AC "|Source|POS Period Close|POS Period Close|" --> <!-- Source: NXT-70305:AC "|Type|Automatic|Automatic|" -->

🔧 **Implementer:** This is two GL accounts where you used to map one. Add it to the same kickoff prep question you already ask for Job 2 ("how many GL accounts for meal sales?"): the district's finance team needs to decide **up front** whether physical-funds prepayments and online prepayments land in the same GL account or two different ones, because the whole reason this split exists is so the daily cash-drawer deposit reconciles separately from the monthly online/processor settlement. <!-- Source: NXT-70305:desc "As a Child Nutrition Director I want student prepayment transactions to automatically post to the general ledger split by source (POS vs. Online/3rd Party) So that I can easily reconcile physical bank deposits against merchant processor reports before exporting to the district ERP" --> *(Persona/intent from `desc` — supporting context, not a behavior claim.)*

⚠️ **The mapping-completeness rule still bites — now twice.** Job 2 already warns that one unmapped active data point halts all posting; that existing rule now applies to **two** prepaid buckets instead of one — map both, don't map one and forget the other. *(The "halts all posting" rule is the guide's existing Job 2 watch-out, not a new claim. This ticket's `desc` states the intent that "both new data points [must] be mapped to GL accounts before posting can occur" <!-- Source: NXT-70305:desc "System requires both new data points to be mapped to GL accounts before posting can occur." --> — supporting context; the ticket's AC does not restate the unmapped-posting gate, so it is not asserted here as new AC behavior.)*

### (Coming) How prepayments get sorted into the two buckets

When the POS period closes, the system looks at each prepayment, reads the **student's current enrollment site**, and groups the journal entries by that site. <!-- Source: NXT-70305:AC "the system retrieves the *Student's Current Enrollment Site* for each transaction." --> <!-- Source: NXT-70305:AC "generates journal entries grouped by that *Enrollment Site*" --> Cash/check prepayments credit the **POS** bucket; online/third-party prepayments credit the **Online** bucket; in both cases the matching debit is to Cash in Bank. <!-- Source: NXT-70305:AC "*Credit:* POS Prepaid Liability (Liability)" --> <!-- Source: NXT-70305:AC "*Credit:* Online Prepaid Liability (Liability)" --> <!-- Source: NXT-70305:AC "*Debit:* Cash in Bank (Asset)" -->

> 📝 **Interpretation (not a source quote):** "groups the journal entries by enrollment site" is the same idea as Job 3's **Distributed (Enrollment Site)** model. The two are consistent. AC for this split states the per-site grouping explicitly; see the Job 3 watch-out below for how the district-level (Centralized) choice interacts.

One default worth knowing: when a prepayment, bonus, or refund has **no source recorded** (the source field is null, blank, or missing), the system falls back to the **POS** bucket — it does not stall or drop the entry. <!-- Source: NXT-70305:AC "|Source is null, blank, or missing on any bonus|{{null}} / {{''}}|Bonus Expense Account|POS Prepaid Liability _(default)_|" --> <!-- Source: NXT-70305:AC "|Original Source is null or missing|{{null}} / {{''}}|POS Prepaid Liability _(default)_|Cash in Bank (Asset)|" -->

---

## (Coming) Change 2 — When meal sales spend prepaid funds, the buckets self-correct at period end

This is the part that surprises people, so read it before you panic at a negative balance.

At the register, a student's balance is **one pooled balance** — the POS doesn't know whether a given dollar was originally a cash deposit or an online deposit. <!-- Source: NXT-70909:desc "At consumption time, the POS has a single pooled student balance. It does not track whether funds originated from POS or Online deposits." --> *(Context from `desc`.)* So every meal sale that draws down prepaid funds debits the **POS** prepaid bucket for the prepaid portion used, regardless of how the money originally came in. <!-- Source: NXT-70909:AC "Debit *POS Prepaid Liability* — full prepaid portion used (not split by funding source)" -->

That means the POS bucket can go **negative** — it's being drawn down faster than physical-funds deposits replenish it, because some of that spending was really online money. To square that up, after all the deposit and meal-sale entries finish for a site and period, the system runs a one-time **reclassification** per posting level per period: <!-- Source: NXT-70909:AC "Reclassification (system-generated, runs once per posting level per period):" -->

- If the POS bucket's ending balance is **zero or positive**, nothing happens — no entry. <!-- Source: NXT-70909:AC "If zero or positive: no entry generated." -->
- If it's **negative**, the system generates one entry that moves funds from the Online bucket into the POS bucket (debit Online prepaid liability, credit POS prepaid liability). <!-- Source: NXT-70909:AC "If negative: generate one entry — Debit Online Prepaid Liability, Credit POS Prepaid Liability." -->
- That transfer is **capped at whatever is actually in the Online bucket** — it never moves more than Online has, even if the POS shortfall is bigger. <!-- Source: NXT-70909:AC "*The amount is capped at the ending ledger balance of Online Prepaid Liability at the same posting level* — never the full absolute value of the negative." -->

⚠️ **A leftover negative after reclassification is correct, not a bug.** If the Online bucket couldn't cover the whole shortfall, the POS prepaid bucket stays negative — and that remaining negative is **real student meal debt** (charge meals are permitted under USDA rules and state anti-lunch-shaming laws). It's expected, the meal-sale entries were never altered, and it's the CN Director's job to work it through normal debt collection. <!-- Source: NXT-70909:AC "Any remaining negative balance on POS Prepaid Liability after reclassification is real — it reflects student meal debt (charge meals permitted under USDA regulations and state anti-lunch-shaming laws). This is accurate and expected. The CN Director must reconcile this through their normal debt collection process." --> The system does **not** create a separate accounts-receivable or student-debt bucket for it — don't go looking for one. <!-- Source: NXT-70909:AC "*This story does not create or post to a separate accounts receivable or student debt data point.*" -->

🔧 **Implementer:** Tell the customer about this *before* go-live, or your first support call after the first period close will be "why is our prepaid liability negative?" The answer is two-part: (1) the reclassification sweep ran and Online was already empty, and (2) what's left is meal debt to collect, not a posting error.

> 📝 **Reposting note (Interpretation of AC):** if a district reopens and reposts a prior period, only **that period's** reclassification entry is recalculated; the individual meal-sale entries don't change, and later periods may re-run their reclassification too because each one reads the running balance. <!-- Source: NXT-70909:AC "If a prior period is reposted, only that period's reclassification entry is regenerated based on the recalculated ending ledger balances. Consumption entries in that period are stateless and do not change. Subsequent periods' reclassification entries may also need regeneration since they read cumulative balances — but their consumption entries remain untouched." --> You won't trigger this by hand — it's automatic — but it explains why a reposted period's prepaid numbers can shift without you touching the meal entries.

⚠️ **You can't post this reclassification yourself, and it won't be in the Template Entries dropdown.** It's system-generated only, and it's flagged so it stands out in the Journal and the Posting Activity Log. If you see a "Prepaid Liability Reclassification" line, the system wrote it — that's expected. <!-- Source: NXT-70909:AC "The reclassification entry does not appear in the template entries dropdown — it is system-generated only and must be visually distinguishable in the journal and Posting Activity Log." -->

> **Open question (do not invent a UI string):** AC gives the entry **description** format as `Prepaid Liability Reclassification | [Period Month Year]` <!-- Source: NXT-70909:AC "Entry description: {{Prepaid Liability Reclassification | [Period Month Year]}}" --> but does **not** state the exact on-screen *label/badge* that makes it "visually distinguishable" in the Journal and Posting Activity Log. Do not write a label (e.g. a color or an icon name) until product confirms it.

---

## (Coming) Change 3 — A couple of related prepaid rules also move to the new buckets

Two legacy rules that used to touch the single prepaid bucket are being re-pointed at the new POS bucket. You don't map these separately — they ride on the POS prepaid mapping — but knowing they exist prevents confusion when you see them in the ledger:

- **Returned checks** reverse against the **POS** bucket (checks are physical, register-only). Worth flagging: a returned-check reversal is logged by a district user in the **back-office account-management** screen, **not** at the register. <!-- Source: NXT-70909:AC "Debit POS Prepaid Liability; Credit Returned Checks (Liability)" --> <!-- Source: NXT-70909:AC "The returned check reversal is logged by a district user in the back-office account management module, not at the POS terminal." -->
- **Sales tax collected on a prepaid payment** also debits the **POS** bucket; if that pushes the bucket negative, the period-end reclassification in Change 2 corrects it. <!-- Source: NXT-70909:AC "Debit POS Prepaid Liability; Credit Sales Tax Owed" --> <!-- Source: NXT-70909:AC "Sales tax is collected only at POS (confirmed in refinement). Always debits POS Prepaid Liability. If this contributes to a negative balance, the reclassification in Rule 4 corrects it." -->
- **Account adjustments** (manually adding or reducing a balance) let the user pick which bucket — POS or Online — the adjustment hits, because the user knows the source. <!-- Source: NXT-70909:AC "Debit Account Adjustments (Expense); Credit POS Prepaid Liability *or* Online Prepaid Liability" --> <!-- Source: NXT-70909:AC "Manual entries — the user selects which data point." -->

🔧 **Implementer:** The old single "Prepaid Account" name shouldn't appear anywhere in the new config once this ships — not in the dropdowns, not in the business-rules drawers, not in template entries. <!-- Source: NXT-70909:AC "\"Prepaid Account\" (PPACC) is no longer referenced in active posting rules, business rules drawers, dropdowns, template entries, or new configuration/UI surfaces." --> If a customer screenshot still shows "Prepaid Account," that environment hasn't picked up the change yet.

---

## (Coming) Change 4 — Sales tax comes out of revenue into its own liability bucket

Today the guide treats taxable sales as revenue. That's changing: on a taxable sale, the system splits the line into a **revenue portion** and a **sales-tax portion**, and posts them to two different places. <!-- Source: NXT-69981:AC "Total Amount = Revenue Portion + Sales Tax Portion" -->

- The **revenue portion** credits the revenue GL account you choose on the Account Mapping page — same as before. <!-- Source: NXT-69981:AC "Credit Revenue Portion to the mapped revenue GL account selected via Account Mapping UI." -->
- The **sales-tax portion** credits a separate **sales-tax-owed liability** account, because the tax isn't your revenue — it's money you owe the taxing authority. <!-- Source: NXT-69981:AC "Credit Sales Tax Portion to the system-configured \"Sales Tax Owed\" liability GL account." -->

⚠️ **Sales tax must never land in the revenue account.** This is the whole point of the split — keeping collected tax out of reported revenue. <!-- Source: NXT-69981:AC "Sales tax must never be credited to the mapped revenue GL account." -->

Which sales are taxable: adult, staff, and visitor meals, plus taxable à-la-carte items. <!-- Source: NXT-69981:AC "Taxable sales include Adult, Staff, Visitor, and taxable A La Carte transactions." -->

> **Open question (do not invent a UI string):** AC names the destination as a "system-configured \"Sales Tax Owed\" liability GL account" but doesn't say whether the implementer maps it on the **same Account Mapping page** as the other data points or in a separate system-settings screen, nor the exact data-point row label shown there. Confirm the mapping location/label before writing a click-path step.

🔧 **Implementer:** Add a "do you collect sales tax, and on what?" question to your Account Mapping prep. If they do, the sales-tax-owed liability account is one more mapping to confirm — and the customer's finance team will want to see tax broken out of revenue, so this is a selling point, not just a chore.

---

## (Coming) Change 5 — Cash-drawer over/short gets its own bucket: Deposit Variances

When the cash drawer doesn't reconcile at **Shift Close** — it's over or short — that difference posts to a dedicated **Deposit Variances** bucket, using whatever GL account you mapped it to on the Account Mapping page. <!-- Source: NXT-69981:AC "When cash over/short differences are detected during Shift Close" --> <!-- Source: NXT-69981:AC "Post the variance amount to the \"Deposit Variances\" data point." --> <!-- Source: NXT-69981:AC "The mapped GL account for \"Deposit Variances\" is used for posting (as configured in Account Mapping)." -->

🔧 **Implementer:** This is one more Account Mapping row to confirm with the customer's finance team — they'll usually have a specific GL account for cash over/short already, so ask for it during the mapping session rather than letting it default.

---

## (Coming) Glossary + "What changed in 2.0" — lines to correct when this ships

Two existing lines in the guide assume the single bucket and will be wrong once C5 ships. Flag them now; update them at release:

- **Glossary / vocabulary:** the legacy single prepaid bucket → **two** buckets, a POS prepaid liability and an Online prepaid liability, split by how funds were collected. <!-- Source: NXT-70305:AC "the single \"Prepaid Account\" data point no longer exists and has been replaced by two new data points: *POS Prepaid Liability* and *Online Prepaid Liability*" -->
- **"What changed in 2.0" table:** add a row — *You used to* park all prepaid money (and sales tax) in one or two lumped buckets → *Now you* map prepaid by collection method (POS vs. Online) and keep sales tax in its own liability, so bank-deposit and online-settlement reconciliation, and tax remittance, each stand on their own. <!-- Source: NXT-70305:desc "District Finance requires these to be separated. The daily cash drawer deposit needs to reconcile independently from the monthly merchant processor settlement." --> <!-- Source: NXT-69981:AC "Sales tax must never be credited to the mapped revenue GL account." --> *(Reconciliation rationale from `desc` — supporting; the behavior claim is AC-backed.)*

---

## (Coming) Watch-out — how this interacts with Job 3 (per-site vs. per-district)

Job 3's radio button still applies. The new prepayment entries are grouped by the **student's current enrollment site**, which is the Distributed (Enrollment Site) model. <!-- Source: NXT-70305:AC "generates journal entries grouped by that *Enrollment Site*" --> AC for the new buckets also defines the site field as *"Enrollment Site or Central Office, per district setting"* — i.e. it honors the Job 3 choice. <!-- Source: NXT-70305:AC "site *=* {{Enrollment Site or Central Office, per district setting)}}" -->

> 📝 **Interpretation, flagged for review:** Job 3 today lists "Pre Payment (POS + Online)" as one of the activities its site/district setting controls. The C5 split breaks that single "Pre Payment" line into two buckets. The two are consistent (both honor "per district setting"), but **Job 3's activity list should be updated** to say POS Prepaid and Online Prepaid separately once C5 ships. This is a wording reconciliation, not a behavior conflict — surfacing it so it isn't missed.

---

## Open questions for the SME / product owner (consolidated)

1. **Exact data-point row labels on the Account Mapping page.** AC gives the data-point *names* "POS Prepaid Liability" / "Online Prepaid Liability" and descriptions, but the guide should confirm these render verbatim as the **on-screen labels** before quoting them as UI strings. (Currently treated as the data-point names from AC, not asserted as pixel-exact UI.) <!-- Source: NXT-70305:AC "*POS Prepaid Liability* and *Online Prepaid Liability*" -->
2. **Sales-tax-owed mapping location + label.** Same Account Mapping page or a separate system-settings screen? Exact row label? (Change 4.)
3. **Reclassification entry's visual treatment.** AC says it must be "visually distinguishable" in the Journal and Posting Activity Log but doesn't state the label/badge/color. (Change 2.)
4. **Deposit Variances row label** on the Account Mapping page — AC gives the data-point name "Deposit Variances"; confirm it's the on-screen label. (Change 5.) <!-- Source: NXT-69981:AC "Post the variance amount to the \"Deposit Variances\" data point." -->
5. **Account-adjustment data-point picker.** AC says the user "selects which data point" (POS vs. Online) for a manual account adjustment but doesn't describe the picker control. Don't write the click-path until confirmed. <!-- Source: NXT-70909:AC "Manual entries — the user selects which data point." -->
