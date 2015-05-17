#training set of strings
#it is a list of query, api_type

training_set_calendar = [

			("Let's meet up on Friday at 3 p.m.", "calendar"),
			("Lets meet tomorrow at 12", "calendar"),
			("Set up a meeting for tomorrow at 12", "calendar"),
			("Can we meet tomorrow at 5 pm", "calendar"),
			("Can you schedule us a meeting for tomorrow at 3", "calendar"),
			("Lets meet tomorrow at 8 am", "calendar"),
			("Benedict, set an appointment for tomorrow at 7", "calendar"),
			("schedule a meeting for January 28th at 5 pm", "calendar"),
			("schedule a meeting for June 4th at 8", "calendar"),
			("can we meet on september 22nd at 3 pm", "calendar")]



training_set_schedule_suggest = [

			("Let's meet later", "schedule_suggest"),
			("Schedule a meeting tomorrow.", "schedule_suggest"),
			("Schedule meeting", "schedule_suggest"),
			("Schedule an appointment", "schedule_suggest"),
			("Schedule an appointment today", "schedule_suggest"),
			("Schedule an appointment for tomorrow", "schedule_suggest"),
			("schedule next week at 9 a.m.", "schedule_suggest"),
			("schedule next week for 9 p.m.", "schedule_suggest"),
			("Can we have a meeting next week", "schedule_suggest"),
			("Benedict, schedule a meeting for next Tuesday", "schedule_suggest"),
			("Next Wednesday let's have a conference", "schedule_suggest"),
			("Can you schedule me a meeting for tomorrow", "schedule_suggest"),
			("Could you find a time that works for all of us", "schedule_suggest"),
			("Can we have a weekly meeting on Thursdays", "schedule_suggest"),
			("Benedict, find us a time that works", "schedule_suggest"),
			("when are all of us free", "schedule_suggest"),
			("when are all of us free next week", "schedule_suggest"),
			("when are all of us free tomorrow", "schedule_suggest"),
			("when are all of us free today", "schedule_suggest"),
			("Let's find a time that works", "schedule_suggest"),
			("find a time that works for me", "schedule_suggest"),
			("find a time that works for all of us", "schedule_suggest"),
			("find a time that works for us", "schedule_suggest"),
			("find us time a meeting for next week", "schedule_suggest"),
			("show us our potential meeting times", "schedule_suggest"),
			("show us our potential meeting times for next week", "schedule_suggest")]


training_set_google_docs = [

			("open up a doc", "google_docs"),
			("open up a document", "google_docs"),
			("open up a Google document", "google_docs"),
			("pull up a document", "google_docs"),
			("open me a document", "google_docs"),
			("open up a dock", "google_docs"),
			("open up a dog", "google_docs"),
			("open a notepad", "google_docs"),
			("open writing document", "google_docs"),
			("open us a document", "google_docs"),
			("display document", "google_docs"),
			("generate a document", "google_docs"),
			("Benedict, can you open up a document", "google_docs"),
			("can you open up a document", "google_docs"),
			("please launch a document", "google_docs"),
			("show me a dock", "google_docs"),
			("pull us up a document", "google_docs"),
			("Benedict, open me a document", "google_docs"),
			("Benedict, show me a dock", "google_docs"),
			("could you open up a document", "google_docs"),
			("open up a document", "google_docs"),
			("open up a document please", "google_docs"),
			("create a document", "google_docs"),
			("view a document", "google_docs")]


training_set_wolfram = [


			("What is the phase of the moon", "wolfram"),
			("twenty two plus five", "wolfram"),
			("What's the weather in Isla Vista", "wolfram"),
			("How long is a foot", "wolfram"),
			("How many stars are in the sky", "wolfram"),
			("How strong is an ant", "wolfram"),
			("How many cups are in a gallon", "wolfram"),
			("How many atoms are in a mole of Carbon", "wolfram"),
			("How many days are in a year", "wolfram"),
			("How many miles are in a lightyear", "wolfram"),
			("How long is a foot", "wolfram"),
			("How long is a foot", "wolfram"),
			("What is a galaxy", "wolfram"),
			("Where is Mexico", "wolfram"),
			("Where is Chicago", "wolfram"),
			("Where is Louisiana", "wolfram"),
			("Where Los Angeles", "wolfram"),
			("Where can I find Bagel Cafe", "wolfram"),
			("Where is San Francisco", "wolfram"),
			("Where is the equator", "wolfram"),
			("Where is Rome", "wolfram"),
			("Where can I find Stockholm", "wolfram"),
			("Where does the president live", "wolfram"),
			("where is the Bermuda triangle", "wolfram"),
			("What is the phase of the moon", "wolfram"),
			("What is the rate of expansion of the universe", "wolfram"),
			("what is the weather", "wolfram"),
			("what is the weather in New York", "wolfram"),
			("what is the weather here", "wolfram"),
			("what is the weather tomorrow", "wolfram"),
			("what is the weather next week", "wolfram"),
			("what is two times two", "wolfram"),
			("what is 100 plus 30", "wolfram"),
			("what is the integral of e to the x", "wolfram"),
			("what is Stoke's theorem", "wolfram"),
			("which city is the capital of Italy", "wolfram"),
			("which country has an eagle as its national bird", "wolfram"),
			("273 kelvin greater than 100 degrees celcius", "wolfram"),
			("which taco bell is closest", "wolfram"),
			("which country has the largest gdp", "wolfram"),
			("which state is the largest in the united states", "wolfram"),
			("which islands are in the pacific ocean", "wolfram"),
			("how many countries are in africa", "wolfram"),
			("What is the derivative of x squared", "wolfram"),
			("How long was the one hundred year's war", "wolfram"),
			("random integer from 0 to 100", "wolfram"),
			("when was the declaration of independence signed", "wolfram"),
			("what is the phase of the moon", "wolfram"),
			("what is the phase of the moon tomorrow", "wolfram"),
			("what is the phase of the moon next week", "wolfram"),
			("Graph x squared", "wolfram"),
			("Graph the function sign", "wolfram"),
			("What is cosine of pie", "wolfram"),
			("What is cosine of pi", "wolfram"),
			("What is the natural log of e", "wolfram"),
			("What is the largest state in the United States", "wolfram"),
			("What is Italy's GDP", "wolfram"),
			("how many grams are in ounce", "wolfram"),
			("what is the conversion of pounds to kilograms", "wolfram")]


