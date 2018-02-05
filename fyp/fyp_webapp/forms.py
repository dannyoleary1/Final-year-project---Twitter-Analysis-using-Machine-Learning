from django import forms

class LDAForm(forms.Form):
    samples = forms.IntegerField(initial=2000)
    features = forms.IntegerField(initial=1000)
    components = forms.IntegerField(initial=3)
    top_words = forms.IntegerField(initial=5)

class KMeansForm(forms.Form):
    clusters = forms.IntegerField(initial=2)
    n_init = forms.IntegerField(initial=100)
    verbose = forms.IntegerField(initial=1)

class NMFForm(forms.Form):
    samples = forms.IntegerField(initial=2000)
    features = forms.IntegerField(initial=1000)
    components = forms.IntegerField(initial=3)
    top_words = forms.IntegerField(initial=5)


