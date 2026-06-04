# Training Transcript — Eligibility: Applications, Income Surveys & Verification

**Date:** May 22, 2026
**Presenters:** Sarah Chen (Implementation Specialist), Marcus Webb (Senior Implementation Specialist)
**Attendees:** Alexandria City Public Schools onboarding cohort (~8 staff, including Eligibility Director Teresa Ruiz)
**Platform:** SchoolCafé 2.0
**Module:** Eligibility
**Duration:** ~62 minutes
**Recording ID:** REC-2026-0522-ELIG-001

---

[00:00]

**Sarah:** Alright, good morning everyone. Um, so today we're covering — actually, Marcus, do you want to introduce what we're doing today? Marcus is going to take the verification section later because he literally wrote the book on it.

**Marcus:** Yeah, happy to. So today is Eligibility — applications, income surveys, and verification. That's the processing, sampling, tracking, the whole nine yards. This is the module that keeps you compliant with the feds, so, uh, pay attention. [laughs]

**Sarah:** [laughs] No pressure. So yeah, we'll start with applications — adding them, viewing them, processing them. Then income surveys. And then Marcus will take over for the verification piece — sampling, tracking, forms, all that. Sound good?

[00:38]

**Sarah:** Okay so, uh, let me share my screen. Can everyone — oh wait. Teresa, you're on mute but I can see you're trying to talk.

**Teresa:** Yeah sorry, I was just going to ask — will you be covering the Family Hub side too? Because our parents are asking about the online application.

**Sarah:** So Family Hub is a separate training. We're doing the back-office side today — when applications come in, how you process them, how you manage them. The Family Hub piece where parents submit online is... I think that's next week? Marcus, is that right?

**Marcus:** Yeah, Thursday. Family Hub applications, the parent portal, all that. Today is your internal workflow.

**Teresa:** Okay, perfect.

[01:15]

**Sarah:** Alright, so. Applications. Navigate to Eligibility, then Applications. And you'll see this page with three tabs — ALL, PENDING APPLICATIONS, and PENDING STUDENTS. We'll go through all three.

[01:28]

**Sarah:** But first, let's add a new application. Click the NEW button in the top right. And you get the Application Entry page. Now — see this wizard at the top? It's got these circles — Students, Benefits, Household Members, Contact Info, Details, Review, Submit. As you complete each section, the circle turns purple. And you can click on any purple circle to jump back to that section. Pretty standard wizard pattern.

[01:55]

**Sarah:** So, Students first. You type a student's name or ID into the search field. Let me type... "Rodriguez." And results pop up. Click SELECT STUDENT on the one you want. And now you get this Add a Student slide deck where you verify the information.

[02:12]

**Sarah:** Here's the important part — the Categorical Status question. Yes or No. Does this student have a categorical eligibility? Like, are they directly certified through SNAP or foster care or whatever? If you click Yes, a Categories dropdown shows up. Pick the category.

[02:30]

**Sarah:** Now here's the — okay, this trips people up every single time. Listen carefully. If you answer Yes but the confirmed Categorical Status is unchecked — meaning the student is categorically eligible but it hasn't been confirmed in the system yet — then the student gets their eligibility from THIS application, not from their categorical status. So the application determination overrides the unconfirmed categorical. Make sense?

**Attendee (Daniel):** Wait, so if a kid is on SNAP but we haven't confirmed it, and we enter an application that says they're Reduced based on income, they get Reduced? Not Free?

**Sarah:** Yes, because the categorical isn't confirmed. Once it IS confirmed — like, once the direct certification match comes through — then the categorical takes over. But until then, the application is what drives eligibility.

**Daniel:** That seems backwards...

**Sarah:** I know, I know. It's a USDA thing. The system is following the reg — the confirmed status is the gatekeeper. If you want, I can — actually, let me not go down the USDA rabbit hole right now. Just remember: confirmed categorical overrides, unconfirmed does not.

[03:28]

**Sarah:** Okay, so you saved the student. Now — if the student doesn't show up in search, you can use the ADD NEW STUDENT button. Same slide deck, but you're entering all the info manually — first name, last name, all that. And the same Categorical Status question. Save, and you're back on the Application Entry page. Click NEXT.

[03:48]

**Sarah:** Benefits section. Three questions. First — "Do any household members receive benefits from FDPIR, SNAP, or TANF?" If Yes, you optionally enter the Recipient Name, then select the Case Type, and enter the Case Number. That Case Number is required.

[04:08]

**Sarah:** Second question — "Has the applicant Refused benefits?" Yes or No. And then NEXT.

**Teresa:** Sarah, quick question. The first question says FDPIR, FS/TANF, SNAP, TANF. But you just said FDPIR, SNAP, TANF. Is FS/TANF separate from TANF?

