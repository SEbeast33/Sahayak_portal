"""
# views.py
from rest_framework import generics
from .models import Scheme
from .serializers import SchemeSerializer
from django.db.models import Q

class SchemeListAPIView(generics.ListAPIView):
    serializer_class = SchemeSerializer

    def get_queryset(self):
        queryset = Scheme.objects.all()
        q = self.request.query_params.get('q')
        category = self.request.query_params.get('category')
        state = self.request.query_params.get('state')
        gender = self.request.query_params.get('gender')
        age_group = self.request.query_params.get('age_group')
        caste = self.request.query_params.get('caste')
        ministry = self.request.query_params.get('ministry')
        residence = self.request.query_params.get('residence')
        minority = self.request.query_params.get('minority')
        differently_abled = self.request.query_params.get('differently_abled')
        benefit_type = self.request.query_params.get('benefit_type')
        language = self.request.query_params.get('language')

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(tags__icontains=q)
            )
        if category:
            queryset = queryset.filter(category__icontains=category)
        if state:
            queryset = queryset.filter(state__icontains=state)
        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)
        if caste:
            queryset = queryset.filter(caste__icontains=caste)
        if ministry:
            queryset = queryset.filter(ministry__icontains=ministry)
        if residence:
            queryset = queryset.filter(residence__icontains=residence)
        if minority:
            queryset = queryset.filter(minority=(minority.lower() == 'true'))
        if differently_abled:
            queryset = queryset.filter(differently_abled=(differently_abled.lower() == 'true'))
        if benefit_type:
            queryset = queryset.filter(benefit_type__icontains=benefit_type)
        if language:
            queryset = queryset.filter(language__iexact=language)

        return queryset

"""
# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from schemes.models import Scheme
from schemes.serializers import SchemeSummarySerializer, SchemeDetailSerializer
from elasticsearch import Elasticsearch, ConnectionError
from elasticsearch.helpers import bulk
from django.db.models import Q
from .models import Feedback
from .serializers import FeedbackSerializer
import json

# Initialize Elasticsearch client with proper configuration
try:
    es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
        timeout=30
    )
    # Test the connection
    if not es.ping():
        raise ConnectionError("Could not connect to Elasticsearch")
    ELASTICSEARCH_AVAILABLE = True
except Exception as e:
    print(f"Elasticsearch is not available: {e}")
    ELASTICSEARCH_AVAILABLE = False
    es = None

def create_index():
    """Create the Elasticsearch index if it doesn't exist"""
    if not ELASTICSEARCH_AVAILABLE:
        print("Elasticsearch is not available. Skipping index creation.")
        return False
        
    try:
        if not es.indices.exists(index='schemes'):
            # Define the index mapping
            mapping = {
                'mappings': {
                    'properties': {
                        'title': {'type': 'text', 'analyzer': 'english'},
                        'description': {'type': 'text', 'analyzer': 'english'},
                        'tags': {'type': 'text', 'analyzer': 'english'},
                        'state': {'type': 'keyword'},
                        'category': {'type': 'keyword'},
                        'ministry': {'type': 'keyword'},
                        'created_at': {'type': 'date'}
                    }
                }
            }
            es.indices.create(index='schemes', body=mapping)
            print("Successfully created Elasticsearch index")
            return True
    except Exception as e:
        print(f"Error creating index: {e}")
        return False

def index_scheme(scheme):
    """Index a single scheme in Elasticsearch"""
    if not ELASTICSEARCH_AVAILABLE:
        return False
        
    try:
        doc = {
            'title': scheme.title,
            'description': scheme.description,
            'tags': scheme.tags,
            'state': scheme.state,
            'category': scheme.category,
            'ministry': scheme.ministry,
            'created_at': scheme.created_at
        }
        es.index(index='schemes', id=scheme.id, body=doc)
        return True
    except Exception as e:
        print(f"Error indexing scheme {scheme.id}: {e}")
        return False

