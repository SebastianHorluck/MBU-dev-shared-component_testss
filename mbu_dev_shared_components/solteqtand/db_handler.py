"""
This module defines the SolteqTandDatabase class, which provides
an interface to interact with the Solteq Tand database.
"""
import pyodbc


class SolteqTandDatabase:
    """Handles database operations related to the Solteq Tand system."""

    def __init__(self, conn_str: str, ssn: str):
        """
        Initializes the SolteqTandDatabase instance.

        Args:
            conn_str (str): Connection string to the Solteq Tand database.
            ssn (str): Social Security Number (CPR) for identifying the patient.
        """
        self.connection_string = conn_str
        self.ssn = ssn

    def _execute_query(self, query: str, params: tuple):
        """
        Executes a query with the provided parameters and returns the result.

        Args:
            query (str): SQL query to execute.
            params (tuple): Parameters to include in the SQL query.

        Returns:
            list: A list of rows returned by the query, where each row is a dictionary.
        """
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = {'data': dict(zip(columns, row)) for row in rows}
        return result

    def check_if_document_exists(self, filename: str, documenttype: str = None, form_id: str = None):
        """
        Checks if a document with the given filename exists for the specified patient,
        optionally filtering by document type and form ID.

        Args:
            filename (str): Name of the file to search for.
            documenttype (str, optional): Type of the document to filter by.
            form_id (str, optional): Form ID to filter by.

        Returns:
            list: A list of matching document records.
        """
        query = """
            WITH LatestActiveDocuments AS (
                SELECT
                    ds.DocumentId,
                    ds.entityId,
                    ds.OriginalFilename,
                    ds.UniqueFilename,
                    ds.DocumentType,
                    ds.DocumentDescription,
                    ds.Priviledged,
                    ds.ContentType,
                    dss.Document_HistoryId,
                    dss.DocumentStoreStatusId,
                    dss.SentToNemSMS,
                    dss.Documented AS [DocumentCreatedDate],
                    dss.Decided AS [DocumentLastEditedDate],
                    ROW_NUMBER() OVER (
                        PARTITION BY ds.DocumentId
                        ORDER BY dss.Document_HistoryId DESC
                    ) AS rn
                FROM [tmtdata_prod].[dbo].[DocumentStore] ds
                JOIN DocumentStoreStatus dss ON ds.DocumentId = dss.DocumentId
            )
            SELECT
                ds.DocumentId,
                ds.entityId,
                ds.OriginalFilename,
                ds.UniqueFilename,
                ds.DocumentType,
                ds.DocumentDescription,
                ds.DocumentCreatedDate,
                ds.DocumentLastEditedDate,
                ds.SentToNemSMS,
                p.cpr
            FROM [tmtdata_prod].[dbo].[PATIENT] p
            JOIN LatestActiveDocuments ds ON ds.entityId = p.patientId
            WHERE ds.rn = 1
                AND ds.DocumentStoreStatusId = 1
                AND p.cpr = ?
                AND ds.OriginalFilename = ?
        """

        params = [self.ssn, filename]

        if documenttype:
            query += " AND ds.DocumentType = ?"
            params.append(documenttype)

        if form_id:
            query += " AND ds.DocumentDescription = ?"
            params.append(form_id)

        params = tuple(params)

        return self._execute_query(query, params)

    def check_extern_dentist(self):
        """
        Checks if the patient is associated with an external dentist.
        (This method is a placeholder and needs to be implemented based on specific requirements.)
        """
        query = """
            SELECT	[patientId]
                    ,[cpr]
                    ,[privateClinicId]
                    ,[c.contractorId]
                    ,[c.isPrimary]
                    ,[c.name]
                    ,[c.streetAddress]
                    ,[c.zip]
                    ,[c.phoneNumber]
            FROM	[tmtdata_prod].[dbo].[PATIENT] p
            JOIN	[CLINIC] c on c.clinicId = p.privateClinicId
            WHERE	cpr = ?
        """
        return self._execute_query(query, (self.ssn))

    def check_if_booking_exists(self):
        """
        Checks if any booking exists for the specified patient.

        Returns:
            list: A list of booking records for the patient.
        """
        query = """
            SELECT  b.StartTime,
                    b.EndTime,
                    b.PatientNotified,
                    b.PatientNotifiedVia,
                    b.BookingText,
                    b.Warnings,
                    b.CreatedDateTime,
                    b.LastModifiedDateTime,
                    bt.Description,
                    bt.PrinterFriendlyText
            FROM [tmtdata_prod].[dbo].[BOOKING] b
            JOIN PATIENT p on p.patientId = b.patientId
            JOIN BOOKINGTYPE bt on bt.BookingTypeID = b.BookingTypeID
            WHERE p.cpr = ?
        """
        return self._execute_query(query, (self.ssn,))

    def check_if_event_exists(self, event_name: str, event_message: str):
        """
        Checks if a specific event exists for the patient based on the event name and message.

        Args:
            event_name (str): The name of the event (clinic name).
            event_message (str): The event message or state.

        Returns:
            list: A list of matching event records for the patient.
        """
        query = """
            SELECT  e.[eventId],
                    e.[type],
                    e.[currentStateText],
                    e.[currentStateDate],
                    e.[timestamp],
                    e.[clinicId],
                    c.name,
                    e.[entityId],
                    e.[eventTriggerDate],
                    p.cpr
            FROM [EVENT] e
            JOIN [PATIENT] p ON p.patientId = e.entityId
            JOIN [CLINIC] c ON c.clinicId = e.clinicId
            WHERE p.cpr = ?
            AND c.name = ?
            AND e.currentStateText = ?
        """
        return self._execute_query(query, (self.ssn, event_name, event_message))

    def get_primary_dental_clinic(self):
        """
        Fetches the primary dental clinic details for the specified patient.

        Returns:
            dict: A dictionary containing patient and clinic details.
        """
        query = """
            SELECT  p.cpr,
                    p.patientId,
                    p.firstName,
                    p.lastName,
                    p.preferredDentalClinicId,
                    p.isPreferredDentalClinicLocked,
                    c.name AS preferredDentalClinicName
            FROM [tmtdata_prod].[dbo].[PATIENT] p
            JOIN [CLINIC] c ON c.clinicId = p.preferredDentalClinicId
            WHERE p.cpr = ?
        """
        return self._execute_query(query, (self.ssn,))

    def get_journal_notes(self, note_message: str = None):
        """
        Fetches the journal notes for the specified patient.

        Returns:
            dict: A dictionary containing the journal notes.
        """
        query = """
            SELECT
                dn.Beskrivelse,
                ds.Dokumenteret,
                ds.Besluttet,
                ds.Art,
                ds.EjerArt
            FROM
                [tmtdata_prod].[dbo].[Forloeb] f
            JOIN
                ForloebSymbolisering fs ON fs.ForloebID = f.ForloebID
            JOIN
                DiagnoseStatus ds ON ds.GEpjID = fs.DiagnoseID
            JOIN
                DiagnostikNotat dn ON dn.KontekstID = ds.KontekstID
            JOIN
                PATIENT p ON p.patientId = f.patientId
            WHERE
                p.cpr = ?
        """
        params = [self.ssn]

        if note_message:
            query += " AND dn.Beskrivelse = ?"
            params.append(note_message)

        query += " ORDER BY ds.Dokumenteret DESC"
        params = tuple(params)

        return self._execute_query(query, params)
