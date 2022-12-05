from ingenico.connect.sdk.factory import Factory
from ingenico.connect.sdk.api_exception import ApiException
from ingenico.connect.sdk.declined_payment_exception import DeclinedPaymentException

from ingenico.connect.sdk.domain.payment.create_payment_request import (
    CreatePaymentRequest,
)
from ingenico.connect.sdk.domain.payment.approve_payment_request import (
    ApprovePaymentRequest,
)
from ingenico.connect.sdk.domain.payment.definitions.approve_payment_non_sepa_direct_debit_payment_method_specific_input import (
    ApprovePaymentNonSepaDirectDebitPaymentMethodSpecificInput,
)
from ingenico.connect.sdk.domain.payment.definitions.order_approve_payment import (
    OrderApprovePayment,
)
from ingenico.connect.sdk.domain.payment.definitions.order_references_approve_payment import (
    OrderReferencesApprovePayment,
)
from order import get_order
from card_payment_method_si import get_card_payment_method_specific_input


CLIENT = Factory.create_client_from_file(
    "./conf",
    "3cdf571bae3bdec5",
    "qCCfYEWiuSVM7orLbgcVpItFk+CBnxQ1rWV1ZnGPiCY=",
)
MERCHANT_ID = "1196"
AMOUNT = 2200

with CLIENT as c:
    # CREATE PAYMENT
    body = CreatePaymentRequest()
    body.card_payment_method_specific_input = get_card_payment_method_specific_input(
        card_number="4567350000427977",
        cvv="456",
        expiry_date="1225",
        currency="USD",
        amount=AMOUNT,
        payment_product_id=1,
    )
    body.order = get_order(currency="USD", amount=2200)

    try:
        create_payment_response = CLIENT.merchant(MERCHANT_ID).payments().create(body)
    except DeclinedPaymentException as e:
        print(e)
    except ApiException as e:
        print(e)

    # GET TOKEN
    from ingenico.connect.sdk.domain.payment.tokenize_payment_request import (
        TokenizePaymentRequest,
    )

    body = TokenizePaymentRequest()
    body.alias = "Some alias"

    token_response = (
        CLIENT.merchant(MERCHANT_ID)
        .payments()
        .tokenize(create_payment_response.payment.id, body)
    )

    # APPROVE PAYMENT
    direct_debit_payment_method_specific_input = (
        ApprovePaymentNonSepaDirectDebitPaymentMethodSpecificInput()
    )
    direct_debit_payment_method_specific_input.date_collect = "20221204"
    direct_debit_payment_method_specific_input.token = token_response.token

    references = OrderReferencesApprovePayment()
    references.merchant_reference = "AcmeOrder0001"

    order = OrderApprovePayment()
    order.references = references

    body = ApprovePaymentRequest()
    body.amount = AMOUNT
    body.direct_debit_payment_method_specific_input = (
        direct_debit_payment_method_specific_input
    )
    body.order = order

    # DELETE TOKEN
    # Delete the token from the original payment in token_response to make a new
    # token next time you run this script. Apparently you can't approve a payment
    # with its token if an earlier payment used the same CC. I have no idea why
    # this is supposedly logical. Sounds illogical to me.
    #
    # from ingenico.connect.sdk.merchant.tokens.delete_token_params import (
    #     DeleteTokenParams,
    # )
    # CLIENT.merchant(MERCHANT_ID).tokens().delete(
    #     "9ae31db5-069c-4efc-95d9-77552d0eda37", DeleteTokenParams()
    # )

    response = (
        CLIENT.merchant(MERCHANT_ID).payments()
        # .approve(token_response.original_payment_id, body)
        .approve(create_payment_response.payment.id, body)
    )
