"""
Database Connector Service
Supports multiple data sources: BigQuery, PostgreSQL, MySQL, SQL Server, Snowflake, Redshift
"""

import pandas as pd
from typing import Dict, Any, Optional
import json


class DatabaseConnector:
    """Connect to various databases and data warehouses"""

    def __init__(self):
        self.connection = None
        self.source_type = None

    def connect_postgresql(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            from sqlalchemy import create_engine

            connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['database']}"
            engine = create_engine(connection_string)

            query = config.get('query', 'SELECT * FROM information_schema.tables LIMIT 10')
            df = pd.read_sql(query, engine)

            engine.dispose()
            return df

        except ImportError:
            raise Exception("psycopg2 and sqlalchemy are required for PostgreSQL. Install with: pip install psycopg2-binary sqlalchemy")
        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {str(e)}")

    def connect_mysql(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Connect to MySQL database"""
        try:
            import pymysql
            from sqlalchemy import create_engine

            connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 3306)}/{config['database']}"
            engine = create_engine(connection_string)

            query = config.get('query', 'SELECT * FROM information_schema.tables LIMIT 10')
            df = pd.read_sql(query, engine)

            engine.dispose()
            return df

        except ImportError:
            raise Exception("pymysql and sqlalchemy are required for MySQL. Install with: pip install pymysql sqlalchemy")
        except Exception as e:
            raise Exception(f"MySQL connection failed: {str(e)}")

    def connect_sqlserver(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Connect to Microsoft SQL Server"""
        try:
            import pyodbc
            from sqlalchemy import create_engine

            connection_string = f"mssql+pyodbc://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 1433)}/{config['database']}?driver=ODBC+Driver+17+for+SQL+Server"
            engine = create_engine(connection_string)

            query = config.get('query', 'SELECT TOP 10 * FROM INFORMATION_SCHEMA.TABLES')
            df = pd.read_sql(query, engine)

            engine.dispose()
            return df

        except ImportError:
            raise Exception("pyodbc and sqlalchemy are required for SQL Server. Install with: pip install pyodbc sqlalchemy")
        except Exception as e:
            raise Exception(f"SQL Server connection failed: {str(e)}")

    def connect_bigquery(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Connect to Google BigQuery"""
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account

            # Expect credentials_json or credentials_path in config
            if 'credentials_json' in config:
                credentials = service_account.Credentials.from_service_account_info(
                    json.loads(config['credentials_json'])
                )
            elif 'credentials_path' in config:
                credentials = service_account.Credentials.from_service_account_file(
                    config['credentials_path']
                )
            else:
                credentials = None  # Use default credentials

            client = bigquery.Client(
                credentials=credentials,
                project=config.get('project_id')
            )

            query = config.get('query', 'SELECT * FROM `project.dataset.table` LIMIT 10')
            df = client.query(query).to_dataframe()

            return df

        except ImportError:
            raise Exception("google-cloud-bigquery is required. Install with: pip install google-cloud-bigquery")
        except Exception as e:
            raise Exception(f"BigQuery connection failed: {str(e)}")

    def connect_snowflake(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Connect to Snowflake Data Warehouse"""
        try:
            import snowflake.connector
            from snowflake.connector.pandas_tools import pd_writer

            conn = snowflake.connector.connect(
                user=config['username'],
                password=config['password'],
                account=config['account'],
                warehouse=config.get('warehouse'),
                database=config.get('database'),
                schema=config.get('schema', 'PUBLIC')
            )

            query = config.get('query', 'SELECT * FROM INFORMATION_SCHEMA.TABLES LIMIT 10')
            df = pd.read_sql(query, conn)

            conn.close()
            return df

        except ImportError:
            raise Exception("snowflake-connector-python is required. Install with: pip install snowflake-connector-python")
        except Exception as e:
            raise Exception(f"Snowflake connection failed: {str(e)}")

    def connect_redshift(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Connect to Amazon Redshift"""
        try:
            import psycopg2
            from sqlalchemy import create_engine

            connection_string = f"redshift+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5439)}/{config['database']}"
            engine = create_engine(connection_string)

            query = config.get('query', 'SELECT * FROM information_schema.tables LIMIT 10')
            df = pd.read_sql(query, engine)

            engine.dispose()
            return df

        except ImportError:
            raise Exception("psycopg2 and sqlalchemy are required for Redshift. Install with: pip install psycopg2-binary sqlalchemy")
        except Exception as e:
            raise Exception(f"Redshift connection failed: {str(e)}")

    def connect_s3(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Read data from Amazon S3"""
        try:
            import boto3
            import io

            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('access_key_id'),
                aws_secret_access_key=config.get('secret_access_key'),
                region_name=config.get('region', 'us-east-1')
            )

            # Get file from S3
            bucket = config['bucket']
            key = config['key']  # File path in S3

            obj = s3_client.get_object(Bucket=bucket, Key=key)
            file_content = obj['Body'].read()

            # Determine file type and read accordingly
            if key.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif key.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(file_content))
            elif key.endswith('.parquet'):
                df = pd.read_parquet(io.BytesIO(file_content))
            else:
                raise Exception(f"Unsupported file type: {key}")

            return df

        except ImportError:
            raise Exception("boto3 is required for S3. Install with: pip install boto3")
        except Exception as e:
            raise Exception(f"S3 connection failed: {str(e)}")

    def connect_azure(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Read data from Azure Data Lake Storage"""
        try:
            from azure.storage.filedatalake import DataLakeServiceClient
            import io

            service_client = DataLakeServiceClient(
                account_url=f"https://{config['account_name']}.dfs.core.windows.net",
                credential=config['account_key']
            )

            file_system_client = service_client.get_file_system_client(config['filesystem'])
            file_client = file_system_client.get_file_client(config['file_path'])

            download = file_client.download_file()
            file_content = download.readall()

            # Determine file type and read accordingly
            file_path = config['file_path']
            if file_path.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(file_content))
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(io.BytesIO(file_content))
            else:
                raise Exception(f"Unsupported file type: {file_path}")

            return df

        except ImportError:
            raise Exception("azure-storage-file-datalake is required. Install with: pip install azure-storage-file-datalake")
        except Exception as e:
            raise Exception(f"Azure Data Lake connection failed: {str(e)}")

    def connect(self, source_type: str, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Connect to a data source and return DataFrame

        Args:
            source_type: Type of data source (postgresql, mysql, bigquery, etc.)
            config: Configuration dictionary with connection details

        Returns:
            pandas DataFrame with the query results
        """
        self.source_type = source_type

        if source_type == 'postgresql':
            return self.connect_postgresql(config)
        elif source_type == 'mysql':
            return self.connect_mysql(config)
        elif source_type == 'sqlserver':
            return self.connect_sqlserver(config)
        elif source_type == 'bigquery':
            return self.connect_bigquery(config)
        elif source_type == 'snowflake':
            return self.connect_snowflake(config)
        elif source_type == 'redshift':
            return self.connect_redshift(config)
        elif source_type == 's3':
            return self.connect_s3(config)
        elif source_type == 'azure':
            return self.connect_azure(config)
        else:
            raise Exception(f"Unsupported source type: {source_type}")

    def list_tables(self, source_type: str, config: Dict[str, Any]) -> list:
        """
        List all tables in the database

        Args:
            source_type: Type of data source
            config: Configuration dictionary with connection details

        Returns:
            List of table names with metadata
        """
        try:
            if source_type == 'postgresql':
                from sqlalchemy import create_engine, inspect

                connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['database']}"
                engine = create_engine(connection_string)
                inspector = inspect(engine)

                tables = []
                for table_name in inspector.get_table_names():
                    tables.append({
                        'name': table_name,
                        'schema': 'public',
                        'type': 'table'
                    })

                engine.dispose()
                return tables

            elif source_type == 'mysql':
                from sqlalchemy import create_engine

                connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 3306)}/{config['database']}"
                engine = create_engine(connection_string)

                query = "SHOW TABLES"
                df = pd.read_sql(query, engine)

                tables = []
                for table_name in df.iloc[:, 0].tolist():
                    tables.append({
                        'name': table_name,
                        'schema': config['database'],
                        'type': 'table'
                    })

                engine.dispose()
                return tables

            elif source_type == 'bigquery':
                from google.cloud import bigquery
                from google.oauth2 import service_account

                if 'credentials_json' in config:
                    credentials = service_account.Credentials.from_service_account_info(
                        json.loads(config['credentials_json'])
                    )
                else:
                    credentials = None

                client = bigquery.Client(
                    credentials=credentials,
                    project=config.get('project_id')
                )

                # List datasets and tables
                tables = []
                datasets = list(client.list_datasets())

                for dataset in datasets[:10]:  # Limit to first 10 datasets
                    dataset_id = dataset.dataset_id
                    dataset_tables = list(client.list_tables(dataset_id))

                    for table in dataset_tables[:50]:  # Limit to 50 tables per dataset
                        tables.append({
                            'name': f"{dataset_id}.{table.table_id}",
                            'schema': dataset_id,
                            'type': table.table_type,
                            'full_name': f"{config.get('project_id')}.{dataset_id}.{table.table_id}"
                        })

                return tables

            elif source_type == 'snowflake':
                import snowflake.connector

                conn = snowflake.connector.connect(
                    user=config['username'],
                    password=config['password'],
                    account=config['account'],
                    warehouse=config.get('warehouse'),
                    database=config.get('database'),
                    schema=config.get('schema', 'PUBLIC')
                )

                query = "SHOW TABLES"
                df = pd.read_sql(query, conn)

                tables = []
                for _, row in df.iterrows():
                    tables.append({
                        'name': row['name'],
                        'schema': row.get('schema_name', config.get('schema', 'PUBLIC')),
                        'type': 'table'
                    })

                conn.close()
                return tables

            elif source_type in ['sqlserver', 'redshift']:
                from sqlalchemy import create_engine

                if source_type == 'sqlserver':
                    connection_string = f"mssql+pyodbc://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 1433)}/{config['database']}?driver=ODBC+Driver+17+for+SQL+Server"
                else:  # redshift
                    connection_string = f"redshift+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5439)}/{config['database']}"

                engine = create_engine(connection_string)

                query = "SELECT table_name, table_schema FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
                df = pd.read_sql(query, engine)

                tables = []
                for _, row in df.iterrows():
                    tables.append({
                        'name': row['table_name'],
                        'schema': row['table_schema'],
                        'type': 'table'
                    })

                engine.dispose()
                return tables

            else:
                raise Exception(f"Table listing not supported for {source_type}")

        except Exception as e:
            raise Exception(f"Failed to list tables: {str(e)}")

    def get_table_schema(self, source_type: str, config: Dict[str, Any], table_name: str) -> dict:
        """
        Get schema/columns for a specific table

        Args:
            source_type: Type of data source
            config: Configuration dictionary with connection details
            table_name: Name of the table

        Returns:
            Dictionary with column information
        """
        try:
            if source_type == 'postgresql':
                from sqlalchemy import create_engine

                connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['database']}"
                engine = create_engine(connection_string)

                query = f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                df = pd.read_sql(query, engine)

                columns = []
                for _, row in df.iterrows():
                    columns.append({
                        'name': row['column_name'],
                        'type': row['data_type'],
                        'nullable': row['is_nullable'] == 'YES'
                    })

                engine.dispose()
                return {'table_name': table_name, 'columns': columns}

            elif source_type == 'mysql':
                from sqlalchemy import create_engine

                connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 3306)}/{config['database']}"
                engine = create_engine(connection_string)

                query = f"DESCRIBE {table_name}"
                df = pd.read_sql(query, engine)

                columns = []
                for _, row in df.iterrows():
                    columns.append({
                        'name': row['Field'],
                        'type': row['Type'],
                        'nullable': row['Null'] == 'YES'
                    })

                engine.dispose()
                return {'table_name': table_name, 'columns': columns}

            elif source_type == 'bigquery':
                from google.cloud import bigquery
                from google.oauth2 import service_account

                if 'credentials_json' in config:
                    credentials = service_account.Credentials.from_service_account_info(
                        json.loads(config['credentials_json'])
                    )
                else:
                    credentials = None

                client = bigquery.Client(
                    credentials=credentials,
                    project=config.get('project_id')
                )

                # Parse table name (format: dataset.table or project.dataset.table)
                table_ref = client.get_table(table_name)

                columns = []
                for field in table_ref.schema:
                    columns.append({
                        'name': field.name,
                        'type': field.field_type,
                        'nullable': field.mode != 'REQUIRED'
                    })

                return {'table_name': table_name, 'columns': columns}

            elif source_type == 'snowflake':
                import snowflake.connector

                conn = snowflake.connector.connect(
                    user=config['username'],
                    password=config['password'],
                    account=config['account'],
                    warehouse=config.get('warehouse'),
                    database=config.get('database'),
                    schema=config.get('schema', 'PUBLIC')
                )

                query = f"DESCRIBE TABLE {table_name}"
                df = pd.read_sql(query, conn)

                columns = []
                for _, row in df.iterrows():
                    columns.append({
                        'name': row['name'],
                        'type': row['type'],
                        'nullable': row['null?'] == 'Y'
                    })

                conn.close()
                return {'table_name': table_name, 'columns': columns}

            elif source_type in ['sqlserver', 'redshift']:
                from sqlalchemy import create_engine

                if source_type == 'sqlserver':
                    connection_string = f"mssql+pyodbc://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 1433)}/{config['database']}?driver=ODBC+Driver+17+for+SQL+Server"
                else:  # redshift
                    connection_string = f"redshift+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5439)}/{config['database']}"

                engine = create_engine(connection_string)

                query = f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                df = pd.read_sql(query, engine)

                columns = []
                for _, row in df.iterrows():
                    columns.append({
                        'name': row['column_name'],
                        'type': row['data_type'],
                        'nullable': row['is_nullable'] == 'YES'
                    })

                engine.dispose()
                return {'table_name': table_name, 'columns': columns}

            else:
                raise Exception(f"Table schema not supported for {source_type}")

        except Exception as e:
            raise Exception(f"Failed to get table schema: {str(e)}")
