import uuid


import os
import stripe
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from fastapi import APIRouter,Request, Depends, HTTPException, status
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse,FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.models import User, Session, Tour,TourImage, Booking
from app.utils import get_current_user, create_session, delete_session,verify_password,hash_password, get_current_admin,send_email,get_authenticated_user,notify_subscribers
from app.database import get_db
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from datetime import timedelta
from fastapi import File, UploadFile
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks,Query

#from app.database import Sessionlocal as DBSession

# Uses the base URL from environment variable or defaults to localhost
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

from dotenv import load_dotenv
load_dotenv()
router = APIRouter()
temporary_reset_tokens = {}
UPLOAD_DIR = "app/static/uploads/tours"
 

templates = Jinja2Templates(directory="app/templates")# template setup
@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Uganda Tours"})


regions = [
    {
        "id": "central",
        "name": "Central Region",
        "food": ["Luwombo", "Matooke", "Groundnut sauce"],
        "dress": "Gomesi for women, Kanzu for men",
        "tradition": "Buganda kingdom ceremonies",
        "images": [
            "central dance.jpg", "central.jpg", "lake victoria.jpg",
            "backcloth.JPG", "food 2.JPG"
        ],
        "video": "XYZ123",
        "credit": "@UgandaTourismBoard",
        "testimonial": "The Buganda kingdom has a rich cultural heritage that dates back centuries."
    },
    {
        "id": "eastern",
        "name": "Eastern Uganda",
        "food": ["Malewa", "Kwon kal", "Simsim paste"],
        "dress": "Suuti for women, Kanzu for men",
        "tradition": "Imbalu circumcision ceremony",
        "images": [
            "https://via.placeholder.com/300x180?text=Eastern+Uganda",
            "https://via.placeholder.com/300x180?text=Imbalu+Ceremony"
        ],
        "video": "dQw4w9WgXcQ",
        "credit": "@ExploreUganda",
        "testimonial": "Our Imbalu ceremony is a rite of passage that connects generations."
    },
    {
        "id": "western",
        "name": "Western Uganda",
        "food": ["Eshabwe", "Akaro", "Obushera"],
        "dress": "Mushanana for women, Kanzu for men",
        "tradition": "Cattle keeping ceremonies",
        "images": [
            "https://via.placeholder.com/300x180?text=Western+Uganda",
            "https://via.placeholder.com/300x180?text=Ankole+Cattle"
        ],
        "video": "DEF789",
        "credit": "@UgandaCulturalHeritage",
        "testimonial": "Our long-horned Ankole cattle are a symbol of pride and wealth."
    },
    {
        "id": "northern",
        "name": "Northern Uganda",
        "food": ["Simsim paste", "Millet", "Dried fish"],
        "dress": "Colorful wraps, Beaded jewelry",
        "tradition": "Acholi warrior dances and storytelling",
        "images": [
            "northenugandadress.JPG", "food 4.JPG", "food 3.JPG"
        ],
        "video": "WCwBlzeOY6U",
        "credit": "@ExploreUganda",
        "testimonial": "Northern Uganda is home to powerful stories, rhythms, and community spirit."
    },
    {
        "id": "southern",
        "name": "Southern Uganda",
        "food": ["Matooke", "Groundnut sauce", "Smoked fish"],
        "dress": "Gomesi, Bark cloth",
        "tradition": "Buganda royal customs and clan systems",
        "images": [
            "https://via.placeholder.com/300x180?text=Southern+Uganda",
            "https://via.placeholder.com/300x180?text=Buganda+Drums",
            "https://via.placeholder.com/300x180?text=Smoked+Fish"
        ],
        "video": "SOU456",
        "credit": "@RoyalBugandaChannel",
        "testimonial": "The Southern region brings the elegance of tradition and royalty together."
    }
]

@router.get("/cultures", response_class=HTMLResponse)
async def show_cultures(request: Request):
    return templates.TemplateResponse("uganda_culture.html", {"request": request, "regions": regions})


@router.get("/tours", response_class=HTMLResponse)
async def tours_page(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    tours = db.query(Tour).all() # fetch all tours
    return templates.TemplateResponse(
        "tours.html",
        {
            "request": request,
            "title": "Our Tours",
            "is_logged_in": user is not None,
            "user": user,
            "tours": tours
        }
    )

    
@router.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})   
    
