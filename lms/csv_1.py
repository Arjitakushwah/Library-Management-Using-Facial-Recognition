import csv
from datetime import datetime
from models import db, Books, BookCategory
from app import app
def import_data_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row since it's missing
        for row_num, row in enumerate(reader, start=1):
            try:
                book = Books(
                    id=row[0].strip(),  # Assuming id is the first column
                    bookName=row[1].strip(),
                    categories=row[2].strip(),
                    author=row[3].strip(),
                    publisher=row[4].strip(),
                    edition=int(row[5].strip()),
                    bookCountAvailable=int(row[6].strip()),
                    totalCount=int(row[7].strip()),
                    bookStatus=row[8].strip(),
                    language=row[9].strip(),
                    createdAt=datetime.strptime(row[10].strip(), '%d-%m-%Y %H:%M:%S'),
                    updatedAt=datetime.strptime(row[11].strip(), '%d-%m-%Y %H:%M:%S'),
                    Book_rating=float(row[12].strip()),
                    review_count=int(row[13].strip()),
                    top_rated=row[14].strip()
                )
                db.session.add(book)
            except IndexError:
                print(f"Row {row_num} is malformed: {row}")

    # Commit changes to the database
    db.session.commit()


# Example usage
if __name__ == '__main__':
    with app.app_context():
        csv_file_path = 'data/Books.csv'
        import_data_from_csv(csv_file_path)
