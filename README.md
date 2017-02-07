# Algo2
Live trading and backtesting platform written in Python.

The library is event-based, which means it is more complex and 
slower than the vectorised/for-loop approach usually employed in researching 
strategies, but display more stable and realistic live behaviour (same code is
 indeed used for both back-testing and live trading) and less prone by 
construction to looking-ahead bias. 


### Flow
The event-loop is as follows:
- the data handler (feeds) reads the data (from csv files or databases) and 
generates a market event (either a new daily bar - BarEvent - or a tick - 
TickEvent - for more granular back-testing or live trading). 
- The market event is then used to produce a signal (SignalEvent),
e.g. a moving average cross.
- In turn the signal is used to generate an order - OrderEvent - after relevant
sizing (e.g. volatility-based) and risk management (e.g. capping number 
of lots).
- Finally the order gets executed by a Broker (either simulated or a live one) 
and the filled order recorded.

Repeat.

### Main Components
- Data handler(s) in feeds: gets data from csv files (or quandl or databases), 
create a market event and pass it to the queue.
- Strategies: transforms a market event into a suggested action (i.e. signal),
create signal event to be passed to the queue.
- Positions (Stocks, ...): represents an instrument (tickers, 
...), and its book-keeping: its quantity, price and market values (pnl, ...).
- Portfolio: handles any new position or modification to a current position 
(forwarding market value updates to the position class), and updates 
overall market/accounting values (closed and still open positions).
- Portfolio handler helps managing the queue during back-testing (and live 
trading) by calling relevant objects (position sizer and refiners, and portfolio 
for positions/value updates).
- Broker(s): executes orders by creating a filled order event and passing to 
the queue.
- Statistics: updates equity curve and relative timestamp to calculate 
statistics (equity_returns, hwm, drawdowns, Sharpe ratio, ...) and to plot.
        
#### TODO list:
- finish volatility position sizing;
- create the pension strategy sample;
- integrate TA-Lib? (see backtrader);
- introduce currency conversion in either position or portfolio;
- create futures position (currently supporting only stocks);
- test Carver's systems (moma + carry);
- create FX position;
- getting more tests done on samples.

   Nice to have: i. getting Sphynx for docs, ii. CI Travis, iii. finish Mongo,
iv. integrate arctic database?