**Sarah:** Good catch. FS/TANF is, um... it's an older label. It stands for Food Stamps slash TANF. Some states still use that terminology. In practice, for your district, you'd use SNAP or TANF. The system lists all of them because different states have different naming conventions. But the Case Type dropdown will narrow it down for you. Don't worry too much about the label — pick the one that matches your state's assistance program.

**Teresa:** Okay, but our state uses a combined case number for SNAP and TANF. Do we enter it twice?

**Sarah:** No, just once. Pick whichever Case Type matches — if it's SNAP, pick SNAP. If it's a combined program, I'd... hmm, actually I'm not sure. Marcus, do you know?

**Marcus:** Yeah, if it's a combined case number, just use SNAP as the Case Type. That's what most states do.

**Teresa:** Even if it's technically a TANF case?

**Marcus:** For purposes of this system, yes. The eligibility engine cares about whether there IS a case number, not which program label you attach to it. The determination logic is the same either way.

**Teresa:** That doesn't sound right to me based on how we've done it before, but okay, I'll take your word for it for now.

[05:30]

**Sarah:** Alright, moving on. Household Members. This is where you enter income information. So first — there's a TOTAL CHILD INCOME field. Click the pencil icon to edit it. Enter the amount, select the Frequency — like weekly, monthly, annually — and save.

[05:48]

**Sarah:** Then ADD HOUSEHOLD MEMBER for each adult. First Name, Last Name. Does this member receive income? If yes, enter the income amounts by source — like earnings, Social Security, whatever — and the frequency for each. Save. Repeat for every household member on the application.

[06:08]

**Sarah:** At the bottom — Household Size. And this is where people make mistakes. The Household Size has to match what's on the paper application. If the family wrote "5" but you only added 3 household members, the system will still use 5 for the calculation. It's what's on the paper that matters, not how many members you actually entered. The system doesn't — 

**Attendee (Maria):** Wait, really? It doesn't validate that?

**Sarah:** It does not. The Household Size field is a manual entry. It doesn't auto-calculate from the members you added. Because sometimes families write down a number that includes people they didn't list individually. Like, they wrote "5" because they have two small children with no income, and they didn't bother listing them. You still enter 5.

**Maria:** That's... kind of a problem. What if someone enters the wrong number?

**Sarah:** That's why there's a Review step before Submit. We'll get there. But yeah, the system trusts what you type. It's on the processor to catch mistakes.

[06:55]

**Sarah:** Okay, NEXT. Contact Info — just the applicant's contact details. Phone, email, address. All optional. NEXT.

[07:02]

**Sarah:** Details — Ethnicity, Racial Identity, Other Benefits. This is demographic data. Also optional. NEXT.

[07:10]

**Sarah:** Review. This is where you double-check everything. You can click the pencil icon next to any section to edit it, or click the wizard circles at the top to jump back. Look at the info, make sure it matches the paper application. NEXT.

[07:22]

**Sarah:** Submit. Okay, this is the big one. First — last four digits of the SSN. Or check "Application has no SSN" if they didn't provide one. Second — click "Application signature confirmed" to certify that the applicant signed it. Language Preference. Application Received Date — and this matters for turnaround time calculations, so don't just put today's date if you received it two weeks ago. Put the actual date it was received.

[07:50]

**Sarah:** Then you'll see Pending Reasons, if there are any. Like, maybe the household size doesn't — actually wait, I think it does flag if the numbers don't add up? Marcus, does it flag household size mismatches?

**Marcus:** Uh, I don't think so. It might flag if income frequency is missing, or if the Case Number format is wrong. But household size, I don't believe that's a pending trigger.

**Sarah:** Okay, yeah. So the Pending Reasons will show things like missing information, format issues, stuff like that. Address them if you can.

[08:15]

**Sarah:** Comments field — optional. And then the Eligibility Determination. This is the good part — the system tells you right here what the determination is. Free, Reduced, or Paid. Based on the income and household size you entered. Or if they have a case number, it might be categorical Free.

[08:32]

**Sarah:** Click SUBMIT. Done! Or — you can click PENDING instead if you need to save it and come back later. The application goes to the Pending tab instead of being processed.

[08:42]

**Sarah:** After submit, you can view the application, export it, print it. And there are two buttons at the bottom — ADD ANOTHER APPLICATION to start the next one, or IM DONE FOR NOW to go back to the Applications page.

[08:55]

**Sarah:** Alright, let me show the ALL tab now. This is where you see all your applications. You've got filters — Academic Year, Site Code, Grade, Entry Method, Status, Benefits. Select your filters, click APPLY, and the results show up below.

[09:10]

**Attendee (Daniel):** What's the Entry Method filter?

