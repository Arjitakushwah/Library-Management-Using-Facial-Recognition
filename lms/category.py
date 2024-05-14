import csv
from datetime import datetime
from models import db, BookCategory 
from app import app # Import your Flask app and SQLAlchemy objects

def import_category_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row since it's missing
        for row_num, row in enumerate(reader, start=1):
            try:
                category = BookCategory(
                    id=row[0].strip(),  # Assuming id is the first column
                    categoryName=row[1].strip(),  # Assuming categoryName is the second column
                    createdAt=datetime.strptime(row[2].strip(), '%Y-%m-%d %H:%M:%S'),  # Adjust format as per your CSV
                    updatedAt=datetime.strptime(row[3].strip(), '%Y-%m-%d %H:%M:%S')   # Adjust format as per your CSV
                )
                db.session.add(category)
            except IndexError:
                print(f"Row {row_num} is malformed: {row}")


    # Commit changes to the database
    db.session.commit()

# Example usage
if __name__ == '__main__':
   # Assuming you have a function to create your Flask app instance
    with app.app_context():
        csv_file_path = 'C:/Users/arjit/Desktop/lms/Data/BookCategory.csv'
        import_category_from_csv(csv_file_path)
