---
key: "LOCAL-2026-06-10-pos-cashier-v2"
source_type: "authored_transcript"
status: "draft"
title: "CS Training - SchoolCafe POS Course 1: Cashier Training (Revised)"
source_url: ""
channel_key: ""
recording_key: ""
product_ref_key: ""
asset_key: ""
content_type: "AUTHORED"
share_status: "INTERNAL"
original_source: "GTS-262b5d25fe4645f5a58576fd869557d5"
original_recorded_at: "2024-08-29"
revision_date: "2026-06-10"
revised_by: "rahul.mehta@cybersoft.net"
duration_sec: 3810
duration: "01:03:30"
transcript_utterance_count: 540
fetched_at: "2026-06-10T00:00:00.000Z"
revision_notes: |
  V2 update from original August 2024 recording.
  Changes grounded in Jira tickets:
    - Food Detection section added (NXT-20746, NXT-20747, NXT-20749, NXT-20750)
    - Mark for Review reasons updated to reflect 12 named defaults (NXT-202)
    - Objectives updated to include Food Detection
  [TO VERIFY]:
    - Card payment on serving-line Pay screen: no Done Done ticket found for serving line;
      NXT-3922 covers Account Management only; NXT-177 (Additional Income) is Ready for Development.
    - Summary Sale and Device Information options on dashboard: present in GUIDE-009 but no
      grounded AC ticket found; recommend confirming with PM before adding to training.
    - "Primero Middle School" site name in demo: confirm whether to update for PrimeroEdge
      rebrand or leave as fictional training site name.
---

# CS Training - SchoolCafe POS Course 1: Cashier Training (Revised)

## Source

- Original GoToStage recording: GTS-262b5d25fe4645f5a58576fd869557d5
- Original recorded: August 29, 2024
- Revision date: 2026-06-10
- Revision basis: Jira tickets NXT-20746, NXT-20747, NXT-20749, NXT-20750 (Food Detection); NXT-202 (Mark for Review Reasons)

## Changes from Original

- **[NEW]** Food Detection section added after second-meal examples (~[00:40:22]–[00:41:41])
- **[UPDATED]** Objectives now include Food Detection
- **[UPDATED]** Mark for Review section revised to name all 12 default review reasons and note customizability
- **[SHIFTED]** All timestamps after ~[00:40:21] are shifted approximately +2 minutes to accommodate the Food Detection insertion

## Transcript

Machine-style authored transcript. New and revised passages are annotated with `<!-- Source: -->` citation comments for grounding traceability. Unchanged passages retain the original wording from the August 2024 recording.

[00:00:00] The broadcast is now starting.
[00:00:02] All attendees are in listen-only mode.
[00:00:34] Welcome everybody.
[00:00:35] Good morning and thank you for joining me for your School Cafe POS Cashier webinar.
[00:00:41] We'll get started in about three minutes.
[00:00:43] Give everybody an opportunity to join, but go ahead and enter into the questions box where you're joining us from this morning.
[00:00:51] That way I know you can hear my voice.
[00:00:53] And again, we will get started in just a few minutes.
[00:03:18] All right.
[00:03:19] We will go ahead and get started.
[00:03:21] Welcome again to your School Cafe POS cashier training.
[00:03:26] My name is Taylor Rathmel.
[00:03:27] I'm a project mentor here at School Cafe and I will be leading our webinar today.
[00:03:33] Don't forget you do have the questions feature where you can enter in any questions that you might have throughout the training.
[00:03:40] Either myself or one of my colleagues on the call will get those questions answered for you as we go through.
[00:03:46] And I will stop every so often to make sure that you have an opportunity to enter those questions.
[00:03:58] Our purpose for today's webinar is to provide an instructional overview on all of the different cashier functions that we have for you within the SchoolCafe POS.

<!-- [UPDATED OBJECTIVES - added Food Detection to list] -->
<!-- Source: NXT-20746 AC: "When turn on food detection, can see in transactions screen that it is working" | NXT-20749 AC: "Food Detection event is triggered by selecting a student when Food Detection is enabled in admin screen" -->

