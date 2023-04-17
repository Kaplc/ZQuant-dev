from sdk.binance_sdk.binance.api import API


class Spot(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://api.binance.com"
        super().__init__(api_key, api_secret, **kwargs)

    # MARKETS
    from sdk.binance_sdk.binance.spot._market import ping
    from sdk.binance_sdk.binance.spot._market import time
    from sdk.binance_sdk.binance.spot._market import exchange_info
    from sdk.binance_sdk.binance.spot._market import depth
    from sdk.binance_sdk.binance.spot._market import trades
    from sdk.binance_sdk.binance.spot._market import historical_trades
    from sdk.binance_sdk.binance.spot._market import agg_trades
    from sdk.binance_sdk.binance.spot._market import klines
    from sdk.binance_sdk.binance.spot._market import ui_klines
    from sdk.binance_sdk.binance.spot._market import avg_price
    from sdk.binance_sdk.binance.spot._market import ticker_24hr
    from sdk.binance_sdk.binance.spot._market import ticker_price
    from sdk.binance_sdk.binance.spot._market import book_ticker
    from sdk.binance_sdk.binance.spot._market import rolling_window_ticker

    # ACCOUNT (including orders and trades)
    from sdk.binance_sdk.binance.spot._trade import new_order_test
    from sdk.binance_sdk.binance.spot._trade import new_order
    from sdk.binance_sdk.binance.spot._trade import cancel_order
    from sdk.binance_sdk.binance.spot._trade import cancel_open_orders
    from sdk.binance_sdk.binance.spot._trade import get_order
    from sdk.binance_sdk.binance.spot._trade import cancel_and_replace
    from sdk.binance_sdk.binance.spot._trade import get_open_orders
    from sdk.binance_sdk.binance.spot._trade import get_orders
    from sdk.binance_sdk.binance.spot._trade import new_oco_order
    from sdk.binance_sdk.binance.spot._trade import cancel_oco_order
    from sdk.binance_sdk.binance.spot._trade import get_oco_order
    from sdk.binance_sdk.binance.spot._trade import get_oco_orders
    from sdk.binance_sdk.binance.spot._trade import get_oco_open_orders
    from sdk.binance_sdk.binance.spot._trade import account
    from sdk.binance_sdk.binance.spot._trade import my_trades
    from sdk.binance_sdk.binance.spot._trade import get_order_rate_limit

    # STREAMS
    from sdk.binance_sdk.binance.spot._data_stream import new_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import renew_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import close_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import new_margin_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import renew_margin_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import close_margin_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import new_isolated_margin_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import renew_isolated_margin_listen_key
    from sdk.binance_sdk.binance.spot._data_stream import close_isolated_margin_listen_key

    # MARGIN
    from sdk.binance_sdk.binance.spot._margin import margin_transfer
    from sdk.binance_sdk.binance.spot._margin import margin_borrow
    from sdk.binance_sdk.binance.spot._margin import margin_repay
    from sdk.binance_sdk.binance.spot._margin import margin_asset
    from sdk.binance_sdk.binance.spot._margin import margin_pair
    from sdk.binance_sdk.binance.spot._margin import margin_all_assets
    from sdk.binance_sdk.binance.spot._margin import margin_all_pairs
    from sdk.binance_sdk.binance.spot._margin import margin_pair_index
    from sdk.binance_sdk.binance.spot._margin import new_margin_order
    from sdk.binance_sdk.binance.spot._margin import cancel_margin_order
    from sdk.binance_sdk.binance.spot._margin import margin_transfer_history
    from sdk.binance_sdk.binance.spot._margin import margin_load_record
    from sdk.binance_sdk.binance.spot._margin import margin_repay_record
    from sdk.binance_sdk.binance.spot._margin import margin_interest_history
    from sdk.binance_sdk.binance.spot._margin import margin_force_liquidation_record
    from sdk.binance_sdk.binance.spot._margin import margin_account
    from sdk.binance_sdk.binance.spot._margin import margin_order
    from sdk.binance_sdk.binance.spot._margin import margin_open_orders
    from sdk.binance_sdk.binance.spot._margin import margin_open_orders_cancellation
    from sdk.binance_sdk.binance.spot._margin import margin_all_orders
    from sdk.binance_sdk.binance.spot._margin import margin_my_trades
    from sdk.binance_sdk.binance.spot._margin import margin_max_borrowable
    from sdk.binance_sdk.binance.spot._margin import margin_max_transferable
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_transfer
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_transfer_history
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_account
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_pair
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_all_pairs
    from sdk.binance_sdk.binance.spot._margin import toggle_bnbBurn
    from sdk.binance_sdk.binance.spot._margin import bnbBurn_status
    from sdk.binance_sdk.binance.spot._margin import margin_interest_rate_history
    from sdk.binance_sdk.binance.spot._margin import new_margin_oco_order
    from sdk.binance_sdk.binance.spot._margin import cancel_margin_oco_order
    from sdk.binance_sdk.binance.spot._margin import get_margin_oco_order
    from sdk.binance_sdk.binance.spot._margin import get_margin_oco_orders
    from sdk.binance_sdk.binance.spot._margin import get_margin_open_oco_orders
    from sdk.binance_sdk.binance.spot._margin import cancel_isolated_margin_account
    from sdk.binance_sdk.binance.spot._margin import enable_isolated_margin_account
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_account_limit
    from sdk.binance_sdk.binance.spot._margin import margin_fee
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_fee
    from sdk.binance_sdk.binance.spot._margin import isolated_margin_tier
    from sdk.binance_sdk.binance.spot._margin import margin_order_usage
    from sdk.binance_sdk.binance.spot._margin import margin_dust_log
    from sdk.binance_sdk.binance.spot._margin import summary_of_margin_account

    # SAVINGS
    from sdk.binance_sdk.binance.spot._savings import savings_flexible_products
    from sdk.binance_sdk.binance.spot._savings import savings_flexible_user_left_quota
    from sdk.binance_sdk.binance.spot._savings import savings_purchase_flexible_product
    from sdk.binance_sdk.binance.spot._savings import savings_flexible_user_redemption_quota
    from sdk.binance_sdk.binance.spot._savings import savings_flexible_redeem
    from sdk.binance_sdk.binance.spot._savings import savings_flexible_product_position
    from sdk.binance_sdk.binance.spot._savings import savings_project_list
    from sdk.binance_sdk.binance.spot._savings import savings_purchase_project
    from sdk.binance_sdk.binance.spot._savings import savings_project_position
    from sdk.binance_sdk.binance.spot._savings import savings_account
    from sdk.binance_sdk.binance.spot._savings import savings_purchase_record
    from sdk.binance_sdk.binance.spot._savings import savings_redemption_record
    from sdk.binance_sdk.binance.spot._savings import savings_interest_history
    from sdk.binance_sdk.binance.spot._savings import savings_change_position

    # Staking
    from sdk.binance_sdk.binance.spot._staking import staking_product_list
    from sdk.binance_sdk.binance.spot._staking import staking_purchase_product
    from sdk.binance_sdk.binance.spot._staking import staking_redeem_product
    from sdk.binance_sdk.binance.spot._staking import staking_product_position
    from sdk.binance_sdk.binance.spot._staking import staking_history
    from sdk.binance_sdk.binance.spot._staking import staking_set_auto_staking
    from sdk.binance_sdk.binance.spot._staking import staking_product_quota

    # WALLET
    from sdk.binance_sdk.binance.spot._wallet import system_status
    from sdk.binance_sdk.binance.spot._wallet import coin_info
    from sdk.binance_sdk.binance.spot._wallet import account_snapshot
    from sdk.binance_sdk.binance.spot._wallet import disable_fast_withdraw
    from sdk.binance_sdk.binance.spot._wallet import enable_fast_withdraw
    from sdk.binance_sdk.binance.spot._wallet import withdraw
    from sdk.binance_sdk.binance.spot._wallet import deposit_history
    from sdk.binance_sdk.binance.spot._wallet import withdraw_history
    from sdk.binance_sdk.binance.spot._wallet import deposit_address
    from sdk.binance_sdk.binance.spot._wallet import account_status
    from sdk.binance_sdk.binance.spot._wallet import api_trading_status
    from sdk.binance_sdk.binance.spot._wallet import dust_log
    from sdk.binance_sdk.binance.spot._wallet import user_universal_transfer
    from sdk.binance_sdk.binance.spot._wallet import user_universal_transfer_history
    from sdk.binance_sdk.binance.spot._wallet import transfer_dust
    from sdk.binance_sdk.binance.spot._wallet import asset_dividend_record
    from sdk.binance_sdk.binance.spot._wallet import asset_detail
    from sdk.binance_sdk.binance.spot._wallet import trade_fee
    from sdk.binance_sdk.binance.spot._wallet import funding_wallet
    from sdk.binance_sdk.binance.spot._wallet import user_asset
    from sdk.binance_sdk.binance.spot._wallet import api_key_permissions
    from sdk.binance_sdk.binance.spot._wallet import bnb_convertible_assets
    from sdk.binance_sdk.binance.spot._wallet import convertible_coins
    from sdk.binance_sdk.binance.spot._wallet import toggle_auto_convertion
    from sdk.binance_sdk.binance.spot._wallet import cloud_mining_trans_history
    from sdk.binance_sdk.binance.spot._wallet import convert_transfer
    from sdk.binance_sdk.binance.spot._wallet import convert_history

    # MINING
    from sdk.binance_sdk.binance.spot._mining import mining_algo_list
    from sdk.binance_sdk.binance.spot._mining import mining_coin_list
    from sdk.binance_sdk.binance.spot._mining import mining_worker
    from sdk.binance_sdk.binance.spot._mining import mining_worker_list
    from sdk.binance_sdk.binance.spot._mining import mining_earnings_list
    from sdk.binance_sdk.binance.spot._mining import mining_bonus_list
    from sdk.binance_sdk.binance.spot._mining import mining_statistics_list
    from sdk.binance_sdk.binance.spot._mining import mining_account_list
    from sdk.binance_sdk.binance.spot._mining import mining_hashrate_resale_request
    from sdk.binance_sdk.binance.spot._mining import mining_hashrate_resale_cancellation
    from sdk.binance_sdk.binance.spot._mining import mining_hashrate_resale_list
    from sdk.binance_sdk.binance.spot._mining import mining_hashrate_resale_details
    from sdk.binance_sdk.binance.spot._mining import mining_account_earning

    # SUB-ACCOUNT
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_create
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_list
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_assets
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_deposit_address
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_deposit_history
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_status
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_enable_margin
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_margin_account
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_margin_account_summary
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_enable_futures
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_futures_transfer
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_margin_transfer
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_transfer_to_sub
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_transfer_to_master
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_transfer_sub_account_history
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_futures_asset_transfer_history
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_futures_asset_transfer
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_spot_summary
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_universal_transfer
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_universal_transfer_history
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_futures_account
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_futures_account_summary
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_futures_position_risk
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_spot_transfer_history
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_enable_leverage_token
    from sdk.binance_sdk.binance.spot._sub_account import managed_sub_account_deposit
    from sdk.binance_sdk.binance.spot._sub_account import managed_sub_account_assets
    from sdk.binance_sdk.binance.spot._sub_account import managed_sub_account_withdraw
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_api_toggle_ip_restriction
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_api_add_ip
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_api_get_ip_restriction
    from sdk.binance_sdk.binance.spot._sub_account import sub_account_api_delete_ip
    from sdk.binance_sdk.binance.spot._sub_account import managed_sub_account_get_snapshot
    from sdk.binance_sdk.binance.spot._sub_account import managed_sub_account_investor_trans_log
    from sdk.binance_sdk.binance.spot._sub_account import managed_sub_account_trading_trans_log

    # FUTURES
    from sdk.binance_sdk.binance.spot._futures import futures_transfer
    from sdk.binance_sdk.binance.spot._futures import futures_transfer_history
    from sdk.binance_sdk.binance.spot._futures import futures_loan_borrow_history
    from sdk.binance_sdk.binance.spot._futures import futures_loan_repay_history
    from sdk.binance_sdk.binance.spot._futures import futures_loan_wallet
    from sdk.binance_sdk.binance.spot._futures import futures_loan_adjust_collateral_history
    from sdk.binance_sdk.binance.spot._futures import futures_loan_liquidation_history
    from sdk.binance_sdk.binance.spot._futures import futures_loan_interest_history

    # BLVTs
    from sdk.binance_sdk.binance.spot._blvt import blvt_info
    from sdk.binance_sdk.binance.spot._blvt import subscribe_blvt
    from sdk.binance_sdk.binance.spot._blvt import subscription_record
    from sdk.binance_sdk.binance.spot._blvt import redeem_blvt
    from sdk.binance_sdk.binance.spot._blvt import redemption_record
    from sdk.binance_sdk.binance.spot._blvt import user_limit_info

    # BSwap
    from sdk.binance_sdk.binance.spot._bswap import bswap_pools
    from sdk.binance_sdk.binance.spot._bswap import bswap_liquidity
    from sdk.binance_sdk.binance.spot._bswap import bswap_liquidity_add
    from sdk.binance_sdk.binance.spot._bswap import bswap_liquidity_remove
    from sdk.binance_sdk.binance.spot._bswap import bswap_liquidity_operation_record
    from sdk.binance_sdk.binance.spot._bswap import bswap_request_quote
    from sdk.binance_sdk.binance.spot._bswap import bswap_swap
    from sdk.binance_sdk.binance.spot._bswap import bswap_swap_history
    from sdk.binance_sdk.binance.spot._bswap import bswap_pool_configure
    from sdk.binance_sdk.binance.spot._bswap import bswap_add_liquidity_preview
    from sdk.binance_sdk.binance.spot._bswap import bswap_remove_liquidity_preview
    from sdk.binance_sdk.binance.spot._bswap import bswap_unclaimed_rewards
    from sdk.binance_sdk.binance.spot._bswap import bswap_claim_rewards
    from sdk.binance_sdk.binance.spot._bswap import bswap_claimed_rewards

    # FIAT
    from sdk.binance_sdk.binance.spot._fiat import fiat_order_history
    from sdk.binance_sdk.binance.spot._fiat import fiat_payment_history

    # C2C
    from sdk.binance_sdk.binance.spot._c2c import c2c_trade_history

    # LOANS
    from sdk.binance_sdk.binance.spot._loan import loan_history
    from sdk.binance_sdk.binance.spot._loan import loan_borrow
    from sdk.binance_sdk.binance.spot._loan import loan_borrow_history
    from sdk.binance_sdk.binance.spot._loan import loan_ongoing_orders
    from sdk.binance_sdk.binance.spot._loan import loan_repay
    from sdk.binance_sdk.binance.spot._loan import loan_repay_history
    from sdk.binance_sdk.binance.spot._loan import loan_adjust_ltv
    from sdk.binance_sdk.binance.spot._loan import loan_adjust_ltv_history
    from sdk.binance_sdk.binance.spot._loan import loan_vip_ongoing_orders
    from sdk.binance_sdk.binance.spot._loan import loan_vip_repay
    from sdk.binance_sdk.binance.spot._loan import loan_vip_repay_history
    from sdk.binance_sdk.binance.spot._loan import loan_vip_collateral_account
    from sdk.binance_sdk.binance.spot._loan import loan_loanable_data
    from sdk.binance_sdk.binance.spot._loan import loan_collateral_data
    from sdk.binance_sdk.binance.spot._loan import loan_collateral_rate
    from sdk.binance_sdk.binance.spot._loan import loan_customize_margin_call

    # PAY
    from sdk.binance_sdk.binance.spot._pay import pay_history

    # CONVERT
    from sdk.binance_sdk.binance.spot._convert import convert_trade_history

    # REBATE
    from sdk.binance_sdk.binance.spot._rebate import rebate_spot_history

    # NFT
    from sdk.binance_sdk.binance.spot._nft import nft_transaction_history
    from sdk.binance_sdk.binance.spot._nft import nft_deposit_history
    from sdk.binance_sdk.binance.spot._nft import nft_withdraw_history
    from sdk.binance_sdk.binance.spot._nft import nft_asset

    # Gift Card (Binance Code in the API documentation)
    from sdk.binance_sdk.binance.spot._gift_card import gift_card_create_code
    from sdk.binance_sdk.binance.spot._gift_card import gift_card_redeem_code
    from sdk.binance_sdk.binance.spot._gift_card import gift_card_verify_code
    from sdk.binance_sdk.binance.spot._gift_card import gift_card_rsa_public_key
    from sdk.binance_sdk.binance.spot._gift_card import gift_card_buy_code
    from sdk.binance_sdk.binance.spot._gift_card import gift_card_token_limit

    # Portfolio Margin
    from sdk.binance_sdk.binance.spot._portfolio_margin import portfolio_margin_account
    from sdk.binance_sdk.binance.spot._portfolio_margin import portfolio_margin_collateral_rate
    from sdk.binance_sdk.binance.spot._portfolio_margin import portfolio_margin_bankruptcy_loan_amount
    from sdk.binance_sdk.binance.spot._portfolio_margin import portfolio_margin_bankruptcy_loan_repay
