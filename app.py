import os
import sys
import re
from collections import Counter
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path

# 1. Inline Settings Configuration
if not settings.configured:
    settings.configure(
        DEBUG=os.environ.get("DJANGO_DEBUG", "True") == "True",
        SECRET_KEY=os.environ.get("SECRET_KEY", "lexi-fallback-secure-key-019283"),
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        ],
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(os.path.dirname(__file__), "templates")],
        }],
        ALLOWED_HOSTS=["*"],
    )

# Standard set of English "stop words" to filter out of the analytics dashboard
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", 
    "by", "about", "against", "between", "into", "through", "during", "before", 
    "after", "above", "below", "from", "up", "down", "of", "is", "am", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", 
    "does", "did", "doing", "i", "you", "he", "she", "it", "we", "they", "this", 
    "that", "these", "those", "as", "if", "that", "not", "your", "my", "our"
}

# 2. Text Processing & Analysis View
def text_analyzer_view(request):
    analysis_results = None
    raw_text = ""

    if request.method == "POST":
        raw_text = request.POST.get("analyzed_text", "")
        
        if raw_text.strip():
            # Standardize string processing: convert everything to lowercase
            clean_text = raw_text.lower()
            
            # Use regex to strip out punctuation marks and keep alphanumeric strings
            words = re.findall(r'\b\w+\b', clean_text)
            
            # Filter out numbers and irrelevant stop words
            filtered_words = [w for w in words if w not in STOP_WORDS and not w.isdigit()]
            
            # Compute frequency metrics using high-performance collections.Counter
            word_counts = Counter(filtered_words)
            
            # Extract the top 15 most frequent keywords for the UI dashboard matrix
            top_words = word_counts.most_common(15)
            
            # Calculate quick metadata summaries
            analysis_results = {
                "total_words": len(words),
                "unique_words": len(word_counts),
                "top_keywords": [{"word": word, "count": count} for word, count in top_words]
            }

    # Pass inputs and calculated outputs cleanly to the context container
    context = {
        "results": analysis_results,
        "submitted_text": raw_text
    }
    return render(request, "index.html", context)

# 3. REST Routing Specifications
urlpatterns = [
    path("", text_analyzer_view),
]

# 4. Production Application Gateway Entry
application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", __name__)
    execute_from_command_line([sys.argv[0], "runserver", "8000"])