**Sarah:** That's how the application was entered — manual, online through Family Hub, um, I think there's a file upload option too? For bulk imports? I'm actually not 100% sure on all the entry methods. But Manual and Online are the main ones.

[09:25]

**Sarah:** So for each application in the list, you've got action icons. The paper icon — View — opens the Application Details page. The clock icon — History — shows you every change that's been made to that application. Who did it, when, what changed. Old value, new value. Very useful for audits.

[09:42]

**Sarah:** On the Application Details page — lots going on. At the top you see the Application Number and Status. Then the Eligibility — Free, Reduced, Paid, whatever it determined. Then you've got these buttons — PROCESS APPLICATION, NOTIFY, MORE ACTIONS.

[10:00]

**Sarah:** PROCESS APPLICATION — use this to process or reprocess. And here's a gotcha — if the application is currently Pending or already Processed, the system requires a comment before you can process it. You can't just click the button and walk away. You have to say WHY you're processing or reprocessing.

[10:18]

**Sarah:** NOTIFY — sends a notification to the household. About their application status, their eligibility, whatever. When you click it, you get email and print options. The system can email if there's a guardian email address on file. Otherwise you print and mail. And — oh, this is cool — the notifications go out in the language the applicant selected. So if they picked Spanish, and you have a Spanish template configured, the letter goes out in Spanish.

[10:45]

**Sarah:** MORE ACTIONS — this dropdown has a bunch of stuff. MARK AS PENDING, REFUSE BENEFITS, DELETE, ADD TO VERIFICATION, APPLICATION IMAGE, EXPORT. Let me hit the important ones.

[10:58]

**Sarah:** REFUSE BENEFITS — this is when a family says "we don't want free or reduced meals." It happens. You click it, and you see the eligibility determination and the basis. Then you select a Result, enter a Start Date, add a comment, and save.

[11:12]

**Sarah:** DELETE — removes the application. But here's the key behavior — if there are students on this application, deleting it returns them to their PREVIOUS eligibility. So if a kid was Paid before this application made them Free, deleting the application puts them back to Paid. You have to select a Reason and add a comment.

[11:30]

**Sarah:** ADD TO VERIFICATION — puts this application in the verification pool. We'll talk way more about verification when Marcus takes over. But this is how you manually add one — you'd use this for Cause applications, for example.

[11:42]

**Sarah:** APPLICATION IMAGE — shows a preview of the submitted application. Like, if they scanned it in, you can see the scanned image here. You can export or print it.

**Sarah:** EXPORT — generates a PDF. You can include or exclude Details, Eligibility, Comments, History. Nice for sending to a supervisor who needs to review an application.

[12:00]

**Sarah:** The Application Details page also has section links on the right side — Summary, Students, Household Members, Contact Information, Details, Notifications, Comments, Documents, Application Status History, Adult Signature / SSN. Click any of those to jump to that section on the page.

[12:18]

**Sarah:** Okay, I want to quickly cover the other two tabs and then we'll move to income surveys.

[12:24]

**Sarah:** PENDING APPLICATIONS tab. This shows applications that either failed automatic processing or were manually saved as Pending. You can View, Delete, or see History. Same actions as the ALL tab but limited to pending ones. If you view a pending application, check the Summary section for the Pending Reasons — that'll tell you why it didn't process automatically.

[12:48]

**Sarah:** PENDING STUDENTS tab. This is — okay, this one's kind of unique. So sometimes applications come in — especially from Family Hub — and the student information doesn't match anyone in your SIS. Like, the parent typed "Johnny Smith" but the SIS has "Jonathan Smith." Or the student hasn't been entered into the SIS yet — maybe they're a new enrollee.

[13:10]

**Sarah:** So these applications land in the PENDING STUDENTS tab. And you've got a few options. First — FIND MATCHES. Click that button and the system tries to find matches in the database. If it finds one, you get a green checkmark in the Matched Status column.

[13:25]

**Sarah:** Then PROCESS MATCHES — select the ones with green checkmarks, click PROCESS MATCHES, confirm, and done. The student gets linked.

[13:32]

**Sarah:** If the system can't find a match, you can manually search. Click the magnifying glass icon next to the student. Type the name into the search field. When you find the right student, click SELECT STUDENT. The system shows you a Compare Details view — Application Details on one side, Matched Student on the other. Compare them, and if they match, click MATCH.

[13:55]

**Sarah:** Or — if the info is just wrong — click the pencil icon to Edit the student's details on the application. Fix the name or ID, save, and try matching again.

[14:08]

**Attendee (Daniel):** What happens if the student genuinely doesn't exist in the SIS? Like they're brand new?

