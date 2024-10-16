from django import forms
from .models import Article, Subcategory, Category, Comment, Subscription

class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles."""

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'subcategory', 'image', 'youtube_link']

    def __init__(self, *args, **kwargs):
        """Initialize the form and update widget attributes for styling."""
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['subcategory'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['youtube_link'].widget.attrs.update({'class': 'form-control'})

        # Update subcategory choices based on selected category
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty subcategories
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.order_by('name')
        else:
            self.fields['subcategory'].queryset = Subcategory.objects.none()

class CommentForm(forms.ModelForm):
    """Form for creating comments on articles."""

    class Meta:
        model = Comment
        fields = ['content', 'parent']  # Include the 'parent' field for threaded comments

    def __init__(self, *args, **kwargs):
        """Initialize the form and update widget attributes for styling."""
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Leave a comment...'
        })
        self.fields['content'].required = True  # Make content required
        self.fields['parent'].widget = forms.HiddenInput()  # Hide the parent field, used internally for replies

    def clean_content(self):
        """Validate the content to ensure it is not empty or only whitespace."""
        content = self.cleaned_data.get('content')
        if not content.strip():
            raise forms.ValidationError("Comment content cannot be empty.")
        return content

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email', 'category', 'subcategory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially set subcategory to empty
        self.fields['subcategory'].choices = [('', 'Select a subcategory')]
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].choices = [
                    (subcategory.id, subcategory.name) for subcategory in Subcategory.objects.filter(category_id=category_id)
                ]
            except (ValueError, TypeError):
                pass  # Invalid input; ignore and leave subcategory choices empty
        elif self.instance.pk:
            # Populate subcategory choices if the instance is being edited
            self.fields['subcategory'].choices = [
                (subcategory.id, subcategory.name) for subcategory in self.instance.category.subcategories.all()
            ]