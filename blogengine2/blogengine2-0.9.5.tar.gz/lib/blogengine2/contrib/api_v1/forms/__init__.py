#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django                     import forms
from blogengine2.contrib.api_v1.model import CategoryManager, db
from .widgets import *

default_conn = db

__all__ = ['DynamicField', 'EntryForm', 'DeleteForm']

class DynamicField(forms.ChoiceField):
    '''ChoiceField subclass with builtin autocomplete widget functionality
    
    By default, use the ``choices`` argument as default iterable of values.
    '''

    def __init__(self, *args, **kwargs):
        # initialize autocomplete widget
        kwargs['widget'] = DynamicTextInput(kwargs['choices'])
        super(DynamicField, self).__init__(*args, **kwargs)

class CategoryForm(forms.Form):
    name = forms.CharField(required=True, label="Name")
    slug = forms.CharField(required=True)

class EntryForm(forms.Form):
    """Basic article entry form.""" 
    def __init__(self, db=default_conn, *args, **kwargs):
    
        _category_choices = [
        ("%s".lower()%item, str(item))for item in db.Category.find()
        ]
        self.declared_fields['category'] = forms.ChoiceField(
            choices=_category_choices, \
            required=False, 
            label='Category')
        super(EntryForm, self).__init__(*args, **kwargs)

    # source file (rst or markdown formats) to upload and convert
    # in sanitized markup
    #source = forms.CharField(
    #    #upload_to='uploads', \
    #    required=True, \
    #    label=_('File'), \
    #    widget=forms.FileInput(), \
    #    help_text=_('Valid file formats: rest, markdown, xhtml')
    #    )
            
    # think metadata like annotations
    #short_description = forms.CharField(required=True, label='Summary', \
    #    widget=forms.TextInput(),
    #    help_text='Summary of the article (140 characters or less!)'
    #    )
    # publish now?    
    #reviewed = forms.BooleanField(required=False, initial=True)
    # this needs to be prepopulated..
    #slug = forms.CharField(required=True)
    
    content = forms.CharField(label='Content', \
        widget=forms.Textarea(attrs={'rows':10, 'cols':20}),
        required=True, help_text='You can use markdown syntax here')

#AddEntryForm = EntryForm

class DeleteForm(forms.Form):
    confirm_unpublish = forms.BooleanField(label='Unpublish this entry?', required=False, initial=True)
    confirm_delete = forms.BooleanField(label='Delete this entry permanently?', required=True, initial=False)