**Sarah:** Then the application stays pending until the student is entered into the SIS. Once the SIS import runs and the student shows up, you can come back here and match them. In PrimeroEdge, we used to have a way to — actually no, forget that. In SchoolCafé 2.0, the student has to exist in the system first. There's no way to create a student record from within Eligibility. That's a Student Management function.

**Daniel:** So we could have an application sitting in pending for weeks?

**Sarah:** Technically yes. The turnaround clock starts from the Received Date though, so you want to get those students entered ASAP. Coordinate with whoever manages your SIS imports.

[14:52]

**Sarah:** Okay, let me real quick do Application Processing. This is a slightly different workflow — instead of going into individual applications, you click the PROCESS button at the top of the Applications page. And now you're in a batch processing mode. You see how many applications are Processed versus Available, and you use PREVIOUS and NEXT buttons to go through them one by one.

[15:12]

**Sarah:** For each application, you see the full details page. You can process it — PROCESS APPLICATION brings up a comment field, then saves and goes to the next one. Or PROCESS APPLICATION & QUIT processes this one and kicks you back to the Applications page. Handy if you just need to handle one.

[15:30]

**Sarah:** Same NOTIFY and MORE ACTIONS buttons we already covered. Same application details sections.

[15:38]

**Sarah:** Questions on applications before I move to income surveys?

[15:42]

**Teresa:** Yeah — when you said the system determines Free, Reduced, or Paid based on income and household size — does it use the federal income eligibility guidelines? And which year's guidelines?

**Sarah:** It uses whatever guidelines your district has configured. Typically yes, the federal IEGs. And it should be — well, the system auto-updates when USDA releases new guidelines each July. But you should verify the numbers are right at the start of each school year. I think there's a Configuration page somewhere that shows the current thresholds...

**Marcus:** It's under Eligibility, Configuration, Income Guidelines. You can see the thresholds there. But don't manually change them — the system pulls them from the USDA data feed. If they look wrong, call support.

**Teresa:** And what about states with higher guidelines? We're in Virginia, and I think our state guidelines might be different from federal.

**Marcus:** The system supports state-level overrides. But that's a configuration thing that would have been set up during implementation. If you're not sure, check with your Cybersoft contact.

[16:38]

**Sarah:** Okay, income surveys. This is — income surveys are different from applications. They're used by districts in Special Provision Programs — CEP, Provision II, that kind of thing. Instead of families applying for free and reduced, they submit household income data for state funding compliance.

[16:58]

**Sarah:** Navigate to Eligibility, Income Surveys. Click NEW. And you get the Add New Survey page. Similar wizard — Students, Household, Details, Contact Info, Comments, Review. Similar purple circle navigation.

[17:12]

**Sarah:** Students section — type a name or ID, click ADD. And note — if the system detects other students in the same household, it'll suggest adding them too. Nice time-saver.

[17:24]

**Sarah:** If the student doesn't exist, click ADD NEW. Enter first and last name — everything else is optional. But these students come in with a PENDING status, and you can edit or delete them.

[17:38]

**Sarah:** Click NEXT. Household. Now this is different from applications. You have two Response Types — Special Assistance and Income.

[17:48]

**Sarah:** Special Assistance — if a household member receives assistance from SNAP, TANF, whatever. Select the Case Type, enter the Case Number. And — this is specific — the Case Number has to match the established format for the case type. So if your state's SNAP numbers are always 10 digits, and someone enters 8 digits, the system will reject it. I think. Actually, I'm not sure if the system validates the format or if it's just a note for the processor to check. Marcus?

**Marcus:** It validates. If the format doesn't match, you'll get an error on submit.

[18:18]

**Sarah:** Income Response Type — if no one in the household receives special assistance. You enter Household Size, select a Frequency, and then select an Income Range from a dropdown. Notice it's a RANGE, not an exact number. Unlike applications where you enter exact income, surveys use income ranges.

[18:38]

**Attendee (Maria):** Why the difference? Why ranges for surveys but exact numbers for applications?

**Sarah:** Because surveys are for aggregate statistical purposes — they're not determining individual eligibility the same way applications do. Applications feed directly into the child's eligibility status. Surveys are for... I want to say it's for the claiming percentage? Or for identifying students in need? Honestly, the USDA policy behind it is complicated and varies by provision type. The bottom line is: applications = exact income, surveys = income range.

**Teresa:** It's for the Identified Student Percentage, or ISP. And also for the FNS-742 — the Verification Collection Worksheet. Different regulatory requirement, different data granularity.

**Sarah:** There you go. Teresa knows this better than I do. [laughs]

[19:25]

**Sarah:** NEXT. Details — Ethnicity, Racial Identity, Other Benefits. Optional. NEXT. Contact Info — optional. NEXT.

[19:32]