[00:04:11] Our objectives today, we're going to cover logging into SchoolCafe.
[00:04:16] We'll access the POS from our SchoolCafe dashboard.
[00:04:19] We'll cover the Open Service screen and talk about entering any opening cash or petty cash on that screen.
[00:04:28] We'll look at our Serving screen and several different transaction examples.
[00:04:34] We'll also cover the Bulk Sales feature in the POS as well as making payments between services.
[00:04:39] We'll touch on our food detection feature for sites that have that enabled.
[00:04:43] And then we will close our service, enter our closing balance, and sign out of our POS.
[00:04:50] Throughout the training today you'll hear me refer to what we call our three C's at School Cafe.
[00:04:56] We always like to remind our cashiers to confirm the student standing in front of you, confirm the items on their tray, and complete the sale.
[00:05:09] This is the School Cafe cashiers log that we have as a resource for your cashiers.
[00:05:16] Good opportunity to write down anything at the POS that may come up during service that might need to be reviewed during reconciliation process.
[00:05:25] So this is just a log where you can write down any errors that occur in a transaction that can be later fixed by your managers in reconciliation.
[00:05:35] This is a resource that you can get from the customer care department or your project mentor, depending on where you are in implementation.
[00:05:44] When we log into the POS from our School Cafe dashboard, we'll see this pop up on our screen.
[00:05:49] This is just School Cafe downloading the most recent site settings and menu grids and balances to make sure that it is up to date and ready to use.
[00:05:59] So we'll go ahead and hop over to our School Cafe dashboard.
[00:06:05] I'm logged into my training environment in School Cafe.
[00:06:08] To access our School Cafe POS, we're going to come over here and open up our Accountability module.
[00:06:14] And then we'll come down to the POS option.
[00:06:17] When I select POS, it will open the POS in a new tab within the same browser and it will automatically log me in.
[00:06:33] So there's that pop-up, School Cafe getting ready to use, and we are brought to our dashboard screen.
[00:06:43] Up here at the top, you will see the site that you are serving at, and then you'll see Good Morning or Good Afternoon and the user that's logged in.
[00:06:52] Below that, you will see some dashboard options that we're going to go through together today, as well as some reports that cashiers have access to from the POS.
[00:07:02] For our training today, I will be serving at a different site because as a cashier that works multiple sites, I do have the opportunity to switch between the sites that I have permissions for.
[00:07:14] So I'll select this hamburger menu up in the top left corner and come down to the switch sites option.
[00:07:22] Again, you will only see that switch sites option if you have permission or access to more than one site.
[00:07:30] So, we'll be serving at Primero Middle School today for our training, and now we are logged into that dashboard.
[00:07:39] I'm going to go ahead and start with our open service option here so that we can see our open service screen.
[00:07:45] On this screen, if you need to change the date of the meals that you're recording, say maybe yesterday you had a power outage and you were unable to enter those meals into POS.
[00:07:56] You can select that calendar icon in this session date field and backdate to the date that you'd like to record sales for.
[00:08:04] For today's training, we'll go ahead and record sales for today's date.
[00:08:09] If you open your register or registers with any petty cash or change fund, you can enter it on this screen.
[00:08:17] To do so, you'll click into the field of the denomination that like to enter and you can use the plus and minus signs to change the count of that specific denomination.
[00:08:27] Remember you are entering the count into these fields not the amount.
[00:08:31] So if I start with 120, 110, and two fives I would enter those counts into those fields.
[00:08:40] You can also use your on-screen keypad to enter those counts as well.
[00:08:45] For today's training we're going to start with a opening balance, so I will delete those counts.
[00:08:52] Once I've filled out this screen and selected the appropriate date, I'll come down to the bottom right corner and click open service.
[00:09:03] Once I click open service, I'll be brought to my serving screen.
[00:09:08] This is your traditional line serving screen.
[00:09:10] Up here in the top left corner, you will see the day of the week that you're serving.
[00:09:15] Again, this does not change the date that the meals are recorded for.
[00:09:19] This simply gives you to menu grids that may be available on different days of the week.
[00:09:25] However, most menu grids are set up to be accessible Monday through Friday, so we typically don't see this day needing changed.
[00:09:34] The next button that you'll see is the meal type.
[00:09:36] The meal type up here in the top part of my screen will default to the correct meal type based on the meal timings configured in your environment.
[00:09:46] So if you open your service and it's your breakfast window, you will see breakfast here.
[00:09:51] If you open service and your lunch window has started you will see lunch.
[00:09:55] In the case that lunch has started for you and you need to serve a few breakfast meals, maybe you had a late bus come in and you have a couple stragglers that need to receive breakfast, you can click on that meal type button and switch from meal type to meal type.
[00:10:11] For training today we are going to serve lunch meals so I'll go ahead and select lunch for my meal type.
[00:10:17] This system will confirm if we're switching meal types outside of the meal timing that we've set.
[00:10:23] It will confirm that we do want to serve lunch during breakfast or serve breakfast during lunch.
[00:10:29] I'll select yes and that meal type will update.
[00:10:34] The next button is where we'll select our menu grid.
[00:10:37] I have several menu grid options in my training environment.
[00:10:41] Depending on what you have set up, you may or may not see multiple options here.
[00:10:45] For training today, I'm going to use our lunch to menu grid, and that menu grid is now displayed on my screen.
[00:10:54] If you have a default menu grid set up in your environment, your menu grid will automatically display for you as soon as you open service.
[00:11:02] So you will not have to click that menu grid button unless you need to change menu grids.
[00:11:09] The last thing that I want to point out on this serving screen before we start our serving examples is this lunch meal button.
[00:11:17] You'll notice that it does have a knife and spoon icon that indicates that that is our reimbursable meal.
[00:11:23] If you have multiple reimbursable meal options on a menu grid, you will see that knife and spoon icon on each of them.
[00:11:30] We also see a star icon in the top right corner of that lunch meal indicating that that is a default menu item.
[00:11:39] If you have a default menu item set up on a menu grid.
[00:11:42] That means that as soon as a student enters their PIN or scans their ID, that reimbursable meal will be automatically added to that transaction.
[00:11:53] I'm gonna stop for just a second and give you an opportunity to enter any questions you might have about the serving screen or the open service screen that we looked at previously.
[00:12:01] And then we will start our serving examples.
[00:12:35] All right, we'll go ahead and continue on.
[00:12:37] I will be entering student PIN numbers in this PIN pad field here mimicking the behavior of students coming through the line and entering a PIN on a PIN pad.
[00:12:47] If your students are coming through the line and scanning IDs or if you're scanning a barcode, the functionality will be the same.
[00:12:53] The student information that displays will be the same.
[00:12:57] Cashiers also have a PIN pad on this screen here.
[00:12:59] If they need to enter a PIN for a student as well, you do have that option.
[00:13:04] So, we'll go ahead and pull up our first student.
[00:13:08] And I've got Elmer that comes through the line.
[00:13:11] Each of our students that comes through the line will show this same information.
[00:13:14] So, we will always see last name, comma, first, ID number, the site that that student's enrolled at, their grade level, and their homeroom in parentheses if we have homerooms in the school cafe system.
[00:13:27] Eligibility status will display below.
[00:13:29] This is something that can be hidden.
[00:13:31] Eligibility status codes are 113 for our paid students, 112 for reduced, and 111 for free.
[00:13:40] Below that we'll see Elmer's current balance and this ending balance will show what his balance will be as soon as this transaction is completed.
[00:13:50] Underneath that we do have the transaction number.
[00:13:53] This number is not a meal count number, this is simply number of transactions.
[00:14:00] If you have photos in Cafe, that student's photo will show over here on the right, and you can select it to enlarge it on that screen to make sure you are serving the correct student.
[00:14:11] Like I mentioned earlier, that default menu item is automatically added to a student's transaction if we have it set up as a default.
[00:14:20] That item can be removed by clicking the X, which we'll look at later.
[00:14:24] But for this first example, we'll go ahead and confirm the student standing in front of us, confirm the items on that tray, And to complete the sale, to debit that $2.35 to Elmer's account, the terminology in School Cafe is to click the charge button.
[00:14:40] So we'll go ahead and complete the sale by clicking charge.
[00:14:44] And that completes our first transaction example.
[00:14:48] I'm going to go through a handful more of other examples, more basic, simple transactions that you will see throughout the serving line.
[00:14:57] then I'll stop after our first section for any questions.
[00:15:02] So we'll go ahead and pull up Glory next.
[00:15:05] Now you'll notice the only difference between Glory and Elmer is her status.
[00:15:09] Glory is a free student with the code 111 and we do see that that lunch meal pulled at $0 for that free eligibility.
[00:15:17] Once again we'll confirm Glory, confirm that item on her tray, and complete the sale by clicking charge.
[00:15:28] Bria comes through the line next, and Bria has some allergies on her account.
[00:15:34] We can see that these food restrictions are dietary allergens on Bria's account.
[00:15:39] She is allergic to wheat, soy, peanuts, and sesame.
[00:15:44] If for whatever reason there is a menu item linked to these ingredients on my menu grid, those food restrictions will prevent the sale of those menu items.
[00:15:55] We'll look a little bit deeper into those food restrictions and the other restrictions on this screen in a later example.
[00:16:02] But you did notice that as soon as I input that pin for Bria, this pop-up automatically displayed on my screen.
[00:16:09] This restrictions pop-up will pop up for you if there are any restrictions on a student's account.
[00:16:16] Once again, we'll dig a little bit deeper into those restrictions a little later in the training.
[00:16:20] for now I'll close out of this pop-up.
[00:16:24] There are no menu items on my menu grid that are linked to any of Bria's allergies so she can have anything on this menu grid.
[00:16:32] I also want to point out that if I need to see those restrictions again, I can click on this alerts button to have that back on my screen.
[00:16:42] Bria is just going to grab that lunch meal today so we will confirm that student, confirm the items on the tray, and complete the sale.
[00:16:55] Jordan comes through the line next And Jordan wants to grab that lunch meal, but also a bag of chips.
[00:17:02] So I'll tap the chips button on my screen or I'll select it with the mouse that I'm using.
[00:17:06] It'll add that bag of chips to that transaction.
[00:17:09] And I do want to demonstrate how we can change the quantity of an item on a transaction.
[00:17:14] If Jordan wanted a second bag of chips, I could re-tap that chips button and it would increase it to two.
[00:17:20] I can tap that chips button as many times as necessary to get to the appropriate quantity.
[00:17:25] I can also click on that number there to have the quantity pop up on my screen.
[00:17:32] Here I see that one bag of chips cost 75 cents, the quantity that I'd like to serve, and then any extended cost.
[00:17:40] We'll go ahead and change that quantity back to one for Jordan here and click complete.
[00:17:45] And then once again I'll confirm Jordan, confirm those items on the tray, complete the sale.
[00:17:55] Morgan comes through the line next and Morgan decides that they're not hungry enough for that lunch meal.
[00:18:01] To remove an item from a transaction, whatever the item may be, whether that is a reimbursable meal that's defaulted to automatically add to the transaction or an a la carte item that was added by accident or needs to be removed, we can click that red X next that item that we'd like to remove.
[00:18:21] Because this is the reimbursable meal for Morgan, the system's confirming for me that I want to remove that meal.
[00:18:28] I'll select yes, and Morgan decides that they just want a side of fruit and a yogurt.
[00:18:36] Again, if I need to remove any item from a transaction, I can click that X to remove it as well.
[00:18:42] We'll add that fresh fruit back on.
[00:18:44] We'll confirm Morgan, confirm those items on the and complete the sale.
[00:18:53] Jacqueline comes through the line next and you'll notice something different about Jacqueline's information.
[00:18:58] She does have a zero dollar balance.
[00:19:00] We do see that if we were to complete this sale by clicking charge she would be pushed into the negatives.
[00:19:06] Whether or not your students can go into the negatives for meals or a la carte is set up in your school cafe environment.
[00:19:13] So if those charge limits have been set you will not be able to charge students into the negative.
[00:19:21] Jacqueline knows that she doesn't have any money in her account and she did bring a cash payment today to pay for that meal.
[00:19:27] So once again, I'll confirm Jacqueline.
[00:19:29] I'll confirm that lunch meal on her tray but because this is a cash transaction, instead of clicking charge to complete this sale, I'm going to use the pay button instead.
[00:19:39] So I'll click pay here and that's going to pull up this pay transaction pop up on my screen for me.
[00:19:46] On the left side, I'll see the sale total, the patron's current balance, and the amount due.
[00:19:52] I do have the option to toggle between cash and check here, and then I have an amount tendered field.
[00:19:58] So for this example, Jacqueline did bring me $5 cash, so I'll enter $5 into that amount tendered.
[00:20:06] I do have these quick denomination buttons appear at the top or an onscreen keypad.
[00:20:10] It's a $5 bill so I'll use the $5 button here and down below you'll see the change due.
[00:20:18] We will look at an example of depositing change into a student's account next but for this example Jacqueline does want her $2.65 change back so I'm going to give her that change while this pay transaction pop-up is on my screen.
[00:20:33] I want to make sure I give that change at this time because as soon as I complete this transaction this pop-up goes away and I no longer know how much change I owe the student.
[00:20:44] So I give Jacqueline her $2.65 and then I'll complete that transaction.
[00:21:03] Trayvon comes through our line next and you can see that Trayvon already has a negative balance.
[00:21:07] There are a couple reasons that could occur, but he knows that and he did bring a payment today as well.
[00:21:14] Trayvon's just going to grab that lunch meal so I will confirm the student, confirm that item, and then again because this is a cash transaction I'm going to click the pay button.
[00:21:24] Now Trayvon brought me a $30 cash payment.
[00:21:28] So I don't have a $30 quick button up here at the top, so I'll use my onscreen keypad.
[00:21:34] And Trayvon says, can you just deposit the change into my account?
[00:21:38] So in order to do that, I'll come down to the bottom and toggle the deposit change option on.
[00:21:44] And that'll me that that $27.65 will automatically be deposited into this student's account and I do not owe them any change.
[00:21:55] So because I do not owe the change, Trayvon is on his way and I can go ahead and complete that transaction.
[00:22:06] Danica comes through the line next and Danica also has a $0 balance.
[00:22:10] She knows that and she brought a payment today as well.
[00:22:14] So we'll confirm Danica, confirm that lunch meal on her tray and once again because we not debiting this transaction to Danica's account, we'll click the pay button.
[00:22:25] Now Danica brought a check payment today so I do want to make sure that I toggle from cash to check on this pay transaction screen.
[00:22:33] Similar screen from cash to check.
[00:22:36] I do lose that option to give change because all change from checks will automatically be deposited into a student's account.
[00:22:45] Danica did bring me a $75 payment today, so I'll click the $75 on the on-screen keypad.
[00:22:52] And for our check number field, check numbers in School Cafe are required to be a minimum of three digits.
[00:22:58] So if you have a check number that's less than three digits, you can always lead with a zero or two to reach that three-digit minimum.
[00:23:06] We'll go ahead and confirm Danica, confirm that she's paying for that meal with her $75 check, check number and then we'll complete that sale.
[00:23:20] Henry comes through the line next and Henry also doesn't have any money in his account however he brought lunch from home today so he's not purchasing anything from the cafeteria.
[00:23:30] Because of that I'm gonna remove that lunch meal and Henry decides he just wants to add money to his account so he's at the lunch table he remembers that mom sent him with cash to give to the cashier in the cafeteria and he brings that to the year to apply to his account.
[00:23:45] To do so, to add money to a student's account on our traditional serving line screen, we'll use the add funds button.
[00:23:52] So we're not charging or paying for anything because there is no transaction to complete, so instead we'll use the add funds button.
[00:24:02] When I click add funds, I do again have the option to switch between cash or check.
[00:24:07] Henry brought me a $20 bill today so I'll use that $20 button on my cash tab.
[00:24:12] I'll see the current balance, the payment that student's making, and their new balance at the bottom.
[00:24:18] I'll go ahead and make that payment.
[00:24:21] And we'll automatically see Henry's balance update here on this screen.
[00:24:25] We do get a payment completed successfully notification at the top of the screen.
[00:24:30] And now I'm ready to continue my serving.
[00:24:34] So I need to get Henry off the screen.
[00:24:36] Again, we don't have a transaction to complete.
[00:24:38] So, to remove Henry from the screen in School Cafe, the terminology is to click the void button.
[00:24:46] Void in School Cafe does not mean undo or cancel.
[00:24:49] It simply means to clear the screen.
[00:24:53] So, when we click void, we are not voiding that payment.
[00:24:56] We're simply clearing Henry off of our screen so that we can continue serving.
[00:25:01] I'm going to pause for just a minute to make sure that there are no questions about that first set of transaction examples.
[00:25:07] and then we will continue on.
[00:26:06] All right, moving on with our next set of examples, I wanna show you a couple different tools that the School Cafe POS has for our cashiers, starting with the queue feature in the top right corner.
[00:26:17] I like to think about our queue as a virtual waiting room because it's gonna hold on to any students who might enter their PIN or scan their ID while a transaction is in progress.
[00:26:28] So we'll go ahead and enter Kenneth's PIN number on the pin pad here and Kenneth comes up on our screen.
[00:26:36] Now say for example Kenneth and I are having a conversation about something at the register and there are students coming up behind Kenneth and entering their pin on a pin pad or scanning their ID on an ID scanner.
[00:26:48] I'm going to go ahead and mimic that behavior by entering another pin number on my pin pad here and you'll see that queue increase to two.
[00:26:56] I'm going to enter a couple more so we've got a couple more students are entering those pins and that queue increases to three and then to four.
[00:27:04] So I know that I have some students in my queue that are waiting for their transaction to be completed.
[00:27:11] Kenneth and I finish our conversation.
[00:27:13] I confirm the student, confirm that item, and complete the sale and the system is going to automatically pull the next student out of that queue so that I can complete their transaction as well.
[00:27:24] I'll go ahead and confirm Rihanna, confirm that lunch meal, and that sale.
[00:27:30] Jacob will come out of the queue next and will complete his sale.
[00:27:34] Trenton's in front of me now.
[00:27:35] He's got that lunch meal but he also has a bag of chips so we'll get that added and then we will complete that sale as well.
[00:27:51] We also have the option to look a student up in the School Cafe POS.
[00:27:56] So the examples that we've seen so far have been PIN entry or ID scanning but we also can look a student up if necessary.
[00:28:05] So I'm going to toggle from the PIN to the lookup tab here and I can look students up three different ways.
[00:28:12] I can look them up by name, homeroom, or what we call rosters in School Cafe.
[00:28:16] We'll talk about all three examples but we'll start with looking students up by name.
[00:28:21] You can look up students up from the site that you're serving at or other schools if you are serving students that might be visiting your site.
[00:28:30] For this first example I'll go ahead and enter full first and full last name here and click search button.
[00:28:38] Ron is the only Ron Vin in my system so he automatically gets pulled up here.
[00:28:43] He's going to grab that lunch meal so I'll go ahead and complete that sale.
[00:28:49] This lookup tool will also be a partial smart search so if I only have a couple letters for the first and or last name I can enter in the information that I have.
[00:29:00] You don't have to have information for both names.
[00:29:03] You can have just first or just last.
[00:29:05] I'm going to go ahead and these search criteria and the system will pull up anyone who matches those search options.
[00:29:14] I can see here that I have three patrons that match that search criteria.
[00:29:18] My first two patrons in my list do not have a grade level listed and they also have an A next to their name.
[00:29:24] That's telling me that those are adults in my system and there is their PIN number as well.
[00:29:30] I can sort by last name or first name if you have a long list and you know you're looking for a student.
[00:29:35] For this example, I am searching for Katie, so I'll select her from the list here.
[00:29:41] Confirm Katie, confirm that lunch meal, and complete that sale.
[00:29:47] If we have homerooms and the school cafe system, we can also look students up by those homerooms.
[00:29:52] So I'm here on the lookup tab.
[00:29:54] I'll come down to the homeroom option.
[00:29:56] You will be able to select a grade level here.
[00:29:59] I'll go ahead and select a homeroom, and then the system will pull up any student that is on that homeroom in School Cafe.
[00:30:10] Once again, I can sort by last name or first name.
[00:30:13] For this first example, I'm going to serve Betty Cahoe, so I find her in my list and select her.
[00:30:20] And then I'll confirm Betty, confirm that lunch meal, and complete that sale.
[00:30:26] The system will assume that you're going to continue serving that group of students in that homeroom, so it will pull that homeroom roster back up on your screen.
[00:30:33] You'll also notice that Betty is no longer listed in my homeroom roster.
[00:30:38] So The idea is that the list gets shorter and shorter as those students are served through the line.
[00:30:43] If I wanted to see those students who had already received a meal, I could show all up here in the top right corner, and we would see Betty back in that list.
[00:30:53] I'm going to go ahead and serve one more student, Ronnie B., from this homeroom.
[00:30:57] So we'll select Ronnie, add that lunch meal, confirm that meal.
[00:31:02] He's also going to get a bag of chips and an extra fruit.
[00:31:05] we will confirm those items and complete that sale.
[00:31:12] Again that roster will pull back up on your screen.
[00:31:14] Ronnie is now removed and once you're finished serving that group of students you can close out.
[00:31:22] We can also serve by what we call special rosters in School Cafe.
[00:31:26] A roster can be created of a group of students that you might want to serve together that are not already grouped in the same homeroom.
[00:31:34] So you might want to create a roster for a group of football players or a club that may be going on a field trip.
[00:31:41] For whatever reason if you want to serve a group of students together you can create a roster for them in School Cafe.
[00:31:49] To serve by roster we'll go to look up and then roster.
[00:31:53] I'll select my roster list and for this example we'll use the chess club and just like we saw with homeroom that roster will be pulled up on my screen.
[00:32:03] I'm going to confirm Paula, confirm that lunch meal, and complete that sale.
[00:32:12] And then again, the system's going to assume that you're going to continue serving that roster.
[00:32:16] Paula has been removed from the list since she's already been served, but I'm not going to serve anyone else in that chess club roster, so I'll go ahead and close out.
[00:32:26] I'm going to pause for just a second to make sure that there are no questions about those tools that we covered in that section of our training, and then we will continue on.
[00:32:34] Be sure to enter those questions into that questions box if you have any and we will get them answered for you.
[00:33:19] All right, moving right along.
[00:33:21] The next couple of things I want to show you are some alerts and restrictions pop up that school cafe has.
[00:33:25] We did see a preview of our restrictions pop up earlier.
[00:33:30] I'll go ahead and head back to that pin entry and pull up our first student with an alert.
[00:33:35] And this is going to be for a visiting student.
[00:33:38] So if you have anyone eating at your site that is not assigned to or enrolled at that site, you will get this visiting patron pop-up.
[00:33:47] This would happen for both adults and students.
[00:33:50] We'll go ahead and click OK.
[00:33:52] And we can serve Bianca as normal.
[00:33:54] We do see that she's visiting us from Basswood Elementary here, but we can still serve Bianca, confirm the student, confirm that lunch meal, and complete that sale.
[00:34:09] Next, we have Frank come through the line and we did see some of these food restrictions a little bit earlier in our training.
[00:34:14] Remember, food restrictions are dietary allergens that have been added to the student's account.
[00:34:20] These food restrictions will prevent the sale of any menu item linked to these allergens.
[00:34:26] So we'll look at a specific example for that in just a moment.
[00:34:30] Down below that, we see special instructions.
[00:34:33] Special instructions are just notes that have been added to student's accounts.
[00:34:37] Special instructions do not prevent the sale of any menu item, so keep that in mind.
[00:34:43] Some special instructions that you may want to add to a student's account, likes to use brother's ID, double check ID, has a twin, things like that.
[00:34:53] Because again, those are just notes for your cashiers.
[00:34:57] Below that, we have some additional restrictions.
[00:34:59] Do we allow the student to charge to their account?
[00:35:02] Do we accept checks for the student?
[00:35:04] And then, all the card restrictions at the bottom.
[00:35:06] We will look at an example of a la carte restrictions next, but right now I want to focus on Frank's allergies, specifically his milk allergy.
[00:35:15] I'll close out of this pop-up to demonstrate that our menu items linked to that milk allergy, so our ice cream and our yogurt do have an exclamation point in the bottom right corner.
[00:35:27] That's telling us that those menu items cannot be served to Frank because of that milk allergy.
[00:35:33] If I try to add the ice cream to Frank's transaction, the system stops me and says this item contains allergens matching this account and cannot be sold.
[00:35:43] So the system will prevent the sale of those a la carte items linked to those dietary restrictions.
[00:35:49] Frank settles for his lunch meal and a bag of chips here, so we'll go ahead and confirm the student, confirm those items, and complete that sale.
[00:36:04] James comes through the line next and James has some restrictions as well.
[00:36:11] We do see at the top that he has an account has a debit purchase restriction.
[00:36:15] We'll talk about that in a moment.
[00:36:17] Now James doesn't have any food restrictions.
[00:36:19] He does have a special instruction.
[00:36:21] Mom said no snacks.
[00:36:22] That's just a note to remember that will not prevent the sale of our snacks.
[00:36:27] But down here at the bottom we do see some a la carte restrictions.
[00:36:30] You will see these Ollicart restrictions for this specific day that it is that you're serving, and what we see here is that James cannot purchase Ollicart using cash on Thursdays, and he cannot purchase Ollicart using his account on Thursdays.
[00:36:44] Even if that money is in there, that charge restriction tells us he cannot use his account to buy Ollicart on Thursdays.
[00:36:53] If I close out of this pop-up, you will notice that James also has a debit purchase restriction on his meaning that he cannot purchase anything using the money on his account for whatever reason.
[00:37:05] Mom has set that debit purchase restriction, but he could still pay for that lunch meal using cash.
[00:37:13] Actually, looks like he has a cash purchase restriction as well.
[00:37:16] I apologize for that, but I do want to talk you through what would happen on your screen if this student with those a la carte restrictions was trying to purchase those all-a-cart items.
[00:37:27] Okay, if James had those all-a-cart restrictions and he got to my register and he had a bag of chips on the tray, if I added that bag of chips, the system would allow me to add it to the transaction.
[00:37:39] However, if I clicked the charge button, it would tell me all-a-cart debit restrictions, excuse me, all-a-cart debit purchases are restricted for this student today.
[00:37:50] If I added that bag of chips and I clicked the pay button because James is flashing a $5 bill in my face telling me that he has money to pay for that bag of chips, and I clicked the pay button.
[00:38:01] Because of that cash purchase restriction, it would say all of cart cash purchases are restricted for this student today.
[00:38:09] So the good thing about those all of cart restrictions is that your cashier does not have to make that decision.
[00:38:15] If those all of cart restrictions are in place on that student's account, the system will not allow you to complete that sale.
[00:38:22] Now, James has both debit and cash restrictions on his account for now, so we will go ahead and void him off of our screen and not complete that sale.
[00:38:32] He's going to go home and talk to mom about those restrictions.
[00:38:40] Morgan comes through our line next, and you might remember Morgan from earlier.
[00:38:44] Morgan came through the line and he only purchased all the cart.
[00:38:47] Because he's already been through our line today, we do have a button that says previous items and the button is green.
[00:38:54] If I wanted to see those previous items I could click on that button and it would show me the items that he purchased, the terminal that he purchased them at, and the time that they were purchased.
[00:39:04] And you'll also notice that because he did not receive a lunch meal yet, that that lunch meal was automatically added to his transaction.
[00:39:12] So again he comes through the line a second time, he decides he's hungry enough for that lunch meal now, so we'll go ahead and complete that sale.
[00:39:25] Elmer comes through the line and if you remember Elmer came through the line earlier and he did purchase that reimbursable meal so because of that we have a previous button but for Elmer it's red and it says previous meal instead of previous item.
[00:39:38] Again I can click on that button to see the meal that Elmer was served and you'll also notice that that lunch meal that default menu item was not added to that transaction that's because Elmer has already received that reimbursable meal today.
[00:39:53] If we allow second meals we can reuse that reimbursable meal button, the system will warn us that this is a second meal and ask us if we want to continue.
[00:40:03] If I allow second meals, I'll select yes.
[00:40:06] And it will pull that lunch meal at the second meal price over here, whatever your second meal price is, with an asterisk that says, hey, this is the second meal for Elmer.
[00:40:17] Okay, so he is not being recorded as having two reimbursable meals.
[00:40:20] That will be recorded as a second meal.
[00:40:24] We'll go ahead and confirm Elmer, confirm those items on his tray, and complete that sale by clicking charge.

