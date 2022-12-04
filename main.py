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

with CLIENT as c:
    # CREATE PAYMENT
    body = CreatePaymentRequest()
    body.card_payment_method_specific_input = get_card_payment_method_specific_input(
        card_number="4567350000427977",
        cvv="456",
        expiry_date="1225",
        currency="EUR",
        amount=2980,
        payment_product_id=1,
    )
    body.order = get_order("EUR")

    try:
        create_payment_response = CLIENT.merchant(MERCHANT_ID).payments().create(body)
        print(create_payment_response)
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
    print(token_response)

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
    body.amount = 2980
    body.direct_debit_payment_method_specific_input = (
        direct_debit_payment_method_specific_input
    )
    body.order = order

    response = (
        CLIENT.merchant(MERCHANT_ID).payments()
        # .approve(token_response.original_payment_id, body)
        .approve(create_payment_response.payment.id, body)
    )