@router.post("/signup", response_class=HTMLResponse)
async def signup(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    full_name = form.get("full_name")
    
    if not all([email, password, full_name]):
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Please fill in all fields"})
    
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already exists"})
    
    hashed_password = hash_password(password)
    
    new_user = User(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})    
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})
    
    session_id = create_session(db, user.id)
    
    response = RedirectResponse(url="/tours", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="auth_session_id", value=session_id, httponly=True, max_age=1800,samesite="Lax",path="/")
    return response
@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("auth_session_id")
    if session_id:
        delete_session(db, session_id)
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="auth_session_id")
    return response   
    
@router.get('/admin/dashboard', response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_admin)):
    if not user.is_admin:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    tours=db.query(Tour).all()
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": user, "tours": tours})

# create a tour
@router.post('/admin/tours/create', response_class=HTMLResponse)
async def create_tour(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    duration: str = Form(...),
    locations: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin)
):
    try:
        # Validate minimum requirements
        if not images:
            request.session['error'] = "At least one image is required"
            return RedirectResponse(url="/admin/tours/create", status_code=303)

        # Create tour
        new_tour = Tour(
            title=title,
            description=description,
            price=price,
            duration=duration,
            locations=locations
        )
        db.add(new_tour)
        db.flush()

        # Process images
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for idx, image in enumerate(images):
            # Validate file type
            if not image.content_type.startswith('image/'):
                continue

            # Generate unique filename
            file_ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, filename)

            # Save file
            contents = await image.read()
            with open(file_path, "wb") as f:
                f.write(contents)

            # Create database entry
            db.add(TourImage(
                tour_id=new_tour.id,
                image_url=f"/static/uploads/{filename}",
                is_primary=(idx == 0)
            ))

        db.commit()
        background_tasks.add_task(notify_subscribers,db, new_tour.id)
        return RedirectResponse(url="/admin/dashboard", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating tour: {str(e)}"
        )

#update tour
@router.post('/admin/tours/update/{tour_id}', response_class=HTMLResponse)
async def update_tour(request: Request, tour_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_admin)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this page")
    
    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    price = form.get("price")
    duration = form.get("duration")
    locations = form.get("locations")
    image_url = form.get("image_url")
    
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    
    if not tour:
        return templates.TemplateResponse("admin/edit_tour.html", {
            "request": request,
            "error": "Tour not found",
            "tour_id": tour_id
        })
    
    if title:
        tour.title = title
    if description:
        tour.description = description
    if price:
        tour.price = price
    if duration:
        tour.duration = duration
    if locations:
        tour.locations = locations
    
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)



@router.post('/admin/tours/delete/{tour_id}', response_class=HTMLResponse)
async def delete_tour(
    request: Request,
    tour_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_admin)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this page")
    
    tour = db.query(Tour).filter(Tour.id == tour_id).first()

    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    
    # Get related images before deleting
    images = db.query(TourImage).filter(TourImage.tour_id == tour.id).all()

    for img in images:
        # Extract filename from image_url
        # URL format: "/static/uploads/filename.jpg"
        filename = img.image_url.split("/")[-1]
        image_path = os.path.join("static", "uploads", filename)
        
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"Deleted file: {image_path}")
            except Exception as e:
                print(f"Error deleting file {image_path}: {str(e)}")
        else:
            print(f"File not found: {image_path}")

    # Delete image records from DB
    db.query(TourImage).filter(TourImage.tour_id == tour.id).delete()

    # Delete the tour itself
    db.delete(tour)
    db.commit()

    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
## edit tour

@router.get('/admin/tours/edit/{tour_id}', response_class=HTMLResponse)
async def edit_tour(request: Request, tour_id: int, 
                   db: Session = Depends(get_db), 
                   user: User = Depends(get_current_admin)):
    tour = db.query(Tour).options(joinedload(Tour.images)).filter(Tour.id == tour_id).first()
    
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    
    return templates.TemplateResponse("admin/edit_tour.html", {
        "request": request,
        "tour": tour,
        "images": tour.images
    })
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    
    
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            
            return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Email not found."})
        # Generate a reset token
        reset_token = str(uuid.uuid4())
        temporary_reset_tokens[reset_token] = {
            "email": email,
            "expires": datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
        }

        # Send email with the reset link
       # reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
        reset_link = f"{BASE_URL.rstrip('/')}/reset-password?token={reset_token}"
        subject = "Forgot Password"
        body = f"Password reset Request, Click here to reset your password: {reset_link}"
        try:
            send_email(user.email, subject, body) 
        except Exception as e: 
            return templates.TemplateResponse("forgot_password.html", {"request": request, "error": f"Failed to send email: {str(e)}"})

        return templates.TemplateResponse("forgot_password.html", {"request": request, "message": "Reset link sent!"})
    
    except Exception as e:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "An unexpected error occurred."})

        
