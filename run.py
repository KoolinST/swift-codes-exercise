from app import create_app
from app.data_parser import parse_swift_codes

app = create_app()

with app.app_context():
    parse_swift_codes("swift_codes.csv")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
