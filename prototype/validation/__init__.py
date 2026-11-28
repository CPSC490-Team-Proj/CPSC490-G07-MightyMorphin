"""Page 3 "Validate extracted information" prototype (#88).

The modules mirror the participants of the page 3 sequence diagram (#87):

- ``app``        Backend API (FastAPI, provisional under #78)
- ``checks``     Automatic checks run on every draft save
- ``store``      Snowflake stand-in (SQLite): records, values, flags, audit events
- ``documents``  AWS S3 stand-in (a local folder): the PDF copy and its checksum
- ``fixtures``   Synthetic records and generated PDFs; no Edwards data

Every service here is a local stand-in. See ``prototype/README.md``.
"""
