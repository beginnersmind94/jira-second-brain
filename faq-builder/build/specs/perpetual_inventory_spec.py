TITLE = 'Perpetual Inventory'
OUT_BASENAME = 'PrimeroEdge-Perpetual-Inventory-FAQ'
INTRO = 'This FAQ answers the most common questions about the PrimeroEdge Perpetual Inventory function in the Inventory module. Every answer is drawn from real PrimeroEdge Customer & Expert Care support cases. It is written for site and district nutrition staff who use Perpetual Inventory to check what is on hand and who need to understand why the numbers sometimes look wrong. More broadly, perpetual inventory is the running, system-maintained on-hand balance; periodic physical counts reconcile it against the shelf, and the adjustments that fall out of that reconciliation roll forward into Financials.'
NAV_NOTE = 'Perpetual Inventory is reached from Inventory -> Inventory -> Perpetual Inventory. Pick a Site, choose Show All Inventory Items or Show Only On Hand Inventory Items, optionally narrow by Item Category or Item Description/Item, then click Apply. Perpetual inventory is what the system thinks you have on hand based on what has been entered - receipts, withdrawals, transfers, and physical counts. If the on-hand number does not match the shelf, it almost always means a transaction was missed, entered twice, or backdated, not that the count itself is broken.'
SECTIONS = [
    ('Finding and printing your perpetual inventory', [
        ('How do I print my perpetual inventory report?',
         ['Go to Inventory -> Inventory -> Perpetual Inventory, choose your Site and search criteria (for example an Item Category), and click Apply. Then click Print Perpetual Inventory to view the report based on what you searched for. There is also a Printable Page option, and an Export icon if you want to save the data in another file format to print or keep.', "The report lists each item's Item Description, Units, Whole Units, and Broken Units, grouped by Storage Category and Item Category."],
         'Tickets 295285, 301390'),
        ('An item I have on the floor is not showing in Perpetual Inventory. Why, and how do I add it?',
         ["The most common reason is the view you are using. If you have Show Only On Hand Inventory Items selected and the item's on-hand balance is zero, it will not appear, and you may see 'no records to display.' Switching to Show All Inventory Items will show items even when the balance is zero.", "If the item genuinely is not in the system's inventory yet, you add it through the Add to Inventory process: go to that item at the correct site (for example the warehouse), add the quantity for today, and finalize the process. Once the addition is completed and saved, the quantity on hand updates and the item appears in perpetual inventory. In support cases where an item never showed up, the add had either not been finished or not been saved. Customer & Expert Care can walk you through the steps or do a screen share if it does not take."],
         'Tickets 298450, 316647'),
        ("Can I print an inventory count sheet before I open (start) the month's physical inventory?",
         ['Yes. You can start a physical inventory and print the count sheet from it without finishing the count. In one support case staff were told to start the inventory just to generate and print the count sheet, then use that sheet to do the physical count.'],
         'Tickets 299108'),
    ]),
    ('Why the on-hand number can look wrong', [
        ('Why does an item still show a full quantity on hand after I used it through production?',
         ['This usually happens when the production withdrawal did not actually pull the item out of inventory. In one case an item used during a promotion still showed the full amount ordered because the single-ingredient recipe was not linked to the stock item in the buying guide, and the item had no weight set, so the system could not pull it automatically onto the production withdrawal. When that link or weight is missing, the item is not withdrawn from perpetual inventory unless someone adds it to that production withdrawal manually.', 'If an item you have clearly used still shows on hand, check that the recipe is linked to the stock item and has a weight, and confirm the item actually appears on the production withdrawal. Customer & Expert Care can review the item history to show what did and did not get withdrawn.'],
         'Tickets 302110, 302410'),
        ('Items on my production withdrawal are showing as 0 on hand even though Perpetual Inventory says I have them. What happened?',
         ['This points to the item already having been withdrawn from that site before the production withdrawal was attempted, so there was nothing left to pull. In support cases the item history report showed the earlier withdrawals that had already cleared the item out of inventory. Run the item history report and trace back to the earlier withdrawal to see where the quantity went.'],
         'Tickets 309859'),
        ('Why does the on-hand count change a minute or two after I enter a transaction?',
         ['The perpetual balance can take a short time to update after a withdrawal or other transaction is entered. In one case an item briefly showed the old count and then displayed the correct, lower number a few minutes later. If a number looks off right after you save, refresh and give it a moment before assuming it is wrong.'],
         'Tickets 317727'),
        ('My count is showing in the wrong unit (for example Whole Units instead of Broken Units / cases instead of eaches). How do I fix it?',
         ["This is driven by the item's whole-unit-to-broken-unit conversion setting, not by the perpetual screen itself. In one case '4 cases and 60 each' was stored as 64 whole units because the item was configured as 1 whole unit = 1 broken unit (a 1-to-1 ratio), so the system added the two counts together into a single unit. The fix is to correct the item's unit conversion so a case and an each are not treated as the same unit. This kind of configuration correction is handled with Customer & Expert Care, who escalate item-conversion issues to the Expert Care Team."],
         'Tickets 315733'),
    ]),
    ('Negative balances', [
        ('Some of my items are showing a negative perpetual balance even though my settings are set to not allow negatives. How is that possible?',
         ['A negative balance usually does not mean the setting failed. It typically comes from how and when transactions were entered. In support cases, negatives appeared because staff were manually adding and withdrawing quantities to work around a process (for example before they were using production records), and because transactions were keyed in out of order or backdated.', 'When transactions are backdated, the running history can briefly show a negative even though the live balance is fine. In one case the negatives stopped appearing entirely once the district switched to entering proper production records instead of the manual add/withdraw workaround. If you still cannot account for a negative, Customer & Expert Care can review the item history with you.'],
         'Tickets 303074, 310872'),
        ('Why did the system let someone withdraw an item when the report shows the balance was negative at that point?',
         ['The system checks whether a withdrawal is allowed based on what was on hand at the time the transaction was actually entered, not the date it was backdated to. The item history report shows two date columns: the Actual Transaction Date (the date the transaction is applied to in inventory history) and the Transaction Date (when it was actually entered into the system). A withdrawal entered today but backdated to an earlier date can make that earlier date look negative on the report, even though there was enough inventory on hand when it was keyed in - which is why the system allowed it.', 'The Perpetual balance is a running total, not a row-by-row calculator: each line reflects every receipt, withdrawal, and unit shift that came before it, so two withdrawals of 12 and 38 will not simply add up to -50. To see the true picture, pull the item history for a wider date range so you can see all the activity that affects the running balance. The practical fix going forward is to enter receipts at the time the product actually arrives so transactions do not have to be backdated.'],
         'Tickets 315728, 310872'),
        ('On the item history, what do the Adjustment and Perpetual columns mean, and how does a reconciliation differ?',
         ['The Adjustment column shows the change that was made (for example, an adjustment of 12 means 12 units were removed), and the Perpetual column shows the resulting inventory balance after that change. If the balance was zero before, removing 12 leaves a perpetual balance of -12.', 'Reconciliation entries are the exception. A physical inventory is not treated as a manual adjustment: the quantity you count and reconcile becomes the new perpetual balance, and the Adjustment shown is just the difference between what was previously recorded and what was physically counted.'],
         'Tickets 315728'),
    ]),
    ('Physical inventory, storage categories, and timing', [
        ('When I started my physical inventory, only one storage category (for example Dry) showed up. The others are missing. How do I get them back?',
         ["This happens when storage categories were unchecked while the physical inventory was being started, so only the checked category is included. There are two ways to correct it: cancel the inventory you started and begin a new one with all storage categories checked, or complete the current 'Period' inventory and then start an 'Interim' physical inventory to capture the storage categories that were missed."],
         'Tickets 302710'),
        ('My whole perpetual inventory zeroed out (or only a few items show) after a reconciliation. What happened?',
         ['This is usually caused by a second, empty inventory being submitted and reconciled on the same day as the real one. In one case a blank inventory was submitted the same day as the period inventory and then reconciled, which zeroed out all the items. If your counts disappear right after reconciling, check whether more than one inventory was reconciled that day; Customer & Expert Care can confirm what was submitted.'],
         'Tickets 299098'),
        ('How do I reopen or edit a physical inventory that has already been reconciled?',
         ["From the inventory list, click View on the inventory, scroll to the bottom, and select Modify Physical Inventory. You can only edit the most recently reconciled inventory (the one showing N/A). If you need to update an earlier month's physical inventory, you have to modify and then cancel the most recent one first before the earlier one can be changed."],
         'Tickets 321008'),
        ("I missed last month's inventory but already received invoices for this month. What should I do?",
         ["Cancel any prior-month inventories that were never reconciled. You can run an 'Interim' inventory on any day of the month - just be consistent about whether you do it before or after receiving in orders."],
         'Tickets 291616'),
        ("Why isn't the upcoming month available yet in the inventory dropdown?",
         ["A month's inventory becomes available in that month. In one case the June inventory was not yet in the dropdown in late May and was expected to appear in June. If a future month is missing, it is generally a timing matter rather than a problem to fix."],
         'Tickets 321362'),
    ]),
    ('Inventory value and access', [
        ('Why is my inventory value different from the market value, and what does the MAP column mean?',
         ['Inventory value and market value are calculated differently, so they will not always match. Market value reflects the current price of what is on hand, while the inventory value reflects how the system has valued the stock you received over time. The Moving Average Price (MAP) is a behind-the-scenes valuation figure that PrimeroEdge does not recommend using as your costing standard.', "The MAP column is intended to be hidden from normal users and shows only for specific internal support roles; in one case it appeared on a district's report when it should have been turned off, and PrimeroEdge worked to remove it for that district. For costing and valuation, use the Valuation Report and the Price Details report, both found in the Reports section of Inventory, rather than the MAP figure."],
         'Tickets 291545, 301390'),
        ('We bought Inventory licenses but do not see Inventory in our system. Do we have to set it up, and do we have to use it?',
         ['Having the license is not the same as having the module turned on. Inventory has both a front-end and a back-end implementation, and if the back-end implementation was not completed, you can have the license but not see Inventory. Whether you are required to use it once it is implemented is a question for the Customer Success team. If you believe you are licensed for Inventory but cannot see it, contact Customer & Expert Care so they can check your implementation status.'],
         'Tickets 302309'),
    ]),
    ('Additional source cases reviewed', [
        ('Which other support cases were reviewed for this guide?',
         ['These additional cases from the source filter were reviewed while building this guide. Each was resolved without distinct new guidance - for example a transient error cleared by refreshing, a question the requester resolved on their own, or a one-off configuration or data fix handled directly with the support team - and is listed here so the guide accounts for every case in the source filter.'],
         'Tickets 290408, 313652'),
    ]),
]
CLOSING = "Still stuck? PrimeroEdge Customer & Expert Care is available by phone at 866.442.6030, Monday-Friday, 6 a.m.-6 p.m. CT. You search, print, and correct your own perpetual inventory on screen, but some fixes - such as correcting an item's unit conversion, reviewing item history behind unexplained negatives, confirming what was reconciled, removing a MAP column that should be hidden, or checking your Inventory implementation - are handled by Customer & Expert Care, who escalate item-configuration issues to the Expert Care Team."
SOURCE_NOTE = 'Source: PrimeroEdge Customer & Expert Care support conversations (Inventory > Perpetual Inventory). Customer, district, and staff identities have been omitted; ticket numbers are internal references only. Product framing was cross-checked against the jira-brain wiki concepts; all behavioral guidance traces to the support cases.'
