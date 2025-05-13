from typing import Optional
from fastapi import APIRouter,Request, Depends, HTTPException, status
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from sqlalchemy.orm import Session
from app.models import User, Session, Tour,TourImage
from app.utils import get_current_user, create_session, delete_session,verify_password, get_user_initials,hash_password, get_current_admin
from app.database import get_db
#from app.database import Sessionlocal as DBSession


router = APIRouter()

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
    return templates.TemplateResponse(
        "tours.html",
        {
            "request": request,
            "title": "Our Tours",
            "is_logged_in": user is not None,
            "user": user
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All fields are required")
    
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    session_id = create_session(db, user.id)
    
    response = RedirectResponse(url="/tours", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=1800)
    return response
@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(db, session_id)
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")
    return response   
    
@router.get('/admin/dashboard', response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_admin)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this page")
    tours=db.query(Tour).all()
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": user, "tours": tours})

# create a tour
@router.post('/admin/tours/create', response_class=HTMLResponse)
async def create_tour(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_admin)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this page")
    
    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    price = form.get("price")
    duration = form.get("duration")
    locations = form.get("locations")
    image_urls = form.getlist[str]=Form(...),
    
    if not all([title, description, price, duration, locations, ])or not image_urls:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All fields are required")
    
    new_tour = Tour(
        title=title,
        description=description,
        price=price,
        duration=duration,
        locations=locations,
        
    )
    
    db.add(new_tour)
    db.flush()
    for idx, image_url in enumerate(image_urls):
        tour_image = TourImage(tour_id=new_tour.id, image_url=image_url, is_primary=(idx == 0))
        db.add(tour_image)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    
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
    if image_url:
        tour.image_url = image_url
    
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
    
    db.delete(tour)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

## edit tour
@router.get('/admin/tours/edit/{tour_id}', response_class=HTMLResponse)
async def edit_tour(request: Request, tour_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_admin)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this page")
    
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    
    if not tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    
    return templates.TemplateResponse("admin/edit_tour.html", {"request": request, "tour": tour})
    
    