<!-- [NEW SECTION — Food Detection] -->
<!-- Source: NXT-20746 AC: "When turn on food detection, can see in transactions screen that it is working" | "When turn off food detection, cannot see any evidence of food detection in the transactions screen" -->
<!-- Source: NXT-20749 AC: "Food Detection event is triggered by selecting a student when Food Detection is enabled in admin screen" | "Food Detection event is NOT triggered by selecting a student when Food Detection is disabled in admin screen" | "When system can't establish connection to the Edge and Food Detection is enabled in admin screen, shows message: Edge Not Found" -->
<!-- Source: NXT-20750 AC: "System shows detection results message" | "System loads the Food items found in the transaction control" | "User can still add other items manually to transaction control even when food detected" | "When transaction is completed, clears message and results screen" -->

[00:40:33] I'm going to take a moment here to cover a feature that some of your sites may have enabled, and that's our food detection feature.
[00:40:41] Not every site will have food detection active, so whether or not you see this on your serving screen depends on how your district has it configured.
[00:40:50] If your site does have food detection enabled, here's what you'll notice.
[00:40:55] When a student enters their PIN or scans their ID, that food detection event is triggered automatically.
[00:41:02] The system communicates with what we call an Edge device that is connected to your POS terminal, and that Edge device scans the student's tray.
[00:41:11] On your serving screen, you will see a Detection Results indicator.
[00:41:15] When the Edge device has successfully scanned the tray and returned those results, that indicator will display green.
[00:41:22] If we have not received scan results back from that device yet, it will display red.
[00:41:28] Now, if your district also has what we call food detection transaction integration turned on, those detected food items will automatically be loaded into the transaction on the right side of your serving screen, just as if you had tapped each of those items yourself on the menu grid.
[00:41:44] One thing that's important to know is that you can still add items manually to the transaction even when food has been detected.
[00:41:52] So if the Edge device did not pick up an item, or a student grabbed something extra, you can still select it from the menu grid and add it just like you normally would.
[00:42:02] And once you complete that transaction, those detection results and messages will clear from the screen automatically, so you're ready for the next student.
[00:42:11] Now, if your POS cannot connect to the Edge device, you will see an Edge Not Found message on your screen.
[00:42:18] If that happens, just continue serving as you normally would without food detection for that transaction, and let your manager know so they can look into the connection.
[00:42:27] Again, whether food detection is enabled at your site is a setting your manager or district controls, so if you're unsure, your manager can confirm what's set up at your location.
[00:42:38] I'm going to pause now to make sure that there are no questions about those alerts, restrictions, and our food detection feature, and then we will continue on.

