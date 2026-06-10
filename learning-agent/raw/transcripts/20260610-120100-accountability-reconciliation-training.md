---
key: "LOCAL-2026-06-10-accountability-reconciliation"
source_type: "authored_transcript"
status: "draft"
title: "CS Training - SchoolCafe Accountability: Reconciliation and Session Management"
original_recorded_at: ""
revision_date: "2026-06-10"
revised_by: "rahul.mehta@cybersoft.net"
duration_sec: 2520
duration: "00:42:00"
revision_notes: "Authored 2026-06-10. Source: GUIDE-013, NXT-3201, NXT-3202, NXT-3205."
---

[00:00:00] The broadcast is now starting.
[00:00:02] All attendees are in listen-only mode.
[00:00:34] Welcome everybody.
[00:00:35] Good morning and thank you for joining me today for our SchoolCafe Accountability training.
[00:00:40] My name is Taylor Rathmel, I'm a project mentor here at SchoolCafe, and today we are going to be walking through reconciliation and session management.
[00:00:48] This is one of those topics that comes up a lot — I get questions about it pretty regularly — so I'm really glad we have time set aside to go through it together.
[00:00:56] Before we dive in, just a couple of housekeeping items.
[00:00:59] You are all in listen-only mode right now, so if you have questions as we go, please drop them into the chat panel and I will keep an eye on it throughout the session.
[00:01:07] I'll pause periodically for questions as well, so don't worry if it feels like we're moving fast — we'll get to your questions.
[00:01:14] Alright, let me share my screen and we'll get started.
[00:01:20] Okay, so you should be seeing the SchoolCafe back-office interface now.
[00:01:24] I'm logged in as a district-level user so I can show you a broad view, but everything we cover today applies at the site level as well — the screens look the same.
[00:01:33] Let's start at the very beginning: what is reconciliation, and why does it matter?
[00:01:38] So every time a cashier opens a register at the POS and starts running meals, SchoolCafe is tracking everything that happens in what we call a session.
[00:01:47] A session is essentially a cashier's shift at the register — it starts when they open the drawer and it ends when they close it out.
[00:01:54] During that session, every transaction is recorded: every meal, every payment, every refund.
[00:02:00] Reconciliation is the process where a manager — that's typically you, the people on this call — reviews what the cashier reported versus what the system actually calculated, and either confirms it matches or investigates the difference.
[00:02:12] This happens every session, every day.
[00:02:15] Not once a week, not once a month — every single session.
[00:02:19] And I want to emphasize that because it's one of the most common gaps I see in districts that are new to SchoolCafe: they treat reconciliation as a periodic audit task rather than a daily workflow, and then they end up with weeks of unreconciled sessions stacking up.
[00:02:32] That becomes a real headache at month-end, trust me.
[00:02:35] So the rhythm we want to build is: sessions close, you reconcile them, same day or first thing next morning.
[00:02:42] Okay, so with that context, let me show you where reconciliation lives in SchoolCafe.
[00:02:47] I'm going to navigate to the Accountability module — you'll see that in the left-hand navigation.
[00:02:52] And within Accountability, we have Sessions.
[00:02:55] Click on Sessions and this is your starting point for everything we're talking about today.
[00:03:00] Now the first thing you'll see is a set of filters at the top of the screen.
[00:03:04] We have Site, Status, and Date.
[00:03:07] These are your main tools for finding the sessions you need to work with.
[00:03:11] Let me walk through each one.
[00:03:13] Site is pretty straightforward — if you're a district-level user like I am right now, you'll see all your sites in that dropdown.
[00:03:20] If you're a site-level user, it'll default to your site and you won't need to touch it.
[00:03:25] Status is where it gets interesting, and we're going to come back to this in detail.
[00:03:30] For now, just know that sessions can be in one of four statuses — OPENED, CLOSED, BALANCED, or RECONCILED — and this filter lets you narrow down to a specific status.
[00:03:40] Date lets you filter by a specific date or date range so you're not looking at every session since the beginning of time.
[00:03:46] Once you've set your filters, you hit the SEARCH button right there — that blue button — and it'll pull up the results.
[00:03:53] Let me do a quick search so you can see what that looks like.
[00:03:56] I'm going to select Primero Middle School as my site, I'll leave status blank for now so we see everything, and I'll put in today's date.
[00:04:04] Hit SEARCH.
[00:04:06] Okay, so I can see here I have three sessions for Primero Middle School from this morning.
[00:04:11] Let me walk you through what you're looking at in this grid.
[00:04:14] The columns are: Session number, Cashier name, Total Sales, Meal Count, and Status.
[00:04:20] So I can see Session 1 was run by Sarah Chen, she had a total sales of $412.50, served 87 meals, and her status shows CLOSED.
[00:04:29] Session 2 was Marcus Webb, $289.75, 61 meals, also CLOSED.
[00:04:35] And Session 3 looks like it's still OPENED — that's probably the late-service cashier who hasn't finished yet.
[00:04:41] Notice the status tags are color-coded, which makes it really easy to scan — each status gets its own distinct color so you can tell at a glance which sessions still need attention.
[00:04:46] OPENED means the cashier is currently serving at the register — that session is still active.
[00:04:52] CLOSED means the cashier has finished and entered their closing balance, but a manager hasn't reconciled it yet.
[00:04:58] BALANCED means the session is closed AND the amounts match — it's ready to reconcile.
[00:05:03] And RECONCILED is what we're working toward — that means the manager has reviewed and confirmed the session.
[00:05:03] I'll show you those other statuses as we work through the session today so you can see them in context.
[00:05:09] There's one more way to find a session I want to show you before we move on.
[00:05:13] Up at the top, you'll see there's a Session # tab.
[00:05:17] If you know the specific session number you're looking for — maybe a cashier called you and said "I need you to look at session 847" — you can flip to that tab and just type in the number directly.
[00:05:27] It's faster than filtering when you have a specific number in hand.
[00:05:30] Okay, let me pause here for a second.
[00:05:32] Any questions so far on finding sessions or the filters?
[00:05:36] I see a question in the chat from Maria — she's asking whether the date filter defaults to today's date or do you have to set it every time.
[00:05:44] Great question, Maria.
[00:05:45] It does not default to today — it defaults to showing everything, so I would always recommend setting the date filter first before you search.
[00:05:52] Otherwise, if you're in a busy district, you can end up with hundreds of sessions in the grid and it's hard to find what you need.
[00:05:59] Good habit to build: set site, set date, then hit search.
[00:06:03] Alright, let's talk about those four session statuses in more detail because they really drive the whole workflow.
[00:06:10] I'm going to walk through them in the order you'd typically encounter them during the day.
[00:06:14] The first status is OPENED.
[00:06:17] An OPENED session means a cashier started their session at the POS and it is still active.
[00:06:22] They're either still running transactions or they've walked away from the register but haven't closed out yet.
[00:06:28] As a manager, you can see OPENED sessions but there's nothing you need to do with them yet — you're just monitoring.
[00:06:34] The second status is CLOSED.
[00:06:37] This is where your work begins.
[00:06:39] A CLOSED session means the cashier has finished at the register and entered their closing balance — meaning they counted their drawer and typed in what they found.
[00:06:48] The session is no longer active but it has not been reviewed yet.
[00:06:52] This is the status you're hunting for when you sit down to do your daily reconciliation.
[00:06:57] The third status is BALANCED.
[00:07:00] A BALANCED session is a CLOSED session where the Over/Under is $0.00.
[00:07:05] Meaning what the cashier reported and what the system calculated are exactly equal.
[00:07:10] This is the happy path — when a session is BALANCED, reconciling it is basically just a confirmation click.
[00:07:16] The fourth status is RECONCILED.
[00:07:19] This means a manager has reviewed the session and clicked the RECONCILE button.
[00:07:23] It's done, it's closed, it's locked in.
[00:07:26] RECONCILED sessions don't need any further action.
[00:07:29] So the progression you want to see is: OPENED in the morning, CLOSED when the cashier finishes, and RECONCILED by end of day or first thing the next morning.
[00:07:38] BALANCED is a sub-state of CLOSED — it means it's ready to reconcile with no discrepancies.
[00:07:44] Now, here's the practical thing I tell everyone: when you sit down to do your reconciliation, you want to filter for CLOSED sessions.
[00:07:51] Because those are the ones waiting for you.
[00:07:53] And specifically, you're looking for CLOSED sessions where the Over/Under is $0.00, meaning the cashier's count matched the system.
[00:08:01] Those are quick wins — you verify, you click RECONCILE, and you're done.
[00:08:05] Sessions where the Over/Under is NOT zero require more investigation before you can reconcile.
[00:08:11] Let me show you that in practice.
[00:08:13] I'm going to filter for CLOSED sessions at Primero Middle School.
[00:08:18] Set site to Primero Middle School, status to CLOSED, today's date, SEARCH.
[00:08:24] Good, now I can see just the sessions that need my attention.
[00:08:27] I've got two CLOSED sessions here — Sarah Chen's Session 1 and Marcus Webb's Session 2.
[00:08:33] And I can already see in the grid that Session 1 shows $0.00 in the Over/Under column, and Session 2 shows a small discrepancy.
[00:08:41] So let's tackle the easy one first — Sarah's session — and walk through the reconciliation process start to finish.
[00:08:48] I'm going to click on Session 1 to open it.
[00:08:51] Okay, and now I'm inside the session detail view.
[00:08:54] Let me orient you to what you're seeing here.
[00:08:57] You'll notice there are tabs across the top — Summary, Closing Balance, and Transactions.
[00:09:02] We'll look at all of these, but we're going to start with Summary because that's the main reconciliation view.
[00:09:08] And you'll also notice there's a RECONCILE button up in the top right area of the screen.
[00:09:13] That's the button we're building toward — but don't click it yet.
[00:09:16] Let's look at the Summary tab first.
[00:09:19] Actually, I want to point out how you get to this screen in the first place.
[00:09:23] When you're in the sessions grid, you'll see a small icon next to each session — that's the Reconcile icon.
[00:09:29] Clicking that icon is what opens the session for reconciliation.
[00:09:32] It's a specific icon, not just a general "open" link, so make sure you're clicking the right thing.
[00:09:37] Okay, back to the Summary tab.
[00:09:40] The Summary tab is laid out with two main columns: the Cashier Column on the left and the System Column on the right.
[00:09:47] Here's what each one means, and this is really the core concept of the whole reconciliation process.
[00:09:52] The Cashier Column shows what the cashier reported.
[00:09:55] This is the closing balance they manually entered at the POS when they closed out their drawer.
[00:10:01] They counted their cash, their checks, their card receipts, and typed in what they found.
[00:10:06] The System Column shows what SchoolCafe calculated based on the actual transactions recorded during that session.
[00:10:13] Every sale, every payment, every refund that went through the system is summed up here.
[00:10:18] The goal is for those two columns to match.
[00:10:21] And the Over/Under line at the bottom of the Summary tab is simply Cashier Column minus System Column.
[00:10:27] If the cashier reported exactly what the system calculated, Over/Under is $0.00.
[00:10:33] If the cashier reported more than the system calculated, you get a positive number — that's an overage.
[00:10:39] If the cashier reported less, you get a negative number — that's a shortage.
[00:10:43] Now look at how the summary breaks down the numbers.
[00:10:46] It's not just one total — it's broken out by payment type.
[00:10:49] You'll see separate rows for cash, checks, and card.
[00:10:53] So if there's a discrepancy, you can see immediately whether it's in the cash count, the check deposits, or something to do with card transactions.
[00:11:00] That's really helpful when you're investigating a discrepancy because it tells you where to look.
[00:11:05] For Sarah's Session 1 here, I can see cash is $0.00 over/under, checks is $0.00, cards is $0.00.
[00:11:13] Everything matches.
[00:11:14] And this is where we see our first status message.
[00:11:18] Right there in the middle of the screen, in a banner or highlighted box, it says — and I want to read this exactly as it appears: "THE SESSION IS BALANCED AND READY TO RECONCILE."
[00:11:28] All caps, that exact text.
[00:11:30] When you see that message, it means the session is closed and the amounts match.
[00:11:35] You are clear to proceed.
[00:11:37] Go ahead and click that RECONCILE button.
[00:11:40] I'm going to click it now.
[00:11:42] And you see what happens — a green confirmation message appears that says "THE SESSION IS RECONCILED."
[00:11:48] The status tag in the header changes to RECONCILED.
[00:11:51] And now there's a BACK button to return you to the Sessions page.
[00:11:55] That's it.
[00:11:56] For a balanced session, that's the entire reconciliation workflow.
[00:11:59] Open the session, confirm the Summary tab shows the balanced message, click RECONCILE, see the green confirmation, hit BACK.
[00:12:07] Let me click BACK and we'll talk through the other status messages before we get to Marcus's session.
[00:12:12] So I mentioned there are three status messages you'll encounter on that Summary tab.
[00:12:17] We just saw the first one: "THE SESSION IS BALANCED AND READY TO RECONCILE."
[00:12:22] The second one is what you see when a session is closed but the amounts don't match.
[00:12:27] That message reads — again, exactly as it appears — "THE SESSION IS NOT BALANCED. Check the opening or closing balance detail for incorrect denominations. Check the session transactions for incorrect transactions."
[00:12:42] That's a mouthful, but it's actually giving you a roadmap for what to investigate.
[00:12:46] It's telling you: go look at the denominations in the closing balance, or go look at the transaction list.
[00:12:52] We'll look at what to do with that message in a moment.
[00:12:55] The third message is "THE SESSION IS NOT CLOSED."
[00:12:59] That one's straightforward — it means the cashier hasn't finished at the register yet.
[00:13:04] They haven't entered a closing balance.
[00:13:06] You can see the session, you can open it, but there's nothing to reconcile yet because the session is still active.
[00:13:12] We'll talk about what to do in that situation in a bit, because there are actually a couple of options.
[00:13:17] Let me pause for questions.
[00:13:19] I see James in the chat asking what does the BACK button do if you accidentally hit RECONCILE on the wrong session.
[00:13:26] James, that's a really important question.
[00:13:28] Once you click RECONCILE and see that green confirmation, the session is reconciled — there's no undo on reconciliation.
[00:13:35] The BACK button just takes you back to the sessions list.
[00:13:38] So make sure you're looking at the right session before you click RECONCILE.
[00:13:42] The session number, cashier name, and date are all visible in the header, so take a second to confirm those before you click.
[00:13:49] Good question.
[00:13:50] Okay, let's look at Marcus's Session 2 which has a discrepancy.
[00:13:55] I'm going back to the sessions grid.
[00:13:57] And I'm clicking the Reconcile icon for Session 2, Marcus Webb.
[00:14:02] So here on the Summary tab, I can see the Cashier Column and the System Column don't match.
[00:14:07] Marcus reported $4.50 more in cash than the system shows.
[00:14:11] And the banner message shows "THE SESSION IS NOT BALANCED. Check the opening or closing balance detail for incorrect denominations. Check the session transactions for incorrect transactions."
[00:14:24] So what do I do with this?
[00:14:26] The first thing is to look at the Closing Balance tab — let me click on that.
[00:14:31] The Closing Balance tab is where the cashier's actual count lives.
[00:14:35] And this is where you can make corrections if the cashier entered denominations incorrectly.
[00:14:40] Let me show you how this tab works because there's some useful functionality here.
[00:14:44] You'll see a denomination entry area — this is how the cashier's closing balance gets entered.
[00:14:49] The system lets you enter the closing balance in two ways.
[00:14:53] You can enter denomination counts — meaning how many ones, how many fives, how many quarters, and so on.
[00:14:59] The system will calculate the total dollar amount from those counts.
[00:15:03] Or you can enter the dollar amount directly for each denomination type, and the system will back-calculate the counts.
[00:15:10] Whichever way is easier for your cashiers is fine — the system handles either input method.
[00:15:15] Below the cash section, you'll see checks and cards.
[00:15:18] And here's something important: checks and cards are not manually entered here.
[00:15:23] They're pulled automatically from the transaction records.
[00:15:26] So if the check total or card total looks wrong, that's not a closing balance problem — that's a transaction problem, and you'd go to the Transactions tab to investigate.
[00:15:35] Now I want to show you a couple of useful features on this tab.
[00:15:39] You'll see a button that lets you clear all cash entries with a single click.
[00:15:43] So if a cashier made a complete mess of their denomination entry and you want to start fresh, one click wipes it all out.
[00:15:49] And there's a print and export option as well, so you can print a closing balance report or export the data if your district needs to keep records in another system.
[00:15:58] One more thing on this tab: if a cashier enters an amount for a coin denomination that doesn't result in a whole number of coins — like entering $0.03 for quarters — the system will show an error message that says the entered amount results in an incorrect coin count and asks them to recount and enter the correct amount.
[00:16:10] That's the system telling you the math doesn't add up for that denomination.
[00:16:14] And importantly — the system will not accept that entry until it is corrected. You cannot save the closing balance with a partial coin error outstanding.
[00:16:19] For Marcus's session here, I can see he entered $4.50 extra in the twenty-dollar bill count.
[00:16:25] Looks like he may have miscounted.
[00:16:27] If I had a chance to verify with Marcus that he did miscounting, I'd correct it here.
[00:16:32] But I want to be clear about process: you shouldn't just change the closing balance without first trying to determine whether the cashier actually had more money or whether it was a counting error.
[00:16:42] That investigation step is important — the reconciliation process is about accuracy, not just making the numbers agree.
[00:16:48] Let me go back to the Summary tab.
[00:16:51] And I want to talk about the situation where a session shows "THE SESSION IS NOT CLOSED."
[00:16:57] Let me navigate back to the sessions list and look at Session 3, the one that was OPENED.
[00:17:03] If I click the Reconcile icon on an OPENED session, the Summary tab will show that third status message: "THE SESSION IS NOT CLOSED."
[00:17:12] And you'll notice the RECONCILE button is grayed out or not active.
[00:17:16] You can't reconcile a session that hasn't been closed.
[00:17:19] So what are your options?
[00:17:21] Option one is to wait.
[00:17:23] If the cashier is still serving or just finishing up, the right answer is usually to let them complete their normal close-out process at the POS.
[00:17:31] They enter their closing balance, the session status changes to CLOSED, and then you can reconcile.
[00:17:37] Option two is a force-close.
[00:17:40] And I want to be really clear about this: force-closing a session is NOT best practice.
[00:17:45] I want you to hear that before I show you where the option lives.
[00:17:48] If you look in the session detail, there is an Edit Pencil icon next to the Closing Date and Time field.
[00:17:55] Clicking that pencil lets you manually enter a closing date and time, which will force the session into a closed state.
[00:18:02] This exists for situations where a cashier truly cannot close out at the POS — maybe there was a system issue at the register, maybe the cashier left in an emergency and the drawer is locked.
[00:18:12] Those are the situations where force-close is appropriate.
[00:18:15] Using it routinely because it's faster than waiting for the cashier to finish is a bad practice and can lead to inaccurate session data.
[00:18:23] So: option one first, force-close only as a last resort.
[00:18:27] Let me pause for questions again.
[00:18:29] I see a question from David: can two managers reconcile the same session at the same time?
[00:18:35] Great question, David — my recommendation is to coordinate with your team so only one person works on a session at a time. [TO VERIFY: whether the system enforces a lock preventing concurrent reconciliation access — check with your district support contact for the definitive answer.]
[00:18:47] Good question, David.
[00:18:49] Okay, let's talk about one more topic before we wrap up, and this is an important one.
[00:18:54] Session deletion.
[00:18:56] I want to cover this because it comes up occasionally and the stakes are high.
[00:19:00] If you are ever looking at a session and think there is something fundamentally wrong with it — wrong cashier, wrong date, transactions that should not exist — there is a delete option.
[00:19:10] But I need you to treat this with a great deal of caution.
[00:19:14] Here's what happens when you delete a session, step by step.
[00:19:17] When you initiate a delete, you'll get a confirmation prompt.
[00:19:21] That prompt does two things.
[00:19:23] First, it requires you to enter a comment — a reason for the deletion.
[00:19:27] This is mandatory.
[00:19:28] You cannot delete without explaining why.
[00:19:30] Second, it shows you the transaction count and payment count for that session, so you understand exactly what you're about to delete.
[00:19:38] If you see 87 transactions, 87 payments, and you only meant to delete one problematic session, you better be sure those are all supposed to go.
[00:19:47] Now here's the part that really matters.
[00:19:50] After you confirm the deletion, you have a 30-second undo window.
[00:19:54] Thirty seconds.
[00:19:56] There will be a countdown visible on screen, and you can click to undo during that window.
[00:20:01] After 30 seconds, the deletion is permanent.
[00:20:05] And permanent means: all the transactions from that session become adjustments.
[00:20:09] Each one gets a label that says "Session Deleted: " followed by the comment you entered.
[00:20:15] They don't disappear from the system — they become adjustments that affect account balances.
[00:20:20] And I want to be very direct about what support can do here: SchoolCafe support cannot reverse a session deletion after that 30-second window closes.
[00:20:29] It cannot be undone.
[00:20:31] So before you click that delete confirmation, you need to be very certain.
[00:20:36] Look at the transaction count.
[00:20:38] Look at the comment you've entered.
[00:20:40] Think about whether this is really what you need to do.
[00:20:42] If you're not sure, do not delete.
[00:20:44] Contact your SchoolCafe project mentor first and talk it through.
[00:20:48] This is not a feature to explore casually.
[00:20:51] Is there a question about this?
[00:20:53] I see one from Priya: what happens to a student's account balance when a session is deleted?
[00:20:59] Priya, that's exactly the right question to be asking.
[00:21:02] When the transactions become adjustments, they do affect account balances — the student's account activity is adjusted to reflect those transactions being reclassified.
[00:21:12] The exact impact depends on the transaction types involved.
[00:21:15] This is one more reason to be very certain before deleting — you're not just cleaning up a session record, you're potentially changing how student account histories look.
[00:21:24] Another excellent reason to call your project mentor if you're not sure.
[00:21:28] Alright, I want to do a quick recap of everything we've covered today before we sign off.
[00:21:33] We started with the purpose of reconciliation: it's a daily workflow, every session, every day, where managers verify that cashier-reported amounts match what the system calculated.
[00:21:43] We looked at how to find sessions using the Site, Status, and Date filters and the SEARCH button.
[00:21:49] We went through the session grid and the columns you'll see: cashier, total sales, meal count, and color-coded status tags.
[00:21:57] We covered the four session statuses: OPENED, CLOSED, BALANCED, and RECONCILED — and the progression you want to see each day.
[00:22:05] We looked at the Summary tab inside a session: the Cashier Column versus the System Column, the Over/Under calculation, and the breakdown by cash, check, and card.
[00:22:15] We went through the three status messages you'll see — the balanced and ready message, the not balanced message with its investigation guidance, and the not closed message.
[00:22:25] We walked through the actual reconciliation workflow for a balanced session: open it, confirm the balanced message, click RECONCILE, see the green confirmation.
[00:22:34] We talked about the Closing Balance tab: denomination entry by count or by amount, checks and cards from transactions, the clear all option, the print and export option, and the partial coin error.
[00:22:44] We covered what to do when a session is not closed: wait for the cashier when possible, and only use the force-close Edit Pencil option as a last resort.
[00:22:54] And we ended with session deletion: the mandatory comment, the transaction count warning, the 30-second undo window, and the fact that support cannot reverse a deletion after that window.
[00:23:05] That's a lot of ground we covered today.
[00:23:07] I hope this gives you a really solid foundation for your daily reconciliation workflow.
[00:23:12] The thing I want you to take away more than anything else is the rhythm: sessions close, you reconcile them, same day.
[00:23:19] Build that habit and reconciliation becomes a quick morning task rather than a big monthly clean-up project.
[00:23:25] I'm going to take a few more questions from the chat before we sign off.
[00:23:28] Lisa is asking: how often should we be checking for OPENED sessions that have been open too long — like, what if a cashier left for the day and forgot to close out?
[00:23:38] Lisa, that's a great operational question.
[00:23:40] I'd recommend checking for OPENED sessions at the end of each service period — after breakfast, after lunch — not waiting until end of day.
[00:23:48] If a session has been open for longer than your typical service window, that's a sign something may have been missed.
[00:23:54] That's when you'd reach out to the cashier, and if they're genuinely unavailable, that's a legitimate use case for the force-close option we discussed.
[00:24:02] Kevin is asking: on the Closing Balance tab, if a cashier's card amount looks wrong, is there a way to see what individual card transactions made up that total?
[00:24:12] Yes, Kevin, that's exactly what the Transactions tab is for.
[00:24:15] The card total on the Closing Balance tab is a sum pulled from transactions, so if it looks off, jump to the Transactions tab and you can see each individual transaction — the type, the amount, the timestamp — and figure out where the discrepancy is.
[00:24:27] That tab is very useful for that kind of investigation.
[00:24:30] One more question from Sophia: can you give us a quick tip for what to do at the start of the day to set ourselves up for efficient reconciliation?
[00:24:39] Sophia, I love this question.
[00:24:41] My tip is: before service even starts, filter for any CLOSED sessions from yesterday that weren't reconciled.
[00:24:47] Knock those out first, while your mind is fresh.
[00:24:50] Then after each service period, come back and check for new CLOSED sessions.
[00:24:54] You don't have to wait until end of day for everything.
[00:24:57] Reconciling as sessions close throughout the day is much less stressful than trying to do everything at once.
[00:25:02] And set up your filters once and use the same filter combination every day — site, date, status CLOSED — so you get into the habit and it becomes second nature.
[00:25:11] Alright, I think that's a great place to wrap up.
[00:25:14] Thank you so much for being with me today.
[00:25:16] I really appreciate everyone's engagement and the great questions in the chat.
[00:25:20] The recording of this session will be available in your training portal, so you can go back and reference anything we covered.
[00:25:26] If you have questions after the session, please reach out to your SchoolCafe project mentor and they can help you through anything specific to your district setup.
[00:25:34] Have a great rest of your day, everyone.
[00:25:36] Take care.
[00:25:38] The broadcast has ended.
