from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Listing, Image, Comment, Upvote, Reply
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
import cloudinary.uploader
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Case, When, IntegerField


def home(request):
    allListings = Listing.objects.all()
    paginator = Paginator(allListings, 8)
    page = request.GET.get('page')
    pageListings = paginator.get_page(page)
    # Iterate over allListings to fetch imageURLs for each listing
    for listing in pageListings:
        first_image = listing.images.first()  # Get the first image for the listing
        if first_image:
            listing.image_url = first_image.imageURL  # Assign the imageURL to listing.image_url
        else:
            listing.image_url = None  # If no image is found, assign None

        if len(listing.title) > 22: # make sure the title is not too long
            listing.title = listing.title[:22] + "..."
    return render(request, "home.html", {"listings": pageListings})

@csrf_exempt
@login_required(login_url='login')
def createListing(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        price = request.POST.get('price')
        images = request.FILES.getlist('images[]')


        if len(title) == 0:
            messages.info(request, 'Title cannot be empty')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        if len(title) > 50:
            messages.info(request, 'Title cannot be longer than 50 characters')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        if len(price) == 0:
            messages.info(request, 'You have to name the price')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        if len(desc) > 1024:
            messages.info(request, f'description cannot be longer that 1024 characters, you have {len(desc)} characters')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        if len(images) == 0:
            messages.info(request, 'You have to include at least one image')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        if len(images) > 10:
            messages.info(request, 'You cannot have more than 10 images')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        if not (price.isdigit() and int(price) >= 0):
            messages.info(request, 'The price must be a non-negative integer')
            return render(request, "create-listing.html", {'title': title, 'desc': desc, 'price': price})
        
        listing = Listing.objects.create(user=request.user, title=title, text=desc, price=price)

        for img in images:
            cloudinary_response = cloudinary.uploader.upload(img)

            image_url = cloudinary_response['secure_url']

            Image.objects.create(listing=listing, imageURL=image_url)



    return render(request, "create-listing.html", {'price': 0})

# listing.html, id is the id of the listing
@csrf_exempt
def showListing(request, id):
    listing = get_object_or_404(Listing, pk=id)
    images = listing.images.all()
    initialCommentAmount = 2 # TODO: change this number

    if request.method == 'POST':
        Comment.objects.create(text=request.POST.get('comment'), user=request.user, listing=listing)
    allComments = Comment.objects.filter(listing=listing).order_by('-upvotes')
    comments = allComments[:initialCommentAmount]

    # get how many comments there are
    commentCount = len(allComments)
    if commentCount == 1:
        commentCountText = "1 Comment"
    else:
        commentCountText = str(commentCount) + " Comments"

    getCommentInfo(request.user.is_authenticated, request.user, comments) # add more neccesary info to comments

    return render(request, 'listing.html', {
            'listing': listing, 
            'images': images, 
            'comments': comments, 
            'comment_count': commentCountText, 
            'has_more_comments': commentCount > initialCommentAmount,
            'comments_loaded': initialCommentAmount
            })

@login_required(login_url='login')
def yourListings(request):
    listings = Listing.objects.filter(user=request.user)

    paginator = Paginator(listings, 8)
    page = request.GET.get('page')
    pageListings = paginator.get_page(page)
    # Iterate over listings to fetch imageURLs for each listing
    for listing in pageListings:
        first_image = listing.images.first()  # Get the first image for the listing
        if first_image:
            listing.image_url = first_image.imageURL  # Assign the imageURL to listing.image_url
        else:
            listing.image_url = None  # If no image is found, assign None

        if len(listing.title) > 22: # make sure the title is not too long
            listing.title = listing.title[:22] + "..."
    return render(request, "home.html", {"listings": pageListings, "your_listings": True})

# load more comments in listing.html
@csrf_exempt
def loadMoreComments(request):
    listing_id = request.POST.get("listing_id")
    already_loaded_comments = int(request.POST.get("loaded_count")) # how many comments are already loaded

    loadCount = 2 # how many more comments we will load

    allComments = Comment.objects.filter(listing=listing_id).order_by('-upvotes')

    endIndex = already_loaded_comments + loadCount
    moreComments = allComments[already_loaded_comments : endIndex]

    getCommentInfo(request.user.is_authenticated, request.user, moreComments) # add more neccesary info to comments

    moreCommentsList = []
    for comment in moreComments:        
        reply_list = []
        for reply in comment.replies:
            reply_list.append({
                'user': reply.user.username,
                'text': reply.text
            })

        cmt = {
            'id': comment.id,
            'text': comment.text,
            'upvotes': comment.upvotes,
            'user': comment.user.username,
            'listing': comment.listing.id,
            'liked': comment.liked,
            'has_next_page': comment.has_next_page,
            'has_prev_page': comment.has_prev_page,
            'reply_count': comment.reply_count,
            'replies': reply_list,
        }

        moreCommentsList.append(cmt)

    return JsonResponse({'more_comments': moreCommentsList, 'has_more_comments': len(allComments) > endIndex, 'comments_loaded': endIndex})


@csrf_exempt
def likeComment(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")

        try:
            comment = Comment.objects.get(id=comment_id)
            # if the user has already upvoted this comment
            if Upvote.objects.filter(comment=comment, user=request.user).exists():
                comment.upvotes -= 1
                comment.save()
                upvote = Upvote.objects.filter(comment=comment, user=request.user).first()
                if upvote:
                    upvote.delete()
                return JsonResponse({"liked": False})
            Upvote.objects.create(user=request.user, comment=comment)
            comment.upvotes += 1
            comment.save()
            return JsonResponse({"liked": True})
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Comment does not exist", "liked": False}, status=404)
    else:
        return JsonResponse({"error": "Invalid request", "liked": False}, status=400)

@csrf_exempt
def postReply(request):
    comment_id = request.POST.get("comment_id")
    reply_text = request.POST.get("reply_text")

    try:
        comment = Comment.objects.get(id=comment_id)
        Reply.objects.create(comment=comment, user=request.user, text=reply_text)
        return JsonResponse({}, status=200)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment does not exist"}, status=404)

@csrf_exempt
def getReplies(request):
    comment_id = request.POST.get("comment_id")
    page = int(request.POST.get("page"))

    repliesPerPage = 5
    startIndex = (page - 1) * repliesPerPage
    endIndex = startIndex + repliesPerPage

    if request.user.is_authenticated:
        # Create a conditional expression for sorting because we want this users replies to be at the top
        order_by_expression = Case(
            When(user=request.user, then=0),  # Assign 0 if user = request.user
            default=1,  # Assign 1 otherwise
            output_field=IntegerField()
        )
        totalReplies = Reply.objects.filter(comment=comment_id).order_by(order_by_expression)
    else:
        totalReplies = Reply.objects.filter(comment=comment_id)

    replies = totalReplies[startIndex:endIndex]

    reply_list = []
    for reply in replies:
        reply_list.append({
            'user': reply.user.username,
            'text': reply.text
        })

    return JsonResponse({'replies': reply_list,
                         'hasNextPage': len(totalReplies) > repliesPerPage * page,
                         'hasPrevPage': page > 1
                        })
@csrf_exempt
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CreateUserForm()
    

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully')
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)

@csrf_exempt
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def deleteListing(request):
    listing_id = request.POST.get("listing_id")
    
    # Check if listing_id exists and is valid
    if listing_id:
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return HttpResponse("Listing not found", status=404)
        

        images = listing.images.all()

        for image in images:
            try:
                cloudinary.api.delete_resources(image.imageURL.public_id)
            except Exception as e:
                print(f"Failed to delete image from Cloudinary: {e}")

        listing.delete()

        # refresh the page
        return HttpResponse("Listing deleted successfully", status=200)
    else:
        return HttpResponse("Invalid request", status=400)

# function to get more info about a list of comments, this is not a view
def getCommentInfo(isAuthenticated, user, comments):
    for comment in comments:
        if not isAuthenticated:
            comment.liked = False
            continue
        # if the user has upvoted this comment
        if Upvote.objects.filter(comment=comment, user=user).exists():
            comment.liked = True
        else:
            comment.liked = False

    for comment in comments: # get the first 5 replies for each comment
        if isAuthenticated:
            # Create a conditional expression for sorting because we want this users replies to be at the top
            order_by_expression = Case(
                When(user=user, then=0),  # Assign 0 if user = request.user
                default=1,  # Assign 1 otherwise
                output_field=IntegerField()
            )
            totalReplies = comment.reply_set.all().order_by(order_by_expression)
        else:
            totalReplies = comment.reply_set.all()
        comment.replies = totalReplies[:5]
        comment.has_next_page = len(totalReplies) > 5
        comment.has_prev_page = False
        if len(totalReplies) == 1:
            comment.reply_count = "1 reply"
        else:
            comment.reply_count = str(len(totalReplies)) + " replies"