[00:43:36] All right, we will continue on with our transaction examples.
[00:43:40] The next example that I want to show you is an error that could be made at the POS.
[00:43:46] So we'll go ahead and enter Sam's ID here.
[00:43:53] Now say Sam comes through the line and Sam has a lunch meal on their tray and they also have a bag of chips and a fruit.
[00:44:00] Now I'm using a touchscreen device at my POS and things are chaotic and I'm not paying attention and I accidentally double tap that fruit button.
[00:44:09] So now Frank, excuse me, Sam has two fruits on his transaction and I don't notice that before I click the charge button.
[00:44:16] And then Sam looks at me and he says, why did you charge me for two fruits?
[00:44:20] I only got one.
[00:44:21] So this is a scenario where I've made an error at the POS and I cannot correct that mistake here through the POS.
[00:44:29] I have to have my managers make that correction later during the reconciliation process.
[00:44:35] This is why we give you that cashier's log to write down a scenario like this that may need to be fixed after service is complete, But you also have the option to mark it for review in School Cafe.
[00:44:48] To mark a transaction for review for whatever reason, we can come up here to the transactions icon in the top of our screen, it looks like a piece of paper, and that's going to open up all of our transactions that have been completed in this session.
[00:45:02] So we'll talk about the information we see on the screen a little bit later, but right now I just want to focus on Sam's transaction here.
[00:45:09] Over on the far right, I do have this icon that looks like a little note.
[00:45:13] I can click on that to see the transaction details for Sam.
[00:45:18] I can confirm that I did, in fact, accidentally charge him for two extra fruits, and I know that he only purchased one.
[00:45:26] To mark that transaction for review, I'm going to find the transaction and click the flag icon next to it.

