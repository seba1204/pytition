"""Forms for social network settings of petitions."""

from django import forms


# This form is not rendered like the others, it is just used to "parse" POSTed data
class SocialNetworkForm(forms.Form):
    """Social Network settings of Petition."""

    twitter_description = forms.CharField(max_length=200, required=False)
    twitter_image = forms.FileField(max_length=500, required=False)
    org_twitter_handle = forms.CharField(max_length=20, required=False)
    remove_twitter_image = forms.BooleanField(required=False, initial=False)
    has_email_share_button = forms.BooleanField(required=False)
    has_facebook_share_button = forms.BooleanField(required=False)
    has_tumblr_share_button = forms.BooleanField(required=False)
    has_linkedin_share_button = forms.BooleanField(required=False)
    has_twitter_share_button = forms.BooleanField(required=False)
    has_mastodon_share_button = forms.BooleanField(required=False)
    has_whatsapp_share_button = forms.BooleanField(required=False)