def index_all_schemes():
    """Index all schemes in Elasticsearch"""
    if not ELASTICSEARCH_AVAILABLE:
        print("Elasticsearch is not available. Skipping indexing.")
        return False
        
    try:
        # Create index if it doesn't exist
        if not create_index():
            return False
        
        # Get all schemes
        schemes = Scheme.objects.all()
        
        # Index each scheme
        success_count = 0
        for scheme in schemes:
            if index_scheme(scheme):
                success_count += 1
        
        print(f"Successfully indexed {success_count} out of {len(schemes)} schemes")
        return success_count > 0
    except Exception as e:
        print(f"Error in index_all_schemes: {e}")
        return False

@api_view(['GET'])
def search_schemes(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    
    if not ELASTICSEARCH_AVAILABLE:
        print("Elasticsearch is not available. Using database search.")
        # Fall back to database search
        schemes = Scheme.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        ).order_by('-created_at')
        
        paginator = Paginator(schemes, limit)
        current_page = paginator.page(page)
        
        serializer = SchemeSummarySerializer(current_page, many=True)
        
        return Response({
            'results': serializer.data,
            'total_count': paginator.count,
            'current_page': page,
            'total_pages': paginator.num_pages,
            'message': 'Using database search as Elasticsearch is not available'
        })
    
    try:
        # Elasticsearch search query
        search_body = {
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['title^3', 'description^2', 'tags'],
                    'type': 'best_fields',
                    'fuzziness': 'AUTO'
                }
            },
            'from': (page - 1) * limit,
            'size': limit
        }
        
        # Execute search
        response = es.search(index='schemes', body=search_body)
        
        # Process results
        schemes = []
        for hit in response['hits']['hits']:
            schemes.append({
                'id': hit['_id'],
                'title': hit['_source']['title'],
                'description': hit['_source']['description'],
                'tags': hit['_source']['tags'],
                'state': hit['_source']['state']
            })

        return Response({
            'results': schemes,
            'total_count': response['hits']['total']['value'],
            'current_page': page,
            'total_pages': (response['hits']['total']['value'] + limit - 1) // limit
        })
    except Exception as e:
        print(f"Elasticsearch error: {e}")
        # Fall back to database search
        schemes = Scheme.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        ).order_by('-created_at')
        
        paginator = Paginator(schemes, limit)
        current_page = paginator.page(page)
        
        serializer = SchemeSummarySerializer(current_page, many=True)
        
        return Response({
            'results': serializer.data,
            'total_count': paginator.count,
            'current_page': page,
            'total_pages': paginator.num_pages,
            'message': 'Using database search as Elasticsearch is not available'
        })

@api_view(['GET'])
def fetch_all_schemes(request):
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))

    schemes = Scheme.objects.filter(language='en').order_by('-created_at')
    paginator = Paginator(schemes, limit)
    current_page = paginator.page(page)

    serializer = SchemeSummarySerializer(current_page, many=True)

    return Response({
        'results': serializer.data,
        'total_count': paginator.count,
        'current_page': page,
        'total_pages': paginator.num_pages
    })

@api_view(['GET'])
def fetch_by_filters(request):
    filters = {}
    for field in ['state', 'age_group', 'gender', 'category', 'caste', 'residence']:
        value = request.GET.get(field)
        if value:
            filters[field] = value

    schemes = Scheme.objects.filter(language='en', **filters)

    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    paginator = Paginator(schemes, limit)
    current_page = paginator.page(page)

    serializer = SchemeSummarySerializer(current_page, many=True)
    return Response({
        'results': serializer.data,
        'total_count': paginator.count,
        'current_page': page,
        'total_pages': paginator.num_pages
    })

@api_view(['GET'])
def fetch_by_uid(request, scheme_id):
    try:
        scheme = Scheme.objects.get(id=scheme_id)
        serializer = SchemeDetailSerializer(scheme)
        return Response(serializer.data)
    except Scheme.DoesNotExist:
        return Response({'error': 'Scheme not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def feedback_api(request):
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Feedback submitted'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})
