# NoSwearBot
[Link](https://discord.com/api/oauth2/authorize?client_id=756954513256087722&permissions=8&scope=bot)
The NoSwearBot is a bot that is made to regulate chat in discord servers,
turning discord servers a safe place where they can't be bullied and people can't spread toxicity while reducing the amount of work that moderators should spend looking at chat.
This project allows admins to blacklist a word in the server to ban it, when said the message is deleted and a warning is sent to the sender and their infrigement count is incremented. Once the count exceeds a threshold set in the server, they get kicked.
Owners are able to delete blacklisted expressions as well and users can view the blacklisted expressions
## Learning outcomes
- Working with asynchronous functions in Python
- The understanding of string and pattern matching through the Knuth-Morris-Pratt algorithm
- Basic CRUD operations in PostgreSQL databases
- Working with Discord.py library and how to make a bot from scratch and discord commands
- The use of coroutines in Python
- The use of a cloud database to store and retrieve data
## Functions
- Blacklist a word
- Remove a word from blacklist
- Displaying the Server's blacklist
- Once sent, the message is checked by the bot, in case a blacklisted word exists a warning is sent to the author and the message is deleted
- Set infrigement threshold

