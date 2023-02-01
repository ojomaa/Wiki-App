from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django import forms
from . import util
from markdown2 import Markdown
import random


markdowner=Markdown()

class SearchForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search here"
    }))

class NewEntryForm(forms.Form):
    title= forms.CharField(label="Title Name", widget = forms.TextInput(attrs={
        "placeholder": "Enter Title"
    }))
    content= forms.CharField(label="Content", widget = forms.Textarea(attrs={
        "placeholder": "Enter Entry Content"
    }))

class EditForm(forms.Form):
    content = forms.CharField(label="content", widget= forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm(),
    })

def entry(request, entry):
    page = util.get_entry(entry)
    page_converted= markdowner.convert(page)
    if page == "":
        return render(request, "encyclopedia/error.html", {
            "title": entry,
            "search_form":SearchForm()
        } )
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": entry,
            "content": page_converted,
            "search_form": SearchForm(),
    })

def search(request):
    if request.method == "POST":
        form= SearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            page = util.get_entry(title)
            if page:
                return redirect(reverse("entry", args=[title]))
            else:
                return render(request, "encyclopedia/search.html", {
                    "title": title,
                    "search_form": SearchForm(),
                    "related_search": util.related(title)
                })

def create(request):
    if request.method == "POST":
        form= NewEntryForm(request.POST)

        #check to see if the form is valid and if it is store it in a variable.
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
        #if the form is invalid, return an error message.
        else:
            messages.error(request, "This Entry is Invalid, please try again.")
            return render(request, "encyclopedia/create.html", {
                "search_form": SearchForm(),
                "new_form": NewEntryForm()
            })
        
        #check to see if there is already an entry with the title input into the form. if there is return a new form and give
        #the user an error message
        if util.get_entry(title):
            messages.error(request, "This title already exists, you cannot create an entry with this title.")
            return render(request, "encyclopedia/create.html", {
                "search_form": SearchForm(),
                "new_form": NewEntryForm()
            })
        #if there isnt an existing entry, save the title and content and take the user to the entry
        else:
            util.save_entry(title, content)
            return redirect(reverse("entry", args = [title]))


    elif request.method == "GET":
        return render(request, "encyclopedia/create.html", {
                "search_form": SearchForm(),
                "new_form": NewEntryForm()
        })

def edit(request, title):
    # save the content of the entry under the variable 'content' and create a form using the EditForm class we made and put the
    #content into that form.
    content = util.get_entry(title)
    form = EditForm(initial={'content': content})
    
    #allow the user to make changes to the content in the entry, save the changes and redirect to the entry page.
    if request.method == "POST":
        post_form = EditForm(request.POST)
        if post_form.is_valid():
            content = post_form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(reverse("entry", args =[title]))

        #otherwise return the edit page with the pre populated text of a specific entry
        else:
            return render(request, "encyclopedia/edit.html", {
                "edit_form": form,
                "title": title
            })
    
    #redirect to the edit page, pre populate it with the content from the entry.
    elif request.method == "GET":
        return render(request, "encyclopedia/edit.html", {
            "edit_form": form,
            "title": title
        })


def random_request(request):
    entries= util.list_entries()

    #random.choice() takes a variable and randomly selects one of its options.
    entry = random.choice(entries)
    return redirect(reverse("entry", args = [entry]))