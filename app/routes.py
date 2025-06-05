import uuid
import os
import stripe
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from fastapi import APIRouter,Request, Depends, HTTPException, status
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.models import User, Session, Tour,TourImage, Booking
from app.utils import get_current_user, create_session, delete_session,verify_password,hash_password, get_current_admin,send_email,get_authenticated_user
from app.database import get_db
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from datetime import timedelta
from fastapi import File, UploadFile
from sqlalchemy.orm import joinedload
from fastapi.responses import JSONResponse

#from app.database import Sessionlocal as DBSession

from dotenv import load_dotenv
load_dotenv()
router = APIRouter()
temporary_reset_tokens = {}
UPLOAD_DIR = "app/static/uploads/tours"
 

templates = Jinja2Templates(directory="app/templates")# template setup
@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Uganda Tours"})

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

#delete tour
@router.post('/admin/tours/delete/{tour_id}', response_class=HTMLResponse)
async def delete_tour(request: Request, tour_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_admin)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this page")
    
    tour = db.query(Tour).filter(Tour.id == tour_id).first()

    if not tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    
    # Delete related images first
    db.query(TourImage).filter(TourImage.tour_id == tour.id).delete()

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
        reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
        subject = "Forgot Password"
        body = f"Password reset Request, Click here to reset your password: {reset_link}"
        try:
            await send_email(user.email, subject, body) 
        except Exception as e: 
            return templates.TemplateResponse("forgot_password.html", {"request": request, "error": f"Failed to send email: {str(e)}"})

        return templates.TemplateResponse("forgot_password.html", {"request": request, "message": "Reset link sent!"})
    
    except Exception as e:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "An unexpected error occurred."})
## resetting password logic
# Remove the separate GET handler and consolidate into one endpoint
@router.get("/reset-password", response_class=HTMLResponse)
@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str = Form(None),
    new_password: str = Form(None),
    confirm_password: str = Form(None),
    db: Session = Depends(get_db)
):
    # Handle GET request
    if request.method == "GET":
        token = request.query_params.get("token")
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
        
        # Check expiration for GET requests too
        token_info = temporary_reset_tokens.get(token)
        if token_info and datetime.utcnow() > token_info["expires"]:
            del temporary_reset_tokens[token]
            return templates.TemplateResponse("reset_password.html", {
                "request": request,
                "error": "Token has expired"
            })
        
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token
        })

    # Handle POST request
    error = None
    try:
        # Server-side validation
        if not token:
            error = "Missing reset token"
            raise ValueError
        
        if not new_password or not confirm_password:
            error = "Please fill in all fields"
            raise ValueError
        
        if new_password != confirm_password:
            error = "Passwords do not match"
            raise ValueError
        
        if len(new_password) < 8:
            error = "Password must be at least 8 characters"
            raise ValueError

        # Token validation
        if token not in temporary_reset_tokens:
            error = "Invalid or expired token"
            raise ValueError

        token_info = temporary_reset_tokens[token]
        if datetime.utcnow() > token_info["expires"]:
            del temporary_reset_tokens[token]
            error = "Token has expired"
            raise ValueError

        # Update user password
        email = token_info["email"]
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            error = "User not found"
            raise ValueError

        # Hash password and update
        hashed_password = hash_password(new_password)
        user.hashed_password = hashed_password
        db.commit()
        db.refresh(user)
        print("upt password:",user.password)

        # Cleanup
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

        # Store booking in session
        request.session['booking'] = {
            "tour_id": tour_id,
            "adults": adults,
            "kids": kids,
            "tour_date": tour_date,
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
                'total_price': booking_data['total_price']
            },
            success_url=str(request.url_for('payment_success')) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=str(request.url_for('payment_page'))
        )

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
        await send_email(
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