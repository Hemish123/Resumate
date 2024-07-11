from django import forms


class CategoryForm(forms.Form):
    field_choices = [
        ('', 'Please Select field'),
        ('it', 'IT'),
        ('non-it', 'Non-IT'),
    ]
    category_choices = {'it' : [
                            ('category1', 'Java Developer'), ('category2', 'DotNet Developer'),
                            ('category3', 'Testing'), ('category4', 'DevOps Engineer'),
                            ('category5', 'Python Developer'), ('category6', 'Web Designing'),
                            ('category8', 'Hadoop'), ('category9', 'Blockchain'),
                            ('category10', 'ETL Developer'), ('category12', 'Data Science'),
                            ('category16', 'Database'), ('category21', 'Automation Testing'),
                            ('category22', 'Network Security Engineer'), ('category23', 'SAP Developer')
                        ],
                        'non-it' : [
                            ('category7', 'HR'), ('category11', 'Operations Manager'),
                            ('category13', 'Sales'), ('category14', 'Mechanical Engineer'),
                            ('category15', 'Arts'), ('category17', 'Electrical Engineering'),
                            ('category18', 'Health and fitness'), ('category19', 'PMO'),
                            ('category20', 'Business Analyst'), ('category24', 'Civil Engineer'),
                            ('category25', 'Advocate')
                        ]
                        }

    field = forms.ChoiceField(
        choices=field_choices,
        widget=forms.Select(attrs={'class': 'select form-control choice-class'}),
        label="Field",
        required=True
    )
    category = forms.ChoiceField(choices=[('', 'Please Select Category')],
                                 widget=forms.Select(attrs={'class': 'select form-control choice-class'}),
                                 required=True
                                 )

    def __init__(self, *args, **kwargs):
        # ignore_dropdown = kwargs.pop('ignore_dropdown', False)
        super().__init__(*args, **kwargs)
        if 'field' in self.data:
            field = self.data.get('field')
            self.fields['category'].choices = self.category_choices.get(field, [('', 'Select City')])
        # if ignore_dropdown:
        #     self.fields['field'].required = False
        #     self.fields['category'].required = False
# Roles :
# Java Developer
# Testing
# DevOps Engineer
# Python Developer
# Web Designing
# HR
# Hadoop
# Blockchain
# ETL Developer
# Operations Manager
# Data Science
# Sales
# Mechanical Engineer
# Arts
# Database
# Electrical Engineering
# Health and fitness
# PMO
# Business Analyst
# DotNet Developer
# Automation Testing
# Network Security Engineer
# SAP Developer
# Civil Engineer
# Advocate

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)