from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.contrib.admin import ModelAdmin, AdminSite
import asyncio

from datetime import datetime
from .models import *
import pandas as pd
import tensorflow as tf
from keras.models import load_model, model_from_json
import pyshark
import csv

model = load_model('tempdata/static/ml/det_model.h5')


def time_to_fraction(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S.%f').time()
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6
    fraction_of_day = total_seconds / (24 * 3600)
    return fraction_of_day


def pred():
    df = pd.read_csv('tempdata/static/ml/captured_packets.csv')
    tm = df['Time']
    df = df.drop(columns=['Destination', 'Info'])

    df['Time'] = df['Time'].apply(lambda x: time_to_fraction(x.split(' ')[1]))
    gd = df.iloc[-1]
    time=gd['Time']
    lth = gd['Length']
    pt = gd['Protocol']
    ip = gd['Source']
    if ip != 'nan':
        if pt == 'TCP':
            pt = pt.replace('TCP','4')
        elif pt == 'ARP':
            pt = pt.replace('ARP','0')
        elif pt == 'TLSv1.2':
            pt = pt.replace('TLSv1.2','5')
        elif pt == 'DNS':
            pt = pt.replace('DNS','1')
        elif pt == 'TLSv1.3':
            pt = pt.replace('TLSv1.3','6')
        elif pt == 'OCSP':
            pt = pt.replace('OCSP','2')
        elif pt == 'QUIC':
            pt = pt.replace('QUIC','3')
        else:
            pass

        pt = int(pt)
        rdf = pd.DataFrame([pd.Series([time,lth,pt])])
        predict = model.predict(rdf)    
        if predict[0][0] > 0.6:
            tp = 'ddos'
            obj = AttackLog(attack_type=tp,timestamp=tm,attacker_ip=ip)
            obj.save()
        else:
            pass


interface = 'Wi-Fi'
cap = pyshark.LiveCapture(interface=interface, display_filter='tcp')
captured_packets = []
try:
    for packet in cap.sniff_continuously(packet_count=25):
        time = packet.sniff_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        source = packet.ip.src if 'ip' in packet else 'N/A'
        destination = packet.ip.dst if 'ip' in packet else 'N/A'
        length = packet.length
        protocol = packet.transport_layer if hasattr(packet, 'transport_layer') else 'N/A'

        captured_packets.append({
            'Time': time,
            'Source': source,
            'Destination': destination,
            'Length': length,
            'Protocol': protocol
        })

except KeyboardInterrupt:
    print('Capture stopped by user.')

finally:
    cap.close()
    csv_filename = 'tempdata/static/ml/captured_packets.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'Source', 'Destination', 'Length', 'Info', 'Protocol']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for packet_data in captured_packets:
            writer.writerow(packet_data)

pred()
        



def index(request):
    return render(request, 'index.html')

def login_page(request):
    return render(request,'login.html')

def login(request):    
    print('inside')
    username = request.POST.get('username')
    password = request.POST.get('password')
    print('<--',username,password,'-->')
    user = User.objects.get(username=username)
    if user is not None:
        # login(request, user)
        print('user')
        if user.username == 'root':
            print('root yes')
            return HttpResponse("<script>window.location.href='/pred_page/'</script>")
            return JsonResponse({"status": "admin"})
        else:
            print('user yes')
            return HttpResponse("<script>window.location.href='/index/'</script>")
            return JsonResponse({"status": "authorized"})
        
    else:
        print('not user')
        return HttpResponse("<script>alert('Unauthorized');window.location.href='/login_page/'</script>")
        return JsonResponse({"status": "unauthorized"})
    


def pred_page(request):      
    obj = AttackLog.objects.all()
    ob = AttackLog.objects.count()
    return render(request,'pred.html',{'users':obj,'count':ob})