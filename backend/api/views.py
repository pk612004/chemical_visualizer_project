import io, os, pandas as pd, csv
from django.conf import settings
from django.http import JsonResponse, FileResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes, authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import UploadedDataset
from .serializers import UploadedDatasetSerializer
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

REQUIRED_COLUMNS = ['Equipment Name','Type','Flowrate','Pressure','Temperature']

def compute_summary(df):

    total = len(df)
    numeric = df.select_dtypes(include='number')
    averages = numeric.mean().to_dict()
    type_dist = df['Type'].value_counts().to_dict() if 'Type' in df.columns else {}
    return {'total': total, 'averages': averages, 'type_distribution': type_dist}

def cleanup_old_files():

    qs = UploadedDataset.objects.all().order_by('-uploaded_at')
    keep = list(qs[:5])
    remove = qs[5:]
    for inst in remove:
        try:
           
            path = inst.csv_file.path
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        inst.delete()

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    file = request.FILES.get('file')
    name = request.data.get('name') or (getattr(file, 'name', 'dataset') if file is not None else 'dataset')
    if not file:
        return JsonResponse({'error':'No file uploaded'}, status=400)

    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5*1024*1024)
    if file.size > max_size:
        return JsonResponse({'error': f'File too large. Max allowed size is {max_size} bytes.'}, status=400)
   
    if not name.lower().endswith('.csv'):
        return JsonResponse({'error':'Only CSV files are allowed (filename must end with .csv).'}, status=400)
    try:
     
        file.seek(0)
        df = pd.read_csv(file)
    except Exception as e:
        return JsonResponse({'error': 'Failed to parse CSV: ' + str(e)}, status=400)
   
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return JsonResponse({'error': f'Missing required columns: {missing}'}, status=400)
    
    for col in ['Flowrate','Pressure','Temperature']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if df[col].isna().all():
            return JsonResponse({'error': f'Column {col} must contain numeric values.'}, status=400)
   
    file.seek(0)
    instance = UploadedDataset.objects.create(name=name)
    instance.csv_file.save(name, ContentFile(file.read()))
   
    path = instance.csv_file.path
    df = pd.read_csv(path)
    summary = compute_summary(df)
    instance.summary_json = summary
    instance.save()
   
    cleanup_old_files()
    return JsonResponse({'id': instance.id, 'summary': summary})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def history(request):
    qs = UploadedDataset.objects.all().order_by('-uploaded_at')[:5]
    serializer = UploadedDatasetSerializer(qs, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_summary(request, pk):
    inst = get_object_or_404(UploadedDataset, pk=pk)
    return JsonResponse({'id':inst.id,'name':inst.name,'summary':inst.summary_json})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_pdf(request, pk):
    inst = get_object_or_404(UploadedDataset, pk=pk)
  
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont('Helvetica', 12)
    
    p.setFont('Helvetica-Bold', 14)
    p.drawString(30,750, f"Report for: {inst.name}")
    p.setFont('Helvetica', 11)
    p.drawString(30,735, f"Uploaded at: {inst.uploaded_at}")
    y = 710
    p.drawString(30,730, f"Uploaded at: {inst.uploaded_at}")
    summary = inst.summary_json or {}
    p.drawString(30,y, 'Summary:')
    y -= 16
    totals = summary.get('total')
    if totals is not None:
        p.drawString(40,y, f"Total rows: {totals}")
        y -= 14
  
    avgs = summary.get('averages', {})
    if avgs:
        p.drawString(40,y, 'Averages:')
        y -= 14
        for k,v in avgs.items():
            p.drawString(48,y, f"{k}")
            p.drawRightString(550, y, f"{v}")
            y -= 14
            if y < 100:
                p.showPage(); p.setFont('Helvetica',11); y = 750
   
    td = summary.get('type_distribution', {})
    if td:
        p.drawString(40,y, 'Type distribution:')
        y -= 14
        for k,v in td.items():
            p.drawString(48,y, f"{k}")
            p.drawRightString(550, y, f"{v}")
            y -= 14
            if y < 100:
                p.showPage(); p.setFont('Helvetica',11); y = 750
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'report_{inst.id}.pdf')



from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@parser_classes([FormParser, MultiPartParser])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def register(request):
    '''Register a new user and return auth token.'''
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return JsonResponse({'error':'username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error':'username already exists'}, status=400)
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse({'token': token.key}, status=201)
