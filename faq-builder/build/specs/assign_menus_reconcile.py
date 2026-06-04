# -*- coding: utf-8 -*-
#
# Reconciliation of the 33 previously-uncited Assign Menus source tickets against
# the existing FAQ in assign_menus_spec.py. Each ticket is either FOLDED into an
# existing Q&A (as an additional supporting case), captured as a NEW Q&A (genuinely
# new resolved guidance), or listed as REVIEWED (no usable content).
#
# Every one of the 33 IDs appears exactly once across APPEND values + NEW sources
# + REVIEWED:
#   290474 290889 291112 292004 292559 294120 296617 296678 297006 298114
#   303084 303800 304343 305356 307298 307341 312880 313018 313523 313547
#   314336 314576 315171 315415 315592 315799 316758 316770 317049 317631
#   318907 319957 320468

# Append these missing ticket IDs to existing Q&As, keyed by the existing Q&A's
# EXACT current sources string:
APPEND = {
    # "How do I assign a menu or menu cycle to a site?"
    # 291112: customer could not assign a cycle until all site groups (Pre-K-12) were checked.
    "Tickets 307164, 317759, 299524": "291112",

    # "When I assign a multi-week cycle, can I make it start on a specific week or day..."
    # 315799: cycle started on the wrong day; fixed by deleting the wrongly-placed days
    #         and re-assigning starting on the desired day.
    # 318907: erased the current week's menus and could not reassign the whole cycle
    #         mid-week; resolved by assigning Menu (single day) rather than Menu Cycle.
    "Tickets 300119, 304375, 320208": "315799 318907",

    # "How do I unassign or remove a menu I assigned by mistake?"
    # 294120: training menus and production plans needed bulk removal for dates before a
    #         cutoff; Expert Care removed them (temporarily widened the past-date editing
    #         window to delete, then restored it).
    "Tickets 293130, 294583, 298386": "294120",

    # "I clicked delete and got a success message, but the menu is still there..."
    # 303800: to remove a menu line's menu from one site, the line had to be added back
    #         under Site Configuration so it appeared, then deleted for that one site.
    # 314336: the menu line was inactive so it did not show under Assign Menus to delete;
    #         reactivating the line made it appear so the menu could be removed.
    "Tickets 298386, 310499": "303800 314336",

    # "I cannot override or replace a menu on a past or current date. How do I fix that?"
    # 313018: a withdrawn production record removed the delete (trash) icon, blocking
    #         removal; undoing the withdrawal at those sites restored the ability to delete.
    # 313523: the "one or more days already have menus assigned. Assigning other menus will
    #         override them" message is only a warning, not a block; the override proceeds.
    # 317049: reassigning en masse for a month is done by clicking the day header in the
    #         month view to reach the reassign/override screen.
    "Tickets 305114, 310831, 307019": "313018 313523 317049",

    # "I changed or copied a menu after assigning it, but the change is not in production..."
    # 297006: swapping a single item on an already-assigned date (renaming a copy did not
    #         flow to the assigned cycle); fix is on that date's production plan -- zero out
    #         the old item and add the new one.
    "Tickets 300609, 305108, 293964": "297006",

    # "I created a new menu line but it does not show up on the Assign Menus page. Why?"
    # 317631: sites/menus were not available to assign because menu configuration had not
    #         been completed; once configured they become assignable.
    "Tickets 300340, 319187, 310499": "317631",

    # "How do I give one site a different menu without changing the others?"
    # 292004: an alternative high school on the high-school meal pattern needed its own menu;
    #         resolution was to switch the menu line when assigning so its menu applies.
    "Tickets 308569, 311852": "292004",

    # "A menu is showing up at a site (or campus) where it does not belong. What causes this?"
    # 298114: a group-level assignment did not reach every site in the group; the workaround
    #         was to reassign those specific sites individually under Organization Level.
    "Tickets 292177, 301451, 304395": "298114",

    # "Can I assign to just one school in a group, or exclude a few sites?"
    # 314576: assign to a single school by choosing that one site from the Organization
    #         Level dropdown.
    "Tickets 318268, 301863": "314576",

    # "Holidays are not being skipped, or dates I should be able to use are blocked..."
    # 305356: menus were blank/missing on certain days because a holiday (Thanksgiving) was
    #         in place for those dates; Expert Care adjusted the holiday meals to restore them.
    "Tickets 304375, 320213, 320208": "305356",
}

