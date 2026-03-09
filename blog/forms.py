from django import forms
from .models import Comment
from django.utils.translation import gettext_lazy as _


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment_body"]
        localized_fields = "__all__"
        widgets = {
            "comment_body": forms.Textarea(
                attrs={"placeholder": _("Write your comment here...")}
            )
        }
        labels = {"comment_body": ""}
