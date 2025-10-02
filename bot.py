from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import os
import time

app = Flask(__name__)
app.secret_key = 'rusyagelirsenins1keroldurur9494'  # Güvenli secret key

# reCAPTCHA anahtarları
RECAPTCHA_SITE_KEY = '6LeZbdwrAAAAAJiGDLXDhGDQYR7tP47Ew0DivbXm'
RECAPTCHA_SECRET_KEY = '6LeZbdwrAAAAAL-Bfj649b4c-VOlRZNexx5Ibapr'

@app.before_request
def check_verification():
    # Statik dosyalar ve robot doğrulama sayfası için kontrol yapma
    if request.endpoint in ['static', 'robot_dogrulama', 'verify_recaptcha', 'logout']:
        return
    
    # Eğer reCAPTCHA doğrulanmamışsa robot doğrulama sayfasına yönlendir
    if not session.get('recaptcha_verified'):
        return redirect(url_for('robot_dogrulama'))

@app.route('/')
def index():
    # reCAPTCHA doğrulanmışsa index sayfasını göster
    return render_template('index.html')

@app.route('/robot-dogrulama', methods=['GET', 'POST'])
def robot_dogrulama():
    # Eğer zaten doğrulanmışsa ana sayfaya yönlendir
    if session.get('recaptcha_verified'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # reCAPTCHA doğrulama
        recaptcha_response = request.form.get('g-recaptcha-response')
        
        if not recaptcha_response:
            error_message = "Lütfen reCAPTCHA'yı doğrulayın."
            return render_template('robot_dogrulama.html', 
                                site_key=RECAPTCHA_SITE_KEY,
                                error_message=error_message)
        
        # Google reCAPTCHA doğrulama isteği
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
            'remoteip': request.remote_addr
        }
        
        try:
            response = requests.post(verify_url, data=data, timeout=10)
            result = response.json()
            
            if result.get('success'):
                # reCAPTCHA başarılı
                session['recaptcha_verified'] = True
                session['verified_at'] = time.time()
                return redirect(url_for('index'))
            else:
                # reCAPTCHA başarısız
                error_message = "reCAPTCHA doğrulaması başarısız. Lütfen tekrar deneyin."
                return render_template('robot_dogrulama.html', 
                                    site_key=RECAPTCHA_SITE_KEY,
                                    error_message=error_message)
                
        except requests.exceptions.RequestException as e:
            error_message = "Doğrulama servisine ulaşılamıyor. Lütfen daha sonra tekrar deneyin."
            return render_template('robot_dogrulama.html', 
                                site_key=RECAPTCHA_SITE_KEY,
                                error_message=error_message)
    
    # GET isteği için reCAPTCHA sayfasını göster
    return render_template('robot_dogrulama.html', site_key=RECAPTCHA_SITE_KEY)

@app.route('/verify-recaptcha', methods=['POST'])
def verify_recaptcha():
    """AJAX endpoint for reCAPTCHA verification"""
    recaptcha_response = request.json.get('g-recaptcha-response')
    
    if not recaptcha_response:
        return jsonify({'success': False, 'message': 'Lütfen reCAPTCHA\'yı doğrulayın.'})
    
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response,
        'remoteip': request.remote_addr
    }
    
    try:
        response = requests.post(verify_url, data=data, timeout=10)
        result = response.json()
        
        if result.get('success'):
            session['recaptcha_verified'] = True
            session['verified_at'] = time.time()
            return jsonify({'success': True, 'redirect': url_for('index')})
        else:
            return jsonify({'success': False, 'message': 'reCAPTCHA doğrulaması başarısız.'})
            
    except requests.exceptions.RequestException:
        return jsonify({'success': False, 'message': 'Doğrulama servisine ulaşılamıyor.'})

@app.route('/logout')
def logout():
    # Oturumu temizle
    session.pop('recaptcha_verified', None)
    session.pop('verified_at', None)
    return redirect(url_for('robot_dogrulama'))

# API test endpoint'leri
@app.route('/api/test/<api_name>')
def test_api(api_name):
    return jsonify({
        'status': 'success', 
        'message': f'{api_name} API testi başlatılıyor...',
        'timestamp': time.time()
    })

@app.route('/api/copy/<path:api_url>')
def copy_api_url(api_url):
    return jsonify({
        'status': 'success', 
        'message': 'API URL panoya kopyalandı',
        'url': api_url
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