<!-- [UPDATED — Mark for Review reasons now named per NXT-202 defaults] -->
<!-- Source: NXT-202 AC: "The default Review Reasons are 1 Should be Cash 2 Should be Check 3 Should be Charge 4 Wrong Payment Amount 5 Return Change 6 Add Item 7 Remove Item 8 2nd Meal Question 9 Patron Detail Error 10 Note Question 11 Restriction Question 12 Other" | "The text for the reason can be edited by the user." -->

[00:45:34] That's going to pull up our list of review reasons that I can select from, so that my manager can see during reconciliation that this transaction was flagged.
[00:45:42] You'll see twelve default review reasons available — things like Remove Item, Add Item, Wrong Payment Amount, Should be Cash, Should be Check, Should be Charge, and a few others including a catch-all called Other.
[00:45:55] Your manager or district admin can also customize the text on any of these reasons to better match your district's workflow.
[00:46:03] For this specific example, I'll use the Remove Item reason since I want to flag that extra fruit that needs to be taken off.
[00:46:11] Selecting that reason will mark that flag red and it will later show my managers that that transaction was marked for review there.
[00:46:19] I also want to write it down on my cashier's log just so I have some more specifics about what item needs to be removed for that student.
[00:46:28] Okay.
[00:46:29] Are there any questions about marking a transaction for review here in the school cafe POS?
[00:46:58] All right we'll go ahead and continue on then.
[00:47:02] The next example I want to show you is an adult transaction for a staff member in our school or our district who has a PED So Brady DeLume is a teacher at Primera Middle School.
[00:47:15] We'll see his information here.
[00:47:16] If we have staff photos, we'll see those as well.
[00:47:19] We'll see the ID for that staff member, the site that they're assigned to, grade level will be blank, and then status for our staff is 224.
[00:47:27] The rest of the information is the same, but you will notice that that default menu item is not added to an adult transaction because it is not considered a reimbursable meal.
[00:47:38] We can use that button for our adult transactions.
[00:47:42] It will pull it at the adult meal price and it will record it as an adult meal, not as a reimbursable meal.
[00:47:50] So we've got Brady, he's got that lunch meal, that bag of chips, a fruit, and a water.
[00:47:55] We'll review those items and then complete that sale.
[00:48:01] Next, I want to direct your attention to the bottom of my POS screen here.
[00:48:06] I call these my no account patron buttons.
[00:48:08] so I've got generic buttons down here that I can use to complete the sale for anybody who does not have a PIN in the system or does not exist in my school cafe system.
[00:48:20] The first button that I want to show you is the program adult button.
[00:48:23] This can be used for your food service staff if they eat free.
[00:48:27] We can click program adult and say you have five head cooks that come through the line and they all want that lunch meal.
[00:48:33] I can add those five lunch meals to that program adult transaction They will pull at $0 and I can complete that sale.
[00:48:50] I also have a generic student button down here at the bottom of my screen.
[00:48:54] If I have a newly enrolled student who does not exist in School Cafe yet, but they need to purchase their lunch meal, I can click the student button here.
[00:49:03] That lunch meal will be added because it is a student transaction and that qualifies as a reimbursable meal, but you will notice that the charge button is disabled.
[00:49:12] Because there is no account to charge that student meal to, this will have to be a cash transaction, so I'll click the pay button.
[00:49:20] Hopefully that new student brought money to buy lunch with today, so they hand you a $5 bill.
[00:49:25] You give them their $2.65 change back, and then you complete that transaction.
[00:49:35] If we ever have visitors on site, such as parents or grandparents that need to purchase a meal, we can use this visitor button here.
[00:49:44] Now you can complete a visitor transaction using cash by adding that lunch meal and clicking the pay button.
[00:49:52] However, if you would allow that parent or that grandparent to purchase that lunch meal, using the money on their child's account, that is also an option.
[00:50:03] This will be dependent upon your process as a district, but if that's something that we would allow, say Katie's mom is on site, She wants to purchase a lunch meal for herself.
[00:50:14] So we do track that under the visitor button But she didn't bring any cash with her today.
[00:50:19] She knows that Katie has money on her account So she says can I just use the money on Katie's account to pay for my lunch meal?
[00:50:26] If that's something that we would allow we would click this select account button here The system tells us to choose the students account and that we want to charge that meal, too So I'll search for Katie here and it'll pull up Katie's information.
[00:50:42] Now you will notice that Katie's name is grayed out and that lunch meal is at the adult meal price.
[00:50:47] This is not a meal that's being recorded for Katie.
[00:50:50] This is not a reimbursable meal.
[00:50:52] This is an adult visitor meal that's being recorded as an adult meal using the money on Katie's account.
[00:50:59] So again, if that's something that we would allow, we're still going to confirm that it is a visitor transaction, confirm that just grabbing that lunch meal and then complete that sale.
[00:51:13] If you have any staff members on site who do not have a PIN number, maybe they don't work for the district full-time, maybe a substitute teacher, you can use the staff button down here for a generic staff meal as well.
[00:51:27] This one does have to be a cash transaction because there is no staff account to charge that meal to, so we'll that lunch meal.
[00:51:37] We'll click the pay button to complete that cash transaction.
[00:51:41] They can also write a check but it would have to be for that exact amount.
[00:51:46] That amount tendered will do five dollars here.
[00:51:48] We'll give that two dollars and fifteen cents and change back and then we'll complete that transaction.
[00:51:55] That concludes the examples that I have for you all here on this traditional serving screen.
[00:52:01] So I am going to pause for just a minute or two to make sure that there no further questions about the traditional serving line service and then we'll look at a couple other screens before we finish up for the day.
[00:52:16] So be sure to get those questions into that questions box if you have any and we'll continue on in just a moment.
[00:53:10] Alright moving right along the next couple of things that I want to show you guys are up here in what we call our hamburger menu.
[00:53:16] So I'll open up my hamburger menu here and the first place want to take you is the bulk sales screen.
[00:53:22] So we'll select bulk sales.
[00:53:25] Now we can serve bulk sales by homeroom or by the special rosters that we discussed earlier.
[00:53:30] We'll do an example of both.
[00:53:33] So bulk sales by homeroom, we'll select that grade level, select the homeroom that we want to serve, select the meal type here.
[00:53:41] So for this example, I'll serve breakfast in the classroom, and then we'll select that menu item.
[00:53:46] You will only see your meal options in this list.
[00:53:49] know a la carte here.
[00:53:51] We'll load those students and it's going to pull up a roster of all of the students in that homeroom.
[00:53:58] I can select all here by clicking the select all button in the top right corner and then I could maybe unselect the students that maybe were absent that day or did not receive that breakfast meal.
[00:54:11] You'll also notice that you do have a plus sign here next to each student's that does give you the opportunity to add funds or charge a la carte items for that specific student.
[00:54:24] The bulk sales feature again is only recording that breakfast meal for the students that have been selected.
[00:54:32] A couple of things to keep in mind about bulk sales.
[00:54:34] It does not consider any allergens or restrictions on accounts.
[00:54:39] It doesn't consider any balances or charge limits and you can only serve one reimbursable meal per meal type through bulk sales.
[00:54:47] So again we selected all, we unselected a few students who were not at school that day, and then we will record sales for those 20 students.
[00:54:59] I can also complete a bulk sale by special roster, so I'll toggle over here to roster.
[00:55:05] We'll select that chess club once again, maybe the chess club went on a field trip and they were served lunch, and then I got a roster from that chess club teacher telling me who received that DM lunch meal.
[00:55:17] So I'll load students.
[00:55:20] I'll see all of those kiddos on that chess club roster.
[00:55:23] You will notice that Paula is disabled here because she did receive that lunch meal through the traditional serving line today.
[00:55:29] So we cannot serve her that second meal through bulk sales.
[00:55:33] We'll go ahead and select all.
[00:55:34] Everybody else in the chess club did receive that lunch meal today.
[00:55:37] So we'll record sales for those 19 students.
[00:55:45] The next screen that I wanna show you is how we can make payments to accounts between services.
[00:55:50] So if you remember, we did add funds to Henry's account through the traditional serving line.
[00:55:56] That is always an option if you have service open.
[00:55:59] But say, for example, you're between your breakfast and your lunch service and a student comes to the cafeteria and hands you money to put on their account.
[00:56:07] You can always access the payments option from your POS.
[00:56:10] You do not have to have a service open to see this payments option.
[00:56:15] and this exists on your dashboard screen as well.
[00:56:18] So we'll go ahead and click payments.
[00:56:21] And again, I can search for students by PIN or by lookup.
[00:56:24] We'll go ahead and search for Joy Springston here.
[00:56:30] Joy comes to the line between, or to the cafeteria between breakfast and lunch and has a payment for me to add to her account.
[00:56:37] So she's got money on her account for lunch.
[00:56:40] We'll see her information up here at the top, her current balance.
[00:56:43] This is being tracked as a transaction in that session.
[00:56:48] It will be its own transaction if we don't have a service open.
[00:56:51] I can do cash or check.
[00:56:53] We'll go ahead and toggle over to check because Joy handed me a hundred dollar check today.
[00:56:58] And then I do need that three-digit check number.
[00:57:02] We've got information down here again, current balance, that payment being made, and her new balance once that payment's completed.
[00:57:09] We do have a threshold set at hundred dollars in School Cafe.
[00:57:12] So when I make that hundred dollar or more payment, the system is just going to confirm with me that that is the correct amount because it's a little bit higher than we typically see.
[00:57:21] If you did type in the correct amount, you'll just click the yes button and that payment will be processed.
[00:57:30] You can also look students up by PIN number on the payment screen if necessary.
[00:57:35] So we've got Abigail that also brings a payment to the cafeteria between services or before breakfast or after lunch.
[00:57:42] She hands me a $50 cash payment, that's why we have that threshold set so that we don't accidentally over apply.
[00:57:51] We've got that $50 payment here, her current balance, her payment, and her new balance down here at the bottom, and we'll go ahead and make that payment.
[00:58:07] I'm going to now open up my hamburger menu and go down to my transaction screen.
[00:58:13] I just want to demonstrate to you guys that if throughout service you have something that needs to be marked for review, but maybe you don't have time in the middle of service to mark it for review in the POS.
[00:58:23] You only have time to make a quick note on that cashier's log.
[00:58:27] You can come in after service to mark that transaction for review.
[00:58:31] So we'll have information about our transactions here on this screen.
[00:58:34] The number, the name of the patron, the time, the meal type.
[00:58:39] Transaction type will have an icon.
[00:58:41] A stack of bills is a cash transaction.
[00:58:43] That little book is a check transaction.
[00:58:46] and then the shopping bag is when we hit the charge button.
[00:58:50] Again, I do have those transaction details over on the right, and I can mark a transaction for review if necessary.
[00:59:02] I'm gonna head back to our serving screen by clicking continue service.
[00:59:08] I'm gonna pull that menu grid back up on the screen for us so that I can demonstrate one more thing before we close out.
[00:59:16] If you have any left-handed cashiers or anybody who prefers that pin pad on the left side of the screen.
[00:59:23] We'll go ahead and open up that hamburger menu and click the switch hands option here.
[00:59:28] And that will mirror that screen for us in the case that that is a better option.
[00:59:34] Go ahead and switch that back.
[00:59:36] And then the last thing that I wanna show you guys here in the POS is how we close service.
[00:59:42] So my last step as a cashier is to close my POS service.
[00:59:47] Best practice is gonna be to open and close for breakfast, as well as open and close for lunch.
[00:59:53] That way, our transactions stay separate for our meal types.
[00:59:57] To close service, I'll come up here to the hamburger menu and click Close Service.
[01:00:05] The School Cafe POS is what we call a blind close application, meaning that it's not going to tell you here on this screen what you should have in your register.
[01:00:13] It's not going to tell you if you balanced.
[01:00:15] It's simply going to ask you to enter those cash denominations were collected through service, and then close.
[01:00:22] You will notice down here that we already have a closing balance.
[01:00:26] You may have guessed that those are the checks that we entered throughout service, so we do have $175 in checks.
[01:00:33] If that's the wrong check amount, make a note on your cashier's log.
[01:00:37] That way that can be reviewed during reconciliation, and then your job is to enter those cash denominations.
[01:00:43] So I'll click into each field of the denominations that I received during service.
[01:00:49] If we entered any opening balance, any petty cash, any change fund, we want to include that in our closing balance.
[01:00:57] So that tells the system that was our change fund, so we're going to include that on this screen.
[01:01:03] So we'll count all of the cash in the register.
[01:01:06] I'll count a couple 20s and I've got three 10s.
[01:01:10] Just entering some random denominations here for you guys to show you.
[01:01:15] Enter four quarters, we'll do three dimes and a couple pennies.
[01:01:20] Now this closing balance should be the total of all of my cash plus all of my checks.
[01:01:27] If not, that will be resolved during the reconciliation process by your managers.
[01:01:32] Once this screen is complete, we'll go ahead and click close service.
[01:01:37] And that is my last step as a cashier at the School Cafe POS.
[01:01:44] I'm going to head back to our PowerPoint now to review what we covered together today, but if you do have any questions, please enter them into the chat.
[01:01:54] I will keep that open for a few minutes, but we'll go ahead and review.
[01:02:00] We logged into our School Cafe account and we accessed the POS through our School Cafe dashboard.
[01:02:06] We opened service and talked about entering any petty cash or change fund on that screen.
[01:02:12] We looked at our serving screen and several different transaction examples.
[01:02:17] We looked at the bulk sales feature as well as payments between services.
[01:02:22] For sites that have it enabled, we also covered our food detection feature and how detected items load into the transaction automatically.
[01:02:30] We closed our service and the last thing that we're going to do that we haven't done yet is sign out.
[01:02:38] So I'm going to head back to School Cafe to show you guys that process for signing out once we're completely done with service and we're ready to sign out of our account.
[01:02:47] We'll come here to the hamburger menu one more time and all the way down to the bottom to click sign out.
[01:02:55] And that concludes our school cafe cashier webinar for this Thursday morning.
[01:03:03] I'm going to hang out for just a minute and make sure that there are no further questions that come through that questions box.
[01:03:09] But if you do not have any other questions, thank you again for joining me this morning.
[01:03:14] This recording will be emailed out to all of those of you who were able to attend as well as the people who registered and were unable to attend.
[01:03:24] So you will receive the recording and have a wonderful rest of your week and long weekend.
