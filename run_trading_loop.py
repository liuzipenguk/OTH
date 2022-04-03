# import time

from optibook.synchronous_client import Exchange
import time
from optibook.synchronous_client import Exchange


import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

e = Exchange()
a = e.connect()

instrument_id = 'PHILIPS_A'
instrument_id2 = 'PHILIPS_B'


def dual_list_once():
	# execute the trading strategy once
	
	book = e.get_last_price_book(instrument_id)
	book2 = e.get_last_price_book(instrument_id2)
	try:
		A_Bid_B_Ask_Spread = book.bids[0].price-book2.asks[0].price
        if A_Bid_B_Ask_Spread > 0:
            print(A_Bid_B_Ask_Spread, '/A Bid - B Ask')
        B_Bid_A_Ask_Spread = book2.bids[0].price-book.asks[0].price
        if B_Bid_A_Ask_Spread > 0:
            print(B_Bid_A_Ask_Spread, '/B Bid - A Ask')
    except IndexError:
        pass


    positions = e.get_positions() # added by qdou
    traded = True
    if A_Bid_B_Ask_Spread > 0:
        print('A bid',book.bids[0].price,'B ask',book2.asks[0].price)
        ArbiVol = min(book.bids[0].volume, book2.asks[0].volume, 40, 250-positions["PHILIPS_A"], 250-positions["PHILIPS_B"],250+positions["PHILIPS_A"],250+positions["PHILIPS_B"])
        print('A_Bid_B_Ask vol = ',ArbiVol)
        # begining with the side with less liquidity > lower volume
        if book2.asks[0].volume > book.bids[0].volume:
            sell = e.insert_order(instrument_id, price=book.bids[0].price, volume=ArbiVol, side='ask', order_type='limit')
            print('sell A at ',book.bids[0].price)
            buy = e.insert_order(instrument_id2, price=book2.asks[0].price, volume=ArbiVol, side='bid', order_type='limit')
            print('buy B at ',book2.asks[0].price)
            print(f"Order Id: {buy}")
            print(f"Order Id: {sell}")
            print(ArbiVol,'/A Bid - B Ask')
        else:
            buy = e.insert_order(instrument_id2, price=book2.asks[0].price, volume=ArbiVol, side='bid', order_type='limit')
            print('buy B at ',book2.asks[0].price)
            sell = e.insert_order(instrument_id, price=book.bids[0].price, volume=ArbiVol, side='ask', order_type='limit')
            print('sell A at ',book.bids[0].price)
            print(f"Order Id: {buy}")
            print(f"Order Id: {sell}")
            print(ArbiVol,'/A Bid - B Ask')

    elif B_Bid_A_Ask_Spread > 0:
        print('B bid' ,book2.bids[0].price, 'A ask' ,book.asks[0].price)
        ArbiVol = min(book2.bids[0].volume, book.asks[0].volume, 40,250-positions["PHILIPS_A"], 250-positions["PHILIPS_B"],250+positions["PHILIPS_A"],250+positions["PHILIPS_B"])
        print('B_Bid_A_Ask vol = ',ArbiVol)
        # begining with the side with less liquidity > lower volume
        if book.asks[0].volume > book2.bids[0].volume:
            sell = e.insert_order(instrument_id2, price=book2.bids[0].price, volume=ArbiVol, side='ask', order_type='limit')
            print('sell B at ',book2.bids[0].price)
            buy = e.insert_order(instrument_id, price=book.asks[0].price, volume=ArbiVol, side='bid', order_type='limit')
            print('buy A at ',book.asks[0].price)
            print(f"Order Id: {buy}")
            print(f"Order Id: {sell}")
            print(ArbiVol,'/B Bid - A Ask')

        else:
            buy = e.insert_order(instrument_id, price=book.asks[0].price, volume=ArbiVol, side='bid', order_type='limit')
            print('buy A at ',book.asks[0].price)
            sell = e.insert_order(instrument_id2, price=book2.bids[0].price, volume=ArbiVol, side='ask', order_type='limit')
            print('sell B at ',book2.bids[0].price)
            print(f"Order Id: {buy}")
            print(f"Order Id: {sell}")
            print(ArbiVol,'/ A AskB - Bid ')
    else:
    	traded = False

	# return a signal for the counter
	if traded:
		return True
	else:
		return False

cnt = 0
cnt_limit = 25
start = time.time()
while True:
	# wait until condition is met,
	if cnt < cnt_limit:
		if dual_list_once():
			cnt += 1
			print('count: {}'.format(cnt)) # comment when actually competing

	# reset timer and counter
	end = time.time()
	
	if end - start>1:
		# condiser comment prints when actually competing
	    print('count and time elapsed: {} and {}'.format(cnt, end-start))
	    print('about to reset')
	    start = time.time()
	    cnt = 0
	    # break