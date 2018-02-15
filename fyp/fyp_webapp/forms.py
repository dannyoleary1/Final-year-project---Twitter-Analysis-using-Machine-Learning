from django import forms
import datetime

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

class DateInput(forms.DateInput):
    input_type = 'date'

class OldTweetsForm(forms.Form):
    index_name = forms.CharField()
    start_date = forms.DateField(input_formats=['%Y-%m-%d',      # '2006-10-25'
                                                '%m/%d/%Y',      # '10/25/2006'
                                                '%m/%d/%y',     # '10/25/06'
                                                "%d/%m/%Y",        #25/10/2006
                                                "%Y/%m/%d",     # 2006/10/25
                                                  ])
    end_date = forms.DateField(input_formats=['%Y-%m-%d',      # '2006-10-25'
                                                '%m/%d/%Y',      # '10/25/2006'
                                                '%m/%d/%y',     # '10/25/06'
                                                "%d/%m/%Y",        #25/10/2006
                                                "%Y/%m/%d",     # 2006/10/25
                                                  ])
    def clean(self):
        cleaned_data = super(OldTweetsForm, self).clean()
        print (cleaned_data.get("index_name"))
        print (cleaned_data.get("start_date"))
        print (cleaned_data.get("end_date"))
        end_date = cleaned_data['end_date']
       # index_name = cleaned_data['index_name']

       # start_date = cleaned_data['start_date']
        # do your cleaning here
        return cleaned_data


