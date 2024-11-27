"""This module contains a class and functions relating to creating an invoice in SAP."""


class InvoiceCreator:
    """
    A class used to create invoices in SAP.

    Attributes:
    ----------
    session : object
        The session object to interact with SAP.
    """

    def __init__(self, session):
        """
        Initialize the InvoiceCreator with a session object.

        Parameters:
        ----------
        session : object
            The session object to interact with SAP.
        """
        self.session = session

    def open_business_partner(self, business_partner_id: str, content_type: str, base_system_id: str):
        """
        Open a business partner in SAP.

        Parameters:
        ----------
        business_partner_id : str
            ID of the business partner.
        content_type : str
            Content type.
        base_system_id : str
            Base system ID.
        """
        self.session.findById('wnd[0]/usr/ctxtLV_BP_IN').text = business_partner_id
        self.session.findById('wnd[0]/usr/ctxtP_IHS_IN').text = content_type
        self.session.findById('wnd[0]/usr/txtP_NBS_IN').text = base_system_id
        self.session.findById('wnd[0]/tbar[1]/btn[8]').press()

    def _create_invoice_row(
            self, row_index: int,
            amount: str,
            start_date: str,
            end_date: str,
            main_transaction_id: str,
            sub_transaction_id: str,
            name_person: str,
            payment_recipient_identifier: str,
            service_recipient_identifier: str,
            business_partner_id: str
            ) -> None:
        """
        Create a row in the invoice.

        Parameters:
        ----------
        row_index : int
            Index of the row in the table.
        amount : str
            Amount for the transaction.
        start_date : str
            Start date of the transaction period.
        end_date : str
            End date of the transaction period.
        main_transaction_id : str
            ID of the main transaction.
        sub_transaction_id : str
            ID of the sub-transaction.
        name_person : str
            Name of the person.
        payment_recipient_identifier : str
            Identifier of the payment recipient.
        service_recipient_identifier : str
            Identifier of the service recipient.
        business_partner_id : str
            ID of the business partner.
        """
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-BELOEB[4,{row_index}]").text = amount
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-LINJE_PERIODE_FRA[6,{row_index}]").text = start_date
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-LINJE_PERIODE_TIL[7,{row_index}]").text = end_date
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-HOVED_TRANS[9,{row_index}]").text = main_transaction_id
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-DEL_TRANS[10,{row_index}]").text = sub_transaction_id
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-FORFALDSDATO[12,{row_index}]").text = start_date
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-STIFTELSESDATO[13,{row_index}]").text = start_date
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-POSTERINGSTEKST[17,{row_index}]").text = name_person
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-BETALINGS_MODT_KODE[18,{row_index}]").text = payment_recipient_identifier
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-BETALINGS_MODT[19,{row_index}]").text = business_partner_id
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-YDELSES_MODT_KODE[20,{row_index}]").text = service_recipient_identifier
        self.session.findById(f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-YDELSES_MODT[21,{row_index}]").text = business_partner_id
        self.session.findById("wnd[0]").sendVKey(0)

    def create_invoice(
            self,
            business_partner_id: str,
            content_type: str,
            base_system_id: str,
            name_person: str,
            start_date: str,
            end_date: str,
            main_transaction_id: str,
            main_transaction_amount: str,
            sub_transaction_id: str,
            sub_transaction_fee_adm_id: str,
            sub_transaction_fee_adm_amount: str,
            sub_transaction_fee_inst_id: str,
            sub_transaction_fee_inst_amount: str,
            payment_recipient_identifier: str,
            service_recipient_identifier: str
            ) -> None:
        """
        Create an invoice with multiple rows.

        Parameters:
        ----------
        business_partner_id : str
            ID of the business partner.
        content_type : str
            Content type.
        base_system_id : str
            Base system ID.
        name_person : str
            Name of the person.
        start_date : str
            Start date of the transaction period.
        end_date : str
            End date of the transaction period.
        main_transaction_id : str
            ID of the main transaction.
        main_transaction_amount : str
            Amount for the main transaction.
        sub_transaction_id : str
            ID of the sub-transaction.
        sub_transaction_fee_adm_id : str
            ID of the sub-transaction for administration fee.
        sub_transaction_fee_adm_amount : str
            Amount for the sub-transaction administration fee.
        sub_transaction_fee_inst_id : str
            ID of the sub-transaction for institution fee.
        sub_transaction_fee_inst_amount : str
            Amount for the sub-transaction institution fee.
        payment_recipient_identifier : str
            Identifier of the payment recipient.
        service_recipient_identifier : str
            Identifier of the service recipient.
        """
        self.open_business_partner(business_partner_id, content_type, base_system_id)
        self.session.findById("wnd[0]/usr/ctxtZDKD0312MODTAGKRAV_UDVEKSLE-FORFALDSDATO").text = start_date

        # Main transaction row
        self._create_invoice_row(
            0,
            main_transaction_amount,
            start_date,
            end_date,
            main_transaction_id,
            sub_transaction_id,
            name_person,
            payment_recipient_identifier,
            service_recipient_identifier,
            business_partner_id
            )

        # Insert new line
        self.session.findById("wnd[0]/usr/btnINDSAETTXTBTN").press()

        # Sub transaction administration fee row
        self._create_invoice_row(
            1,
            sub_transaction_fee_adm_amount,
            start_date,
            end_date,
            main_transaction_id,
            sub_transaction_fee_adm_id,
            name_person,
            payment_recipient_identifier,
            service_recipient_identifier,
            business_partner_id
            )

        # Insert new line
        self.session.findById("wnd[0]/usr/btnINDSAETTXTBTN").press()

        # Sub transaction institution fee row
        self._create_invoice_row(
            2,
            sub_transaction_fee_inst_amount,
            start_date,
            end_date,
            main_transaction_id,
            sub_transaction_fee_inst_id,
            name_person,
            payment_recipient_identifier,
            service_recipient_identifier,
            business_partner_id
            )