@router.get("/reset-password", response_class=HTMLResponse)
async def show_reset_password_form(request: Request, token: str = ""):
    if not token:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Missing reset token"
        })

    if token not in temporary_reset_tokens:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Invalid or expired token"
        })

    token_info = temporary_reset_tokens[token]
    if datetime.utcnow() > token_info["expires"]:
        del temporary_reset_tokens[token]
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Token has expired"
        })

    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token
    })
@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password_post(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    error = None
    try:
        if not new_password or not confirm_password:
            error = "Please fill in all fields"
            raise ValueError
        
        if new_password != confirm_password:
            error = "Passwords do not match"
            raise ValueError
        
        if len(new_password) < 8:
            error = "Password must be at least 8 characters"
            raise ValueError

        if token not in temporary_reset_tokens:
            error = "Invalid or expired token"
            raise ValueError

        token_info = temporary_reset_tokens[token]
        if datetime.utcnow() > token_info["expires"]:
            del temporary_reset_tokens[token]
            error = "Token has expired"
            raise ValueError

        email = token_info["email"]
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            error = "User not found"
            raise ValueError

        hashed_password = hash_password(new_password)
        user.hashed_password = hashed_password
        db.commit()
        db.refresh(user)

        del temporary_reset_tokens[token]

        return RedirectResponse(url="/login", status_code=303)

    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": error or "An error occurred",
            "token": token
        })
        
        