# New Q&As to add (section_title must match an existing section in assign_menus_spec.py):
NEW = [
    ("Holidays, dates, and other limitations",
     "When I set a holiday with Remove Menu Assignments and reopen it, no sites are checked. Did my change save?",
     ["Yes, your change saved. When you enter a holiday and use Remove Menu Assignments, you check the sites, save, and get the green success message; but if you reopen that holiday to edit it, the Remove Menu Assignments site list shows up empty (no sites checked). Support verified this across multiple PrimeroEdge versions and confirmed it is the intended design rather than a sign that your selection was lost.",
      "In other words, the empty checkboxes on re-open do not mean the holiday or the removal failed. If you need to confirm what a holiday actually did to a day's assignments, check the affected dates on the Menu Calendar at Menu Planning -> Menus -> Assign Menus."],
     "Tickets 290474"),

    ("CACFP, Supper, Summer, and SFSP menus",
     "If I assign At Risk / After School Supper menus, will they overwrite my Regular breakfast and lunch menus?",
     ["No. Assigning At Risk (After School) Supper menus does not overwrite your Regular breakfast and lunch menus. Supper is its own meal type on its own menu line, so its assignments sit alongside the regular meals rather than replacing them. In SchoolCafe, parents see Breakfast, Lunch, Supper, and Snack as separate views, which is why the supper assignment does not disturb the regular menus.",
      "If you were told otherwise, it was a misunderstanding. You may still need to copy the supper menus into the correct site group before assigning, but doing so will not remove your regular menus."],
     "Tickets 290889"),

    ("Menu lines, site groups, and configuration",
     "My a la carte items are missing from production even though the menu is assigned. Why?",
     ["This happens when the menu that was assigned did not have a la carte selected. Production is built from exactly what was on the menu at the time it was assigned, so if a la carte was not checked on that menu, those items will not appear on the production plan.",
      "To fix it, check the a la carte option on the menu, then reassign that menu to the dates you need so the updated version (with a la carte) flows into production."],
     "Tickets 303084"),

    ("Menu lines, site groups, and configuration",
     "A menu line appears in the Assign Menus list for sites that should not have it. Will assigning under that line affect the wrong sites?",
     ["No. A menu line can appear as a selectable option on the Assign Menus page even at the broader selection level, but assigning a menu under that line only places it on the sites that are actually configured for that line. Support tested this by assigning under a line and confirmed the menu landed only on the sites set up for it, not on sites without the line attached.",
      "So it is safe to assign your menus under the intended line (for example, separate summer breakfast and lunch lines); the assignment follows the line's site configuration. If you still see a menu on a site that genuinely should not have it, check that site's menu line setup under Site Configuration."],
     "Tickets 316758"),

    ("Menus not appearing in SchoolCafe",
     "I assigned and published the menu to the right site, but it is missing for certain grades in SchoolCafe. What is wrong?",
     ["A menu only displays for the grades the menu itself is built to cover, even when it is correctly assigned to the right site. For example, a menu set up for grades K-8 will show when you view SchoolCafe for a K-8 grade but will be blank for grades 9-12, because the menu does not include those grades. Setting the SchoolCafe grade selector to a grade the menu covers makes it appear.",
      "This often shows up after copying a menu, where the copy did not carry the full grade range you needed. The fix is to make sure the menu includes the grades you serve at that site. Separately, if a day is simply blank in SchoolCafe but everything is assigned correctly, re-publishing the menus for those dates frequently brings them back."],
     "Tickets 315171"),
]

# Remaining tickets with no usable content (just the IDs, space-separated):
#   292559 - subject line only ("Assign Menus"); no description or resolution.
#   296617 - daily-varying fruits/cereals for carb counting; no assign-menus path, advised
#            printing nutritionals. Out of scope for assigning menus.
#   296678 - could not switch cycle items for a date; routed to a Menu Planning specialist,
#            no documented diagnosis or resolution.
#   304343 - one-line request ("Fix menu so that it can be assigned"); no content.
#   307298 - breakfast analysis non-compliant after a line change; routed to the PA state
#            contact (CN Resource). Out of scope / routed elsewhere.
#   307341 - could not advance past December; self-resolved next day, attributed to a
#            transient server issue.
#   312880 - Nutrislice third-party API integration items not syncing; integration / out of
#            scope for Assign Menus.
#   313547 - publish-menus backend error for one district; Expert Care backend investigation,
#            no new user-facing guidance beyond the standard publish steps already covered.
#   315415 - alt-text on recipe images for SchoolCafe (ADA accessibility); not assign-menus
#            guidance.
#   315592 - sugar-content warning color shade (UI/accessibility enhancement request); out
#            of scope.
#   316770 - general platform/module questions and an Inventory sales referral; not
#            assign-menus guidance.
#   319957 - menu not available for a grade level; inconclusive chat, customer routed to
#            phone, no documented resolution.
#   320468 - "need help assigning the correct menu"; self-resolved immediately, no diagnosis.
REVIEWED = "292559 296617 296678 304343 307298 307341 312880 313547 315415 315592 316770 319957 320468"