**Sarah:** Comments section — Language Preference, Survey Accepted Date (NOT Survey Submitted Date — it's the date the district accepted the survey), Add Comment field. And there's a Signature Confirmed checkbox. And — oh, this is different from applications — you can upload documents right here. Drag and drop or select files. Like if the family submitted a paper survey and you scanned it.

[19:55]

**Sarah:** NEXT. Review everything. Then SUBMIT. Or MARK AS PENDING to save for later. After submit, you can export the summary as a PDF and either ADD ANOTHER SURVEY or I'M DONE FOR NOW.

[20:08]

**Sarah:** For viewing surveys — navigate to Income Surveys, you've got ALL tab and PENDING tab. Similar to applications. ALL tab shows everything with filters for Academic Year and Benefits. PENDING tab shows pending ones.

[20:22]

**Sarah:** On each survey, you can View Details or View History. On the details page, you've got PROCESS SURVEY, NOTIFY, and MORE ACTIONS. The MORE ACTIONS has MARK AS PENDING SURVEY and DELETE SURVEY. Both require a comment.

[20:40]

**Sarah:** One thing I want to call out — the Processing page. Not the PROCESS button on applications — this is a separate page under Eligibility called Processing. It shows you batches of applications that were processed within a date range. So you select an Academic Year, enter a Start Date and End Date, click APPLY, and you see processing sessions.

[21:00]

**Sarah:** Click View on a session and you get the Session Summary. From there, you can click any Application Number to jump to its details. And there's a GENERATE APPLICATION APPROVAL LIST button — this creates a printable approval list that your supervisor or verification officer can sign off on. Export as PDF or print. This is your audit trail document.

[21:22]

**Sarah:** That's it for my part. Marcus, you want to take verification?

[21:28]

**Marcus:** Yeah, let me get my screen sharing going... one sec...

[long pause]

**Marcus:** Can you all see my screen? Okay, great. So — verification. This is the part of the program that nobody likes but everybody has to do. USDA requires every school food authority to verify a sample of applications each year. What that means is you pull a sample of approved applications, contact those families, and ask them to prove their income or benefits. If they can't or don't respond, you adjust their eligibility.

[22:00]

**Marcus:** In SchoolCafé 2.0, the verification workflow has four main pieces: Sampling, Tracking, Tracking Forms, and Inactive Applications. Let's start with Sampling.

[22:12]

**Marcus:** Navigate to Eligibility, then Verification, then Sampling. Or it might be — I always forget — it might just be Eligibility, Sampling. Let me find it. Yeah, it's under — okay, I see it. Sampling.

[22:25]

**Marcus:** Click SCHEDULE SAMPLE. And you get the Create Sample page with its own wizard. First question: Verification Type. "How would you like to have your verification samples scheduled this year?" Two options — A single sample, which is Standard, or Multiple smaller samples, which is Rolling.

[22:45]

**Marcus:** Standard means you pull one sample, usually around November 15th — that's the typical target — and you verify that entire batch. Rolling means you pull smaller samples at multiple dates throughout the fall. Rolling is newer and some districts like it because it spreads the workload. But most districts still do Standard.

**Teresa:** We've always done Standard. Is there an advantage to Rolling?

**Marcus:** Honestly? For most districts, Standard is fine. Rolling makes sense if you have a really high volume of applications and you want to start verification earlier. But it adds complexity because you have to manage multiple sample dates and make sure you don't miss any. I'd stick with Standard unless you have a specific reason to change.

[23:20]

**Marcus:** Click NEXT. Sample Process. "Which sample method are you using this year?" Three options — Standard (formerly Error Prone), Alternate One (formerly Random), and Alternate Two (formerly Focused).

**Teresa:** Why did they rename them?

**Marcus:** USDA updated the terminology a couple years ago. Error Prone is now Standard because it's the default. Random is Alternate One. Focused is Alternate Two. If you hear the old names, they mean the same thing.

**Marcus:** Uh, I should clarify — Standard, the sample method, is different from Standard the verification type we just talked about. Confusing, I know. One is about WHEN you sample (single date vs. rolling), the other is about HOW you select which applications to sample (error prone targeting vs. random vs. focused). Two different things with the same name.

[23:55]

**Marcus:** Click NEXT. Verification Dates. If you chose Rolling, you'll see "What dates should be used for rolling samples?" and you click ADD DATE to add each sampling date. For Standard, you skip that.

[24:08]

**Marcus:** Then: "What date should be used for final sample?" Edit the Sampling Date if needed. And: "What date should students be counted on for the Verification Collection Worksheet (FNS-742)?" Edit the Verification Collection Date if needed.

[24:25]

**Marcus:** Now — important rule. If either of these dates falls on a weekend, move them. The system should warn you, but double-check. And if you change either date, a comment is required. You can't just silently adjust verification dates.

[24:40]

**Marcus:** Click NEXT. Exclude Sites. You'll see a list of all your sites with checkboxes. By default, they're all selected — meaning all sites are INCLUDED in verification. To exclude a site, uncheck it.

[24:55]

**Marcus:** Wait — I said that wrong. Let me reread this. Okay, it says "Deselect the site(s) that should be excluded for verification." So... you deselect to exclude. If you click the header checkbox, it deselects ALL sites — which would exclude everything. Don't do that. [laughs]

**Marcus:** And there's a note: "Sites operating under special provision programs (CEP/Provision II) should remain selected." That might sound counterintuitive — why would CEP schools be in the verification sample? — but it's because the verification process for CEP is different. It's not about individual household verification; it's about the ISP recalculation. They need to be in the sample pool for the numbers to work out.

**Daniel:** Wait I thought CEP schools were exempt from verification?

**Marcus:** CEP schools don't do traditional household-level verification, that's true. But they still need to be included in the sample for reporting purposes. The system handles it differently on the back end — it's not going to send verification letters to families at CEP schools. It's about the statistical sample being accurate. It's — honestly, this is one of those areas where the USDA rules are really confusing and the system just implements them. If you're not sure how it applies to your specific situation, talk to your state agency.

**Teresa:** He's right. We had this exact question with the state last year. CEP schools stay in the pool but the system knows not to contact families at those sites.

[26:00]

**Marcus:** Okay. Click SCHEDULE SAMPLE. Confirmation message. And here's the thing that surprises people — the sample generates OVERNIGHT, not in real-time. So you schedule it, and then the next morning the sample is ready. Don't sit there hitting refresh expecting it to appear immediately.

**Attendee (unknown):** Why overnight? That seems slow.

**Marcus:** Because the sampling algorithm has to analyze every approved application across the district, calculate the three-percent minimum, apply the error-prone targeting or random selection or whatever method you chose, and then exclude sites you deselected. For large districts with tens of thousands of applications, that's a non-trivial calculation. Running it as a batch job overnight keeps the system from bogging down during the day.

[26:42]

**Marcus:** Once the sample is generated, you'll see it on the Sampling page. And you've got these buttons next to each sample: HISTORY, RECALCULATE, EDIT SITES, ADD DATE, DELETE.

**Marcus:** RECALCULATE regenerates the sample. Use this if — let me think of a scenario — if applications were processed after the sample was generated. Like, you generated the sample on Monday, but a bunch of applications came in Tuesday. You'd recalculate to potentially include them.

**Marcus:** EDIT SITES lets you change which sites are included on the spot.

**Marcus:** ADD DATE is for rolling samples only — adds more dates.

**Marcus:** DELETE resets the entire verification sample. But note — applications that were added for Cause will still be available after regeneration. The "for Cause" ones are manual additions and they persist.

[27:30]

**Marcus:** Alright, Tracking. Navigate to Tracking. This is where you manage the actual verification process for each application in your sample. You've got FIVE tabs — Incomplete Applications, No Response Applications, Completed Applications, Deselected Applications, and... let me look... I know there's a fifth one. Oh wait, there might only be four. One second.

**Sarah:** [from off-screen] I think it's Incomplete, No Response, Completed, and Deselected.

**Marcus:** Yeah, four tabs. My bad. I was thinking of Tracking Forms, which is a separate page.

[28:00]

**Marcus:** INCOMPLETE APPLICATIONS tab. These are applications that are IN the verification sample but haven't been completed yet. Select Academic Year, Sample Number, APPLY. And you see the list.

[28:12]

**Marcus:** Click View on one. The Verification Details page. At the top — STATUS and LAST ACTION. Then you've got buttons: APPLICATION DETAILS takes you to the full application. NOTIFY sends a verification letter. VERIFICATION RESPONSE is where you enter the family's response — their proof of income or case number or whatever.

[28:35]

**Marcus:** When you click VERIFICATION RESPONSE, you get a page with questions based on what the family submitted. Answer them, and click VERIFICATION COMPLETE when everything is entered. That moves the application from Incomplete to Completed.

[28:48]

**Marcus:** Below the buttons, you've got expandable sections: Milestone Dates, Pre-Verification Application Information, Notifications and Comments, and Documents. You can add comments and upload documents — like scanned pay stubs or benefit verification letters.

[29:05]

**Marcus:** Now — the NOTIFY button on this page is for individual applications. But you can also do BULK notifications from the tab view. Select the checkboxes next to multiple applications, click NOTIFY, and you get the Sending Notice(s) slide deck.

[29:20]

**Marcus:** "Which letter are you sending?" — Selection Notice or Follow-up Notice. Selection Notice is the first letter you send. Follow-up Notice is when they haven't responded and you're sending a reminder. Then your Email/Print options — Email/Print (both), Email Only, Print All, Print Only. Select Sort By method. And NOTIFY.

[29:42]

**Marcus:** Oh, and this is really important — see the Auto Follow-up Notice toggle? Turn this on, select the number of days, and the system will automatically send follow-up notices if the family doesn't respond within that timeframe. This is huge for compliance because one of the biggest verification pain points is families who just never respond. This automation saves you from having to manually track who needs a follow-up letter. I believe it defaults to 10 days but you can change it.

[30:10]

**Teresa:** Does that require guardian email on file?

**Marcus:** For email notifications, yes. If there's no email, it won't send automatically — you'd have to do a print batch. But for a lot of your families, especially if they applied through Family Hub, the email should be there.

[30:25]

**Marcus:** History icon shows you the action history for each application — who did what, when.

[30:32]

**Marcus:** NO RESPONSE APPLICATIONS tab. After the follow-up notification is sent and there's still no response — or if the family submitted a "No Response" reply through Family Hub — the application moves here. This is your holding pen for families who aren't cooperating.

[30:50]

**Marcus:** Same View functionality — Verification Details, APPLICATION DETAILS, NOTIFY, VERIFICATION RESPONSE. Plus a NO RESPONSE button. That button is important. When you click it, you're telling the system: "This family has been contacted, they've had sufficient time, and they have not responded. Terminate their benefits."

[31:10]

**Marcus:** And the system implements that based on — there's a setting called Adverse Action – Number of Days. It's a system configuration value. After that many days, the students on the application drop to Paid status. I think the USDA minimum is 10 days from the date of the adverse action notice, but your district may configure it longer.

**Daniel:** So we manually have to click NO RESPONSE for each one?

**Marcus:** You can do it in bulk. Select multiple checkboxes, click the NO RESPONSE button at the top of the page. But yes, it's an explicit action. The system won't automatically terminate benefits just because the auto-follow-up was sent. That would be... legally problematic. [laughs] You need a human in the loop for that decision.

[31:52]

**Marcus:** COMPLETED APPLICATIONS tab. These are applications where verification is done — the family responded, you entered their data, everything's resolved. Each has an OUTCOME — like, did their eligibility change or stay the same?

[32:05]

**Marcus:** The buttons here are slightly different. You still have APPLICATION DETAILS and NOTIFY. But instead of VERIFICATION RESPONSE, you have ROLLBACK TO INCOMPLETE. This is your "oops" button — if you completed the verification but then realize you made a mistake, or new information comes in, you can roll it back. It returns the application to Incomplete status and may impact eligibility. A comment is required and you get a confirmation pop-up.

[32:30]

**Marcus:** For the notification on completed applications, you've got an additional letter type — Change / Completion Notice. So your options are Selection Notice, Follow-up Notice, or Change / Completion Notice.

[32:42]

**Marcus:** DESELECTED APPLICATIONS tab. If an application is removed from verification — maybe it was added by mistake, or the family withdrew — it shows up here. You can View it, and there's a RESTORE APPLICATION button to put it back in Incomplete if needed. Enter a comment, click Okay.

[33:00]

**Marcus:** And last piece — Tracking Forms. This is a separate page. Navigate to... actually I think it's still under Tracking? Let me find it. It might be its own nav item.

**Sarah:** It's under Eligibility, I think Verification, Tracking Forms? Or maybe just Eligibility, Tracking Forms.

**Marcus:** Found it. Okay, Tracking Forms. This shows individual tracking forms for each application in the sample. Academic Year dropdown, APPLY. And you see a table with Application Numbers and Student IDs.

[33:30]

**Marcus:** Click the App Info icon for an application and you get the Verification Tracking Form — a detailed form showing the application's progress through verification. Milestones, dates, results. You can export it as a PDF.

[33:42]

**Marcus:** You can also print tracking forms in bulk. Select checkboxes, click PRINT for selected, or PRINT ALL for everything. And there's a DOWNLOAD ALL button to export to — I want to say Excel? Yeah, export to Excel. Or the download icon does the same thing.

[34:00]

**Marcus:** Oh, and Inactive Applications. Almost forgot. This is a separate tab — it shows applications that fell inactive during the verification timeframe. What does that mean? It means the students on those applications moved to a different eligibility source. Like, maybe they got directly certified through SNAP after the verification sample was pulled. So their application became moot — they're now Free via direct certification, not via the application. The application goes inactive.

[34:28]

**Marcus:** You can view the Application Number, Student IDs, Process Date, Eligibility Start Date, and Inactive Date. That's it — it's a read-only report. There aren't any actions to take on these; they're just for your records.

[34:42]

**Marcus:** Alright, that's verification from start to finish. Sampling → Tracking → Tracking Forms → Inactive. And the key thing I want everyone to remember is the workflow: Generate your sample, send Selection Notices, wait for responses, enter verification responses as they come in, send Follow-up Notices to non-responders, mark No Response for families that never respond, and then generate your FNS-742 report. Teresa probably has this tattooed on her arm at this point.

**Teresa:** [laughs] I wish. We have a 42-step checklist we follow.

[35:10]

**Marcus:** Questions?

[35:12]

**Daniel:** Yeah, what about the three-percent rule? You mentioned it earlier. How does the system ensure the sample is at least three percent?

**Marcus:** The sampling algorithm handles that automatically based on the method you chose. Standard method — or Error Prone — targets applications that are most likely to have errors, but it ensures the minimum sample size meets the USDA three-percent requirement. Alternate One is truly random. Alternate Two lets you focus on specific criteria. All three guarantee the minimum sample. You don't have to manually count.

**Daniel:** And what if we want more than three percent?

**Marcus:** Then you'd... hmm. I don't think there's a "sample size" override. You could manually ADD TO VERIFICATION for additional applications from the Applications page. But the system's algorithm generates the USDA-minimum sample. If you need more, it's a manual addition.

**Teresa:** Actually, in past systems, there was an option to set the percentage higher. Is that not in SchoolCafé?

**Marcus:** I honestly don't remember. Let me check... I don't see it on the Create Sample wizard. It might be in Configuration. Let me add that to the follow-up list.

[36:10]

**Maria:** One more — when you said the auto-follow-up sends automatically, does it log who sent it? Like, does it say "System" or does it log the user who enabled the toggle?

**Marcus:** Good question. I believe it logs as a system action. So in the History, it would show "Auto Follow-up" or something similar as the actor, not a specific user. But I could be wrong on the exact wording. Check the History after the first auto-follow-up fires and you'll see.

[36:35]

**Sarah:** One thing I want to add before we wrap up — and this applies to both applications and verification — the notification system. When you send letters, the language matters. We mentioned this earlier but I want to reinforce it. When you're on the Application Details page, there's a Received Date and Language field. The Language field drives which template the notification uses. So if you have Spanish, Chinese, Arabic templates configured, and the family selected Spanish, the notification goes out in Spanish. If you DON'T have a template for that language, I believe it falls back to English? Marcus, is that right?

**Marcus:** Yep. Falls back to English.

**Sarah:** So make sure your templates are configured before you start bulk notifications. Otherwise everyone gets English regardless of preference.

[37:15]

**Sarah:** Okay, I think we're good. Teresa, anything else from your end?

**Teresa:** Just to clarify for my team — the verification dates. The FNS-742 date and the final sample date. Those are different dates. The FNS-742 is the Verification Collection Worksheet, and the date on that is the day you count students, which might not be the same day you pull the sample. Our state requires October — is it October 1st? — as the count date. And the sample date is whenever you actually generate the sample, which for us is usually late October or early November.

**Marcus:** That's exactly right. They're two different dates in the wizard for that reason. Don't set them to the same date unless your state specifically says to.

[37:55]

**Teresa:** And one more question — you showed us the PROCESS APPLICATION button on the individual application, and also the PROCESS button at the top of the Applications page for batch processing. Are those doing the same thing?

**Sarah:** Sort of. The PROCESS button at the top puts you in a sequential workflow — it queues up all available applications and you process them one by one with PREVIOUS/NEXT navigation. The PROCESS APPLICATION button on the details page processes just that one application. Same outcome, different workflow. Batch mode is faster if you have a stack of applications to get through.

**Teresa:** And the PROCESS APPLICATION & QUIT button?

**Sarah:** That's only in the batch mode. It processes the current application AND exits back to the Applications page. So instead of going to the next application in the queue, it drops you out of the queue entirely. Useful if you're in batch mode but only needed to process one.

[38:40]

**Marcus:** I think that's a wrap. Let me pull up the parking lot items real quick. We have: whether the system validates household size against household members entered, the exact entry methods available in the filter dropdown, combined SNAP/TANF case number handling, sample size percentage override, and auto-follow-up logging. I'll get answers on all of these and send them over by end of week.

**Sarah:** And I have: bulk allergen import — oh wait, that was from the Item Management training. [laughs] Never mind. I think we're clean.

[39:10]

**Sarah:** Alright everyone, thanks for sticking with us. We'll send out the recording and the parking lot follow-ups. Next up is Family Hub on Thursday. Have a good rest of your day.

[39:22]

[END OF RECORDING]
