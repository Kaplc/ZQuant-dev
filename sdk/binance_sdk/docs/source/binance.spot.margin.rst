Margin Endpoints
================

Margin Account Transfer (MARGIN)
--------------------------------
.. autofunction:: binance.spot.Spot.margin_transfer

Margin Account Borrow (MARGIN)
------------------------------
.. autofunction:: binance.spot.Spot.margin_borrow

Margin Account Repay(MARGIN)
----------------------------
.. autofunction:: binance.spot.Spot.margin_repay

Query Margin Asset (MARKET_DATA)
--------------------------------
.. autofunction:: binance.spot.Spot.margin_asset

Query Margin Pair (MARKET_DATA)
-------------------------------
.. autofunction:: binance.spot.Spot.margin_pair

Get All Margin Assets (MARKET_DATA)
-----------------------------------
.. autofunction:: binance.spot.Spot.margin_all_assets

Get All Margin Pairs (MARKET_DATA)
----------------------------------
.. autofunction:: binance.spot.Spot.margin_all_pairs

Query Margin PriceIndex (MARKET_DATA)
-------------------------------------
.. autofunction:: binance.spot.Spot.margin_pair_index

Margin Account New Order (TRADE)
--------------------------------
.. autofunction:: binance.spot.Spot.new_margin_order

Margin Account Cancel Order (TRADE)
-----------------------------------
.. autofunction:: binance.spot.Spot.cancel_margin_order

Get Transfer History (USER_DATA)
--------------------------------
.. autofunction:: binance.spot.Spot.margin_transfer_history

Query Loan Record (USER_DATA)
-----------------------------
.. autofunction:: binance.spot.Spot.margin_load_record

Query Repay Record (USER_DATA)
--------------------------------
.. autofunction:: binance.spot.Spot.margin_repay_record

Get Interest History (USER_DATA)
--------------------------------
.. autofunction:: binance.spot.Spot.margin_interest_history

Get Force Liquidation Record (USER_DATA)
----------------------------------------
.. autofunction:: binance.spot.Spot.margin_force_liquidation_record

Query Cross Margin Account Details (USER_DATA)
----------------------------------------------
.. autofunction:: binance.spot.Spot.margin_account

Query Margin Account's Order (USER_DATA)
----------------------------------------
.. autofunction:: binance.spot.Spot.margin_order

Query Margin Account's Open Order (USER_DATA)
---------------------------------------------
.. autofunction:: binance.spot.Spot.margin_open_orders

Margin Account Cancel all Open Orders on a Symbol (USER_DATA)
-------------------------------------------------------------
.. autofunction:: binance.spot.Spot.margin_open_orders_cancellation

Query Margin Account's All Orders (USER_DATA)
---------------------------------------------
.. autofunction:: binance.spot.Spot.margin_all_orders

Query Margin Account's Trade List (USER_DATA)
---------------------------------------------
.. autofunction:: binance.spot.Spot.margin_my_trades

Query Max Borrow (USER_DATA)
----------------------------
.. autofunction:: binance.spot.Spot.margin_max_borrowable

Query Max Transfer-Out Amount (USER_DATA)
-----------------------------------------
.. autofunction:: binance.spot.Spot.margin_max_transferable

Isolated Margin Account Transfer (MARGIN)
-----------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_transfer

Get Isolated Margin Transfer History (USER_DATA)
------------------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_transfer_history

Query Isolated Margin Account Info (USER_DATA)
----------------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_account

Query Isolated Margin Symbol (USER_DATA)
----------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_pair

Get All Isolated Margin Symbol(USER_DATA)
-----------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_all_pairs

Toggle BNB Burn On Spot Trade And Margin Interest (USER_DATA)
-------------------------------------------------------------
.. autofunction:: binance.spot.Spot.toggle_bnbBurn

Get BNB Burn Status (USER_DATA)
-------------------------------
.. autofunction:: binance.spot.Spot.bnbBurn_status

Get Margin Interest Rate History (USER_DATA)
--------------------------------------------
.. autofunction:: binance.spot.Spot.margin_interest_rate_history

Margin Account New OCO (TRADE)
------------------------------
.. autofunction:: binance.spot.Spot.new_margin_oco_order

Margin Account Cancel OCO (TRADE)
---------------------------------
.. autofunction:: binance.spot.Spot.cancel_margin_oco_order

Query Margin Account's OCO (USER_DATA)
--------------------------------------
.. autofunction:: binance.spot.Spot.get_margin_oco_order

Query Margin Account's all OCO (USER_DATA)
------------------------------------------
.. autofunction:: binance.spot.Spot.get_margin_oco_orders

Query Margin Account's Open OCO (USER_DATA)
-------------------------------------------
.. autofunction:: binance.spot.Spot.get_margin_open_oco_orders

Disable Isolated Margin Account (TRADE)
---------------------------------------
.. autofunction:: binance.spot.Spot.cancel_isolated_margin_account

Enable Isolated Margin Account (TRADE)
--------------------------------------
.. autofunction:: binance.spot.Spot.enable_isolated_margin_account

Query Enabled Isolated Margin Account Limit (USER_DATA)
-------------------------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_account_limit

Query Cross Margin Fee Data (USER_DATA)
---------------------------------------
.. autofunction:: binance.spot.Spot.margin_fee

Query Isolated Margin Fee Data (USER_DATA)
------------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_fee

Query Isolated Margin Tier Data (USER_DATA)
-------------------------------------------
.. autofunction:: binance.spot.Spot.isolated_margin_tier

Query Current Margin Order Count Usage (TRADE)
----------------------------------------------
.. autofunction:: binance.spot.Spot.margin_order_usage

Margin Dust Log (USER_DATA)
---------------------------
.. autofunction:: binance.spot.Spot.margin_dust_log

Get Summary of Margin account (USER_DATA)
-----------------------------------------
.. autofunction:: binance.spot.Spot.summary_of_margin_account
