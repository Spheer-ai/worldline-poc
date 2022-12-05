from ingenico.connect.sdk.factory import Factory
from ingenico.connect.sdk.domain.definitions.address import Address
from ingenico.connect.sdk.domain.definitions.amount_of_money import AmountOfMoney
from ingenico.connect.sdk.domain.hostedcheckout.create_hosted_checkout_request import (
    CreateHostedCheckoutRequest,
)
from ingenico.connect.sdk.domain.hostedcheckout.definitions.hosted_checkout_specific_input import (
    HostedCheckoutSpecificInput,
)
from ingenico.connect.sdk.domain.payment.definitions.customer import Customer
from ingenico.connect.sdk.domain.payment.definitions.order import Order
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

CLIENT = Factory.create_client_from_file(
    "./conf",
    "3cdf571bae3bdec5",
    "qCCfYEWiuSVM7orLbgcVpItFk+CBnxQ1rWV1ZnGPiCY=",
)
MERCHANT_ID = "1196"
AMOUNT = 2200

with CLIENT as c:
    hosted_checkout_specific_input = HostedCheckoutSpecificInput()
    hosted_checkout_specific_input.locale = "nl_NL"
    hosted_checkout_specific_input.variant = "101"

    amount_of_money = AmountOfMoney()
    amount_of_money.amount = AMOUNT
    amount_of_money.currency_code = "USD"

    billing_address = Address()
    billing_address.country_code = "NL"

    customer = Customer()
    customer.billing_address = billing_address
    customer.merchant_customer_id = "1234"

    order = Order()
    order.amount_of_money = amount_of_money
    order.customer = customer

    body = CreateHostedCheckoutRequest()
    body.hosted_checkout_specific_input = hosted_checkout_specific_input
    body.order = order

    # Create the hosted checkout.
    create_hosted_checkout_response = (
        c.merchant(MERCHANT_ID).hostedcheckouts().create(body)
    )

    # Link for the user to pay.
    # "payment" is a special shared domain of Worldline.
    full_redirect_url = (
        f"https://payment.{create_hosted_checkout_response.partial_redirect_url}"
    )
    print(f"{full_redirect_url=}")

    # Get hosted checkout status. (Has the user already paid?)
    hosted_checkout_status = (
        c.merchant(MERCHANT_ID)
        .hostedcheckouts()
        .get(create_hosted_checkout_response.hosted_checkout_id)
    )
    # If the user has paid, statusses will be:
    #   "PAYMENT_CREATED",
    #   "SUCCESFUL"
    #   and "PENDING_APPROVAL".
    if (
        hosted_checkout_status.status != "PAYMENT_CREATED"
        or hosted_checkout_status.created_payment_output.payment_status_category
        != "SUCCESSFUL"
        or hosted_checkout_status.created_payment_output.payment.status
        != "PENDING_APPROVAL"
    ):
        exit()

    # GET TOKEN
    from ingenico.connect.sdk.domain.payment.tokenize_payment_request import (
        TokenizePaymentRequest,
    )

    body = TokenizePaymentRequest()
    body.alias = "Some alias"

    token_response = (
        CLIENT.merchant(MERCHANT_ID)
        .payments()
        .tokenize(hosted_checkout_status.created_payment_output.payment.id, body)
    )

    # APPROVE PAYMENT
    direct_debit_payment_method_specific_input = (
        ApprovePaymentNonSepaDirectDebitPaymentMethodSpecificInput()
    )
    direct_debit_payment_method_specific_input.date_collect = "20221205"
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

    approve_payment_response = (
        CLIENT.merchant(MERCHANT_ID).payments()
        # .approve(token_response.original_payment_id, body)
        .approve(hosted_checkout_status.created_payment_output.payment.id, body)
    )

    # CREATE PAYOUT
    from ingenico.connect.sdk.domain.definitions.address import Address
    from ingenico.connect.sdk.domain.definitions.amount_of_money import AmountOfMoney
    from ingenico.connect.sdk.domain.definitions.bank_account_iban import (
        BankAccountIban,
    )
    from ingenico.connect.sdk.domain.definitions.company_information import (
        CompanyInformation,
    )
    from ingenico.connect.sdk.domain.definitions.contact_details_base import (
        ContactDetailsBase,
    )
    from ingenico.connect.sdk.domain.payment.definitions.personal_name import (
        PersonalName,
    )
    from ingenico.connect.sdk.domain.payout.create_payout_request import (
        CreatePayoutRequest,
    )
    from ingenico.connect.sdk.domain.payout.definitions.bank_transfer_payout_method_specific_input import (
        BankTransferPayoutMethodSpecificInput,
    )
    from ingenico.connect.sdk.domain.payout.definitions.payout_customer import (
        PayoutCustomer,
    )
    from ingenico.connect.sdk.domain.payout.definitions.payout_details import (
        PayoutDetails,
    )
    from ingenico.connect.sdk.domain.payout.definitions.payout_references import (
        PayoutReferences,
    )

    bank_account_iban = BankAccountIban()
    bank_account_iban.account_holder_name = "Wile E. Coyote"
    bank_account_iban.iban = "IT60X0542811101000000123456"

    bank_transfer_payout_method_specific_input = BankTransferPayoutMethodSpecificInput()
    bank_transfer_payout_method_specific_input.bank_account_iban = bank_account_iban
    bank_transfer_payout_method_specific_input.payout_date = "20221212"
    bank_transfer_payout_method_specific_input.payout_text = "Payout Acme"
    bank_transfer_payout_method_specific_input.swift_code = "swift"

    amount_of_money = AmountOfMoney()
    amount_of_money.amount = AMOUNT
    amount_of_money.currency_code = "USD"

    address = Address()
    address.city = "Burbank"
    address.country_code = "US"
    address.house_number = "411"
    address.state = "California"
    address.street = "N Hollywood Way"
    address.zip = "91505"

    company_information = CompanyInformation()
    company_information.name = "Acme Labs"

    contact_details = ContactDetailsBase()
    contact_details.email_address = "wile.e.coyote@acmelabs.com"

    name = PersonalName()
    name.first_name = "Wile"
    name.surname = "Coyote"
    name.surname_prefix = "E."
    name.title = "Mr."

    customer = PayoutCustomer()
    customer.address = address
    customer.company_information = company_information
    customer.contact_details = contact_details
    customer.name = name

    references = PayoutReferences()
    references.merchant_reference = "AcmeOrder001"

    payout_details = PayoutDetails()
    payout_details.amount_of_money = amount_of_money
    payout_details.customer = customer
    payout_details.references = references

    body = CreatePayoutRequest()
    body.bank_transfer_payout_method_specific_input = (
        bank_transfer_payout_method_specific_input
    )
    body.payout_details = payout_details

    response = c.merchant(MERCHANT_ID).payouts().create(body)
