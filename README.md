How to run:

1. first check config.json

    a. change API_ID and API_HASH according to your account
    
    b. SESSION_NAME is just a name to mark when you execute the
       script
       
    c. SOURCE_CHANNEL_LIST is a list of channels that you want
       get the messsage from
       
    d. DESTINATION_CHANNEL_ID is our private channel for
       testing purposes. you can create your own channel and change the ID accordingly
       
    e. HEALTH_CHECK_INTERVAL_SECOND is a time that we want to check current status internet connection
    
    f. IGNORE_LIST is a list of characters as message filter. Update the list accordingly.

2. run: pip install -r requirements.txt

    This just to make sure we use the same versions of Telethon library.

3. run: python forwarder.py
