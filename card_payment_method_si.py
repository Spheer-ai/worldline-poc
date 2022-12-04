from ingenico.connect.sdk.domain.definitions.amount_of_money import AmountOfMoney
from ingenico.connect.sdk.domain.definitions.card import Card
from ingenico.connect.sdk.domain.payment.definitions.card_payment_method_specific_input import (
    CardPaymentMethodSpecificInput,
)
from ingenico.connect.sdk.domain.payment.definitions.redirection_data import (
    RedirectionData,
)
from ingenico.connect.sdk.domain.payment.definitions.three_d_secure import ThreeDSecure


def get_card_payment_method_specific_input(
    card_number: str,
    cvv: str,
    expiry_date: str,
    currency: str,
    amount: int,
    payment_product_id: int,
):
    card = Card()
    card.card_number = card_number
    card.cardholder_name = "MMT de Wijk"
    card.cvv = cvv
    card.expiry_date = expiry_date

    authentication_amount = AmountOfMoney()
    authentication_amount.amount = amount
    authentication_amount.currency_code = currency

    redirection_data = RedirectionData()
    redirection_data.return_url = "https://hostname.myownwebsite.url"

    three_d_secure = ThreeDSecure()
    three_d_secure.authentication_amount = authentication_amount
    three_d_secure.authentication_flow = "browser"
    three_d_secure.challenge_canvas_size = "600x400"
    three_d_secure.challenge_indicator = "challenge-requested"
    three_d_secure.exemption_request = "none"
    three_d_secure.redirection_data = redirection_data
    three_d_secure.skip_authentication = False

    card_payment_method_specific_input = CardPaymentMethodSpecificInput()
    card_payment_method_specific_input.card = card
    card_payment_method_specific_input.is_recurring = False
    card_payment_method_specific_input.merchant_initiated_reason_indicator = (
        "delayedCharges"
    )
    card_payment_method_specific_input.payment_product_id = payment_product_id
    card_payment_method_specific_input.three_d_secure = three_d_secure
    card_payment_method_specific_input.transaction_channel = "ECOMMERCE"

    return card_payment_method_specific_input
