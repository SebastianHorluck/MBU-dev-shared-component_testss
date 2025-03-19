"""
This module defines the SolteqTandDatabase class, which provides
an interface to interact with the Solteq Tand database.
"""
import pyodbc


class SolteqTandDatabase:
    """Handles database operations related to the Solteq Tand system."""

    def __init__(self, conn_str: str):
        """
        Initializes the SolteqTandDatabase instance.

        Args:
            conn_str (str): Connection string to the Solteq Tand database.
        """
        self.connection_string = conn_str

    def _execute_query(self, query: str, params: tuple):
        """
        Executes a SQL query with parameters and returns the results as a list of dictionaries.

        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters for the SQL query.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row from the query result.
        """
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        result = [dict(zip(columns, row)) for row in rows]

        return result

    def _construct_sql_statement(self, base_query, filters=None, or_filters=None, order_by=None, order_direction="ASC"):  # noqa
        """
        Dynamically constructs a SQL query by applying filters.

        Args:
            base_query (str): The base SQL query with a WHERE clause.
            filters (dict, optional): Key-value pairs for AND conditions.
            or_filters (list of dict, optional): List of OR condition dictionaries.

        Returns:
            tuple: The final SQL query and the corresponding parameters.
        """
        params = []
        where_clauses = []

        # Handling AND filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, tuple) and len(value) == 2:  # BETWEEN filtering
                    where_clauses.append(f"{key} BETWEEN ? AND ?")
                    params.extend(value)
                elif isinstance(value, list):  # IN filtering
                    placeholders = ", ".join("?" for _ in value)
                    where_clauses.append(f"{key} IN ({placeholders})")
                    params.extend(value)
                elif isinstance(value, str) and "%" in value:  # LIKE filtering
                    where_clauses.append(f"{key} LIKE ?")
                    params.append(value)
                else:  # Default equality filtering
                    where_clauses.append(f"{key} = ?")
                    params.append(value)

        # Handling OR filters
        or_clauses = []
        if or_filters:
            for or_filter in or_filters:
                sub_clauses = []
                sub_params = []
                for key, value in or_filter.items():
                    if isinstance(value, list):
                        placeholders = ", ".join("?" for _ in value)
                        sub_clauses.append(f"{key} IN ({placeholders})")
                        sub_params.extend(value)
                    elif isinstance(value, str) and "%" in value:
                        sub_clauses.append(f"{key} LIKE ?")
                        sub_params.append(value)
                    else:
                        sub_clauses.append(f"{key} = ?")
                        sub_params.append(value)

                if sub_clauses:
                    or_clauses.append(f"({' OR '.join(sub_clauses)})")
                    params.extend(sub_params)

        # Adding AND filters
        if where_clauses:
            base_query += " AND " + " AND ".join(where_clauses)

        # Adding OR filters
        if or_clauses:
            base_query += " AND (" + " OR ".join(or_clauses) + ")"

        # Adding ORDER BY clause
        if order_by:
            order_direction = "ASC" if order_direction.upper() not in ["ASC", "DESC"] else order_direction.upper()
            base_query += f" ORDER BY {order_by} {order_direction}"

        return base_query, params

    def get_list_of_documents(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves a list of documents based on the specified filters.

        Args:
            filters (dict, optional): Filtering criteria for document retrieval.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of document records matching the criteria.
        """
        base_query = """
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
                ds.rn,
                ds.DocumentStoreStatusId,
                p.cpr
            FROM [tmtdata_prod].[dbo].[PATIENT] p
            JOIN LatestActiveDocuments ds ON ds.entityId = p.patientId
            WHERE 1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)

    def get_list_of_extern_dentist(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves a list of external dentists associated with the patient.

        Args:
            filters (dict, optional): Filtering criteria for external dentists.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of external dentist records.
        """
        base_query = """
            SELECT	p.[patientId]
                    ,p.[cpr]
                    ,p.[privateClinicId]
                    ,c.[contractorId]
                    ,c.[isPrimary]
                    ,c.[name]
                    ,c.[streetAddress]
                    ,c.[zip]
                    ,c.[phoneNumber]
            FROM	[tmtdata_prod].[dbo].[PATIENT] p
            JOIN	[CLINIC] c on c.clinicId = p.privateClinicId
            WHERE	1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)

    def get_list_of_bookings(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves a list of bookings for the specified patient.

        Args:
            filters (dict, optional): Filtering criteria for booking retrieval.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of booking records.
        """
        base_query = """
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
            WHERE	1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)

    def get_list_of_events(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves a list of events related to the patient.

        Args:
            filters (dict, optional): Filtering criteria for event retrieval.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of event records matching the criteria.
        """
        base_query = """
            SELECT  e.[eventId],
                    e.[type],
                    e.[currentStateText],
                    e.[currentStateDate],
                    e.[timestamp],
                    e.[clinicId],
                    c.name,
                    e.[entityId],
                    e.[eventTriggerDate],
                    p.cpr,
                    e.archived
            FROM [EVENT] e
            JOIN [PATIENT] p ON p.patientId = e.entityId
            JOIN [CLINIC] c ON c.clinicId = e.clinicId
            WHERE	1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)

    def get_list_of_primary_dental_clinics(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves details of the primary dental clinics associated with the patient.

        Args:
            filters (dict, optional): Filtering criteria for clinic retrieval.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of primary dental clinic details.
        """
        base_query = """
            SELECT  p.cpr,
                    p.patientId,
                    p.firstName,
                    p.lastName,
                    p.preferredDentalClinicId,
                    p.isPreferredDentalClinicLocked,
                    c.name AS preferredDentalClinicName
            FROM [tmtdata_prod].[dbo].[PATIENT] p
            JOIN [CLINIC] c ON c.clinicId = p.preferredDentalClinicId
            WHERE	1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)

    def get_list_of_journal_notes(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves journal notes associated with the specified patient.

        Args:
            filters (dict, optional): Filtering criteria for journal note retrieval.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of journal notes matching the criteria.
        """
        base_query = """
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
            WHERE	1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)

    def get_list_of_clinics(self, filters=None, or_filters=None, order_by=None, order_direction="ASC"):
        """
        Retrieves a list of clinics.

        Args:
            filters (dict, optional): Filtering criteria for external dentists.
            or_filters (list of dict, optional): OR conditions for filtering.

        Returns:
            list: A list of external dentist records.
        """
        base_query = """
            SELECT
                clinicId
                ,name
                ,type
                ,streetAddress
                ,countyCode
                ,zip
                ,phoneNumber
                ,contractorId
            FROM
                [tmtdata_prod].[dbo].[CLINIC]
            WHERE	1=1
        """
        final_query, params = self._construct_sql_statement(base_query, filters, or_filters, order_by, order_direction)
        return self._execute_query(final_query, params)