training_set_wikipedia = [

			("who is the wizard of oz", "wikipedia"),
			("who plays Ted in how I met your mother", "wikipedia"),
			("who is Mr. T", "wikipedia"),
			("who is Samuel L Jackson", "wikipedia"),
			("who is Azeem", "wikipedia"),
			("who holds the ring to rule them all", "wikipedia"),
			("who is Alfred Hitchcock", "wikipedia"),
			("who Jay Freeman", "wikipedia"),
			("who plays Captain Picard", "wikipedia"),
			("who is Gauss", "wikipedia"),
			("who is Neil deGrass Tyson", "wikipedia"),
			("What is pi", "wikipedia"),
			("Eiffel tower", "wikipedia"),
			("the beatles", "wikipedia"),
			("Mickey mouse", "wikipedia"),
			("coca cola", "wikipedia"),
			("Obama", "wikipedia"),
			("Black Hole", "wikipedia"),
			("General Relativity", "wikipedia"),
			("mathematical set", "wikipedia"),
			("the trivial topology", "wikipedia"),
			("Eiffel Tower", "wikipedia"),
			("the Magna Carta", "wikipedia"),
			("Albert Einstein", "wikipedia"),
			("Michael Jackson", "wikipedia"),
			("New York City", "wikipedia"),
			("meteorology", "wikipedia"),
			("webRTC", "wikipedia"),
			("Amazon AWS", "wikipedia"),
			("Star Trek", "wikipedia"),
			("Monty python's flying circus", "wikipedia"),
			("the golden gate bridge", "wikipedia"),
			("the statue of liberty", "wikipedia"),
			("the movie pulp fiction", "wikipedia"),
			("dogs", "wikipedia"),
			("Who Obama", "wikipedia"),
			("Who is Kendrick Lamar", "wikipedia"),
			("Who is the president of France", "wikipedia"),
			("Who is the leader of Russia", "wikipedia"),
			("Who are the Beastie Boys", "wikipedia")]

training_set_google = [

			("Why are dogs", "google"),
			("When is my birthday", "google"),
			("Why do dogs have feet", "google"),
			("Is God just a slob like one of us", "google"),
			("Miley Cyrus twerk video", "google"),
			("where can I find a bible study group in my area", "google"),
			("at what age do boys start their period", "google"),
			("why is bing a bad search engine", "google"),
			("what time is the lakers game on tonight", "google"),
			("what is the internet", "google"),
			("where does the Michael Cera fan club meet", "google"),
			("how do I clean the spots out of my underwear", "google"),
			("what is Rick rolling", "google"),
			("who is Luke's father", "google"),
			("how do you make special brownies", "google"),
			("when should I use an Oxford comma", "google"),
			("how do I prevent my parents from talking about the birds and the bees", "google"),
			("when will hoverboards exist", "google"),
			("where did the dinosaurs go", "google"),
			("what is a blue waffle", "google"),
			("how to avoid paying taxes", "google"),
			("What are the biggest problems facing humanity", "google"),
			("When can I see my children again", "google"),
			("what does it mean to drop the kids off at the pool", "google"),
			("What are these spots on my genitals", "google"),
			("Why do birds suddenly appear", "google"),
			("where can I meet girls", "google"),
			("how special do you need to be to be in the special olympics", "google"),
			("where do babies come from", "google"),
			("Where is a good place to get Chinese food", "google"),
			("how often should I go to the dentist", "google"),
			("how do I make friends", "google"),
			("do girls fart", "google"),
			("best hangover cures", "google"),
			("what is the meaning of wife", "google"),
			("why do men have nipples", "google"),
			("why does it hurt when I pee", "google"),
			("what is Jennifer Lawrence's relationship status", "google"),
			("where in the world is Carmen Sandiego", "google"),
			("how do I ask out Becky from fourth period", "google")]

