from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load dataset
df = pd.read_excel("hotel_data.xlsx")

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == "a@admin.com" and password == "a":
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    seasons = df["Season"].unique().tolist()
    locations = df["Location"].unique().tolist()
    return render_template("dashboard.html", seasons=seasons, locations=locations)

@app.route("/get_hotels", methods=["POST"])
def get_hotels():
    data = request.get_json()
    location = data.get("location")
    season = data.get("season")
    
    # Filter hotels based on location and season
    hotels = df[(df["Location"] == location) & (df["Season"] == season)]
    hotel_list = hotels[["Hotel Name", "Rate (on Double Occupancy)", "Extra Bed Price", "CWB"]].to_dict("records")

    # Format response
    response = [{
        "name": hotel["Hotel Name"],
        "price": hotel["Rate (on Double Occupancy)"],
        "extra_bed_price": hotel["Extra Bed Price"],
        "cwb_price": hotel["CWB"]
    } for hotel in hotel_list]
    return jsonify(response)

@app.route("/quotation", methods=["POST"])
def quotation():
    men = int(request.form.get("men", 0))
    women = int(request.form.get("women", 0))
    children = int(request.form.get("children", 0))
    persons = men + women + children
    season = request.form.get("season")
    extra_beds = int(request.form.get("extra_beds", 0))
    cwb = int(request.form.get("cwb", 0))
    selected_hotels = request.form.getlist("hotels")

    total_price = 0

    # Calculate rooms required
    adults = men + women  # Total adults
    rooms = (adults // 2) + (adults % 2)  # Each room can accommodate 2 adults

    # Calculate extra beds for children
    if children > 0:
        # Each bed can accommodate 2 children
        beds_needed_for_children = (children // 2) + (children % 2)
        # Each room can provide 1 bed for children (shared with adults)
        beds_available_in_rooms = rooms
        # Extra beds are needed if beds_needed_for_children > beds_available_in_rooms
        extra_beds += max(0, beds_needed_for_children - beds_available_in_rooms)

    hotels_data = []  # Store formatted hotel details

    for hotel in selected_hotels:
        hotel_data = json.loads(hotel)  # Use json.loads instead of eval()
        hotel_name = hotel_data["name"]
        
        hotel_info = df[(df["Hotel Name"] == hotel_name) & (df["Season"] == season)].iloc[0]
        hotel_price = int(hotel_info["Rate (on Double Occupancy)"])
        extra_bed_price = int(hotel_info["Extra Bed Price"]) if not pd.isna(hotel_info["Extra Bed Price"]) else 0
        cwb_price = int(hotel_info["CWB"]) if not pd.isna(hotel_info["CWB"]) else 0

        total_price += hotel_price * rooms  # Add hotel price for required rooms
        total_price += extra_bed_price * extra_beds  # Add extra bed charges
        total_price += cwb_price * cwb  # Add CWB charges

        hotels_data.append({
            "name": hotel_name,
            "location": hotel_data.get("location", "Unknown"),  # Ensure safe retrieval
            "price": hotel_price,
            "extra_bed_price": extra_bed_price,
            "cwb_price": cwb_price
        })

    # Calculate commission (₹2000 per person)
    commission = persons * 2000
    total_price += commission  # Add commission to the total price

    # Return JSON response with redirect URL
    return jsonify({
        "redirect": url_for("quotation_page", 
                           persons=persons, 
                           men=men, 
                           women=women, 
                           children=children,
                           rooms=rooms,
                           extra_beds=extra_beds,
                           cwb=cwb,
                           total_price=total_price,
                           hotels=json.dumps(hotels_data),  # Pass processed list as JSON
                           commission=commission)
    })
@app.route("/quotation_page")
def quotation_page():
    persons = int(request.args.get("persons"))
    men = int(request.args.get("men"))
    women = int(request.args.get("women"))
    children = int(request.args.get("children"))
    rooms = int(request.args.get("rooms"))
    extra_beds = int(request.args.get("extra_beds"))
    cwb = int(request.args.get("cwb"))
    total_price = int(request.args.get("total_price"))
    commission = int(request.args.get("commission"))
    hotels = json.loads(request.args.get("hotels"))  # Deserialize hotels data

    # Extract extra_bed_price and cwb_price from the first selected hotel
    extra_bed_price = hotels[0]["extra_bed_price"] if hotels else 0
    cwb_price = hotels[0]["cwb_price"] if hotels else 0

    return render_template("quotation.html", 
                           persons=persons, 
                           men=men, 
                           women=women, 
                           children=children,
                           rooms=rooms,
                           extra_beds=extra_beds,
                           cwb=cwb,
                           total_price=total_price,
                           hotels=hotels,
                           commission=commission,
                           extra_bed_price=extra_bed_price,
                           cwb_price=cwb_price)

if __name__ == "__main__":
    app.run(debug=True)
else:
    # This is required for Vercel deployment
    import sys
    from flask import Flask, request

    def vercel_handler(event, context):
        from flask import Response

        # Convert Vercel event to Flask request
        environ = {
            'REQUEST_METHOD': event['httpMethod'],
            'PATH_INFO': event['path'],
            'QUERY_STRING': event.get('queryStringParameters', {}),
            'wsgi.input': BytesIO(event.get('body', '').encode('utf-8')),
            'CONTENT_TYPE': event.get('headers', {}).get('Content-Type', ''),
        }

        with app.request_context(environ):
            try:
                response = app.full_dispatch_request()
            except Exception as e:
                response = app.make_response(app.handle_exception(e))

        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
