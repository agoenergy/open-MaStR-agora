from datetime import date, datetime
from dateutil.parser import parse
import dateutil
import os
import shutil
import sqlite3
import open_mastr.settings as settings
from warnings import warn

# import xml dependencies
from os.path import expanduser
from open_mastr.xml_download.utils_download_bulk import download_xml_Mastr
from open_mastr.xml_download.utils_write_sqlite import convert_mastr_xml_to_sqlite

# import soap_API dependencies
from open_mastr.soap_api.mirror import MaStRMirror

# import initialize_database dependencies
from open_mastr.utils.helpers import db_engine
import open_mastr.orm as orm
from sqlalchemy.schema import CreateSchema


class Mastr:
    """
    Mirror the MaStR database and keep it up-to-date.

    A sqlite database is used to mirror the MaStR database. It can be filled with
    data either from the MaStR-bulk download or from the MaStR-API.

    .. code-block:: python

       from open_mastr import Mastr

       db = Mastr()
       db.download()
    """

    def __init__(self, empty_schema=False) -> None:

        # Define the paths for the zipped xml download and the sql databases
        self._xml_folder_path = os.path.join(
            expanduser("~"), ".open-MaStR", "data", "xml_download"
        )
        self._sqlite_folder_path = os.path.join(
            expanduser("~"), ".open-MaStR", "data", "sqlite"
        )
        os.makedirs(self._xml_folder_path, exist_ok=True)
        os.makedirs(self._sqlite_folder_path, exist_ok=True)

        # setup database engine and connection
        self.DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite")
        self._engine = db_engine()
        SQLITE_DATABASE_PATH = settings.SQLITE_DATABASE_PATH
        self._sql_connection = sqlite3.connect(SQLITE_DATABASE_PATH)

        # Initialize database structure
        self.empty_schema = empty_schema
        self._initialize_database(empty_schema)

    def download(
        self,
        method="bulk",
        technology=None,
        bulk_date_string="today",
        bulk_cleansing=True,
        api_processes=None,
        api_limit=None,
        api_date=None,
        api_chunksize=None,
        api_data_types=None,
        api_location_types=None,
        initialize_db=None,
    ) -> None:
        """
        Download the MaStR either via the bulk download or via the MaStR API and write it to a
        sqlite database.

        Parameters
        ----------

        method: str
            Either "API" or "bulk". Determines whether the data is downloaded via the
            zipped bulk download or via the MaStR API. The latter requires an account
            from marktstammdatenregister.de,
            (see :ref:`Configuration <Configuration>`).
        technology: str or list or None
            Determines which technologies are written to the database. If None, all technologies are
            used. If it is a list, possible entries are "wind", "solar", "biomass", "hydro", "gsgk",
            "combustion", "nuclear", "gas", "storage", "electricity_consumer", "location", "market",
            "grid", "balancing_area" or "permit". If only one technology is of interest, this can be
            given as a string.
        bulk_date_string: str
            Either "today" if the newest data dump should be downloaded from the MaStR website. If
            an already downloaded dump should be used, state the date of the download in the format
            "yyyymmdd".
        bulk_cleansing: bool
            If True, data cleansing is applied after the download (which is recommended)
        api_processes: int or None or "max"
            Number of parallel processes used to download additional data.
            Defaults to `None`. If set to "max", the maximum number of possible processes
            is used.
        api_limit: int or None
            Limit number of units that data is download for. Defaults to `None` which refers
            to query data for existing data requests, for example created by
            :meth:`~.create_additional_data_requests`. Note: There is a limited number of
            requests you are allowed to have per day, so setting api_limit to a value is
            recommended.
        api_date: None or :class:`datetime.datetime` or str
            Specify backfill date from which on data is retrieved

            Only data with modification time stamp greater that `date` is retrieved.

            * `datetime.datetime(2020, 11, 27)`: Retrieve data which is is newer than this
            time stamp
            * 'latest': Retrieve data which is newer than the newest data already in the table.
              .. warning::

                 Don't use 'latest' in combination with `limit`. This might lead to
                 unexpected results.
            * `None`: Complete backfill

            Defaults to `None`.
        api_chunksize: int or None
            Data is downloaded and inserted into the database in chunks of `chunksize`.
            Defaults to 1000.
        api_data_types: list or None
            Select type of additional data that should be retrieved. Choose from
            "unit_data", "eeg_data", "kwk_data", "permit_data".
        api_location_types: list or None
            Select type of location that should be retrieved. Choose from
            "location_elec_generation", "location_elec_consumption", "location_gas_generation",
            "location_gas_consumption".
        """

        self._validate_parameter_format_for_download_method(
            method=method,
            technology=technology,
            bulk_date_string=bulk_date_string,
            bulk_cleansing=bulk_cleansing,
            api_processes=api_processes,
            api_limit=api_limit,
            api_date=api_date,
            api_chunksize=api_chunksize,
            api_data_types=api_data_types,
            api_location_types=api_location_types,
        )

        if method == "bulk":

            # Find the name of the zipped xml folder
            if bulk_date_string == "today":
                bulk_download_date = date.today().strftime("%Y%m%d")
            else:
                # proper format already tested in
                # self._validate_parameter_format_for_download_method
                bulk_download_date = parse(bulk_date_string).strftime("%Y%m%d")

            _zipped_xml_file_path = os.path.join(
                self._xml_folder_path,
                f"Gesamtdatenexport_{bulk_download_date}.zip",
            )

            if os.path.exists(_zipped_xml_file_path):
                print("MaStR already downloaded.")
            else:
                if bulk_date_string != "today":
                    raise Exception(
                        "There exists no file for given date. MaStR can only be downloaded "
                        "from the website if today's date is given."
                    )
                shutil.rmtree(self._xml_folder_path, ignore_errors=True)
                os.makedirs(self._xml_folder_path, exist_ok=True)
                download_xml_Mastr(_zipped_xml_file_path)
                print(f"MaStR was successfully downloaded to {self._xml_folder_path}.")

            # Map technology input to the .xml file names like 'einheitensolar'
            bulk_include_tables = self._technology_to_include_tables(
                technology=technology
            )

            convert_mastr_xml_to_sqlite(
                con=self._sql_connection,
                engine=self._engine,
                zipped_xml_file_path=_zipped_xml_file_path,
                include_tables=bulk_include_tables,
                bulk_cleansing=bulk_cleansing,
                bulk_download_date=bulk_download_date,
            )
            print("Bulk download and data cleansing was successful.")

        if method == "API":
            print(
                f"Downloading with soap_API.\n\n   -- Settings --  \nunits after date: "
                f"{api_date}\nunit download limit per technology: "
                f"{api_limit}\nparallel_processes: {api_processes}\nchunksize: "
                f"{api_chunksize}\ntechnologies: {technology}\ndata_types: "
                f"{api_data_types}\nlocation_types: {api_location_types}"
            )
            mastr_mirror = MaStRMirror(
                empty_schema=False,
                parallel_processes=api_processes,
                DB_ENGINE=self.DB_ENGINE,
                restore_dump=None,
            )
            # Download basic unit data
            mastr_mirror.backfill_basic(technology, limit=api_limit, date=api_date)

            # Download additional unit data
            for tech in technology:
                # mastr_mirror.create_additional_data_requests(tech)
                for data_type in api_data_types:
                    mastr_mirror.retrieve_additional_data(
                        tech, data_type, chunksize=api_chunksize, limit=api_limit
                    )

            # Download basic location data
            mastr_mirror.backfill_locations_basic(limit=api_limit, date="latest")

            # Download extended location data
            if api_location_types:
                for location_type in api_location_types:
                    mastr_mirror.retrieve_additional_location_data(
                        location_type, limit=api_limit
                    )

    def _initialize_database(self, empty_schema) -> None:
        engine = self._engine
        with engine.connect().execution_options(autocommit=True) as con:
            if empty_schema:
                con.execute(
                    f"DROP SCHEMA IF EXISTS {orm.Base.metadata.schema} CASCADE;"
                )
            # con.dialect.has_schema(con, {orm.Base.metadata.schema})
            # con.execute('CREATE SCHEMA IF NOT EXISTS (?);', (orm.Base.metadata.schema))
            if self.DB_ENGINE == "docker":
                engine.execute(CreateSchema(orm.Base.metadata.schema))
        orm.Base.metadata.create_all(engine)

    def _validate_parameter_format_for_download_method(
        self,
        method,
        technology,
        bulk_date_string,
        bulk_cleansing,
        api_processes,
        api_limit,
        api_date,
        api_chunksize,
        api_data_types,
        api_location_types,
    ) -> None:
        # method parameter

        if method != "bulk" and method != "API":
            raise ValueError("parameter method has to be either 'bulk' or 'API'.")

        if method == "API":
            if any(
                parameter is not None
                for parameter in [bulk_date_string, bulk_cleansing]
            ):
                warn(
                    "For method = 'API', bulk download related parameters (with prefix bulk_) are ignored."
                )

        if method == "bulk":
            if any(
                parameter is not None
                for parameter in [
                    api_processes,
                    api_limit,
                    api_date,
                    api_chunksize,
                    api_data_types,
                    api_location_types,
                ]
            ):
                warn(
                    "For method = 'bulk', API related parameters (with prefix api_) are ignored."
                )

        if not isinstance(technology, (str, list)) and technology is not None:
            raise ValueError("parameter technology has to be a string, list, or None")
        if isinstance(technology, str):
            technology = [technology]
        if isinstance(technology, list):
            bulk_technologies = [
                "wind",
                "solar",
                "biomass",
                "hydro",
                "gsgk",
                "combustion",
                "nuclear",
                "gas",
                "storage",
                "electricity_consumer",
                "location",
                "market",
                "grid",
                "balancing_area",
                "permit",
            ]
            for value in technology:
                if value not in bulk_technologies:
                    raise ValueError(
                        'Allowed values for parameter technology are "wind", "solar",'
                        'biomass", "hydro", "gsgk", "combustion", "nuclear", "gas", '
                        '"storage", "electricity_consumer", "location", "market", '
                        '"grid", "balancing_area" or "permit"'
                    )

        if bulk_date_string != "today":
            try:
                temp_date = parse(bulk_date_string)
            except (dateutil.parser._parser.ParserError, TypeError):
                raise ValueError(
                    "parameter bulk_date_string has to be a proper date in the format yyyymmdd"
                    "or 'today'."
                )

        if type(bulk_cleansing) != bool:
            raise ValueError("parameter bulk_cleansing has to be boolean")

        if (
            api_processes != "max"
            and not isinstance(api_processes, int)
            and api_processes is not None
        ):
            raise ValueError(
                "parameter api_processes has to be 'max' or an integer or 'None'"
            )

        if not isinstance(api_limit, int) and api_limit is not None:
            raise ValueError("parameter api_limit has to be an integer or 'None'.")

        if (
            not isinstance(api_date, datetime)
            and api_date != "latest"
            and api_date is not None
        ):
            raise ValueError(
                "parameter api_date has to be 'latest' or a datetime object or 'None'."
            )

        if not isinstance(api_chunksize, int) and api_chunksize is not None:
            raise ValueError("parameter api_chunksize has to be an integer or 'None'.")

        if not isinstance(api_data_types, list) and api_data_types is not None:
            raise ValueError("parameter api_data_types has to be a list or 'None'.")

        if isinstance(api_data_types, list):
            for value in api_data_types:
                if value not in [
                    "unit_data",
                    "eeg_data",
                    "kwk_data",
                    "permit_data",
                    None,
                ]:
                    raise ValueError(
                        'list entries of api_data_types have to be "unit_data", "eeg_data", "kwk_data" '
                        'or "permit_data".'
                    )

        if not isinstance(api_location_types, list) and api_location_types is not None:
            raise ValueError("parameter api_location_types has to be a list or 'None'.")

        if isinstance(api_location_types, list):
            for value in api_location_types:
                if value not in [
                    "location_elec_generation",
                    "location_elec_consumption",
                    "location_gas_generation",
                    "location_gas_consumption",
                    None,
                ]:
                    raise ValueError(
                        'list entries of api_data_types have to be "location_elec_generation",'
                        '"location_elec_consumption", "location_gas_generation" or'
                        ' "location_gas_consumption".'
                    )

    def _technology_to_include_tables(
        self,
        technology,
        all_technologies=orm.bulk_technologies,
        tables_map=orm.bulk_include_tables_map,
    ) -> list:
        """
        Check the user input 'technology' and convert it to the list 'include_tables' which contains
        file names from zipped
        bulk download.
        Parameters
        ----------
        technology: None, str, list
            The user input for technology selection
            * `None`: All technologies (default)
            * `str`: One technology
            * `list`: List of technologies
        all_technologies: list
            All possible selections
        tables_map: dict
            Dictionary that maps the technologies to the file names in the zipped bulk download folder
        Returns
        -------
        list
            List of file names
        -------

        """
        # Convert technology input into a standard list
        chosen_technologies = []
        if technology is None:
            # All technologies are to be chosen
            chosen_technologies = all_technologies
        elif isinstance(technology, str):
            # Only one technology is chosen
            chosen_technologies = [technology]
        elif isinstance(technology, list):
            # list of technologies is given
            chosen_technologies = technology

        # Check if given technologies match with the valid options from 'orm.bulk_technologies'
        for tech in chosen_technologies:
            if tech not in all_technologies:
                raise Exception(
                    f"The input technology = {technology} does not match with the "
                    f"possible technology options. Only following technology options are available "
                    f"bulk_technologies = {all_technologies}"
                )

        # Map technologies to include tables
        include_tables = []
        for tech in chosen_technologies:
            # Append table names to the include_tables list respectively
            include_tables += tables_map[tech]

        return include_tables
