import csv
from decimal import Decimal
from os import listdir
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import *


if __name__ == '__main__':
    # Create tables.
    Base.metadata.create_all(engine)

    # Insert master data.
    mst_data_dir = 'mltd/models/mst_data/'
    with Session(engine) as session:
        session.execute(text('PRAGMA foreign_keys=OFF'))

        for filename in listdir(mst_data_dir):
            if 'mst' not in filename:
                continue
            table_name = filename.split('.')[0]
            table = Base.metadata.tables[table_name]
            with open(f'{mst_data_dir}{table_name}.csv',
                      encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                data = list(reader)
            # Convert CSV data into proper data types because they are
            # all read as strs.
            for row in data:
                for fieldname in fieldnames:
                    column = table.c[fieldname]
                    if column.nullable and not row[fieldname]:
                        # If column is nullable, replace null-equivalent
                        # values with None.
                        row[fieldname] = None
                    elif str(column.type) == 'BOOLEAN' and row[fieldname]:
                        row[fieldname] = (False if row[fieldname] == '0'
                                          else True)
                    elif str(column.type) == 'INTEGER' and row[fieldname]:
                        row[fieldname] = int(row[fieldname])
                    elif str(column.type) == 'DATETIME' and row[fieldname]:
                        # Convert str to UTC datetime.
                        row[fieldname] = datetime.strptime(
                            row[fieldname], '%Y-%m-%dT%H:%M:%S%z'
                        ).astimezone(timezone.utc)
                    elif (column.type.__class__.__name__ == 'Uuid'
                            and row[fieldname]):
                        row[fieldname] = UUID(row[fieldname])
            session.execute(table.insert(), data)

        session.execute(text('PRAGMA foreign_keys=ON'))
        # Validate foreign keys after inserting master data.
        session.execute(text('PRAGMA foreign_key_check'))
        session.commit()

