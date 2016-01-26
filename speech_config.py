from dotmap import DotMap

session = DotMap({"greeting": "Hi. Welcome to the Met Office NLP app",
		          "reprompt": "Hey, I said HI",
		 		  "sign_off": "Thanks very much for using our app. See you later.",
		   		  "help": "I can't help you."})

Activity = DotMap({"title": "TITLE",
				   "question": "What do you want to do",
		           "reprompt": "I SAID WHAT DO YOU WANT TO DO!",
		           "help": "Which word don't you understand"})

start_time = DotMap({"title": "TITLE",
				     "question": "When do you want to do that",
		             "reprompt": "I SAID WHEN DO YOU WANT TO DO THAT!",
		             "help": "Which word don't you understand"})

location = DotMap({"title": "TITLE",
				   "question": "Where do you want to do that",
		           "reprompt": "I SAID WHERE DO YOU WANT TO DO THAT!",
		           "help": "Which word don't you understand"})