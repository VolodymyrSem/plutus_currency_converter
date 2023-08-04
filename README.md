# PLUTUS currency converter

Terminal currency converter application PLUTUS.

The application works with all Europe and North American currencies (USD, CAD). 
Complete list of currencies is defined further.

May be used for:
* Getting actual or prepared rate for a pair of currencies
* Getting how much is needed to pay for amount of a target currency when it's possible to have double/triple conversion
* Storing rates in an internal database
* Predefining user's pairs of currencies for getting all rates at once

The application uses two sources of rates: API and an internal database after downloading all rates into it.
The source may be changed in the main menu.

Updating rates in the internal database may be done at any time by user's confirming. 

Inputted currencies may be as alphabetic codes or three first letters of the country in which the currency is. 
Searching needed code with prefix is processed by predefined prefix tree (Trie).

The application supports 162 currencies.

# Main menu

Main menu has this format:

    x. Switch rates' source (actual by default)

    1. Exchange calculator
    2. Make a payment with a conversion
    3. Show rate for saved currencies
    4. Refresh your database if needed
    5. Create new pairs of saved currencies
    6. Delete pair from saved currencies
    7. Delete ALL pairs from saved currencies
    0. Exit

    Write a number (0...7 or x): 

x. The choice for changing the source from which the application will get rates. 
To use prepared rates, it is needed to download them first by choosing '4. Refresh your database if needed'.

1. Input amount of an owned currency and two currencies (owned and target) to get an amount of the target currency 


2. The same, but the amount is for target currency. 
    
    In this case, user will 'buy' target currency and wants to know how much will it cost.

    Also, it is needed to input a card system which is verified for existence of double/triple conversion in this particular operation.

    This choice is mainly used for getting an info whether purchases in a foreign country will be overpaid or not due to possible conversions.


3. User may get rates for all saved pairs at once only by choosing this choice.


4. This choice is used to refresh or create an internal database if needed. It's used much faster compared to the API.


5. User may add new pairs of saved currencies in the database by this choice.


6. User may delete one or more pairs from saved pairs.


7. Also, user may delete all saved pairs at once.