@router.get("/book/{tour_id}", response_class=HTMLResponse)
async def book_tour(
    request: Request,
    tour_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Validate tour exists
    tour = db.query(Tour).options(joinedload(Tour.images)).filter(Tour.id == tour_id).first()
    if not tour:
        return RedirectResponse(url="/tours", status_code=status.HTTP_303_SEE_OTHER)

    # Add today's date for date input validation
    today = datetime.now().date().isoformat()

    return templates.TemplateResponse("booking.html", {
        "request": request,
        "tour": tour,
        "user": user,
        "today": today  # Needed for date input min attribute
    })

@router.post("/process_booking", response_class=HTMLResponse)  # Changed endpoint name
async def process_booking(
    request: Request,
    tour_id: int = Form(...),
    adults: int = Form(...),
    kids: int = Form(...),
    tour_date: str = Form(...),
    donate: Optional[str] = Form(None),

    tour_type: str = Form('normal'),#Setting the default tour type to 'normal'
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        # Validate inputs
        if adults < 1:  # At least 1 adult required
            raise HTTPException(status_code=400, detail="At least 1 adult required")
        
        if kids < 0:
            raise HTTPException(status_code=400, detail="Invalid number of kids")

        # Fetch the tour
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")

        # Validate tour date
        try:
            tour_date_obj = datetime.strptime(tour_date, "%Y-%m-%d").date()
            if tour_date_obj < datetime.today().date():
                raise ValueError("Date in past")
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid tour date") from e

        # Calculate total price
        total_price = (adults + kids) * tour.price
        
        
        #Adding private tour price adjustment
        if tour_type == 'private':
            total_price *= 1.35  # 35% increase for private tours
            
            request.session['tour_type'] = 'private'
        else:
            request.session['tour_type'] = 'normal' # Making the tour type normal by default   
          
        donation_amount = 10.0 if donate else 0.0
        
        total_price += donation_amount
        
    

        # Store booking in session
        request.session['booking'] = {
            "tour_id": tour_id,
            "adults": adults,
            "kids": kids,
            "tour_date": tour_date,
            "donation": donation_amount,  # Store donation amount
            "total_price": float(total_price)  # Ensure JSON serializable
        }

        return RedirectResponse(url="/payment", status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException as he:
        # Rethrow HTTP exceptions
        raise he
    except Exception as e:
        # Log the error
        print(f"Booking processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your booking"
        )
        
## Viewing of the Booked tours        
@router.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")

    # Calculate date threshold (30 days ago)
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query bookings with filters
    bookings = db.query(Booking).filter(
        Booking.user_id == user.id,
        Booking.deleted_at.is_(None),
        or_(
            Booking.payment_status != 'cancelled',
            and_(
                Booking.payment_status == 'cancelled',
                Booking.cancelled_at >= one_month_ago
            )
        )
    ).all()
    
    # Get current datetime for cancellation eligibility checks
    current_datetime = datetime.utcnow()
    
    return templates.TemplateResponse("my_bookings.html", {
        "request": request,
        "bookings": bookings,
        "current_datetime": current_datetime,  # Ensure this name matches template
        "title": "My Bookings",
        "user": user
    })
# 
    
# 

# Add these new routes for a user to cancel a booking and download their ticket
@router.post("/cancel-booking/{booking_id}", response_class=RedirectResponse)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Fetch booking
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if cancellation is allowed (at least 24 hours before tour)
    cancellation_deadline = booking.tour_date - timedelta(hours=24)
    if datetime.utcnow() > cancellation_deadline:
        return templates.TemplateResponse("cancellation_error.html", {
            "request": Request,
            "error": "Cancellation is only allowed up to 24 hours before the tour"
        })
    
    # Update booking status
    booking.payment_status = "cancelled"
    booking.cancelled_at = datetime.utcnow() 
    db.commit()
    
    # Send cancellation confirmation email
    send_email(
        user.email,
        "Booking Cancelled",
        f"Your booking for {booking.tour.title} on {booking.tour_date} has been cancelled.Your money will be refunded within 3-5 business days.Thank you for using our service!"
    )
    
    return RedirectResponse(url="/my-bookings", status_code=303)

@router.post("/delete-booking/{booking_id}", response_class=RedirectResponse)
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Fetch booking that meets deletion criteria
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user.id,
        Booking.payment_status == 'cancelled',  # Only allow deletion of cancelled bookings
        Booking.deleted_at.is_(None)  # Not already deleted
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Perform soft delete by setting deletion timestamp
    booking.deleted_at = datetime.utcnow()
    db.commit()
    
    return RedirectResponse(url="/my-bookings", status_code=303)
   


## Download a tour booked receipt
# @router.get("/download-ticket/{booking_id}")
# async def download_ticket(
#     booking_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     # Fetch booking with tour details
#     booking = db.query(Booking).options(joinedload(Booking.tour)).filter(
#         Booking.id == booking_id,
#         Booking.user_id == user.id,
#         Booking.payment_status == "completed"
#     ).first()
    
#     if not booking:
#         raise HTTPException(status_code=404, detail="Ticket not available")
    
#     # Generate ticket filename
#     filename = f"ticket_{booking_id}.pdf"
#     filepath = os.path.join("app", "static", "tickets", filename)
    
#     # Create directory if needed
#     os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
#     # Render HTML template for ticket
#     ticket_html = templates.get_template("ticket_template.html").render({
#         "booking": booking,
#         "user": user
#     })
    
#     # Convert to PDF
#     pdfkit.from_string(ticket_html, filepath)
    
#     # Return the PDF file
#     return FileResponse(filepath, filename=f"{booking.tour.title.replace(' ', '_')}_ticket.pdf")    
# @router.get("/payment", response_class=HTMLResponse)
# async def payment_page(
#     request: Request,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     booking = request.session.get('booking')
    
#     # Validate booking exists
#     if not booking:
#         return RedirectResponse(url="/tours", status_code=status.HTTP_303_SEE_OTHER)
    
#     try:
#         # Verify tour still exists
#         tour = db.query(Tour).filter(Tour.id == booking['tour_id']).first()
#         if not tour:
#             request.session.pop('booking', None)
#             return RedirectResponse(url="/tours", status_code=status.HTTP_303_SEE_OTHER)
            
#         return templates.TemplateResponse("payment.html", {
#             "request": request,
#             "total_price": booking["total_price"],
#             "tour_title": tour.title,
#             "tour_id": tour.id,
#             "paypal_client_id": os.getenv("PAYPAL_CLIENT_ID"),
#             "paypal_env": os.getenv("PAYPAL_MODE", "sandbox")
#         })
        
#     except Exception as e:
#         print(f"Payment error: {str(e)}")
#         return RedirectResponse(url="/tours", status_code=status.HTTP_303_SEE_OTHER)
    

@router.post("/complete_booking")
async def complete_booking(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        booking_data = request.session.get('booking')
        payment_data = await request.json()
        
        if not booking_data:
            raise HTTPException(400, "Booking session expired")
        
        # Create booking record
        new_booking = Booking(
            user_id=user.id,
            tour_id=booking_data["tour_id"],
            adults=booking_data["adults"],
            kids=booking_data["kids"],
            tour_date=datetime.strptime(booking_data["tour_date"], "%Y-%m-%d"),
            total_price=booking_data["total_price"],
            donation=booking_data.get('donation', 0.0),
            payment_id=payment_data["payment_id"],
            payment_status=payment_data["status"]
            
        )
        
        db.add(new_booking)
        db.commit()
        
        # Send confirmation email
        await send_email(
            user.email,
            "Booking Confirmed",
            f"""Your booking details:
            - Tour: {new_booking.tour.title}
            - Date: {new_booking.tour_date}
            - Participants: {new_booking.adults} adults, {new_booking.kids} kids
            - Total: ${new_booking.total_price}"""
        )
        
        # Clear session
        request.session.pop('booking', None)
        
        return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        print(f"Booking error: {str(e)}")
        raise HTTPException(500, "Booking processing failed")
    
    
@router.get("/confirmation", response_class=HTMLResponse)
async def confirmation_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("confirmation.html", {
        "request": request,
        "user": user
    })    
    

# Initialize Stripe after loading environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Add these new routes
@router.post("/create-stripe-session")
async def create_stripe_session(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        booking_data = request.session.get('booking')
        if not booking_data:
            raise HTTPException(status_code=400, detail="Booking session expired")

        tour = db.query(Tour).filter(Tour.id == booking_data["tour_id"]).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        
        donation_amount = float(booking_data.get("donation", 0.0))
        total_price = float(booking_data["total_price"])  

        # Create Stripe session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(booking_data["total_price"] * 100),
                    'product_data': {
                        'name': tour.title,
                        'description': f"{booking_data['adults']} Adults, {booking_data['kids']} Kids"
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={
                'user_id': user.id,
                'tour_id': tour.id,
                'adults': booking_data['adults'],
                'kids': booking_data['kids'],
                #'total_price': booking_data['total_price'],
                'total_price': str(total_price),
                


                'tour_date': booking_data['tour_date']
            },
            success_url = f"{BASE_URL.rstrip('/')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url = f"{BASE_URL.rstrip('/')}/payment")
        

        return JSONResponse({"id": session.id})

    except Exception as e:
        print(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

@router.get("/payment/success", response_class=HTMLResponse)
async def payment_success(
    request: Request,
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Create booking record
        new_booking = Booking(
            user_id=user.id,
            tour_id=session.metadata['tour_id'],
            adults=session.metadata['adults'],
            kids=session.metadata['kids'],
            tour_date=datetime.strptime(session.metadata['tour_date'], "%Y-%m-%d"),
            total_price=session.metadata['total_price'],
            payment_method='stripe',
            payment_id=session.payment_intent,
            
            payment_status='completed'
        )
        
        db.add(new_booking)
        db.commit()

        # Send confirmation email
        send_email(
            user.email,
            "Booking Confirmation",
            f"""Your booking details:
            Tour: {new_booking.tour.title}
            Date: {new_booking.tour_date}
            Adults: {new_booking.adults}
            Children: {new_booking.kids}
            Total: ${new_booking.total_price}
            Payment ID: {session.payment_intent}"""
        )

        return RedirectResponse(url="/confirmation", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Payment success error: {str(e)}")
        return RedirectResponse(url="/payment-error", status_code=303)

# Update your existing payment route to include Stripe context
@router.get("/payment", response_class=HTMLResponse)
async def payment_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    booking = request.session.get('booking')
    if not booking:
        return RedirectResponse(url="/tours", status_code=303)
    
    try:
        tour = db.query(Tour).filter(Tour.id == booking['tour_id']).first()
        if not tour:
            request.session.pop('booking', None)
            return RedirectResponse(url="/tours", status_code=303)
            
        return templates.TemplateResponse("payment.html", {
            "request": request,
            "total_price": booking["total_price"],
            "tour_title": tour.title,
            "tour_id": tour.id,
            "is_private":booking.get("tour_type") == "private",
            "base_price": tour.price,
            "paypal_client_id": os.getenv("PAYPAL_CLIENT_ID"),
            "stripe_public_key": os.getenv("STRIPE_PUBLIC_KEY"),
            "paypal_env": os.getenv("PAYPAL_MODE", "sandbox")
        })
        
    except Exception as e:
        print(f"Payment error: {str(e)}")
        return RedirectResponse(url="/tours", status_code=303)
    
# # Creating a newsletter to send new tours to users    
# @router.post("/subscribe_newsletter",response_class=HTMLResponse)
# async def subscribe_newsletter(
#     request: Request,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)):
#     if not user:
#         return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
#     # Toggle newsletter subscription
#     user.newsletter_subscribed = not user.newsletter_subscribed
#     db.commit()
#     message = "Subscribed to newsletter" if user.newsletter_subscribed else "Unsubscribed from newsletter"
#     return templates.TemplateResponse("newsletter.html", {
#         "request": request,
#         "message": message,
#         "is_subscribed": user.newsletter_subscribed
#     })
    
# @router.get("/unsubscribe_newsletter", response_class=HTMLResponse)
# async def unsubscribe_newsletter(
#     request: Request,
#     db: Session = Depends(get_db),
#     token: str =Query(..., description="Unsubscribe token")
    
# ):
#     user=db.query(User).filter(User.unsubscribe_token == token).first()
#     if not user:
#         return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
#     # Unsubscribe user from newsletter
#     user.newsletter_subscribed = False
#     user.unsubscribe_token = str(uuid.uuid4())
#     db.commit()
    
#     return templates.TemplateResponse("unsubscribe_newsletter.html", {"request":request}
#     )
   
# # routes.py
# @router.get("/user/unsubscribe_newsletter", response_class=HTMLResponse)
# async def user_unsubscribe_newsletter(
#     request: Request,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     user.newsletter_subscribed = False
#     user.unsubscribe_token = str(uuid.uuid4())  # Invalidate old token
#     db.commit()
    
#     return templates.TemplateResponse("unsubscribe_newsletter.html", {
#         "request": request,
#         "email": user.email
#     })    
    
    
# Update the subscription routes
@router.get("/subscribe_newsletter", response_class=HTMLResponse)
@router.post("/subscribe_newsletter", response_class=HTMLResponse)
async def subscribe_newsletter(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Handle GET requests (show form)
    if request.method == "GET":
        return templates.TemplateResponse("newsletter.html", {
            "request": request,
            "is_subscribed": user.newsletter_subscribed if user else False
        })
    
    # POST handling
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    if user.newsletter_subscribed:
        return RedirectResponse(url="/newsletter_status", status_code=303)
    
    user.newsletter_subscribed = True
    db.commit()
    
    return templates.TemplateResponse("newsletter.html", {
        "request": request,
        "message": "Successfully subscribed to our newsletter!",
        "is_subscribed": True
    })

@router.get("/unsubscribe_newsletter", response_class=HTMLResponse)
async def unsubscribe_newsletter(
    request: Request,
    token: str = Query(..., description="Unsubscribe token"),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.unsubscribe_token == token).first()
    if not user:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Invalid unsubscribe link"
        })
    
    user.newsletter_subscribed = False
    user.unsubscribe_token = str(uuid.uuid4())
    db.commit()
    
    return templates.TemplateResponse("newsletter.html", {
        "request": request,
        "message": "You've been unsubscribed from our newsletter",
        "is_subscribed": False,
        "email": user.email
    })

@router.post("/user/unsubscribe_newsletter", response_class=HTMLResponse)
async def user_unsubscribe_newsletter(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    user.newsletter_subscribed = False
    user.unsubscribe_token = str(uuid.uuid4())
    db.commit()
    
    return templates.TemplateResponse("newsletter.html", {
        "request": request,
        "message": "You've been unsubscribed from our newsletter",
        "is_subscribed": False,
        "email": user.email
    })

@router.get("/newsletter_status", response_class=HTMLResponse)
async def newsletter_status(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("newsletter.html", {
        "request": request,
        "is_subscribed": user.newsletter_subscribed,
        "message": f"You are {'subscribed' if user.newsletter_subscribed else 'not subscribed'} to our newsletter"
    })        
    
    
        