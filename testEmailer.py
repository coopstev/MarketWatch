from Emailer import Emailer
recipients = ["coopstev012@gmail.com", "lilypad22003@gmail.com"]
emailer = Emailer(recipients)
emailer.send_email("/home/ubuntu/MarketWatch/notifications/testText.txt")