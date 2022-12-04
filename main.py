from ingenico.connect.sdk.factory import Factory
from ingenico.connect.sdk.api_exception import ApiException
from ingenico.connect.sdk.declined_payment_exception import DeclinedPaymentException
from ingenico.connect.sdk.domain.definitions.address import Address
from ingenico.connect.sdk.domain.definitions.amount_of_money import AmountOfMoney
from ingenico.connect.sdk.domain.definitions.card import Card
from ingenico.connect.sdk.domain.definitions.company_information import (
    CompanyInformation,
)
from ingenico.connect.sdk.domain.payment.create_payment_request import (
    CreatePaymentRequest,
)
from ingenico.connect.sdk.domain.payment.definitions.address_personal import (
    AddressPersonal,
)
from ingenico.connect.sdk.domain.payment.definitions.browser_data import BrowserData
from ingenico.connect.sdk.domain.payment.definitions.card_payment_method_specific_input import (
    CardPaymentMethodSpecificInput,
)
from ingenico.connect.sdk.domain.payment.definitions.contact_details import (
    ContactDetails,
)
from ingenico.connect.sdk.domain.payment.definitions.customer import Customer
from ingenico.connect.sdk.domain.payment.definitions.customer_device import (
    CustomerDevice,
)
from ingenico.connect.sdk.domain.payment.definitions.line_item import LineItem
from ingenico.connect.sdk.domain.payment.definitions.line_item_invoice_data import (
    LineItemInvoiceData,
)
from ingenico.connect.sdk.domain.payment.definitions.order import Order
from ingenico.connect.sdk.domain.payment.definitions.order_invoice_data import (
    OrderInvoiceData,
)
from ingenico.connect.sdk.domain.payment.definitions.order_references import (
    OrderReferences,
)
from ingenico.connect.sdk.domain.payment.definitions.personal_information import (
    PersonalInformation,
)
from ingenico.connect.sdk.domain.payment.definitions.personal_name import PersonalName
from ingenico.connect.sdk.domain.payment.definitions.redirection_data import (
    RedirectionData,
)
from ingenico.connect.sdk.domain.payment.definitions.shipping import Shipping
from ingenico.connect.sdk.domain.payment.definitions.shopping_cart import ShoppingCart
from ingenico.connect.sdk.domain.payment.definitions.three_d_secure import ThreeDSecure


from ingenico.connect.sdk.domain.definitions.bank_account_iban import BankAccountIban
from ingenico.connect.sdk.domain.definitions.contact_details_base import (
    ContactDetailsBase,
)
from ingenico.connect.sdk.domain.payout.create_payout_request import CreatePayoutRequest
from ingenico.connect.sdk.domain.payout.definitions.bank_transfer_payout_method_specific_input import (
    BankTransferPayoutMethodSpecificInput,
)
from ingenico.connect.sdk.domain.payout.definitions.payout_customer import (
    PayoutCustomer,
)
from ingenico.connect.sdk.domain.payout.definitions.payout_details import PayoutDetails
from ingenico.connect.sdk.domain.payout.definitions.payout_references import (
    PayoutReferences,
)
from ingenico.connect.sdk.declined_payout_exception import DeclinedPayoutException
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


CLIENT = Factory.create_client_from_file(
    "./conf",
    "3cdf571bae3bdec5",
    "qCCfYEWiuSVM7orLbgcVpItFk+CBnxQ1rWV1ZnGPiCY=",
)
MERCHANT_ID = "1196"

with CLIENT as c:
    # CREATE PAYMENT
    card = Card()
    card.card_number = "4567350000427977"
    card.cardholder_name = "MMT de Wijk"
    card.cvv = "456"
    card.expiry_date = "1225"

    authentication_amount = AmountOfMoney()
    authentication_amount.amount = 2980
    authentication_amount.currency_code = "EUR"

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
    card_payment_method_specific_input.payment_product_id = 1
    card_payment_method_specific_input.three_d_secure = three_d_secure
    card_payment_method_specific_input.transaction_channel = "ECOMMERCE"

    body = CreatePaymentRequest()
    body.card_payment_method_specific_input = card_payment_method_specific_input
    body.order = get_order("EUR")

    try:
        create_payment_response = CLIENT.merchant(MERCHANT_ID).payments().create(body)
        pass
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
        CLIENT.merchant("1196")
        .payments()
        .tokenize(create_payment_response.payment.id, body)
    )
    print(f"{token_response.is_new_token=}")

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
