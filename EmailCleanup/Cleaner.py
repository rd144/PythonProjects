import imapclient
import pyzmail
from bs4 import BeautifulSoup
import re

#TODO - Currently Set to work with gmail, this should also work with other clients
#TODO - A UI on top of the framework would be a good learning experience

print("CODE START")

mailbox = imapclient.IMAPClient('imap.gmail.com', ssl=True)
mailbox.login(' rossdingwall2014@gmail.com ', ' hpnbipmqcbkunnxo ')
mailbox.select_folder('[Gmail]/All Mail')

print("Mailbox Connected")

#TODO - Optimise Email Search
"""
Currently this searches for all Emails. This could run into size and processing issues. 
Instead, it should work back day by day accumulating emails and dealing with them in a piece meal manner
"""

unique_IDs = mailbox.search('ALL') #'SINCE 01-Jun-2020'
raw_messages = mailbox.fetch(unique_IDs,['BODY[]'])
print('Emails Found: {email_count}'.format(email_count=len(unique_IDs)))
unsubscribe_pattern = re.compile('.*unsubscribe.*',re.IGNORECASE)

emailer_dict = {}
totals = 0

for index,ID in enumerate(unique_IDs):

    print(index,index%len(unique_IDs))

    cleaned_message = pyzmail.PyzMessage.factory(raw_messages[ID][b'BODY[]'])

    # TODO Split into it's own function
    from_addresses = cleaned_message.get_addresses('from')
    for emailer_details in from_addresses:
        totals += 1
        name,address = emailer_details
        if name in emailer_dict:
            emailer_dict[name]['Count'] += 1
        else:
            emailer_dict[name] = {'Count':1}

    # # TODO Create and Seperate Unsubscribe Search
    # raw_soup = cleaned_message.html_part.get_payload().decode(cleaned_message.html_part.charset)
    # soup = BeautifulSoup(raw_soup, 'html.parser')
    # unsubscribe_elements = soup.body.find_all('a',string=unsubscribe_pattern)

print(totals)
import json
file = open('test.json','w')
json.dump(emailer_dict,file)