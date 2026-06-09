Inventory  Distribution  (SC) Open
Showcase
FEB  05, 2026, 9:55 AM
ID: 573-873-494
TRANSCRIPT
Justin  Miller
0:01
All right. Thank you. So distribution is simply the movement of inventory product from one site to multiple other sites. I have defined it very vaguely like that on purpose. We 
will kind of expand on that in a moment. So the way we have built this in School Cafe is that any site with an inventory license can be assigned with the inventory distribution
site type. A common theme you'll notice, and I'll touch on this more on the next slide, is that we're not really using the word warehouse too much. So I'll kind of expand on 
that more in a moment. But distribution, inventory distribution, that's the terminology that we're using. So any site can be assigned with that site type, which then makes 
them eligible to be linked to an internal vendor. That site then through the structure of the internal vendor becomes available to the other sites to place orders.
Justin  Miller
0:59
So really simple. They will simply place orders to this internal site the same way they would an external vendor. Now, where the inventory part kind of really comes in is that 
distribution site, their perpetual inventory is the basis for how orders are being fulfilled. So their perpetual inventory will be linked to that vendor. And as part of the 
distribution process, they will effectively be pulling items from their own inventory and then basically  doing a very big transfer. We'll touch on the transfer thing a little bit more
as well in a few slides. The contracts, the vendor contracts, the configuration that we have associated  with the internal vendor contracts dictates basically  everything. It 
dictates how the items are grouped, how the sites are grouped, how the schedule is executed, how all of these things come together.
Justin  Miller
2:04
I wanted to... I'm going to kind of dedicate a slide to this because it's not super important in the context of the showcase , but it is important in how we position and market 
and convey this feature. So this is, of course, one to one with what Primeroge  and with what our competitors consider central warehouse. The only reason we've kind of 
geared away from that terminology is for two things. One, this really isn't central anymore. And that's a strength, not a weakness  of this. That's a feature of this that we can 
broadcast and we can emphasize . The way that we have kind of positioned distribution is theoretically, at least, any site can become a distribution site. We've seen a lot in 
the industry recently that a lot of schools are using kind of a satellite distribution system.
Justin  Miller
3:00
So a high school maybe we see this more often in our production prep site and that that use case is fairly straightforward. But what we've also seen is satellite distribution, 
not just satellite prepping, but satellite. I like, hey, I still need a route or I still need some form of like shipping or trucking, that sort of thing. So we have some of that stuff on 
prep site, but we want distribution to eventually be the place that you use for any distribution, for the flow of product from one site to other sites. Okay. But here on the last 
point, we can call it whatever we want. We definitely want to make sure that everybody knows that we're saying central warehouse when we say distribution. Warehouse  
distribution, central warehouse distribution, it can be anything.
Justin  Miller
3:54
The point here is the way we've positioned distribution expands the number of available applications. So I think in the past we might have heard, oh, you have a few satellite 
sites and we immediately think, okay, that's a prep site. This approach allows us to potentially similarly  match distribution to those customers  as well. So, you know, maybe 
in an ideal world, we have a district that has three distribution licenses because all three of those sites do, you know, product delivery.
Justin  Miller
4:30
I will switch over to School Cafe in a moment, kind of going through these first couple of slides, and then we'll hop back over. So a bit of a refresher on how distribution 
works through the form of the contract. There are three major components that come together to determine how distribution works. Your shipping groups are associated  with
items. Your shipping groups determine how items are grouped together, primarily for the purpose of shipping, as the name implies. Delivery groups are similar concepts, but 
they are associated  to sites. They can be used to cluster sites for the purpose of schedule management , but they can also be used to organize and sequence Your sites for 
into routes into deliverable routes. So I go to this school first and this other school second and so on.
Justin  Miller
5:24
The shipping schedule combines those two groups into the tool that you use to say, here's when I deliver these products and here's who I deliver them to on these days. So 
let me.
Justin  Miller
5:51
All right, pretty busy screen, but we'll try to break these things down. So here I have an internal vendor. This is my warehouse. I have several contracts here. The one we 
want to focus on for now, don't worry about any of this stuff, is this first one. So my main contract here, which is active until 2027, and I have these three columns that we 
just touched on in the slideshow. So shipping groups, delivery groups, and shipping schedules. The way we configure this is when you create a new contract, by default, you
will have a group called default. For delivery groups, you will also have a group called default, and then you will have a group called unassigned  if you want to tuck some 
sites away for not ordering. Every  contract, in theory, is functional out of the box.
Justin  Miller
6:41
If a school district or a distribution site does not need more complex group configuration, you can simply roll with the default. If all your items go on the same truck and you 
don't split them apart by day or by truck or by route or anything, then you can just use the default shipping group and that'll be great. Similarly , for delivery groups, if you just 
deliver to all your sites on the same day or You just break them up by day. You don't break them up into like routes, you know, an A and a B. Then again, you can just kind of 
use the default. But what I've done for my main contract here is I've configured two additional shipping groups, a cold frozen and a dry non-food. And as you can see here, I 
deliver those on somewhat different days, sometimes  on the same day, sometimes  not.
Justin  Miller
7:31
The delivery groups, I have created two additional as well, north and south. I've pretty much evenly split the district into north and south delivery groups. And I've put a few 
sites here in the unassigned  because they don't order from me. And then on our shipping schedule here, these two things come together. This is where it can start to get a 
little confusing, but I am showing you all of this for a reason. We will touch on summer  routes here in a bit. And this is where this configuration will hopefully make a little bit 
more sense. So when we open up the schedule here, we're looking at kind of the overview. The best way to really look at this information is to pick a specific shipping group 
because the way this works is that you will configure a schedule for each shipping group.
Justin  Miller
8:16
So if I've said I've split all my items up into a cold group and a dry group, And now I'm configuring the distinct schedules for those two things. So as I mentioned here, we 
require a distinct schedule for each configured shipping group. So I have a cold frozen. I deliver Monday and Wednesday  to the north group. And then I do Tuesday, 
Thursday  for the south group. And then if we switch over to our dry non-food, you'll see it's kind of a similar structure. This can be configured a number of very different 
ways. You can make this as complex as needed, or you can kind of keep it simple. I suspect most of our customers  would prefer to keep it pretty simple.
Justin  Miller
9:13
All right, moving into the new things. So hopefully that refresher was sufficient. If not, we'll touch on this more during the demo. The things that we're here to talk about that 
are new, that are new to distribution and kind of add the expanded part of it. We have now added five distribution settings, or I think as we call them, the distribution 
preferences. These five major settings should provide parity with most of the complexity we see in the industry. Regarding  different operational processes , right? So I have 
kind of an explanation here and then I'll throw you in the site in a moment, but they're a little bit simpler than they sound. Display available quantity to sites. So there's always
a little variation in how much distribution sites want their other sites to see what they have on hand.
Justin  Miller
10 :11
That's what this setting is for. Do you want them to even see what you have on hand? And if so, which particular value do you want them to see? Do you want them to see 
what you have on hand right now as of this very moment? Or do you want it to consider the orders that that warehouse is going to be receiving in the next week? So these 
are projected and actual. Again, I'll expand on this more in a moment. Allow orders to exceed available quantity. It kind of piggybacks off that first setting and says, OK, 
based on what you've said that they can see, can they exceed that? Can they order more than that? Sorts of substitutions determines whether I can just add items, whether 
I as a distribution site personnel can add any item to a distribution or if I have to use the contract.
Justin  Miller
11 :00
And allow non-substitution added items is kind of a similar setting where we've added the ability for you to just freely add items to a distribution if you wish. So maybe you're 
sending out a Monday delivery and you have some free product you want to give out. This setting determines whether the distribution site personnel can just kind of add 
items that weren't ordered. If this is not enabled, the only items that the distribution site can add are the ones that were ordered or substitutions for those. And this one's a bit
confusing. I won't spend too much time on this, but this basically  determines when a particular date becomes locked down for ordering. So if I'm in the middle of assignment  
on Monday, I don't want people to... Place  more orders for Monday.
Justin  Miller
11 :50
Or maybe I do. So that's what that setting is for. All of this also has thorough explanations  built right into the website. So if I go back to our contract here. Again, this is a very 
busy screen. We're doing a lot of stuff in the contracts. So we're really using icons here. Your feedback is always welcome. We can obviously tweak the icons we use and 
whatnot. But this new gear icon here is for accessing  my distribution preferences. So as you can see here, going through those settings I just discussed , for this particular 
contract, I am allowing my sites to see my projected quantity on hand. That is... That is including any on-hand orders. So if I place an order to get 100 more cases next 
week, that 100 cases will be visible if my sites come to place an order for me next week.
Justin  Miller
12 :43
If I don't want to do that, I can do actual. And then, of course, I can just say I don't want them to see it at all. Any of these info icons will give you a probably overly thorough 
explanation of the How the setting works, what it does. I do suspect that the way we've set these up to load by default should be accommodating  to most people. So that I 
don't suspect this is not necessarily  a mandatory configuration everybody has to review.
Justin  Miller
13 :22
So I'll touch more on the settings, but there's not a whole lot to demo here other than This works behind the scenes. The actual way that distributions are loaded on the 
calendar, the way that orders are placed, none of that is heavily affected by this. It's just how things work in the back end. When does a delivery day not become available or
which items can I add to a distribution? All of these settings tied to functionalities we've already developed and we've already presented. So there's not necessarily  new 
things to show here, but hopefully this is all kind of making sense. And if not, I will kind of circle back to this as I'm doing the more thorough demo here in a bit. So settings is 
the distribution preferences is one of the three major new things that we've added.
Justin  Miller
14 :13
The second, perhaps more exciting, would be what we what we're calling seasonal  contracts. So again, as I've Kind of mentioned here, everything's being anchored to the 
contract. This is where we define the parameters  that affect distribution. Everything's  being assigned to the contract. So the goal here with seasonal  contracts was how do 
we accommodate  Off-season operational changes without disrupting the main distribution process. So summer  routes are maybe a better way of kind of connecting this. 
How do we accommodate  summer  routes? Oftentimes, operations may simplify during the summer  or certain operations. You know, you may deliver on fewer days. You say,
hey, in the summer, I'm just doing Monday and Wednesday. We're not doing four or five days a week.
Justin  Miller
15 :12
In the summer, you may reduce, you may have fewer personnel. So maybe you're sending all the items on one truck instead of, you know, two or three trucks. So all of that 
particular configuration is derived, again, from the contract. So seasonal  contracts are a way for us to basically  create an extension of the main contract. So here we have 
this seasonal  contract checkbox. Again, another explanation of what that is and what that does. I'll create one here in a moment. But as you can see here, I have two 
seasonal  contracts for this vendor already configured. I have my summer  26 and my summer  27. Notably, my shipping group, delivery group, and my shipping schedule are
different for this summer  configuration. So as I mentioned, in the summer, I don't need to split my items by cold and dry.
Justin  Miller
16 :04
In the summer, we're kind of lightweight and small enough that we just put all the items on.
Justin  Miller
16 :16
Sorry, if anybody has any questions, feel free to send them in. Okay. And then similarly  in the summer, I have kind of configured different delivery groups here. So maybe 
weekly, we're just going to do weekly deliveries for a lot of these sites. In the summer, I've put all my elementary sites as unorderable. This is not necessarily  to imitate what 
really happens in the real world, but obviously not every school generally participates in summer  school. So This is how all of these pieces will be managed. There are other,
you know, there's ordering conditions and there's other things like that. I just want to say we're doing our best to put all of this configuration into the vendor config itself. So 
you don't have to go, you know, say, oh, let me remove the ordering conditions for these sites.
Justin  Miller
17 :01
You can just tuck them in this little group. And as long as this date range is applicable, these sites will not be able to order. So from June 1st  to July 24th, this contract will 
basically  take over and override, kind of supersede the main contract. So if I'm placing orders as a site for May 30th, I'm going to be part of the main contract here. If I'm
placing an order for July 1st , I'm going to be part of the seasonal  contract, the summer  contract. Again, this is working mostly behind the scenes, right? The way that I place 
an order doesn't change. The appearance  of the calendar doesn't change. The main purpose here is to, strange.
Justin  Miller
18 :05
Here we go. The main purpose here is simply to make sure that the data is loading correctly according to the date range assigned. So all of these are part of my regular 
contract, but if my seasonal  contract starts on the 16th , any orders placed for that will adhere to the seasonal  contract.
Justin  Miller
18 :31
So the seasonal  contract can be created for any date range as long as it falls within the date range of the main contract. That means it doesn't have to be a summer. It could 
be a winter. It could be one week. It could be You know, staff week, it can be a number of things. If they need or can benefit from a customized contract configuration during 
that date range, they can set it up like a seasonal  contract. As I just demonstrated, the contract configuration and the distribution preferences are completely distinct for 
seasonal  contracts. So that means... Not just the shipping groups, delivery groups. It also means my settings. Excuse  me, I clicked the wrong contract. So maybe during the 
summer, I don't want them to exceed available quantity.
Justin  Miller
19 :20
I don't have the capacity to deal with negatives and overages and that sort of thing. In the summer, we want to simplify our options. We're not going to allow non-
substitutions. We're not going to allow anybody to exceed or available quantity. And we want everybody to see the actual quantity. But during the school year, I'm okay if 
people use my projected. During the school year, I'm okay if people exceed available quantity. So this is the intention of seasonal  contracts is to accommodate  summer  
routes without disrupting the overall operation.
Terri Brown
19 :54
So, Justin, question. Like in Primero  Edge, we always have at the end of the year, they want to set their orders for the beginning of the year before they leave for summer. 
This will prevent having to change routes because they'll be able to set their back-to-school orders before they leave without having to change anything. Is that correct?
Justin  Miller
20:18
That's exactly correct. Yeah. And yeah, to kind of tie it to the primary, because admittedly, this was built And very much in mind with the experiences we had trying to 
accommodate  that in Pramod  Edge. So we added some date range to the routes a couple of years ago, but we didn't add year. And so then they had to go and they had to 
add year. So this is intended to just kind of be a little bit more future-proof way of handling that. Yeah, that's a good question. I want to importantly note that While all the 
contract configuration is distinct, the item list is not. The item list is simply inherited from the main contract. This means we're not asking you to, you do not have to reset up 
your items for the summer. The assumption  here is that you're not radically changing the items that you deliver during the summer, right?
Justin  Miller
21 :15
So when I switch my contract drop down here to the summer  contract, You'll see here it says inherited from contract as you know, this is the main contract. So my item list, 
the actual list of items is the same. However, all of these attributes can be customized. Again, I don't suspect that this is something that customers  will need to do a lot, but 
theoretically, You could have a different price during summer. You could certainly do something like in summer, I have a, you know, I have a lead time on these items. It 
takes me a little longer to get them ready in the summer. Or in the summer, I have limited quantities. So I need to, you know, I need to cap everybody at 10  cases per order. 
So the item list itself, the items that are here in this contract do not change across seasonal  contracts.
Justin  Miller
22:10
You're simply allowed to customize the attribute. So as you can see here in my summer  contract, everything is in the default group. When I switch back to the main contract,
items are in those respective cold, frozen or dry non-food groups.
Justin  Miller
22:33
Yeah, so that's kind of the example I gave here. List of items exactly the same. This may not seem super significant, but I think this is a really important point. We're using 
our framework here in inventory to make things as flexible as possible. We're using the contracts to accomplish  that, but I just want to really clarify that the items themselves  
are kind of anchored to the vendor. Again, this is one of those things that's very, very capable, but I do suspect And most users aren't going to need this level of complexity, 
but it's good that we have it for those really complicated, you know, central production, central where all that stuff in the in the future, those really bigger, larger districts. 
They'll they'll benefit from these sorts of things.
Justin  Miller
23:26
The more exciting thing here. Hotchot distribution. So I know I spent a good deal of time on this in the release review. This is the third major change that we have made to 
distribution recently. This is kind of the big one. So hotshot distributions. There's two ways of looking at these. The simpler way is this version here. Did you forget to make a 
substitution when you sent out a truck this morning and now you have a site saying, hey, I need my milk or I need my cereal or whatever it may be? Or do you for some 
reason need to deliver on a Saturday  when you don't normally receive orders on a Saturday ? Yeah. This is what Hotshot Distributions is for. They're simply manual  
distributions that you create from scratch instead of from received orders.
Justin  Miller
24:21
The main distribution tool works only through orders, meaning you can't really create a distribution unless your sites have asked you for a product. And then of course you 
can make changes from that point, but you still rely on the sites to place that initial order. So hotshots kind of allows us to just circumvent that process entirely. When we 
create a hotshot, the sites, items and quantities all have to be manually  assigned. It could be tedious work, of course, however, we do have customers  kind of currently 
doing things like this. Maybe not too difficult. After that manual  assignment , however, after manually  selecting the sites and manually  adding the items, the remainder of the 
distribution tool works exactly the same that our regular distributions work.
Justin  Miller
25:10
So picking all my pick tickets, my shipping, my trucks, all of that stuff works exactly the same that a normal distribution would work. And then notably, To kind of make
everything fit correctly in our school cafe inventory module architecture, we will still create an order on behalf of that site, on behalf of those sites, if the distribution site sends
them a hotshot. So if I decide on Monday, hey, I'm just going to send my high school some product. I got some free samples  or something. I'm going to send them to my high
schools. They obviously didn't create an order, but when I ship that product to them, an order will be created in the system on their behalf so that they can receive that 
hotshot distribution. So this is where I think it would be helpful if I start throwing something.
Justin  Miller
26:09
So here we have my distribution. I apologize, I'm going to have to hop from QA to UAT a little bit. So if the data looks a little different, I apologize. So I have three regular
distributions for next week in various statuses  and number of orders. These are regular distributions. These are derived from orders. If I look at these, you'll see the order,
the order number, the value, so on, and then you can go take a look at it if you want. But these are regular orders that the sites placed to me at the distribution site. If, 
however, I want to create a hotshot, I just click this button and I pick a date. I'm going to do Sunday. So we'll load up here into the distribution. Now, the screen I was just on, 
normally, this is where you would see the orders.
Justin  Miller
27:01
Again, we don't have orders, so we just have to manually  select these sites. Say  I'm going to do a little special, let's fall in line with the example I used. So let's just grab our 
high schools here. We just have four of them. I'm going to assign these four sites. After I've added a site, I can get started on this distribution. I can add more, I can do 
whatever I want. But once I have at least a site here, I can get started. So this also kind of doubles as a demo of the regular distribution in a way. So this kind of refresher on 
how a lot of the assignment  and whatnot works as well, the picking and everything. So I also have to manually  add items here, right? So I'm going to just kind of quickly go 
through here and add a few items. Let's say I'm just taking them some juice.
Justin  Miller
27:55
They ran out of juice. Everybody  needs some apple juice, orange juice, so on. I'll just give them multiple kinds of orange juice. You can add as many items as you want, and 
then you click this Add For Items button. They'll be here. Again, this is where the tool should start to look the way it normally looks. You'll see your quantity on hand here. If 
you want to, you can use these tools to see. Quantity on hand expressed in other units, how the pack sizes work. I won't get into that stuff too much. Here's our, how do I 
say that? This is like the quantity on hand timeline almost. This is a more expanded way of seeing, hey, what do I have coming in? What do I have going out? As you can 
see here, I have 184 , but I've already committed 13  to a different distribution.
Justin  Miller
28:49
If I had an order on hand, if I had an order on the way from my vendor, from the main vendor, from Cisco or whoever, that quantity in transit might say, you know, 20 cases
on the way, something like that, right? So these are the kind of more advanced things that we didn't really have a chance to kind of Show off until now we have a distribution 
site, right? Your average elementary school probably doesn't have that much product going in and out that they need this kind of view, but your distribution site might
certainly have that. And not to make things too complicated, as you can see here, it says projected. That relates to that setting that we were talking about earlier with the, do 
I want to use projected or actual? Is that protected quantity in hand, right?
Justin  Miller
29:43
So kind of trying to tie some of that together. So this is a hotshot, so I have to manually  add these quantities. I'm just going to give all my high schools three. On a regular 
distribution, you have a nice little button that just says assign all, and it will just simply populate all the quantities with what the sites ordered. But again, We didn't get orders 
for these, so I'm having to kind of manually  specify. In any case, with our edit all functionality here, I don't think it's too cumbersome  or difficult to use. So once we have a few
items on the distribution, again, I can add more items here. I can do whatever. But Once all my items have at least some assigned quantity, meaning there are no zero items 
on the distribution, I can complete my assignment .
Justin  Miller
30:39
At this point, this is the regular distribution. For my picking, my quantities report, all of this, at this point, the flow is exactly the same as a regular distribution. But I'm going to 
push forward to shipping so I can tie things together with... The contract configuration we were talking about. So here, this is not the summer  contract. I know I'm kind of 
hopping around these three things we talked about, but this is my regular contract. So my deliveries are split up according to those groups. I have cold north, cold south, dry 
north, dry south. I probably don't need four trucks today. Especially  considering that a lot of them are, there's only four sites total, right? So we have this modify shipments  
button. I don't know if I was really able to brag about this enough before, so I'm going to spend a little time on it.
Justin  Miller
31 :38
But there's a number of ways I might want to modify this, right? I might want to say, hey, we're just going to take all the cold stuff on one truck. And then a little bit later in the 
day, we'll take all the dry stuff or vice versa, whatever it may be. Or I might say, hey, you're already going to King High. Just take them both their cold and their dry stuff. The 
Modify Shipments  tool comes in here to manage this. Now, again, hopefully you set your configuration up in a way that these shipments  load in a format that you find 
enjoyable. Hopefully you're not every day having to modify your shipments . But since this is a hotshot, it's loading according to the normal contract configuration. But this is 
a special Sunday  delivery. So I don't really need all of this complexity that I normally need from Monday through Friday.
Justin  Miller
32:29
So I'm going to combine my shipments . I'm going to say we're just going to combine both north into a single. So now we have cold, dry, north. And now I'm delivering these 
two schools all of their items. I'm going to do the same thing here with South.
Justin  Miller
32:56
Now I just have two shipments . We're taking everything to King High and Independence High on one truck and then everything to these other two schools on the other truck.
You know what? Hey, that's still too much. I'm going to combine them again. Now we just have one truck. I can... Modify these details here. I can change the name. I can just
say, you know, Sunday  High School.
Justin  Miller
33:26
These
Terri Brown
33:26
That is very cool.
Justin  Miller
33:29
driver names load according to some of these smaller things I didn't think to show, but again, I'm jumping across environments . But if you configure contact persons here, 
We will pull those names in as options. You, of course, can simply just say, hey, today Terry's taken me. And then we can adjust the time. This will simply affect the receipt. 
So when I'm bringing some juice for Sunday, Sunday, Go ahead and close this. Now we're back in view mode. Again, this is a regular distribution tool. So this is the same
way it will work for regular distributions. You can, by the way, in the modify shipments , you can break them back apart. You can also move orders from one shipment to 
another if you want to just slide like one school from a truck to another, that kind of thing.
Justin  Miller
34:33
And then if you made a mistake or something, you can just reset this back to the way that it was and it'll load back in that four orders or that four shipments . We might want 
to revisit that. Now, shipping, remember, I'm showing a hotshot here. Nobody ordered. If this was a normal distribution, we would already have orders. And when I say, hey, 
I'm shipping these, Those orders would then become available to receive. But remember, this is a hotshot. Nobody actually placed any orders. So I'm going to, before I click 
shipping here, I'm just going to open up our list of orders. And we'll see that, well, we did place some orders, but not for Sunday, right? So everything here is a standard 
order. These are all regular orders. As you can see, I was rapidly making these right before the meeting.
Justin  Miller
35:28
So I'm going to click this ship selected here. We're going to mark this truck as shipped. So now we got our speeding truck. It's marked as shipped. And as you can see here, 
orders have been generated. So these are new orders. If I pop over here to the list, you can see we end right around 197 . I think there's a 198  I canceled or something. And 
so these are now generating with 200, 201 . Oh, there we go. There's 198 . So if I click apply here again, there's four new orders in the list. But they are assigned an entry 
method of hotshot. So to differentiate them from a regular order, which is a standard order, this may also say production if they created a production order. But to 
differentiate these, these are marked with a hotshot. And the reason for that, we're just creating the order so that they can create the receipt.
Justin  Miller
36:25
And obviously, like we can do a little bit more here. You know, we can put some labels that say, hey, this is a hotshot order, you know, just so the user knows, hey, I didn't, 
hey, where did this order come from? Well, it's a hotshot, you know. But the purpose of this is simply so they can get over here and receive that hotshot distribution, receive 
that hotshot shipment. Until sites create a receipt, so you see here we got pending receipt, I can technically revert it. So if I have to call Terry and say, hey, turn around, turn 
around, we forgot something, come back real quick, I can click this, revert it, and then this order will go away. It'll vanish. So the sites creating their receipts is true. Triggered
by the distribution site marking the shipment as shipped.
Justin  Miller
37:14
I'm going to go ahead and create this real quick so we can show you the way that that appears over here. Partly  received. Now I can no longer revert it. Of course, I can still 
call Terry and ask her to come back, but I can't. Revert  it in the system because Johnson High already created their receipt. I don't have time to go create all these receipts,
but if we did create all four of these receipts, this truck would officially say fully received. So that is hotshots and tied in a bit with our configuration and our distribution 
settings. What I'm going to do here, and I will pause for questions before I do this, but what I'm going to do here is I'm going to create a seasonal  contract since we appear to
have the time, and then we'll place some orders for that seasonal  contract time range.
Justin  Miller
38:25
First, I guess I forgot one more thing. I have one more slide about hotshots I would like to talk about. Because  I think I touched on it a little bit. So this is Hotshots in the 
context of kind of their typical use case, right? Their kind of special manual  distribution. However, there is another way to kind of look at this. And that is using Hotshots as 
your primary distribution process. This might be a little corner case, but we have witnessed many customers  in our industry often share responsibilities for multiple sites. Or 
sometimes  we have customers  who are not large enough as a district to necessarily  justify having every single site manager go place their own orders, create their own 
receipts. A lot of times we encounter people that say, Oh, you know, I place all the orders for the elementary schools and then the high school and middle submit their own or
or, hey, I just do everything for the whole district.
Justin  Miller
39:25
I only have seven sites. I know exactly what they need. I know when they need it. I don't really need them to place orders. Well, this is where Hot Shots could come in as a 
more meaningful, a bigger tool. So all the stuff we've shown today with the distribution settings, the seasonal  contracts, and the way we use the configuration, my hope is 
that all of that is flexible enough to accommodate  customers  that may have what I'm calling less than perfect distribution operation, less than perfect process. So hopefully, if
you do have a few sites that are just really bad at managing, at placing orders, Hopefully our substitution tools and our item addition tools might be good enough to make 
that up without you having to give up on regular distributions.
Justin  Miller
40:12
But if for some reason or another, it's just too much of an ask for everybody to place orders, the distribution site could use I just don't need anybody to place orders. So this 
is where hotshots could be used in kind of a more recurring form, right? So we have, this one is a little important to me because especially since COVID , we've had more 
and more people doing these kind of hybrid practices where, you know, hey, I just, they don't, I can't get them to log in. You know, they're not going to log in and do all this, 
but I already know what they need. They send me an email every weekend. Can I just use that to plug it in and send a distribution? Using hotshots, you can now. And that's
the end of my slideshow. I will start showing a little bit more of the demo, but I wanted to pause.
Justin  Miller
41 :29
I see there's some conversation in the chat. Are there any questions or any comments or anything before I proceed to show some of the seasonal  contracts?
Kelsey  Brown
41 :45
Yeah, Justin, I was wondering, so when you are like in the middle of a distribution, you have one that's in progress, if you change the distribution settings, do those carry 
over to the in progress one? Like for instance, you gave the example of you have the settings set to the projected quantity. So then when you showed it, it was showing, you 
know, the projected quantity in that breakdown. So if you were to change it to actual, would it Reflect in real time in your in progress distribution that you have.
Justin  Miller
42:15
That is an excellent question. For the most part, no. The distribution at the time you create it, it will look at what the configuration is and it will anchor itself to that. That was 
kind of intentional. Some of the settings will. So, for example, I might have mixed some things up. The QOH setting. We do obviously use the projected and stuff in the 
distribution. That setting is mostly for how sites will see that quantity when they're placing an order. Let me do that real quick.
Justin  Miller
42:57
So when I'm ordering from the internal vendor, I get this extra little piece of information, which is, oh, they don't deliver on that day.
Justin  Miller
43:31
There we go. So when I'm ordering from an internal vendor, I see this available quantity. This quantity is referencing that. Obviously, we don't have that big fly out with all the 
extra details here. It's just a simple number. So this is referencing that setting. If you were to change that setting, this would immediately update. So if I'm a site and I'm
placing an order and it's showing me the actual, Somebody changes that setting. If I come here and I just click apply again and I refresh the screen, it's possible that this
might switch and say, you know, 42 available. But as far as the distributions, the actual distributions on the calendar, no, these are anchored to the way the configuration was
at the time that you started it. It's a very, very good question, though, because depending on Yeah, like depending on how your seasonal  contract works and whatnot, it 
might pick one configuration over another.
Justin  Miller
44:32
Can you change this? Oh, that was the question. Okay, got it. All right, so here's what we're going to do real quick. We're going to make a weird February  seasonal  contract. 
We're going to make a Valentine's seasonal  contract. So here's my main contract. It goes forever to the end of time. So that's pretty easy. I'm going to create 26 Valentine. 
Mark this as a seasonal  contract. Notice the end date option. The no end date goes away when I do that. Can't have a seasonal  contract. It lasts forever. A little explanation
here. You know me, I'm kind of a wordy person. So wherever possible, we have these tool tips that will kind of explain things. Again, your feedback is welcome. If you have 
better ways of kind of communicating  this or any ideas or anything, please feel free to send them our way.
Justin  Miller
45:36
I'm going to put this for just next week. And this might actually directly address Kelsey's  question. These settings I talked about earlier, when you create a contract, we go 
ahead and put everything on one big page. But after the contract is created, we split these up into those two different screens, kind of noting that.
Justin  Miller
46:10
All right. So we have our Valentine's contract from the 9th to the 13th  next week. For that, we're just going to use the default groups. We're not going to do cold and dry or 
north and south. We're just going to use the default groups. And I'll put a few of these in the unassigned  group.
Justin  Miller
46:41
So our main contract, cold, dry, default, north, so on. Kind of going back to that calendar.
Justin  Miller
46:53
Again, cold and dry here, right? So now if I create a hotshot or if I receive a regular distribution, it's a lot easier for me to quickly create a hotshot than it is for me to go place 
15  orders from the schools. But you can kind of imagine I got an order for the 12th , right? If I now create a hotshot for the 12th , I'll assign a few sites. I'm going to do this 
very lightweight so we can kind of get to the part we're trying to see, right? So we'll just add one item.
Justin  Miller
47:48
So since this one is now in the context of that seasonal  contract, when I go to shipping, it's just using the default. So default, default here. Now to kind of Go a step further.
Technically, these three distributions also fall within the seasonal  contract. However, I started these before the seasonal  contract was active. So to kind of directly answer 
what Kelsey  was asking, this distribution will still be bound to the regular contract because that's when I started it. At least I'm pretty sure.
Justin  Miller
48:47
Right. So there we go. There's our cold and south. So if this just if these orders had came in after I had created that seasonal  contract, they would be using the default 
default. So, again, I know it's just like it's a little hard to clearly demonstrate, but. The everything's kind of working in the back end to make sure that. The orders are going to 
the right contract. The right shipping groups are being used. And then if I place an order for the 14th  or later, we're right back on the main contract. A few smaller things, 
when we actually, when the date actually happens to be within this date range, these little chips here will kind of update. They'll say, they'll say, The main contract is paused 
and it'll show the seasonal  contract is active.
Justin  Miller
49:45
And then, of course, when the date range ends, it just it just reverts back.
Terri Brown
50:08
Yes.
Justin  Miller
50:10
Let me see if. See if we can. Throw that.
Justin  Miller
50:35
You know what? Let's do it like this.
Justin  Miller
50:48
All right. I'm going to. So we have it. We have enough of everything. If I do auto assign right here, we have enough of everything. So that's why everything looks good. I'm 
going to go kind of arbitrarily take a bunch of our jalapenos away and see if I can show that.
Justin  Miller
51 :27
All right. So we just withdrew 60 cases of jalapeno. I'm going to refresh this.
Justin  Miller
51 :39
Oh, right. I only assigned three. OK.
Justin  Miller
51 :51
So if the assigned quantity is greater than the available quantity, it will be red. We'll have this kind of information in the footer. We have a kind of a quick toggle here. So, hey,
I just want to see the items that I have some issues  with. That's what this toggle is for. And this actually, you know, I can't complete assignment  until I resolve this issue. So
that's one check is that you can't proceed forward until that's taken care of. But then, of course, kind of getting in the weeds here a little bit. In between the time I complete 
assignment  and I start picking, I could have more Product like being withdrawn. Right. So my I could have had enough quantity on hand at the time of assignment , but
maybe when I started picking. Somebody withdrew another case that that same red font and that same information will will show up here.
Justin  Miller
52:53
It's a little difficult to kind of quickly show, but I guess I could go. Do that one more time.
Terri Brown
53:03
I love the toggle that lists them all, the ones that have problems for large distributions. That's pretty awesome.
Justin  Miller
53:13
Yeah, they should just have to basically  just deal with those and not have to mess with anything else. Okay,
Justin  Miller
53:40
I guess I got rid of all of them. I have to check on that later. Yeah, hard to throw some of these things, but obviously many people are transacting  in inventory at the same 
time, and a lot of people... You know, touching the same parts. So I believe what happens is at the time of assignment , we I don't want to misspeak  on behalf of Dev, but we 
can obviously provide this information a little later on. But we at some point, we do reserve the quantity to make sure that it doesn't get like double dipped. I believe we do 
that at the time that picking is started. So these three cases are now reserved for this distribution to
Raju  Cherukuri
54:24
So, yes.
Justin  Miller
54:25
Thank you, Roger. Perfect. Makes sense. Yeah, and I know I covered this in the last showcase , but just since we're kind of here, all of these, we have our pick tickets. We 
have quite a few options here with how you can kind of group things if you want to separate them by site order or group them in certain ways. We have the Quantities Report
that I'm very, very proud of. I know it's a bit confusing what's going on here. There's a lot going on in this slide out, but this is kind of a super report that can be used to 
compare quantities. Or just view different quantities. So we have sort of canned reports here like picking variants  that sort of automatically  picks the kind of the columns for 
you. You can summarize  them for the whole distribution or you can break them out into like site order details so you can see each page or each, excuse me, each order on 
its own page.
Justin  Miller
55:34
So assigned quantity, picked quantity, and the discrepancy  between the two of them. Obviously, I didn't. I don't have any. I just did everything perfect. But we can kind of go 
through here and compare if we want to say, hey, they ordered so much, but they only got this much. You can also make your own custom report if you want. So you can just
compare three quantities. You don't have to use the discrepancy. So there's a lot of flexibility here. We have several reports in PrimeraEdge  that several like different reports 
that hopefully are all basically  consolidated inside this super report.
Dawn  Smith
56:31
Is that rollback?
Justin  Miller
56:33
Let me actually think we can do this one. Yeah, so there's kind of subtle... Well, this one's not subtle at all, but after we revert shipping,
Dawn  Smith
56:44
Okay. We were hoping it wasn't like the nuclear option or something. Okay.
Justin  Miller
56:51
yeah, no, it just goes back to the previous step. It is worth noting we have this function, the rollback, tied to like a distinct permission . So I know kind of in Primero  is the 
same way where not everybody has that ability to rollback. So None of these, everything you see in red that like has a backwards arrow or something, they're all tied to a 
single permission . So if you want to prevent people from doing that, they can. We have it all the way from shipping all the way back to review. So for picking and shipping, 
it's a big red button. But when we're on assignment , it turns into like a smaller icon sometimes . So do you want to go right now? We're on picking if I want to go back to 
assignment . I'll click this. And then. I don't remember if we have a way to go back to.
Muhammad  Aly
57:45
I think it's because this is a hotshot. We only have the cancel hotshot.
Muhammad  Aly
57:50
Yes, exactly.
Justin  Miller
57:52
Yeah, that's thank you. Yeah, if this was a regular distribution. You can technically go all the way back to the very, very beginning.
Justin  Miller
58:01
So there's my rollback.
Dawn  Smith
58:02
It was in red, so we were concerned.
Justin  Miller
58:05
Yeah, yeah. Everything  with the rollback is given that like kind of dark red color. And all of those are tied to. Yeah, so we went all the way from shipping all the way back to 
unassigned .
Dawn  Smith
58:18
Nice.
Justin  Miller
58:25
All right. And that is kind of it for my showcase . I guess we got done with a little bit of time to spare. Great questions. And I see a lot of feedback in the chat, so I appreciate 
that. Is there anything else anybody would like me to show or talk about while we're here looking at distribution?
Justin  Miller
58:54
I'm coming back to, I see there was some discussion  about Some of the positioning, I know Gordon mentioned, you know, for marketing materials  and so on, we need to be 
careful to, you know, call things what people are familiar with and whatnot. So, yeah, I just want to, you know, again, I kind of relinquish control of that, you know, obviously, 
you know, But I just want to make sure we my intention here is simply to make sure we don't kind of narrow our own opportunities. If somebody says, you know, hey, I don't 
have a traditional warehouse, there might still be opportunity there. And Mohammed  and I have some big plans. This is more of a long term thing to better to better connect 
prep site and distribution. I think once we get to that point, this idea that we're talking about, this satellite distribution and these sorts of things, will make a lot more sense.
Justin  Miller
59:52
I think it'll really click. And I really look forward to us potentially having people using really cool hybrid satellite kitchen distribution, all of that stuff.
Justin  Miller
1 :00:10
All right. I don't think I'm trying to make sure I'm not missing anything while I still have everybody, but that's all I have for today. So if there are no more questions, I will let 
everybody go a little
Terri Brown
1 :00:24
Thanks , Justin.
Taylor  Rathmell
1 :00:27
Thanks , Justin.
Raju  Cherukuri
1 :00:28
Really  great tomorrow.
Dawn  Smith
1 :00:28
Thank you.
Daimien  Burks
1 :00:29
Thanks  for it, Justin.
Justin  Miller
1 :00:29
early. Thanks , everyone.
